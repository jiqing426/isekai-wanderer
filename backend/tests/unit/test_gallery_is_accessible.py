"""Tests for gallery.py is_accessible field.

CR-043 DEV-001 AC-001, AC-002, AC-003, AC-004

AC-001: Each CG item contains is_accessible boolean field
AC-002: free user — unlocked CG is_accessible=true, locked CG is_accessible=false
AC-003: standard user — all CG is_accessible=true
AC-004: basic user — same as free (is_accessible=false for unlocked=false CGs)
"""

import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.subscription_service import SubscriptionService


class TestGalleryIsAccessible:
    """AC-001, AC-002, AC-003, AC-004"""

    def test_subscription_service_importable(self):
        """SubscriptionService can be imported from gallery.py context."""
        from app.services.subscription_service import SubscriptionService
        assert SubscriptionService is not None

    @pytest.mark.asyncio
    async def test_gallery_returns_is_accessible_field(self):
        """AC-001: Each CG item in the response contains is_accessible field."""
        from app.api.v1.gallery import get_collection_items

        user_uuid = uuid.uuid4()
        mock_db = AsyncMock()

        # Mock CG assets
        mock_cg_asset = MagicMock()
        mock_cg_asset.id = uuid.uuid4()
        mock_cg_asset.name = "Test CG"
        mock_cg_asset.image_url = "/assets/cg/test.jpg"

        mock_route = MagicMock()
        mock_route.title = "Test Route"

        cg_result = MagicMock()
        cg_result.all.return_value = [(mock_cg_asset, mock_route)]
        unlocked_result = MagicMock()
        unlocked_result.all.return_value = []

        mock_sub_service = MagicMock()
        mock_sub_service.get_user_tier = AsyncMock(return_value="free")

        mock_db.execute = AsyncMock(side_effect=[cg_result, unlocked_result])

        with patch("app.api.v1.gallery.SubscriptionService", return_value=mock_sub_service):
            result = await get_collection_items(
                script_id=str(uuid.uuid4()),
                db=mock_db,
                user_id=str(user_uuid),
            )

        items = result["items"]
        assert len(items) >= 1
        for item in items:
            assert "is_accessible" in item
            assert isinstance(item["is_accessible"], bool)

    @pytest.mark.asyncio
    async def test_free_user_locked_cg_not_accessible(self):
        """AC-002: free user — locked CG has is_accessible=false."""
        from app.api.v1.gallery import get_collection_items

        user_uuid = uuid.uuid4()
        mock_db = AsyncMock()

        mock_cg_asset = MagicMock()
        mock_cg_asset.id = uuid.uuid4()
        mock_cg_asset.name = "Locked CG"
        mock_cg_asset.image_url = "/assets/cg/locked.jpg"

        mock_route = MagicMock()
        mock_route.title = "Route"

        cg_result = MagicMock()
        cg_result.all.return_value = [(mock_cg_asset, mock_route)]
        unlocked_result = MagicMock()
        unlocked_result.all.return_value = []  # No unlocked CGs

        mock_sub_service = MagicMock()
        mock_sub_service.get_user_tier = AsyncMock(return_value="free")

        mock_db.execute = AsyncMock(side_effect=[cg_result, unlocked_result])

        with patch("app.api.v1.gallery.SubscriptionService", return_value=mock_sub_service):
            result = await get_collection_items(
                script_id=str(uuid.uuid4()),
                db=mock_db,
                user_id=str(user_uuid),
            )

        item = result["items"][0]
        assert item["is_accessible"] is False  # Locked + free = not accessible

    @pytest.mark.asyncio
    async def test_free_user_unlocked_cg_accessible(self):
        """AC-002: free user — unlocked CG has is_accessible=true."""
        from app.api.v1.gallery import get_collection_items

        user_uuid = uuid.uuid4()
        cg_uuid = uuid.uuid4()
        mock_db = AsyncMock()

        mock_cg_asset = MagicMock()
        mock_cg_asset.id = cg_uuid
        mock_cg_asset.name = "Unlocked CG"
        mock_cg_asset.image_url = "/assets/cg/unlocked.jpg"

        mock_route = MagicMock()
        mock_route.title = "Route"

        cg_result = MagicMock()
        cg_result.all.return_value = [(mock_cg_asset, mock_route)]
        unlocked_result = MagicMock()
        unlocked_result.all.return_value = [(cg_uuid,)]  # This CG is unlocked

        mock_sub_service = MagicMock()
        mock_sub_service.get_user_tier = AsyncMock(return_value="free")

        mock_db.execute = AsyncMock(side_effect=[cg_result, unlocked_result])

        with patch("app.api.v1.gallery.SubscriptionService", return_value=mock_sub_service):
            result = await get_collection_items(
                script_id=str(uuid.uuid4()),
                db=mock_db,
                user_id=str(user_uuid),
            )

        item = result["items"][0]
        assert item["is_accessible"] is True  # Unlocked + free = accessible

    @pytest.mark.asyncio
    async def test_standard_user_all_cg_accessible(self):
        """AC-003: standard user — all CGs have is_accessible=true (even locked ones)."""
        from app.api.v1.gallery import get_collection_items

        user_uuid = uuid.uuid4()
        mock_db = AsyncMock()

        mock_cg_asset = MagicMock()
        mock_cg_asset.id = uuid.uuid4()
        mock_cg_asset.name = "Locked CG"
        mock_cg_asset.image_url = "/assets/cg/locked.jpg"

        mock_route = MagicMock()
        mock_route.title = "Route"

        cg_result = MagicMock()
        cg_result.all.return_value = [(mock_cg_asset, mock_route)]
        unlocked_result = MagicMock()
        unlocked_result.all.return_value = []  # Not unlocked

        mock_sub_service = MagicMock()
        mock_sub_service.get_user_tier = AsyncMock(return_value="standard")

        mock_db.execute = AsyncMock(side_effect=[cg_result, unlocked_result])

        with patch("app.api.v1.gallery.SubscriptionService", return_value=mock_sub_service):
            result = await get_collection_items(
                script_id=str(uuid.uuid4()),
                db=mock_db,
                user_id=str(user_uuid),
            )

        item = result["items"][0]
        assert item["is_accessible"] is True  # standard tier → all accessible

    @pytest.mark.asyncio
    async def test_premium_user_all_cg_accessible(self):
        """AC-003: premium user — all CGs have is_accessible=true."""
        from app.api.v1.gallery import get_collection_items

        user_uuid = uuid.uuid4()
        mock_db = AsyncMock()

        mock_cg_asset = MagicMock()
        mock_cg_asset.id = uuid.uuid4()
        mock_cg_asset.name = "Locked CG"
        mock_cg_asset.image_url = "/assets/cg/locked.jpg"

        mock_route = MagicMock()
        mock_route.title = "Route"

        cg_result = MagicMock()
        cg_result.all.return_value = [(mock_cg_asset, mock_route)]
        unlocked_result = MagicMock()
        unlocked_result.all.return_value = []

        mock_sub_service = MagicMock()
        mock_sub_service.get_user_tier = AsyncMock(return_value="premium")

        mock_db.execute = AsyncMock(side_effect=[cg_result, unlocked_result])

        with patch("app.api.v1.gallery.SubscriptionService", return_value=mock_sub_service):
            result = await get_collection_items(
                script_id=str(uuid.uuid4()),
                db=mock_db,
                user_id=str(user_uuid),
            )

        item = result["items"][0]
        assert item["is_accessible"] is True

    @pytest.mark.asyncio
    async def test_basic_user_same_as_free(self):
        """AC-004: basic user — is_accessible logic same as free (locked=false)."""
        from app.api.v1.gallery import get_collection_items

        user_uuid = uuid.uuid4()
        mock_db = AsyncMock()

        mock_cg_asset = MagicMock()
        mock_cg_asset.id = uuid.uuid4()
        mock_cg_asset.name = "Locked CG"
        mock_cg_asset.image_url = "/assets/cg/locked.jpg"

        mock_route = MagicMock()
        mock_route.title = "Route"

        cg_result = MagicMock()
        cg_result.all.return_value = [(mock_cg_asset, mock_route)]
        unlocked_result = MagicMock()
        unlocked_result.all.return_value = []

        mock_sub_service = MagicMock()
        mock_sub_service.get_user_tier = AsyncMock(return_value="basic")

        mock_db.execute = AsyncMock(side_effect=[cg_result, unlocked_result])

        with patch("app.api.v1.gallery.SubscriptionService", return_value=mock_sub_service):
            result = await get_collection_items(
                script_id=str(uuid.uuid4()),
                db=mock_db,
                user_id=str(user_uuid),
            )

        item = result["items"][0]
        assert item["is_accessible"] is False  # basic = same as free for CG access
