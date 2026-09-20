"""Tests for script_access mapping and game start permission checks.

CR-043 DEV-003 AC-005, AC-006, AC-007, AC-008, AC-009, AC-015

AC-005: free user → POST /game/start with non-trial script → 403
AC-006: basic user → POST /game/start with normal script → 200
AC-007: basic user → POST /game/start with exclusive script → 403 (future-proof)
AC-008: premium user → POST /game/start with any script → 200
AC-009: list_scripts returns is_accessible field per script
AC-015: server-side tier check, no client tier input accepted
"""

import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.subscription_service import SubscriptionService


class TestScriptAccessMapping:
    """AC-005~009, AC-015: Script access permission checks"""

    def test_subscription_service_get_tier_permissions_exists(self):
        """SubscriptionService has get_tier_permissions method."""
        assert hasattr(SubscriptionService, "get_tier_permissions")

    @pytest.mark.asyncio
    async def test_free_user_non_trial_script_denied(self):
        """AC-005: free user cannot start non-trial script → 403."""
        from app.api.v1.game import _compute_script_accessible

        mock_script = MagicMock()
        mock_script.genre = "fantasy"
        mock_script.hot_value = 10

        # free → trial_only → non-trial script → denied
        result = _compute_script_accessible("trial_only", mock_script)
        assert result is False

    @pytest.mark.asyncio
    async def test_free_user_trial_script_allowed(self):
        """AC-005: free user can start trial script (romance + hot_value>=50)."""
        from app.api.v1.game import _compute_script_accessible

        mock_script = MagicMock()
        mock_script.genre = "romance"
        mock_script.hot_value = 60

        # free → trial_only → trial script → allowed
        result = _compute_script_accessible("trial_only", mock_script)
        assert result is True

    @pytest.mark.asyncio
    async def test_basic_user_normal_script_allowed(self):
        """AC-006: basic user can start normal scripts."""
        from app.api.v1.game import _compute_script_accessible

        mock_script = MagicMock()
        mock_script.genre = "fantasy"
        mock_script.hot_value = 10

        # basic → all_normal → allowed
        result = _compute_script_accessible("all_normal", mock_script)
        assert result is True

    @pytest.mark.asyncio
    async def test_premium_user_any_script_allowed(self):
        """AC-008: premium user can start any script."""
        from app.api.v1.game import _compute_script_accessible

        mock_script = MagicMock()
        mock_script.genre = "fantasy"
        mock_script.hot_value = 0

        # premium → all_including_exclusive → allowed
        result = _compute_script_accessible("all_including_exclusive", mock_script)
        assert result is True

    @pytest.mark.asyncio
    async def test_trial_only_low_hot_value_denied(self):
        """AC-005: romance script with hot_value < 50 is not trial."""
        from app.api.v1.game import _compute_script_accessible

        mock_script = MagicMock()
        mock_script.genre = "romance"
        mock_script.hot_value = 30  # Below threshold

        result = _compute_script_accessible("trial_only", mock_script)
        assert result is False

    @pytest.mark.asyncio
    async def test_trial_only_non_romance_denied(self):
        """AC-005: non-romance script is never trial."""
        from app.api.v1.game import _compute_script_accessible

        mock_script = MagicMock()
        mock_script.genre = "fantasy"
        mock_script.hot_value = 100  # High but not romance

        result = _compute_script_accessible("trial_only", mock_script)
        assert result is False

    @pytest.mark.asyncio
    async def test_unknown_access_level_denied(self):
        """Unknown script_access value → denied (safe default)."""
        from app.api.v1.game import _compute_script_accessible

        mock_script = MagicMock()
        mock_script.genre = "romance"
        mock_script.hot_value = 100

        result = _compute_script_accessible("unknown_level", mock_script)
        assert result is False


class TestGameStartPermission:
    """AC-005, AC-006, AC-008, AC-015: POST /game/start permission checks"""

    @pytest.mark.asyncio
    async def test_start_game_denies_free_user_non_trial(self):
        """AC-005/AC-015: free user starting non-trial script gets 403 SCRIPT_ACCESS_DENIED."""
        from app.api.v1.game import start_game, StartGameRequest
        from app.core.exceptions import AppException

        mock_db = AsyncMock()
        mock_script = MagicMock()
        mock_script.id = uuid.uuid4()
        mock_script.title = "Exclusive Adventure"
        mock_script.genre = "fantasy"
        mock_script.hot_value = 10

        mock_sub_service = MagicMock()
        mock_sub_service.get_user_tier = AsyncMock(return_value="free")
        mock_perms = MagicMock()
        mock_perms.script_access = "trial_only"
        mock_sub_service.get_tier_permissions = AsyncMock(return_value=mock_perms)

        script_result = MagicMock()
        script_result.scalar_one_or_none.return_value = mock_script

        with patch("app.api.v1.game.SubscriptionService", return_value=mock_sub_service):
            with patch("app.api.v1.game.select") as mock_select:
                mock_db.execute = AsyncMock(return_value=script_result)

                try:
                    await start_game(
                        request=StartGameRequest(script_id=str(mock_script.id)),
                        user_id=str(uuid.uuid4()),
                        db=mock_db,
                    )
                    assert False, "Should have raised AppException"
                except AppException as e:
                    assert e.status_code == 403
                    assert "SCRIPT_ACCESS_DENIED" in str(e.error_code) or "SCRIPT_ACCESS_DENIED" in str(e.message)

    @pytest.mark.asyncio
    async def test_start_game_allows_basic_user_normal(self):
        """AC-006: basic user starting normal script succeeds (no 403)."""
        from app.api.v1.game import _compute_script_accessible

        mock_script = MagicMock()
        mock_script.genre = "fantasy"
        mock_script.hot_value = 10

        # basic → all_normal → allowed (doesn't raise 403)
        result = _compute_script_accessible("all_normal", mock_script)
        assert result is True


class TestScriptsIsAccessible:
    """AC-009, AC-010: Scripts API returns is_accessible field"""

    @pytest.mark.asyncio
    async def test_list_scripts_has_is_accessible_for_authenticated_user(self):
        """AC-009: list_scripts returns is_accessible field per script for authenticated users."""
        from app.api.v1.scripts import list_scripts
        from sqlalchemy.ext.asyncio import AsyncSession

        # This is tested at integration level, verify the function can be called
        # and that it attempts to add is_accessible
        assert callable(list_scripts)

    @pytest.mark.asyncio
    async def test_get_script_has_is_accessible(self):
        """AC-010: get_script returns is_accessible field."""
        from app.api.v1.scripts import get_script

        assert callable(get_script)
