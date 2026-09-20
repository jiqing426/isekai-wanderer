"""Subscription service — tier management and permission checks (CR-016)."""

import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import Subscription, SubscriptionTier, SubscriptionStatus
from app.models.payment import Subscription as LegacySubscription, Fragment, FragmentTransaction
from app.models.user import User
from app.schemas.subscription import TierPermissions

logger = logging.getLogger(__name__)


# Tier fragment quotas (monthly)
TIER_FRAGMENT_QUOTAS: Dict[str, int] = {
    SubscriptionTier.free.value: 0,
    SubscriptionTier.basic.value: 300,
    SubscriptionTier.standard.value: 600,
    SubscriptionTier.premium.value: 1200,
}


# Tier permission definitions
TIER_PERMISSIONS: Dict[str, TierPermissions] = {
    SubscriptionTier.free.value: TierPermissions(
        archive_limit=1,           # PRD: 1 个存档位
        script_access="trial_only",
        voice_enabled=False,
        rewind_c15=False,
        ugc_access=False,
        fragment_discount=0.0,     # PRD: 无折扣
        hidden_options=False,
        dialogue_limit=0,          # 使用动态梯度额度
    ),
    SubscriptionTier.basic.value: TierPermissions(
        archive_limit=5,           # PRD: 5 个存档位
        script_access="all_normal",
        voice_enabled=False,
        rewind_c15=False,
        ugc_access=False,
        fragment_discount=0.0,     # PRD: 无折扣
        hidden_options=False,
        dialogue_limit=30,         # PRD: 30次/天
    ),
    SubscriptionTier.standard.value: TierPermissions(
        archive_limit=-1,          # PRD: 无限存档
        script_access="all_normal",
        voice_enabled=True,
        rewind_c15=True,
        ugc_access=False,
        fragment_discount=0.0,     # PRD: 无折扣
        hidden_options=True,
        dialogue_limit=-1,         # 无限
    ),
    SubscriptionTier.premium.value: TierPermissions(
        archive_limit=-1,
        script_access="all_including_exclusive",
        voice_enabled=True,
        rewind_c15=True,
        ugc_access=True,
        fragment_discount=0.7,     # PRD: 7 折 = 0.7
        hidden_options=True,
        dialogue_limit=-1,
    ),
}


