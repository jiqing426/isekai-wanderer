"""Unit tests for settings.py get_member_info data source fix.

CR-043 DEV-005 AC-018, AC-019

AC-018: tier from SubscriptionService.get_user_tier(), status/expires_at from Subscription table
AC-019: member-info tier matches subscription/status API tier (same data source)
"""

import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

from app.services.subscription_service import SubscriptionService, SubscriptionTier


class TestMemberInfoDataSource:
    """AC-018, AC-019: get_member_info uses SubscriptionService as data source"""

    def test_subscription_service_get_user_tier_exists(self):
        """SubscriptionService has get_user_tier method."""
        assert hasattr(SubscriptionService, "get_user_tier")

    def test_subscription_service_get_user_subscription_exists(self):
        """SubscriptionService has get_user_subscription method."""
        assert hasattr(SubscriptionService, "get_user_subscription")

    @pytest.mark.asyncio
    async def test_member_info_tier_from_subscription_service(self):
        """AC-018: tier is obtained from SubscriptionService.get_user_tier(), not user.subscription_tier."""
        from app.api.v1.settings import get_member_info

        user_uuid = uuid.uuid4()
        mock_db = AsyncMock()

        mock_sub_service = MagicMock()
        mock_sub_service.get_user_tier = AsyncMock(return_value="standard")
        mock_sub_service.get_user_subscription = AsyncMock(return_value=None)

        mock_user = MagicMock()
        mock_user.subscription_tier = "free"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_fragment_result = MagicMock()
        mock_fragment_result.scalar_one_or_none.return_value = None
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_tx_result = MagicMock()
        mock_tx_result.scalars.return_value = mock_scalars

        mock_db.execute = AsyncMock(side_effect=[mock_result, mock_fragment_result, mock_tx_result])

        with patch("app.api.v1.settings.SubscriptionService", return_value=mock_sub_service):
            result = await get_member_info(
                user_id=str(user_uuid),
                db=mock_db,
            )

        assert result["tier"] == "standard"

    @pytest.mark.asyncio
    async def test_member_info_status_from_subscription_table(self):
        """AC-018: status and expires_at are read from Subscription table, not User.trial_*."""
        from app.api.v1.settings import get_member_info

        user_uuid = uuid.uuid4()
        mock_db = AsyncMock()

        from datetime import datetime, timezone
        started_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
        expires_at = datetime(2026, 12, 31, tzinfo=timezone.utc)

        mock_subscription = MagicMock()
        mock_subscription.status = "active"
        mock_subscription.tier = "premium"
        mock_subscription.started_at = started_at
        mock_subscription.expires_at = expires_at

        mock_sub_service = MagicMock()
        mock_sub_service.get_user_tier = AsyncMock(return_value="premium")
        mock_sub_service.get_user_subscription = AsyncMock(return_value=mock_subscription)

        mock_user = MagicMock()
        mock_user.subscription_tier = "premium"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_fragment_result = MagicMock()
        mock_fragment_result.scalar_one_or_none.return_value = None
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_tx_result = MagicMock()
        mock_tx_result.scalars.return_value = mock_scalars

        mock_db.execute = AsyncMock(side_effect=[mock_result, mock_fragment_result, mock_tx_result])

        with patch("app.api.v1.settings.SubscriptionService", return_value=mock_sub_service):
            result = await get_member_info(
                user_id=str(user_uuid),
                db=mock_db,
            )

        assert result["status"] == "active"
        assert result["expires_at"] is not None
        assert result["member_since"] is not None

    @pytest.mark.asyncio
    async def test_member_info_no_subscription_defaults(self):
        """AC-018: When no active subscription, tier=free, status=inactive."""
        from app.api.v1.settings import get_member_info

        user_uuid = uuid.uuid4()
        mock_db = AsyncMock()

        mock_sub_service = MagicMock()
        mock_sub_service.get_user_tier = AsyncMock(return_value="free")
        mock_sub_service.get_user_subscription = AsyncMock(return_value=None)

        mock_user = MagicMock()
        mock_user.subscription_tier = "free"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_fragment_result = MagicMock()
        mock_fragment_result.scalar_one_or_none.return_value = None
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_tx_result = MagicMock()
        mock_tx_result.scalars.return_value = mock_scalars

        mock_db.execute = AsyncMock(side_effect=[mock_result, mock_fragment_result, mock_tx_result])

        with patch("app.api.v1.settings.SubscriptionService", return_value=mock_sub_service):
            result = await get_member_info(
                user_id=str(user_uuid),
                db=mock_db,
            )

        assert result["tier"] == "free"
        assert result["status"] == "inactive"
        assert result["expires_at"] is None
        assert result["member_since"] is None

    @pytest.mark.asyncio
    async def test_member_info_tier_consistent_with_subscription_api(self):
        """AC-019: member-info tier is the same value that subscription/status API returns."""
        from app.api.v1.settings import get_member_info

        user_uuid = uuid.uuid4()
        mock_db = AsyncMock()

        mock_sub_service = MagicMock()
        mock_sub_service.get_user_tier = AsyncMock(return_value="standard")
        mock_sub_service.get_user_subscription = AsyncMock(return_value=None)

        mock_user = MagicMock()
        mock_user.subscription_tier = "free"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_fragment_result = MagicMock()
        mock_fragment_result.scalar_one_or_none.return_value = None
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_tx_result = MagicMock()
        mock_tx_result.scalars.return_value = mock_scalars

        mock_db.execute = AsyncMock(side_effect=[mock_result, mock_fragment_result, mock_tx_result])

        with patch("app.api.v1.settings.SubscriptionService", return_value=mock_sub_service):
            result = await get_member_info(
                user_id=str(user_uuid),
                db=mock_db,
            )

        mock_sub_service.get_user_tier.assert_called_once_with(user_uuid)
        assert result["tier"] == "standard"
