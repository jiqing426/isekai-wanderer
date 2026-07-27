"""Paywall trigger service — modal/banner/toast control (CR-016)."""

import logging
import uuid
from datetime import datetime, timezone, date, timedelta
from typing import Dict, Any, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.paywall_event import PaywallEvent, PaywallScene, PaywallDisplayType
from app.models.user import User
from app.services.subscription_service import SubscriptionService
from app.services.quota_service import QuotaService

logger = logging.getLogger(__name__)

# Daily modal limit
DAILY_MODAL_LIMIT = 2

# Honeymoon period threshold
HONEYMOON_DAYS = 3


class PaywallService:
    """Service for paywall trigger control and rate limiting."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._subscription_service = SubscriptionService(db)
        self._quota_service = QuotaService(db)

    async def _get_user(self, user_id: uuid.UUID) -> Optional[User]:
        """Fetch user record."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def _get_user_days_since_registration(self, user: User) -> int:
        """Calculate days since user registration."""
        now = datetime.now(timezone.utc)
        created_at = user.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        return (now - created_at).days

    async def _is_honeymoon_period(self, user: User) -> bool:
        """Check if user is in honeymoon period (day 1-3)."""
        days = await self._get_user_days_since_registration(user)
        return days <= HONEYMOON_DAYS

    async def _get_daily_modal_count(self, user_id: uuid.UUID, today: date) -> int:
        """Get modal count for today."""
        result = await self.db.execute(
            select(func.count()).select_from(PaywallEvent).where(
                and_(
                    PaywallEvent.user_id == user_id,
                    PaywallEvent.display_type == PaywallDisplayType.modal.value,
                    func.date(PaywallEvent.triggered_at) == today,
                )
            )
        )
        return result.scalar() or 0

    async def check_trigger(self, user_id: uuid.UUID, scene: str) -> Dict[str, Any]:
        """Check if paywall should be triggered for a scene.

        Returns:
            Dict with should_show, display_type, payload
        """
        user = await self._get_user(user_id)
        if not user:
            return {"should_show": False, "display_type": None, "payload": None}

        # Rule: Subscribed users — all paywall guidance permanently disabled
        if await self._subscription_service.is_exempt_from_quota(user_id):
            return {"should_show": False, "display_type": None, "payload": None}

        days_since_reg = await self._get_user_days_since_registration(user)
        is_honeymoon = await self._is_honeymoon_period(user)
        today = datetime.now(timezone.utc).date()

        # Rule: Registration <= 3 days Free users — disable all modals, only banner/toast
        if days_since_reg <= HONEYMOON_DAYS:
            display_type = PaywallDisplayType.banner.value
            return {
                "should_show": True,
                "display_type": display_type,
                "payload": {"reason": "new_user_restriction", "days_since_reg": days_since_reg}
            }

        # T1 special rules (quota exhaustion)
        if scene == PaywallScene.T1_quota.value:
            return await self._check_t1_trigger(user_id, user, is_honeymoon, today)

        # Check daily modal limit for other scenes
        modal_count = await self._get_daily_modal_count(user_id, today)

        # Rule: Daily modal limit 2, downgrade to banner if exceeded
        if modal_count >= DAILY_MODAL_LIMIT:
            display_type = PaywallDisplayType.banner.value
        else:
            display_type = PaywallDisplayType.modal.value

        return {
            "should_show": True,
            "display_type": display_type,
            "payload": {
                "scene": scene,
                "modal_count_today": modal_count,
                "is_honeymoon": is_honeymoon,
            }
        }

    async def _check_t1_trigger(
        self,
        user_id: uuid.UUID,
        user: User,
        is_honeymoon: bool,
        today: date
    ) -> Dict[str, Any]:
        """T1 special rules for quota exhaustion.

        - Honeymoon (day 1-3): only banner
        - Growth/Regular: modal (C29 popup)
        - C29 must show: ① upgrade subscription ② fragment purchase
        """
        modal_count = await self._get_daily_modal_count(user_id, today)

        if is_honeymoon:
            # Honeymoon period: only banner
            return {
                "should_show": True,
                "display_type": PaywallDisplayType.banner.value,
                "payload": {
                    "scene": PaywallScene.T1_quota.value,
                    "reason": "honeymoon_period",
                    "message": "蜜月期额度耗尽，仅显示横幅"
                }
            }
        else:
            # Growth/Regular period: modal (C29 popup)
            # Check if should downgrade due to daily limit
            if modal_count >= DAILY_MODAL_LIMIT:
                display_type = PaywallDisplayType.banner.value
            else:
                display_type = PaywallDisplayType.modal.value

            return {
                "should_show": True,
                "display_type": display_type,
                "payload": {
                    "scene": PaywallScene.T1_quota.value,
                    "reason": "quota_exhausted",
                    "show_upgrade": True,      # C29: show upgrade subscription
                    "show_fragment": True,     # C29: show fragment purchase
                    "modal_count_today": modal_count,
                }
            }

    async def record_modal_shown(self, user_id: uuid.UUID, scene: str) -> None:
        """Record that a modal was shown to user.

        Args:
            user_id: User UUID
            scene: Paywall scene that triggered the modal
        """
        event = PaywallEvent(
            user_id=user_id,
            scene=scene,
            display_type=PaywallDisplayType.modal.value,
            triggered_at=datetime.now(timezone.utc),
        )
        self.db.add(event)
        await self.db.flush()
        logger.info(f"Modal shown recorded: user={user_id}, scene={scene}")

    async def record_paywall_event(
        self,
        user_id: uuid.UUID,
        scene: str,
        display_type: str
    ) -> None:
        """Record any paywall event (modal/banner/toast).

        Args:
            user_id: User UUID
            scene: Paywall scene
            display_type: modal/banner/toast
        """
        event = PaywallEvent(
            user_id=user_id,
            scene=scene,
            display_type=display_type,
            triggered_at=datetime.now(timezone.utc),
        )
        self.db.add(event)
        await self.db.flush()
        logger.info(f"Paywall event recorded: user={user_id}, scene={scene}, type={display_type}")

    async def get_daily_modal_count(self, user_id: uuid.UUID) -> int:
        """Get today's modal count for user.

        Returns:
            Number of modals shown today
        """
        today = datetime.now(timezone.utc).date()
        return await self._get_daily_modal_count(user_id, today)

    async def should_downgrade(self, user_id: uuid.UUID) -> bool:
        """Check if paywall should be downgraded from modal to banner.

        Returns:
            True if should downgrade (daily limit reached or new user)
        """
        user = await self._get_user(user_id)
        if not user:
            return True

        # Subscribed users: no paywall at all
        if await self._subscription_service.is_exempt_from_quota(user_id):
            return False

        # New users (<= 3 days): always downgrade to banner
        days_since_reg = await self._get_user_days_since_registration(user)
        if days_since_reg <= HONEYMOON_DAYS:
            return True

        # Check daily modal limit
        today = datetime.now(timezone.utc).date()
        modal_count = await self._get_daily_modal_count(user_id, today)
        return modal_count >= DAILY_MODAL_LIMIT

    async def reset_daily_modal_counter(self) -> int:
        """Reset daily modal counter at UTC 00:00.

        Returns:
            Number of records from previous day (for logging)
        """
        today = datetime.now(timezone.utc).date()
        yesterday = today - timedelta(days=1)

        # Count yesterday's modal events
        result = await self.db.execute(
            select(func.count()).select_from(PaywallEvent).where(
                and_(
                    PaywallEvent.display_type == PaywallDisplayType.modal.value,
                    func.date(PaywallEvent.triggered_at) == yesterday,
                )
            )
        )
        count = result.scalar() or 0

        logger.info(f"Daily modal counter reset: {count} modals from {yesterday}")
        return count

    async def is_user_triggered_subscription(self, user_id: uuid.UUID, scene: str) -> bool:
        """Check if paywall was triggered by user's own subscription entry click.

        User-initiated subscription entry is not subject to rate limiting.

        Args:
            user_id: User UUID
            scene: Paywall scene

        Returns:
            True if user-initiated (no rate limit), False otherwise
        """
        # This would typically be passed as a parameter from the API layer
        # For now, return False (rate limit applies)
        # The API layer should handle this check and bypass rate limiting
        return False

    async def get_paywall_stats(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """Get paywall statistics for a user.

        Returns:
            Dict with today's modal count, total events, etc.
        """
        today = datetime.now(timezone.utc).date()

        # Today's modal count
        today_modal = await self._get_daily_modal_count(user_id, today)

        # Total events
        result = await self.db.execute(
            select(func.count()).select_from(PaywallEvent).where(
                PaywallEvent.user_id == user_id
            )
        )
        total_events = result.scalar() or 0

        # Total modals
        result = await self.db.execute(
            select(func.count()).select_from(PaywallEvent).where(
                and_(
                    PaywallEvent.user_id == user_id,
                    PaywallEvent.display_type == PaywallDisplayType.modal.value,
                )
            )
        )
        total_modals = result.scalar() or 0

        return {
            "today_modal_count": today_modal,
            "daily_modal_limit": DAILY_MODAL_LIMIT,
            "total_events": total_events,
            "total_modals": total_modals,
        }
