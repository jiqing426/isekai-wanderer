"""Unit tests for UGC content moderation service (Phase 3, Task 1)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.moderation.keyword_filter import KeywordFilter, FilterResult, FilterMatch
from app.services.moderation.content_safety_adapter import (
    ContentSafetyAdapter,
    ContentSafetyResult,
    ContentSafetyFlag,
    ModerationCategory,
)
from app.services.moderation.service import ModerationService, ModerationResult


class TestKeywordFilter:
    """Tests for KeywordFilter class."""

    def test_init_default_keywords(self):
        """Test initialization with default keyword library."""
        filter = KeywordFilter()
        assert filter.keyword_count > 0
        assert filter.block_threshold == 3

    def test_init_custom_keywords(self):
        """Test initialization with custom keywords."""
        custom = [("test_word", "test", 2)]
        filter = KeywordFilter(keywords=custom, block_threshold=2)
        assert filter.keyword_count == 1
        assert filter.block_threshold == 2

    def test_check_clean_text(self):
        """Test checking clean text returns safe result."""
        filter = KeywordFilter()
        result = filter.check("Hello, this is a clean message about gaming.")
        assert result.is_safe is True
        assert result.blocked is False
        assert result.match_count == 0

    def test_check_empty_text(self):
        """Test checking empty text returns safe result."""
        filter = KeywordFilter()
        result = filter.check("")
        assert result.is_safe is True
        assert result.blocked is False

    def test_check_whitespace_only(self):
        """Test checking whitespace-only text returns safe result."""
        filter = KeywordFilter()
        result = filter.check("   \n\t  ")
        assert result.is_safe is True

    def test_check_profanity_match(self):
        """Test checking text with profanity triggers match."""
        filter = KeywordFilter()
        result = filter.check("他妈的这是什么东西")
        assert result.is_safe is False
        assert result.blocked is True
        assert result.match_count > 0
        assert result.highest_severity >= 3

    def test_check_violence_match(self):
        """Test checking text with violence triggers match."""
        filter = KeywordFilter()
        result = filter.check("我要杀了你")
        assert result.is_safe is False
        assert result.blocked is True
        assert any(m.category == "violence" for m in result.matches)

    def test_check_sexual_match(self):
        """Test checking text with sexual content triggers match."""
        filter = KeywordFilter()
        result = filter.check("裸聊服务")
        assert result.is_safe is False
        assert result.blocked is True
        assert any(m.category == "sexual" for m in result.matches)

    def test_check_spam_match(self):
        """Test checking text with spam triggers match."""
        filter = KeywordFilter()
        result = filter.check("加微信领红包")
        # Spam is severity 2, below default threshold 3
        assert result.match_count > 0
        assert any(m.category == "spam" for m in result.matches)

    def test_check_case_insensitive(self):
        """Test that matching is case-insensitive."""
        filter = KeywordFilter()
        # Add a custom pattern
        filter.add_keyword(r"badword", "test", 3)
        result1 = filter.check("This contains BADWORD in text")
        result2 = filter.check("This contains badword in text")
        assert result1.match_count == result2.match_count

    def test_add_keyword(self):
        """Test adding a new keyword pattern."""
        filter = KeywordFilter(keywords=[])
        assert filter.keyword_count == 0

        filter.add_keyword(r"custom_bad", "custom", 4)
        assert filter.keyword_count == 1

        result = filter.check("This is custom_bad content")
        assert result.blocked is True
        assert result.highest_severity == 4

    def test_add_invalid_regex(self):
        """Test adding invalid regex pattern doesn't crash."""
        filter = KeywordFilter()
        initial_count = filter.keyword_count

        # Invalid regex (unmatched bracket)
        filter.add_keyword(r"[invalid", "test", 3)

        # Should not add the invalid pattern
        assert filter.keyword_count == initial_count

    def test_remove_keyword(self):
        """Test removing a keyword pattern."""
        filter = KeywordFilter()
        initial_count = filter.keyword_count

        # Add a custom keyword
        filter.add_keyword(r"removable", "test", 2)
        assert filter.keyword_count == initial_count + 1

        # Remove it
        filter.remove_keyword(r"removable")
        assert filter.keyword_count == initial_count

    def test_sanitize_text(self):
        """Test sanitizing text replaces matches."""
        filter = KeywordFilter()
        sanitized = filter.sanitize("他妈的这是什么")
        assert "他妈的" not in sanitized
        assert "***" in sanitized

    def test_sanitize_empty_text(self):
        """Test sanitizing empty text returns empty string."""
        filter = KeywordFilter()
        assert filter.sanitize("") == ""
        assert filter.sanitize(None) is None

    def test_sanitize_custom_replacement(self):
        """Test sanitizing with custom replacement string."""
        filter = KeywordFilter()
        sanitized = filter.sanitize("他妈的测试", replacement="[FILTERED]")
        assert "[FILTERED]" in sanitized

    def test_multiple_matches(self):
        """Test text with multiple different matches."""
        filter = KeywordFilter()
        result = filter.check("他妈的我要杀了你这个傻逼")
        assert result.match_count >= 2
        assert result.highest_severity >= 3
        assert result.blocked is True

    def test_match_position_tracking(self):
        """Test that match positions are correctly tracked."""
        filter = KeywordFilter()
        text = "前面是正常文本，然后他妈的出现在中间"
        result = filter.check(text)
        if result.matches:
            match = result.matches[0]
            assert match.position >= 0
            assert match.matched_text in text


