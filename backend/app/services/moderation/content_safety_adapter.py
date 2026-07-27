"""External content safety API adapter.

Provides a unified interface for integrating with external moderation services
(e.g., Baidu Content Moderation, Tencent Cloud Content Security, OpenAI Moderation).
Falls back gracefully when external service is unavailable.
"""

import logging
from typing import Optional, List
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ModerationCategory(str, Enum):
    """Standard moderation categories."""
    HATE = "hate"
    HARASSMENT = "harassment"
    SEXUAL = "sexual"
    VIOLENCE = "violence"
    SELF_HARM = "self_harm"
    SPAM = "spam"
    POLITICAL = "political"
    PROFANITY = "profanity"


@dataclass
class ContentSafetyFlag:
    """A single moderation flag from external API."""
    category: ModerationCategory
    confidence: float  # 0.0 to 1.0
    flagged: bool


@dataclass
class ContentSafetyResult:
    """Aggregated result from content safety check."""
    is_safe: bool
    flags: List[ContentSafetyFlag] = field(default_factory=list)
    provider: str = "none"  # e.g., "openai", "baidu", "tencent", "none"
    latency_ms: float = 0.0
    error: Optional[str] = None

    @property
    def highest_confidence(self) -> float:
        if not self.flags:
            return 0.0
        return max(f.confidence for f in self.flags if f.flagged) if any(f.flagged for f in self.flags) else 0.0

    @property
    def flagged_categories(self) -> List[ModerationCategory]:
        return [f.category for f in self.flags if f.flagged]


class ContentSafetyAdapter:
    """Adapter for external content safety APIs.

    Supports multiple providers with automatic fallback:
    - OpenAI Moderation API
    - Baidu Content Moderation (placeholder)
    - Tencent Cloud Content Security (placeholder)

    When no provider is configured or all fail, returns a safe-pass result
    (delegates to local keyword filter as primary defense).
    """

    def __init__(self, provider: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize content safety adapter.

        Args:
            provider: Provider name ("openai", "baidu", "tencent"). None = disabled.
            api_key: API key for the provider.
        """
        self.provider = provider
        self.api_key = api_key
        self._client = None

    async def _init_openai_client(self):
        """Lazily initialize OpenAI client for moderation."""
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                raise

    async def check(self, text: str) -> ContentSafetyResult:
        """Check text content using configured external provider.

        Args:
            text: Text to moderate.

        Returns:
            ContentSafetyResult with flags and safety status.
        """
        if not text or not text.strip():
            return ContentSafetyResult(is_safe=True, provider="none")

        if self.provider is None:
            return ContentSafetyResult(
                is_safe=True,
                provider="none",
                error="No external provider configured",
            )

        import time
        start = time.monotonic()

        try:
            if self.provider == "openai":
                result = await self._check_openai(text)
            elif self.provider == "baidu":
                result = await self._check_baidu(text)
            elif self.provider == "tencent":
                result = await self._check_tencent(text)
            else:
                result = ContentSafetyResult(
                    is_safe=True,
                    provider="none",
                    error=f"Unknown provider: {self.provider}",
                )

            elapsed = (time.monotonic() - start) * 1000
            result.latency_ms = elapsed
            return result

        except Exception as e:
            elapsed = (time.monotonic() - start) * 1000
            logger.error(f"Content safety check failed ({self.provider}): {e}")
            return ContentSafetyResult(
                is_safe=True,  # Fail-open: let keyword filter handle
                provider=self.provider or "none",
                latency_ms=elapsed,
                error=str(e),
            )

    async def _check_openai(self, text: str) -> ContentSafetyResult:
        """Check content using OpenAI Moderation API."""
        await self._init_openai_client()

        response = await self._client.moderations.create(
            model="omni-moderation-latest",
            input=text,
        )

        result_data = response.results[0]
        flags = []

        # Map OpenAI categories to our enum
        category_map = {
            "hate": ModerationCategory.HATE,
            "harassment": ModerationCategory.HARASSMENT,
            "sexual": ModerationCategory.SEXUAL,
            "violence": ModerationCategory.VIOLENCE,
            "self-harm": ModerationCategory.SELF_HARM,
        }

        scores = result_data.category_scores
        categories = result_data.categories

        for openai_cat, our_cat in category_map.items():
            flagged = getattr(categories, openai_cat, False)
            confidence = getattr(scores, openai_cat, 0.0)
            flags.append(ContentSafetyFlag(
                category=our_cat,
                confidence=confidence,
                flagged=flagged,
            ))

        is_safe = not result_data.flagged

        return ContentSafetyResult(
            is_safe=is_safe,
            flags=flags,
            provider="openai",
        )

    async def _check_baidu(self, text: str) -> ContentSafetyResult:
        """Check content using Baidu Content Moderation API.

        Placeholder — implement when Baidu API credentials are configured.
        """
        logger.warning("Baidu content moderation not yet implemented")
        return ContentSafetyResult(
            is_safe=True,
            provider="baidu",
            error="Baidu moderation not implemented",
        )

    async def _check_tencent(self, text: str) -> ContentSafetyResult:
        """Check content using Tencent Cloud Content Security.

        Placeholder — implement when Tencent API credentials are configured.
        """
        logger.warning("Tencent content moderation not yet implemented")
        return ContentSafetyResult(
            is_safe=True,
            provider="tencent",
            error="Tencent moderation not implemented",
        )

    async def close(self):
        """Close external API client."""
        if self._client:
            await self._client.close()
            self._client = None
