"""Integration tests for NarrativeEngine with PromptBuilder (CR-027)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.services.narrative.narrative_engine import NarrativeEngine
from app.models.script import Character, Node, NodeChoice


class TestNarrativeEngineCR027:
    """Test NarrativeEngine integration with PromptBuilder."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return MagicMock()

    @pytest.fixture
    def sample_character(self):
        """Sample character with inner drive."""
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
    def sample_node(self):
        """Sample story node."""
        node = Node()
        node.id = uuid4()
        node.node_type = "dialogue"
        node.content = {"text": "艾莉丝看着你，等待你的回应"}
        return node

    @pytest.fixture
    def narrative_engine(self, mock_db):
        """Create NarrativeEngine with mocked dependencies."""
        with patch('app.services.narrative.narrative_engine.ScriptService') as mock_script, \
             patch('app.services.narrative.narrative_engine.RuleEngine') as mock_rule, \
             patch('app.services.narrative.narrative_engine.MemoryService') as mock_memory, \
             patch('app.services.narrative.narrative_engine.AffectionService') as mock_affection:
            
            engine = NarrativeEngine(mock_db)
            engine.script_service = mock_script.return_value
            engine.rule_engine = mock_rule.return_value
            engine.memory_service = mock_memory.return_value
            engine.affection_service = mock_affection.return_value
            
            # Setup default mocks
            engine.rule_engine.get_affection_for_character = AsyncMock(return_value=50)
            engine.memory_service.recall = AsyncMock(return_value=[])
            
            yield engine

    @pytest.mark.asyncio
    async def test_generate_validated_dialogue_uses_prompt_builder(
        self, narrative_engine, sample_character, sample_node
    ):
        """Test that _generate_validated_dialogue uses PromptBuilder."""
        user_id = uuid4()
        session = MagicMock()
        session.choice_history = []

        with patch('app.services.prompt_builder.PromptBuilder') as mock_pb_class:
            mock_pb = AsyncMock()
            mock_pb.build_prompt = AsyncMock(return_value={
                "system_prompt": "Test system prompt",
                "user_prompt": "Test user prompt"
            })
            mock_pb_class.return_value = mock_pb

            with patch('app.services.narrative.narrative_engine.llm_gateway') as mock_llm:
                mock_llm.generate_with_system = AsyncMock(return_value="生成的对话文本")
                
                # Mock rule engine validation
                narrative_engine.rule_engine.validate_dialogue = AsyncMock(
                    return_value=MagicMock(passed=True)
                )

                result = await narrative_engine._generate_validated_dialogue(
                    node=sample_node,
                    character=sample_character,
                    session=session,
                    user_id=user_id
                )

                # Verify PromptBuilder was used
                mock_pb.build_prompt.assert_called_once()
                assert "text" in result
                assert result["text"] == "生成的对话文本"

    @pytest.mark.asyncio
    async def test_generate_validated_dialogue_fallback_on_prompt_builder_failure(
        self, narrative_engine, sample_character, sample_node
    ):
        """Test fallback when PromptBuilder fails."""
        user_id = uuid4()
        session = MagicMock()
        session.choice_history = []

        with patch('app.services.prompt_builder.PromptBuilder') as mock_pb_class:
            mock_pb = AsyncMock()
            mock_pb.build_prompt = AsyncMock(side_effect=Exception("PromptBuilder error"))
            mock_pb_class.return_value = mock_pb

            with patch('app.services.narrative.narrative_engine.llm_gateway') as mock_llm:
                # Mock simple dialogue generation (fallback)
                mock_llm.generate_dialogue = AsyncMock(return_value="Fallback dialogue")
                
                # Mock rule engine validation
                narrative_engine.rule_engine.validate_dialogue = AsyncMock(
                    return_value=MagicMock(passed=True)
                )

                result = await narrative_engine._generate_validated_dialogue(
                    node=sample_node,
                    character=sample_character,
                    session=session,
                    user_id=user_id
                )

                # Should still return valid result via fallback
                assert "text" in result
                assert result["text"] == "Fallback dialogue"

    @pytest.mark.asyncio
    async def test_generate_validated_dialogue_retry_on_validation_failure(
        self, narrative_engine, sample_character, sample_node
    ):
        """Test retry mechanism when validation fails."""
        user_id = uuid4()
        session = MagicMock()
        session.choice_history = []

        with patch('app.services.prompt_builder.PromptBuilder') as mock_pb_class:
            mock_pb = AsyncMock()
            mock_pb.build_prompt = AsyncMock(return_value={
                "system_prompt": "Test system prompt",
                "user_prompt": "Test user prompt"
            })
            mock_pb_class.return_value = mock_pb

            with patch('app.services.narrative.narrative_engine.llm_gateway') as mock_llm:
                mock_llm.generate_with_system = AsyncMock(return_value="Generated text")
                
                # Mock rule engine: fail twice, then pass
                validation_results = [
                    MagicMock(passed=False),
                    MagicMock(passed=False),
                    MagicMock(passed=True)
                ]
                narrative_engine.rule_engine.validate_dialogue = AsyncMock(
                    side_effect=validation_results
                )

                result = await narrative_engine._generate_validated_dialogue(
                    node=sample_node,
                    character=sample_character,
                    session=session,
                    user_id=user_id
                )

                # Should retry and eventually succeed
                assert "text" in result
                assert mock_llm.generate_with_system.call_count == 3

    @pytest.mark.asyncio
    async def test_generate_validated_dialogue_final_fallback(
        self, narrative_engine, sample_character, sample_node
    ):
        """Test final fallback when all retries fail."""
        user_id = uuid4()
        session = MagicMock()
        session.choice_history = []

        with patch('app.services.prompt_builder.PromptBuilder') as mock_pb_class:
            mock_pb = AsyncMock()
            mock_pb.build_prompt = AsyncMock(return_value={
                "system_prompt": "Test system prompt",
                "user_prompt": "Test user prompt"
            })
            mock_pb_class.return_value = mock_pb

            with patch('app.services.narrative.narrative_engine.llm_gateway') as mock_llm:
                mock_llm.generate_with_system = AsyncMock(return_value="Bad text")
                
                # Mock rule engine: always fail
                narrative_engine.rule_engine.validate_dialogue = AsyncMock(
                    return_value=MagicMock(passed=False)
                )

                result = await narrative_engine._generate_validated_dialogue(
                    node=sample_node,
                    character=sample_character,
                    session=session,
                    user_id=user_id
                )

                # Should use simple dialogue fallback
                assert "text" in result
                assert result["emotion"] == "neutral"

    @pytest.mark.asyncio
    async def test_backward_compatibility_without_inner_drive(
        self, narrative_engine, sample_node
    ):
        """Test backward compatibility with characters without inner drive."""
        user_id = uuid4()
        session = MagicMock()
        session.choice_history = []

        # Character without inner drive fields
        char = Character()
        char.id = uuid4()
        char.name = "普通角色"
        char.description = "普通NPC"
        char.dialogue_style = "neutral"
        # No desire/fear/secret fields

        with patch('app.services.prompt_builder.PromptBuilder') as mock_pb_class:
            mock_pb = AsyncMock()
            mock_pb.build_prompt = AsyncMock(return_value={
                "system_prompt": "Test system prompt",
                "user_prompt": "Test user prompt"
            })
            mock_pb_class.return_value = mock_pb

            with patch('app.services.narrative.narrative_engine.llm_gateway') as mock_llm:
                mock_llm.generate_with_system = AsyncMock(return_value="对话文本")
                
                narrative_engine.rule_engine.validate_dialogue = AsyncMock(
                    return_value=MagicMock(passed=True)
                )

                result = await narrative_engine._generate_validated_dialogue(
                    node=sample_node,
                    character=char,
                    session=session,
                    user_id=user_id
                )

                # Should work without errors
                assert "text" in result
                assert result["text"] == "对话文本"
