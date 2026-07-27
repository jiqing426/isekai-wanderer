"""Dialogue quota service — dynamic gradient quota engine (CR-016)."""

import logging
import uuid
from datetime import datetime, timezone, date, timedelta
from typing import Dict, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dialogue_quota import DialogueQuota, LifecycleStage
from app.models.user import User
from app.services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)

# Quota by lifecycle stage
LIFECYCLE_QUOTAS: Dict[str, int] = {
    LifecycleStage.honeymoon.value: 10,
    LifecycleStage.growth.value: 5,
    LifecycleStage.regular.value: 3,
    LifecycleStage.returnee.value: 5,  # 3-day returnee window
}

# Lifecycle stage thresholds
HONEYMOON_DAYS = 3   # registration day 1-3
GROWTH_DAYS = 7      # registration day 4-7
# regular = day 8+
RETURNEE_INACTIVE_DAYS = 7  # 7+ days no login → returnee
RETURNEE_DURATION_DAYS = 3  # returnee stage lasts 3 days


class QuotaService:
    """Service for dynamic dialogue quota management."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._subscription_service = SubscriptionService(db)

    async def _get_user(self, user_id: uuid.UUID) -> Optional[User]:
        """Fetch user record."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def calculate_lifecycle_stage(self, user: User) -> str:
        """Determine user's lifecycle stage based on registration and login patterns.

        Priority: honeymoon > returnee (within 3-day window) > growth > regular

        Args:
            user: User ORM object

        Returns:
            LifecycleStage string value
        """
        now = datetime.now(timezone.utc)
        created_at = user.created_at

        if created_at.tzinfo is None:
            from datetime import timezone as tz
            created_at = created_at.replace(tzinfo=tz.utc)

        days_since_registration = (now - created_at).days

        # Day 1-3: honeymoon
        if days_since_registration <= HONEYMOON_DAYS:
            return LifecycleStage.honeymoon.value

        # Check returnee: user has returnee_activated_at and still within 3-day window
        if user.returnee_activated_at:
            activated_at = user.returnee_activated_at
            if activated_at.tzinfo is None:
                from datetime import timezone as tz
                activated_at = activated_at.replace(tzinfo=tz.utc)
            days_since_activation = (now - activated_at).days
            if days_since_activation < RETURNEE_DURATION_DAYS:
                return LifecycleStage.returnee.value
            # Returnee window expired — clear the field
            # (will be re-set on next qualifying return)

        # Check if user qualifies as returnee now (7+ days inactive)
        if user.last_login:
            last_login = user.last_login
            if last_login.tzinfo is None:
                from datetime import timezone as tz
                last_login = last_login.replace(tzinfo=tz.utc)
            days_since_last_login = (now - last_login).days
            if days_since_last_login >= RETURNEE_INACTIVE_DAYS:
                # Activate returnee status — set the timestamp
                user.returnee_activated_at = now
                return LifecycleStage.returnee.value

        # Day 4-7: growth
        if days_since_registration <= GROWTH_DAYS:
            return LifecycleStage.growth.value

        # Day 8+: regular
        return LifecycleStage.regular.value

    async def get_daily_base_quota(self, user_id: uuid.UUID) -> int:
        """Get daily base quota for user based on lifecycle stage.

        Returns:
            Base quota count (10/5/3) or 0 if subscribed (unlimited)
        """
        # Subscribed users are exempt from dynamic quota
        if await self._subscription_service.is_exempt_from_quota(user_id):
            return -1  # unlimited

        user = await self._get_user(user_id)
        if not user:
            return LIFECYCLE_QUOTAS[LifecycleStage.regular.value]

        stage = await self.calculate_lifecycle_stage(user)
        return LIFECYCLE_QUOTAS.get(stage, LIFECYCLE_QUOTAS[LifecycleStage.regular.value])

    async def _get_or_create_quota(self, user_id: uuid.UUID, today: date, for_update: bool = False) -> DialogueQuota:
        """Get today's quota record or create one.
        
        Args:
            user_id: User UUID
            today: Date to get quota for
            for_update: If True, use SELECT FOR UPDATE to lock the row
        """
        stmt = select(DialogueQuota).where(
            and_(
                DialogueQuota.user_id == user_id,
                DialogueQuota.date == today,
            )
        )
        if for_update:
            stmt = stmt.with_for_update()
        
        result = await self.db.execute(stmt)
        quota = result.scalar_one_or_none()
        if not quota:
            base_quota = await self.get_daily_base_quota(user_id)
            # For subscribed users (base_quota == -1), store a sentinel
            quota = DialogueQuota(
                user_id=user_id,
                date=today,
                base_quota=base_quota if base_quota != -1 else -1,
                consumed=0,
                fragment_extra=0,
                fragment_consumed=0,
            )
            self.db.add(quota)
            await self.db.flush()
        return quota

    async def get_user_quota_status(self, user_id: uuid.UUID) -> Dict:
        """Get current quota status for user.

        Returns:
            Dict with base_quota, consumed, fragment_extra, fragment_consumed, remaining, is_exempt
        """
        is_exempt = await self._subscription_service.is_exempt_from_quota(user_id)
        today = datetime.now(timezone.utc).date()
        quota = await self._get_or_create_quota(user_id, today)

        # BUG-005 fix: If user is now subscribed but quota record still has
        # free-tier base_quota, update it to unlimited (-1)
        if is_exempt and quota.base_quota != -1:
            quota.base_quota = -1
            await self.db.flush()

        base_remaining = max(0, quota.base_quota - quota.consumed) if quota.base_quota != -1 else -1
        fragment_remaining = max(0, quota.fragment_extra - quota.fragment_consumed)

        if base_remaining == -1:
            remaining = -1  # unlimited
        else:
            remaining = base_remaining + fragment_remaining

        return {
            "base_quota": quota.base_quota,
            "consumed": quota.consumed,
            "fragment_extra": quota.fragment_extra,
            "fragment_consumed": quota.fragment_consumed,
            "remaining": remaining,
            "is_exempt": is_exempt,
        }

    async def consume_quota(self, user_id: uuid.UUID) -> bool:
        """Consume one quota unit. Uses base quota first, then fragment.
        
        Uses SELECT FOR UPDATE to prevent concurrent consumption issues.

        Returns:
            True if consumption succeeded, False if no quota remaining.
        """
        # Subscribed users always succeed
        if await self._subscription_service.is_exempt_from_quota(user_id):
            return True

        today = datetime.now(timezone.utc).date()
        # Lock the row to prevent concurrent consumption
        quota = await self._get_or_create_quota(user_id, today, for_update=True)

        # Try base quota first
        if quota.base_quota != -1 and quota.consumed < quota.base_quota:
            quota.consumed += 1
            await self.db.flush()
            return True

        # Then fragment quota
        if quota.fragment_consumed < quota.fragment_extra:
            quota.fragment_consumed += 1
            await self.db.flush()
            return True

        # No quota remaining
        return False

    async def add_fragment_quota(self, user_id: uuid.UUID, amount: int) -> None:
        """Add fragment-purchased extra quota.

        Args:
            user_id: User UUID
            amount: Number of extra dialogue units to add
        """
        today = datetime.now(timezone.utc).date()
        quota = await self._get_or_create_quota(user_id, today)
        quota.fragment_extra += amount
        await self.db.flush()
        logger.info(f"Fragment quota added: user={user_id}, amount={amount}")

    async def reset_all_daily_quotas(self) -> int:
        """Reset all daily quotas at UTC 00:00.

        - Base quota is refreshed (new record created with new day)
        - Fragment extra is zeroed (does not carry over)

        Returns:
            Number of quota records affected (from previous day)
        """
        today = datetime.now(timezone.utc).date()
        yesterday = today - timedelta(days=1)

        # Fragment extra doesn't carry over — zero out yesterday's records
        result = await self.db.execute(
            select(DialogueQuota).where(DialogueQuota.date == yesterday)
        )
        old_quotas = result.scalars().all()
        count = len(old_quotas)

        # We don't delete old records (audit trail); new day creates new records
        # Fragment carryover prevention: old records' fragment_extra is irrelevant
        # because new records start with fragment_extra=0

        logger.info(f"Daily quota reset: {count} records from {yesterday}")
        return count

    async def is_exempt_from_quota(self, user_id: uuid.UUID) -> bool:
        """Check if user is exempt from quota (subscribed users).

        Args:
            user_id: User UUID

        Returns:
            True if subscribed, False otherwise
        """
        return await self._subscription_service.is_exempt_from_quota(user_id)

    async def get_lifecycle_info(self, user_id: uuid.UUID) -> Dict:
        """Get lifecycle stage info for a user.

        Returns:
            Dict with stage, days_since_registration, days_since_last_login, daily_base_quota
        """
        user = await self._get_user(user_id)
        if not user:
            return {
                "stage": LifecycleStage.regular.value,
                "days_since_registration": 0,
                "days_since_last_login": None,
                "daily_base_quota": LIFECYCLE_QUOTAS[LifecycleStage.regular.value],
            }

        now = datetime.now(timezone.utc)
        created_at = user.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        days_since_reg = (now - created_at).days
        days_since_login = None
        if user.last_login:
            last_login = user.last_login
            if last_login.tzinfo is None:
                last_login = last_login.replace(tzinfo=timezone.utc)
            days_since_login = (now - last_login).days

        stage = await self.calculate_lifecycle_stage(user)
        base_quota = await self.get_daily_base_quota(user_id)

        return {
            "stage": stage,
            "days_since_registration": days_since_reg,
            "days_since_last_login": days_since_login,
            "daily_base_quota": base_quota,
        }