class SubscriptionService:
    """Service for subscription tier and permission management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_tier(self, user_id: uuid.UUID) -> str:
        """Get current subscription tier for user.
        
        Returns the tier string (free/basic/standard/premium).
        Falls back to 'free' if no active subscription found.
        """
        # First check user.subscription_tier for quick lookup
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user and user.subscription_tier and user.subscription_tier != "free":
            # Verify there's an active subscription record
            sub_result = await self.db.execute(
                select(Subscription).where(
                    Subscription.user_id == user_id,
                    Subscription.status == SubscriptionStatus.active.value
                ).order_by(Subscription.started_at.desc())
            )
            sub = sub_result.scalar_one_or_none()
            if sub:
                # Check if subscription is still valid
                if sub.expires_at and sub.expires_at < datetime.now(timezone.utc):
                    # Subscription expired, update status
                    sub.status = SubscriptionStatus.expired.value
                    user.subscription_tier = SubscriptionTier.free.value
                    await self.db.flush()
                    return SubscriptionTier.free.value
                return sub.tier
        
        return SubscriptionTier.free.value

    async def get_tier_permissions(self, tier: str) -> TierPermissions:
        """Get all permissions for a specific tier.
        
        Args:
            tier: Subscription tier string (free/basic/standard/premium)
            
        Returns:
            TierPermissions object with all permissions for the tier
        """
        return TIER_PERMISSIONS.get(tier, TIER_PERMISSIONS[SubscriptionTier.free.value])

    async def check_permission(self, user_id: uuid.UUID, permission_name: str) -> bool:
        """Check if user has a specific permission.
        
        Args:
            user_id: User UUID
            permission_name: Name of the permission to check
            
        Returns:
            True if user has the permission, False otherwise
        """
        tier = await self.get_user_tier(user_id)
        permissions = await self.get_tier_permissions(tier)
        
        if not hasattr(permissions, permission_name):
            logger.warning(f"Unknown permission: {permission_name}")
            return False
        
        value = getattr(permissions, permission_name)
        
        # For boolean permissions, return directly
        if isinstance(value, bool):
            return value
        
        # For numeric permissions, check if > 0 or == -1 (unlimited)
        if isinstance(value, (int, float)):
            return value != 0
        
        # For string permissions (like script_access), check if not empty/restricted
        if isinstance(value, str):
            return value != "" and value != "trial_only"
        
        return bool(value)

    async def get_permission_value(self, user_id: uuid.UUID, permission_name: str) -> Any:
        """Get the actual value of a permission for a user.
        
        Args:
            user_id: User UUID
            permission_name: Name of the permission
            
        Returns:
            The permission value (bool, int, str, or float)
        """
        tier = await self.get_user_tier(user_id)
        permissions = await self.get_tier_permissions(tier)
        
        if not hasattr(permissions, permission_name):
            logger.warning(f"Unknown permission: {permission_name}")
            return None
        
        return getattr(permissions, permission_name)

    async def on_subscription_created(
        self,
        user_id: uuid.UUID,
        tier: str,
        expires_at: datetime | None = None
    ) -> Subscription:
        """Handle subscription creation/activation.
        
        Args:
            user_id: User UUID
            tier: New subscription tier
            expires_at: Subscription expiration time
            
        Returns:
            Created Subscription record
        """
        # Create new subscription record (CR-016 table)
        subscription = Subscription(
            user_id=user_id,
            tier=tier,
            status=SubscriptionStatus.active.value,
            started_at=datetime.now(timezone.utc),
            expires_at=expires_at,
            fragment_quota=TIER_FRAGMENT_QUOTAS.get(tier, 0),
            last_fragment_grant_at=datetime.now(timezone.utc),
            next_fragment_grant_at=datetime.now(timezone.utc) + timedelta(days=30),
        )
        self.db.add(subscription)
        
        # Update user's subscription_tier
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user:
            user.subscription_tier = tier
        
        # Sync to legacy subscriptions table for backward compatibility
        price_map = {
            "basic": 1.99,
            "standard": 4.99,
            "premium": 9.99,
        }
        legacy_sub = LegacySubscription(
            user_id=user_id,
            plan_id=tier,
            status="active",
            started_at=datetime.now(timezone.utc),
            expires_at=expires_at,
            price=price_map.get(tier, 0.0),
            quota_total=50 if tier == "free" else 999999,
            quota_used=0,
            quota_period="honeymoon" if tier == "free" else None,
            auto_renew=False,
        )
        self.db.add(legacy_sub)
        
        await self.db.flush()

        # BUG-005 fix: Update today's dialogue_quota record to reflect
        # the new subscription status (base_quota = -1 means unlimited).
        if tier != SubscriptionTier.free.value:
            from app.models.dialogue_quota import DialogueQuota
            today = datetime.now(timezone.utc).date()
            quota_result = await self.db.execute(
                select(DialogueQuota).where(
                    DialogueQuota.user_id == user_id,
                    DialogueQuota.date == today,
                )
            )
            quota = quota_result.scalar_one_or_none()
            if quota:
                quota.base_quota = -1  # unlimited sentinel
            logger.info(
                f"Subscription created: user={user_id}, tier={tier}, "
                f"quota updated to unlimited"
            )
        else:
            logger.info(f"Subscription created: user={user_id}, tier={tier}")
        
        # Grant initial fragments for this month
        await self._grant_fragments(user_id, tier)
        
        return subscription

    async def on_subscription_expired(self, user_id: uuid.UUID) -> None:
        """Handle subscription expiration — downgrade to Free tier.
        
        Args:
            user_id: User UUID
        """
        # Update CR-016 subscription status
        result = await self.db.execute(
            select(Subscription).where(
                Subscription.user_id == user_id,
                Subscription.status == SubscriptionStatus.active.value
            )
        )
        sub = result.scalar_one_or_none()
        if sub:
            sub.status = SubscriptionStatus.expired.value
        
        # Sync to legacy subscriptions table
        legacy_result = await self.db.execute(
            select(LegacySubscription).where(
                LegacySubscription.user_id == user_id,
                LegacySubscription.status == "active"
            )
        )
        legacy_sub = legacy_result.scalar_one_or_none()
        if legacy_sub:
            legacy_sub.status = "expired"
        
        # Downgrade user tier
        user_result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        if user:
            user.subscription_tier = SubscriptionTier.free.value
        
        await self.db.flush()
        logger.info(f"Subscription expired: user={user_id}, downgraded to free")

    async def is_exempt_from_quota(self, user_id: uuid.UUID) -> bool:
        """Check if user is exempt from dynamic quota (subscribed users).
        
        Subscribed users (basic/standard/premium) are exempt from the
        Free tier dynamic gradient quota system.
        
        Args:
            user_id: User UUID
            
        Returns:
            True if user is subscribed (not free), False otherwise
        """
        tier = await self.get_user_tier(user_id)
        return tier != SubscriptionTier.free.value

    async def get_user_subscription(
        self, user_id: uuid.UUID
    ) -> Subscription | None:
        """Get the current active subscription for a user.
        
        Args:
            user_id: User UUID
            
        Returns:
            Active Subscription or None
        """
        result = await self.db.execute(
            select(Subscription).where(
                Subscription.user_id == user_id,
                Subscription.status == SubscriptionStatus.active.value
            ).order_by(Subscription.started_at.desc())
        )
        return result.scalar_one_or_none()

    async def _grant_fragments(
        self,
        user_id: uuid.UUID,
        tier: str
    ) -> None:
        """Grant monthly fragments to user.
        
        Args:
            user_id: User UUID
            tier: Subscription tier
        """
        amount = TIER_FRAGMENT_QUOTAS.get(tier, 0)
        if amount <= 0:
            return
        
        # Get or create fragment balance
        result = await self.db.execute(
            select(Fragment).where(Fragment.user_id == user_id)
        )
        fragment = result.scalar_one_or_none()
        
        if fragment:
            fragment.balance += amount
        else:
            fragment = Fragment(user_id=user_id, balance=amount)
            self.db.add(fragment)
        
        # Record transaction
        transaction = FragmentTransaction(
            user_id=user_id,
            amount=amount,
            reason=f"subscription_grant:{tier}",
        )
        self.db.add(transaction)
        
        await self.db.flush()
        logger.info(f"Granted {amount} fragments to user {user_id} ({tier})")

    async def process_monthly_grants(self) -> int:
        """Process monthly fragment grants for all active subscriptions.
        
        This should be called by a daily cron job to check and grant
        fragments for subscriptions that are due.
        
        Returns:
            Number of users granted fragments
        """
        now = datetime.now(timezone.utc)
        
        # Find all active subscriptions due for grant
        result = await self.db.execute(
            select(Subscription).where(
                Subscription.status == SubscriptionStatus.active.value,
                Subscription.next_fragment_grant_at <= now
            )
        )
        subscriptions = result.scalars().all()
        
        granted_count = 0
        for sub in subscriptions:
            # Grant fragments
            await self._grant_fragments(sub.user_id, sub.tier)
            
            # Update grant timestamps
            sub.last_fragment_grant_at = now
            sub.next_fragment_grant_at = now + timedelta(days=30)
            
            granted_count += 1
            logger.info(
                f"Monthly grant processed: user={sub.user_id}, tier={sub.tier}"
            )
        
        await self.db.commit()
        return granted_count