class TestContentSafetyAdapter:
    """Tests for ContentSafetyAdapter class."""

    @pytest.mark.asyncio
    async def test_check_no_provider(self):
        """Test checking with no provider configured."""
        adapter = ContentSafetyAdapter(provider=None)
        result = await adapter.check("test text")
        assert result.is_safe is True
        assert result.provider == "none"

    @pytest.mark.asyncio
    async def test_check_empty_text(self):
        """Test checking empty text."""
        adapter = ContentSafetyAdapter(provider="openai", api_key="test")
        result = await adapter.check("")
        assert result.is_safe is True

    @pytest.mark.asyncio
    async def test_check_unknown_provider(self):
        """Test checking with unknown provider."""
        adapter = ContentSafetyAdapter(provider="unknown", api_key="test")
        result = await adapter.check("test text")
        assert result.is_safe is True
        assert "Unknown provider" in result.error

    @pytest.mark.asyncio
    async def test_check_openai_success(self):
        """Test successful OpenAI moderation check."""
        adapter = ContentSafetyAdapter(provider="openai", api_key="test-key")

        # Mock OpenAI client
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.results = [MagicMock(
            flagged=False,
            categories=MagicMock(
                hate=False,
                harassment=False,
                sexual=False,
                violence=False,
                **{"self-harm": False},
            ),
            category_scores=MagicMock(
                hate=0.01,
                harassment=0.02,
                sexual=0.03,
                violence=0.04,
                **{"self-harm": 0.01},
            ),
        )]
        mock_client.moderations.create = AsyncMock(return_value=mock_response)
        adapter._client = mock_client

        result = await adapter._check_openai("clean text")
        assert result.is_safe is True
        assert result.provider == "openai"
        assert len(result.flags) > 0

    @pytest.mark.asyncio
    async def test_check_openai_flagged(self):
        """Test OpenAI moderation flags content."""
        adapter = ContentSafetyAdapter(provider="openai", api_key="test-key")

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.results = [MagicMock(
            flagged=True,
            categories=MagicMock(
                hate=True,
                harassment=False,
                sexual=False,
                violence=False,
                **{"self-harm": False},
            ),
            category_scores=MagicMock(
                hate=0.95,
                harassment=0.1,
                sexual=0.05,
                violence=0.2,
                **{"self-harm": 0.01},
            ),
        )]
        mock_client.moderations.create = AsyncMock(return_value=mock_response)
        adapter._client = mock_client

        result = await adapter._check_openai("hate speech content")
        assert result.is_safe is False
        assert result.provider == "openai"
        assert ModerationCategory.HATE in result.flagged_categories

    @pytest.mark.asyncio
    async def test_check_baidu_placeholder(self):
        """Test Baidu moderation placeholder implementation."""
        adapter = ContentSafetyAdapter(provider="baidu", api_key="test")
        result = await adapter._check_baidu("test text")
        assert result.is_safe is True
        assert result.provider == "baidu"
        assert "not implemented" in result.error.lower()

    @pytest.mark.asyncio
    async def test_check_tencent_placeholder(self):
        """Test Tencent moderation placeholder implementation."""
        adapter = ContentSafetyAdapter(provider="tencent", api_key="test")
        result = await adapter._check_tencent("test text")
        assert result.is_safe is True
        assert result.provider == "tencent"
        assert "not implemented" in result.error.lower()

    @pytest.mark.asyncio
    async def test_check_exception_handling(self):
        """Test exception handling in external check."""
        adapter = ContentSafetyAdapter(provider="openai", api_key="test-key")
        adapter._init_openai_client = AsyncMock(side_effect=Exception("API Error"))

        result = await adapter.check("test text")
        # Should fail-open (safe) and log error
        assert result.is_safe is True
        assert result.error is not None
        assert "API Error" in result.error

    @pytest.mark.asyncio
    async def test_close_client(self):
        """Test closing the external API client."""
        adapter = ContentSafetyAdapter(provider="openai", api_key="test")
        mock_client = AsyncMock()
        adapter._client = mock_client

        await adapter.close()
        mock_client.close.assert_called_once()
        assert adapter._client is None


