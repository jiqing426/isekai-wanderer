"""Unit tests for ModelRouter.stream_with_fallback()

CR-042 DEV-001 AC-017, AC-018, AC-019

AC-017: stream_with_fallback(scenario, messages, **kwargs) -> AsyncGenerator[str, None]
         — method exists, returns AsyncGenerator, yields tokens one by one.
AC-018: Primary model stream failure → auto-switch to fallback model, no user interruption.
AC-019: All fallback models fail → yield scenario-specific friendly fallback text (non-streaming, single yield).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import AsyncGenerator

from app.llm.model_router import ModelRouter, ScenarioType, model_router


class TestStreamWithFallbackExists:
    """AC-017: stream_with_fallback method exists and returns AsyncGenerator"""

    def test_method_exists(self):
        """stream_with_fallback method is defined on ModelRouter."""
        assert hasattr(ModelRouter, "stream_with_fallback")

    def test_method_is_async_generator(self):
        """stream_with_fallback is an async generator function."""
        import inspect
        assert inspect.isasyncgenfunction(ModelRouter.stream_with_fallback)

    @pytest.mark.asyncio
    async def test_returns_async_generator(self):
        """Calling stream_with_fallback returns an async generator."""
        router = ModelRouter()

        # Mock _stream_model to yield tokens
        async def mock_stream_model(model, messages, **kwargs):
            yield "hello"
            yield " world"

        with patch.object(router, "_stream_model", side_effect=mock_stream_model):
            gen = router.stream_with_fallback(
                ScenarioType.FREE_CHAT,
                [{"role": "user", "content": "hi"}],
            )
            # Verify it's an async generator
            import inspect
            assert inspect.isasyncgen(gen)

    @pytest.mark.asyncio
    async def test_yields_tokens_sequentially(self):
        """stream_with_fallback yields tokens one by one from primary model."""
        router = ModelRouter()

        async def mock_stream_model(model, messages, **kwargs):
            for token in ["你", "好", "呀"]:
                yield token

        with patch.object(router, "_stream_model", side_effect=mock_stream_model):
            tokens = []
            async for chunk in router.stream_with_fallback(
                ScenarioType.FREE_CHAT,
                [{"role": "user", "content": "hi"}],
            ):
                tokens.append(chunk)

            assert tokens == ["你", "好", "呀"]


class TestStreamWithFallbackFallback:
    """AC-018: Primary model failure → auto-switch to fallback model"""

    @pytest.mark.asyncio
    async def test_primary_failure_switches_to_fallback(self):
        """When primary model stream fails, fallback model is tried."""
        router = ModelRouter()
        call_count = {"value": 0}

        async def mock_stream_model(model, messages, **kwargs):
            call_count["value"] += 1
            if call_count["value"] == 1:
                # Primary model fails
                raise ConnectionError("Primary model timeout")
            # Fallback model succeeds
            yield "fallback"
            yield " response"

        with patch.object(router, "_stream_model", side_effect=mock_stream_model):
            tokens = []
            async for chunk in router.stream_with_fallback(
                ScenarioType.NARRATIVE,
                [{"role": "user", "content": "continue story"}],
            ):
                tokens.append(chunk)

            assert call_count["value"] == 2
            assert tokens == ["fallback", " response"]

    @pytest.mark.asyncio
    async def test_multiple_fallbacks_before_success(self):
        """Multiple models fail before one succeeds."""
        router = ModelRouter()
        call_count = {"value": 0}

        async def mock_stream_model(model, messages, **kwargs):
            call_count["value"] += 1
            if call_count["value"] <= 2:
                raise TimeoutError(f"Model {model.name} timed out")
            yield "third"
            yield " model"
            yield " works"

        with patch.object(router, "_stream_model", side_effect=mock_stream_model):
            tokens = []
            async for chunk in router.stream_with_fallback(
                ScenarioType.NARRATIVE,
                [{"role": "user", "content": "hi"}],
            ):
                tokens.append(chunk)

            assert call_count["value"] == 3
            assert tokens == ["third", " model", " works"]

    @pytest.mark.asyncio
    async def test_fallback_does_not_interrupt_stream(self):
        """User experience is not interrupted — fallback seamlessly continues."""
        router = ModelRouter()

        async def mock_stream_model(model, messages, **kwargs):
            if model.tier == "S":
                raise ConnectionError("S-tier failed")
            yield "A-tier"
            yield " response"

        with patch.object(router, "_stream_model", side_effect=mock_stream_model):
            result_text = ""
            async for chunk in router.stream_with_fallback(
                ScenarioType.NARRATIVE,
                [{"role": "user", "content": "hi"}],
            ):
                result_text += chunk

            assert result_text == "A-tier response"


class TestStreamWithFallbackAllFail:
    """AC-019: All fallback models fail → yield scenario-specific fallback text"""

    @pytest.mark.asyncio
    async def test_all_fail_yields_fallback_text(self):
        """All models fail → single yield of scenario-specific friendly text."""
        router = ModelRouter()

        async def mock_stream_model(model, messages, **kwargs):
            raise Exception(f"Model {model.name} failed")

        with patch.object(router, "_stream_model", side_effect=mock_stream_model):
            tokens = []
            async for chunk in router.stream_with_fallback(
                ScenarioType.FREE_CHAT,
                [{"role": "user", "content": "hi"}],
            ):
                tokens.append(chunk)

            # Should yield exactly one fallback text
            assert len(tokens) == 1
            # FREE_CHAT fallback text should contain role-play style
            assert "走神" in tokens[0] or "抱歉" in tokens[0]

    @pytest.mark.asyncio
    async def test_all_fail_narrative_fallback_text(self):
        """NARRATIVE scenario gets narrative-specific fallback text."""
        router = ModelRouter()

        async def mock_stream_model(model, messages, **kwargs):
            raise Exception("All failed")

        with patch.object(router, "_stream_model", side_effect=mock_stream_model):
            tokens = []
            async for chunk in router.stream_with_fallback(
                ScenarioType.NARRATIVE,
                [{"role": "user", "content": "continue"}],
            ):
                tokens.append(chunk)

            assert len(tokens) == 1
            assert "故事" in tokens[0] or "停滞" in tokens[0] or "流淌" in tokens[0]

    @pytest.mark.asyncio
    async def test_all_fail_choice_generation_fallback_text(self):
        """CHOICE_GENERATION scenario gets choice-specific fallback text."""
        router = ModelRouter()

        async def mock_stream_model(model, messages, **kwargs):
            raise Exception("All failed")

        with patch.object(router, "_stream_model", side_effect=mock_stream_model):
            tokens = []
            async for chunk in router.stream_with_fallback(
                ScenarioType.CHOICE_GENERATION,
                [{"role": "user", "content": "generate"}],
            ):
                tokens.append(chunk)

            assert len(tokens) == 1
            assert "选项" in tokens[0] or "无法生成" in tokens[0]

    @pytest.mark.asyncio
    async def test_all_fail_default_fallback_text(self):
        """Unknown/unmapped scenario gets default fallback text."""
        router = ModelRouter()

        async def mock_stream_model(model, messages, **kwargs):
            raise Exception("All failed")

        with patch.object(router, "_stream_model", side_effect=mock_stream_model):
            tokens = []
            # Use a scenario that doesn't have a specific fallback text
            async for chunk in router.stream_with_fallback(
                ScenarioType.EMOTION_INFERENCE,
                [{"role": "user", "content": "infer"}],
            ):
                tokens.append(chunk)

            assert len(tokens) == 1
            assert "抱歉" in tokens[0] or "稍后" in tokens[0]

    @pytest.mark.asyncio
    async def test_fallback_text_is_single_yield(self):
        """Fallback text is yielded exactly once (non-streaming fallback)."""
        router = ModelRouter()

        async def mock_stream_model(model, messages, **kwargs):
            raise Exception("All failed")

        with patch.object(router, "_stream_model", side_effect=mock_stream_model):
            count = 0
            async for _ in router.stream_with_fallback(
                ScenarioType.FREE_CHAT,
                [{"role": "user", "content": "hi"}],
            ):
                count += 1

            assert count == 1


class TestStreamWithFallbackParams:
    """Test parameter passing and kwargs"""

    @pytest.mark.asyncio
    async def test_kwargs_passed_to_stream_model(self):
        """kwargs (temperature, max_tokens) are passed through to _stream_model."""
        router = ModelRouter()
        received_kwargs = {}

        async def mock_stream_model(model, messages, **kwargs):
            received_kwargs.update(kwargs)
            yield "ok"

        with patch.object(router, "_stream_model", side_effect=mock_stream_model):
            async for _ in router.stream_with_fallback(
                ScenarioType.FREE_CHAT,
                [{"role": "user", "content": "hi"}],
                temperature=0.5,
                max_tokens=200,
            ):
                pass

            assert received_kwargs.get("temperature") == 0.5
            assert received_kwargs.get("max_tokens") == 200

    @pytest.mark.asyncio
    async def test_messages_passed_to_stream_model(self):
        """messages list is passed through to _stream_model."""
        router = ModelRouter()
        received_messages = []

        async def mock_stream_model(model, messages, **kwargs):
            received_messages.append(messages)
            yield "ok"

        test_messages = [
            {"role": "system", "content": "You are a character."},
            {"role": "user", "content": "Hello"},
        ]

        with patch.object(router, "_stream_model", side_effect=mock_stream_model):
            async for _ in router.stream_with_fallback(
                ScenarioType.FREE_CHAT,
                test_messages,
            ):
                pass

            assert len(received_messages) == 1
            assert received_messages[0] == test_messages
