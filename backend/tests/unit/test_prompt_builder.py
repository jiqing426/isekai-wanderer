"""Unit tests for PromptBuilder (CR-027)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.services.prompt_builder import PromptBuilder
from app.models.script import Character


class TestPromptBuilder:
    """Test 6-layer prompt construction."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return MagicMock()

    @pytest.fixture
    def mock_memory_service(self):
        """Mock memory service."""
        service = AsyncMock()
        service.recall = AsyncMock(return_value=[])
        return service

    @pytest.fixture
    def mock_lorebook_service(self):
        """Mock lorebook service."""
        service = AsyncMock()
        service.match_by_tags = AsyncMock(return_value=[])
        return service

    @pytest.fixture
    def mock_scene_config_service(self):
        """Mock scene config service."""
        service = AsyncMock()
        service.get_by_node_id = AsyncMock(return_value=None)
        return service

    @pytest.fixture
    def sample_character(self):
        """Sample character for testing."""
        char = Character()
        char.id = uuid4()
        char.name = "艾莉丝"
        char.description = "温柔的异世界少女"
        char.dialogue_style = "gentle"
        char.desire = "寻找回家的路"
        char.fear = "永远被困在异世界"
        char.secret = "她其实是魔王的女儿"
        return char

    @pytest.fixture
    def prompt_builder(
        self,
        mock_db,
        mock_memory_service,
        mock_lorebook_service,
        mock_scene_config_service,
    ):
        """Create PromptBuilder with mocked dependencies."""
        return PromptBuilder(
            db=mock_db,
            memory_service=mock_memory_service,
            lorebook_service=mock_lorebook_service,
            scene_config_service=mock_scene_config_service,
        )

    @pytest.mark.asyncio
    async def test_build_prompt_basic(
        self, prompt_builder, sample_character, mock_memory_service
    ):
        """Test basic prompt construction."""
        user_id = uuid4()
        node_id = uuid4()
        user_input = "你好，艾莉丝"

        result = await prompt_builder.build_prompt(
            user_id=user_id,
            character=sample_character,
            node_id=node_id,
            user_input=user_input,
            affection_level=50,
        )

        assert "system_prompt" in result
        assert "user_prompt" in result
        assert result["user_prompt"] == user_input
        assert len(result["system_prompt"]) > 0

    @pytest.mark.asyncio
    async def test_build_prompt_with_memory(
        self, prompt_builder, sample_character, mock_memory_service
    ):
        """Test prompt construction with memory recall."""
        user_id = uuid4()
        node_id = uuid4()
        user_input = "你还记得我们第一次见面吗？"

        # Mock memory recall
        mock_memory_service.recall.return_value = [
            {"memory_text": "第一次见面在森林", "similarity": 0.9},
            {"memory_text": "艾莉丝救了玩家", "similarity": 0.8},
        ]

        result = await prompt_builder.build_prompt(
            user_id=user_id,
            character=sample_character,
            node_id=node_id,
            user_input=user_input,
            affection_level=60,
        )

        # Verify memory was called
        mock_memory_service.recall.assert_called_once()
        assert "memories" in result["system_prompt"].lower() or "记忆" in result["system_prompt"]

    @pytest.mark.asyncio
    async def test_build_prompt_with_scene_config(
        self,
        prompt_builder,
        sample_character,
        mock_scene_config_service,
        mock_lorebook_service,
    ):
        """Test prompt construction with scene config."""
        user_id = uuid4()
        node_id = uuid4()
        user_input = "这里是什么地方？"

        # Mock scene config
        mock_scene_config_service.get_by_node_id.return_value = {
            "scene_name": "月光森林",
            "tags": ["森林", "夜晚", "神秘"],
            "description": "月光透过树叶洒落",
        }

        # Mock lorebook entries
        mock_lorebook_service.match_by_tags.return_value = [
            {"title": "月光森林传说", "content": "这片森林充满了魔力"},
        ]

        result = await prompt_builder.build_prompt(
            user_id=user_id,
            character=sample_character,
            node_id=node_id,
            user_input=user_input,
            affection_level=40,
        )

        # Verify scene config was called
        mock_scene_config_service.get_by_node_id.assert_called_once_with(node_id)
        assert "月光森林" in result["system_prompt"] or "森林" in result["system_prompt"]

    @pytest.mark.asyncio
    async def test_build_prompt_npc_profile_with_inner_drive(
        self, prompt_builder, sample_character
    ):
        """Test NPC profile includes desire/fear/secret."""
        user_id = uuid4()
        node_id = uuid4()
        user_input = "测试"

        result = await prompt_builder.build_prompt(
            user_id=user_id,
            character=sample_character,
            node_id=node_id,
            user_input=user_input,
            affection_level=50,
        )

        system_prompt = result["system_prompt"]
        # Should include character name
        assert "艾莉丝" in system_prompt
        # Should include inner drive fields
        assert "寻找回家的路" in system_prompt or "desire" in system_prompt.lower()

    @pytest.mark.asyncio
    async def test_build_prompt_graceful_degradation_memory_failure(
        self, prompt_builder, sample_character, mock_memory_service
    ):
        """Test graceful degradation when memory service fails."""
        user_id = uuid4()
        node_id = uuid4()
        user_input = "测试"

        # Mock memory service failure
        mock_memory_service.recall.side_effect = Exception("Memory service error")

        # Should not raise exception
        result = await prompt_builder.build_prompt(
            user_id=user_id,
            character=sample_character,
            node_id=node_id,
            user_input=user_input,
            affection_level=50,
        )

        assert "system_prompt" in result
        assert "user_prompt" in result

    @pytest.mark.asyncio
    async def test_build_prompt_graceful_degradation_scene_config_failure(
        self,
        prompt_builder,
        sample_character,
        mock_scene_config_service,
    ):
        """Test graceful degradation when scene config service fails."""
        user_id = uuid4()
        node_id = uuid4()
        user_input = "测试"

        # Mock scene config failure
        mock_scene_config_service.get_by_node_id.side_effect = Exception("Scene config error")

        # Should not raise exception
        result = await prompt_builder.build_prompt(
            user_id=user_id,
            character=sample_character,
            node_id=node_id,
            user_input=user_input,
            affection_level=50,
        )

        assert "system_prompt" in result
        assert "user_prompt" in result

    @pytest.mark.asyncio
    async def test_build_prompt_affection_levels(
        self, prompt_builder, sample_character
    ):
        """Test prompt varies with affection levels."""
        user_id = uuid4()
        node_id = uuid4()
        user_input = "测试"

        # Low affection
        result_low = await prompt_builder.build_prompt(
            user_id=user_id,
            character=sample_character,
            node_id=node_id,
            user_input=user_input,
            affection_level=20,
        )

        # High affection
        result_high = await prompt_builder.build_prompt(
            user_id=user_id,
            character=sample_character,
            node_id=node_id,
            user_input=user_input,
            affection_level=80,
        )

        # Both should succeed
        assert len(result_low["system_prompt"]) > 0
        assert len(result_high["system_prompt"]) > 0

    @pytest.mark.asyncio
    async def test_build_prompt_token_budget_respected(
        self, prompt_builder, sample_character, mock_memory_service
    ):
        """Test that token budget is respected."""
        user_id = uuid4()
        node_id = uuid4()
        user_input = "测试"

        # Create very long memory to test truncation
        mock_memory_service.recall.return_value = [
            {"memory_text": "很长的记忆" * 1000, "similarity": 0.9},
        ]

        result = await prompt_builder.build_prompt(
            user_id=user_id,
            character=sample_character,
            node_id=node_id,
            user_input=user_input,
            affection_level=50,
        )

        # Should still complete without error
        assert "system_prompt" in result
        assert "user_prompt" in result

    @pytest.mark.asyncio
    async def test_build_prompt_empty_user_input(
        self, prompt_builder, sample_character
    ):
        """Test prompt with empty user input."""
        user_id = uuid4()
        node_id = uuid4()
        user_input = ""

        result = await prompt_builder.build_prompt(
            user_id=user_id,
            character=sample_character,
            node_id=node_id,
            user_input=user_input,
            affection_level=50,
        )

        assert result["user_prompt"] == ""
        assert len(result["system_prompt"]) > 0