class TestContentSafetyResult:
    """Tests for ContentSafetyResult dataclass."""

    def test_highest_confidence_no_flags(self):
        """Test highest_confidence with no flags."""
        result = ContentSafetyResult(is_safe=True, flags=[])
        assert result.highest_confidence == 0.0

    def test_highest_confidence_with_flags(self):
        """Test highest_confidence with multiple flags."""
        flags = [
            ContentSafetyFlag(category=ModerationCategory.HATE, confidence=0.3, flagged=True),
            ContentSafetyFlag(category=ModerationCategory.VIOLENCE, confidence=0.9, flagged=True),
            ContentSafetyFlag(category=ModerationCategory.SEXUAL, confidence=0.1, flagged=False),
        ]
        result = ContentSafetyResult(is_safe=False, flags=flags)
        assert result.highest_confidence == 0.9

    def test_flagged_categories(self):
        """Test flagged_categories property."""
        flags = [
            ContentSafetyFlag(category=ModerationCategory.HATE, confidence=0.8, flagged=True),
            ContentSafetyFlag(category=ModerationCategory.VIOLENCE, confidence=0.1, flagged=False),
            ContentSafetyFlag(category=ModerationCategory.SEXUAL, confidence=0.7, flagged=True),
        ]
        result = ContentSafetyResult(is_safe=False, flags=flags)
        assert ModerationCategory.HATE in result.flagged_categories
        assert ModerationCategory.SEXUAL in result.flagged_categories
        assert ModerationCategory.VIOLENCE not in result.flagged_categories


