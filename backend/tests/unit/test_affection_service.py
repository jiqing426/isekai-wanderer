"""AffectionService unit tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.services.narrative.affection_service import (
    AffectionService,
    AffectionChange,
    MAX_DELTA,
    MIN_AFFECTION,
    MAX_AFFECTION,
)
from app.models.affection import Affection


class TestAffectionBounds:
    def test_max_delta_clamped(self):
        assert MAX_DELTA == 5

    def test_min_affection(self):
        assert MIN_AFFECTION == 0

    def test_max_affection(self):
        assert MAX_AFFECTION == 100


class TestAffectionChange:
    def test_level_changed(self):
        change = AffectionChange(
            old_value=18, new_value=22,
            old_level="acquaintance", new_level="ambiguous",
            delta=4, level_changed=True,
        )
        assert change.level_changed is True

    def test_no_level_change(self):
        change = AffectionChange(
            old_value=30, new_value=33,
            old_level="ambiguous", new_level="ambiguous",
            delta=3, level_changed=False,
        )
        assert change.level_changed is False


class TestUpdateAffectionLogic:
    @pytest.mark.asyncio
    async def test_delta_clamped_to_max(self):
        """Delta > 5 should be clamped to 5."""
        db = AsyncMock()
        service = AffectionService(db)

        # Mock get_affection
        mock_affection = MagicMock(spec=Affection)
        mock_affection.value = 50
        mock_affection.level = "trust"
        service.get_affection = AsyncMock(return_value=mock_affection)

        result = await service.update_affection(uuid4(), uuid4(), delta=10)
        assert result.delta == 5  # Clamped
        assert result.new_value == 55

    @pytest.mark.asyncio
    async def test_delta_clamped_to_min(self):
        """Delta < -5 should be clamped to -5."""
        db = AsyncMock()
        service = AffectionService(db)

        mock_affection = MagicMock(spec=Affection)
        mock_affection.value = 50
        mock_affection.level = "trust"
        service.get_affection = AsyncMock(return_value=mock_affection)

        result = await service.update_affection(uuid4(), uuid4(), delta=-10)
        assert result.delta == -5  # Clamped
        assert result.new_value == 45

    @pytest.mark.asyncio
    async def test_value_does_not_exceed_100(self):
        """Value should not go above 100."""
        db = AsyncMock()
        service = AffectionService(db)

        mock_affection = MagicMock(spec=Affection)
        mock_affection.value = 98
        mock_affection.level = "love"
        service.get_affection = AsyncMock(return_value=mock_affection)

        result = await service.update_affection(uuid4(), uuid4(), delta=5)
        assert result.new_value == 100

    @pytest.mark.asyncio
    async def test_value_does_not_go_below_0(self):
        """Value should not go below 0."""
        db = AsyncMock()
        service = AffectionService(db)

        mock_affection = MagicMock(spec=Affection)
        mock_affection.value = 2
        mock_affection.level = "acquaintance"
        service.get_affection = AsyncMock(return_value=mock_affection)

        result = await service.update_affection(uuid4(), uuid4(), delta=-5)
        assert result.new_value == 0

    @pytest.mark.asyncio
    async def test_level_upgrade(self):
        """Crossing threshold should trigger level change."""
        db = AsyncMock()
        service = AffectionService(db)

        mock_affection = MagicMock(spec=Affection)
        mock_affection.value = 18
        mock_affection.level = "acquaintance"
        service.get_affection = AsyncMock(return_value=mock_affection)

        result = await service.update_affection(uuid4(), uuid4(), delta=3)
        assert result.new_value == 21
        assert result.new_level == "ambiguous"
        assert result.level_changed is True