class TestModerationService:
    """Tests for ModerationService class."""

    def test_init_keyword_only(self):
        """Test initialization with keyword-only mode."""
        service = ModerationService(enable_external=False)
        assert service.enable_external is False
        assert service.keyword_filter is not None

    def test_init_external_no_config(self):
        """Test initialization with external requested but no config."""
        service = ModerationService(enable_external=True)
        # Should fall back to keyword-only
        assert service.enable_external is False

    @pytest.mark.asyncio
    async def test_moderate_clean_text(self):
        """Test moderating clean text."""
        service = ModerationService(enable_external=False)
        result = await service.moderate("This is a clean message about gaming")
        assert result.blocked is False
        assert result.safe is True
        assert len(result.reasons) == 0

    @pytest.mark.asyncio
    async def test_moderate_empty_text(self):
        """Test moderating empty text."""
        service = ModerationService(enable_external=False)
        result = await service.moderate("")
        assert result.blocked is False
        assert result.safe is True

    @pytest.mark.asyncio
    async def test_moderate_profanity(self):
        """Test moderating text with profanity."""
        service = ModerationService(enable_external=False)
        result = await service.moderate("他妈的这是什么东西")
        assert result.blocked is True
        assert result.safe is False
        assert len(result.reasons) > 0

    @pytest.mark.asyncio
    async def test_moderate_violence(self):
        """Test moderating text with violence."""
        service = ModerationService(enable_external=False)
        result = await service.moderate("我要杀了你")
        assert result.blocked is True
        assert result.safe is False

    @pytest.mark.asyncio
    async def test_moderate_with_context(self):
        """Test moderating with user_id and context."""
        service = ModerationService(enable_external=False)
        result = await service.moderate(
            "clean text",
            user_id="user123",
            context="chat"
        )
        assert result.safe is True

    @pytest.mark.asyncio
    async def test_moderate_batch(self):
        """Test batch moderation."""
        service = ModerationService(enable_external=False)
        texts = [
            "clean text 1",
            "他妈的脏话",
            "clean text 2",
        ]
        results = await service.moderate_batch(texts)
        assert len(results) == 3
        assert results[0].safe is True
        assert results[1].blocked is True
        assert results[2].safe is True

    def test_sanitize_text(self):
        """Test text sanitization."""
        service = ModerationService(enable_external=False)
        sanitized = service.sanitize("他妈的测试内容")
        assert "他妈的" not in sanitized
        assert "***" in sanitized

    @pytest.mark.asyncio
    async def test_moderate_with_external_enabled(self):
        """Test moderation with external API enabled (mocked)."""
        service = ModerationService(
            enable_external=True,
            external_provider="openai",
            external_api_key="test-key"
        )

        # Mock the safety adapter
        mock_adapter = AsyncMock()
        mock_adapter.check = AsyncMock(return_value=ContentSafetyResult(
            is_safe=True,
            provider="openai",
        ))
        service.safety_adapter = mock_adapter
        service.enable_external = True

        result = await service.moderate("clean text")
        assert result.safe is True
        mock_adapter.check.assert_called_once()

    @pytest.mark.asyncio
    async def test_moderate_external_flags_content(self):
        """Test moderation when external API flags content."""
        service = ModerationService(enable_external=False)

        # Mock external adapter that flags content
        mock_adapter = AsyncMock()
        mock_adapter.check = AsyncMock(return_value=ContentSafetyResult(
            is_safe=False,
            flags=[
                ContentSafetyFlag(
                    category=ModerationCategory.VIOLENCE,
                    confidence=0.95,
                    flagged=True,
                )
            ],
            provider="openai",
        ))
        service.safety_adapter = mock_adapter
        service.enable_external = True

        result = await service.moderate("some borderline text")
        assert result.blocked is True
        assert result.safe is False

    @pytest.mark.asyncio
    async def test_moderate_external_failure_fallback(self):
        """Test moderation falls back when external API fails."""
        service = ModerationService(enable_external=False)

        # Mock external adapter that raises exception
        mock_adapter = AsyncMock()
        mock_adapter.check = AsyncMock(side_effect=Exception("API Error"))
        service.safety_adapter = mock_adapter
        service.enable_external = True

        # Clean text should still pass (keyword filter only)
        result = await service.moderate("clean text")
        assert result.safe is True

    @pytest.mark.asyncio
    async def test_close_service(self):
        """Test closing the moderation service."""
        service = ModerationService(enable_external=False)
        mock_adapter = AsyncMock()
        service.safety_adapter = mock_adapter

        await service.close()
        mock_adapter.close.assert_called_once()


class TestModerationResult:
    """Tests for ModerationResult dataclass."""

    def test_summary_blocked(self):
        """Test summary for blocked content."""
        result = ModerationResult(
            blocked=True,
            safe=False,
            reasons=["Keyword filter blocked content (severity 4)"]
        )
        assert "BLOCKED" in result.summary

    def test_summary_passed(self):
        """Test summary for passed content."""
        result = ModerationResult(blocked=False, safe=True)
        assert "PASSED" in result.summary

    def test_summary_flagged(self):
        """Test summary for flagged (but not blocked) content."""
        result = ModerationResult(
            blocked=False,
            safe=False,
            reasons=["External API flagged content"]
        )
        assert "FLAGGED" in result.summary
