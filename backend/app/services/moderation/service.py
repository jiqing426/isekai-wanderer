"""Unified content moderation service.

Combines local keyword filtering with optional external content safety APIs
to provide comprehensive UGC moderation.

Architecture:
  1. Keyword filter (fast, local, always available)
  2. External content safety API (slower, more accurate, optional)
  3. Merge results → final moderation decision

Usage:
    service = ModerationService()
    result = await service.moderate("some user text")
    if result.blocked:
        raise ValidationError("Content contains prohibited material")
"""

import logging
from typing import Optional, List
from dataclasses import dataclass, field

from app.core.config import settings

from .keyword_filter import KeywordFilter, FilterResult
from .content_safety_adapter import ContentSafetyAdapter, ContentSafetyResult, ModerationCategory

logger = logging.getLogger(__name__)


@dataclass
class ModerationResult:
    """Final moderation result combining all checks."""
    blocked: bool
    safe: bool
    keyword_result: Optional[FilterResult] = None
    safety_result: Optional[ContentSafetyResult] = None
    reasons: List[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        if self.blocked:
            return f"BLOCKED: {', '.join(self.reasons)}"
        if not self.safe:
            return f"FLAGGED: {', '.join(self.reasons)}"
        return "PASSED: No issues detected"


class ModerationService:
    """Unified content moderation service.

    Provides a single entry point for moderating user-generated content,
    combining fast local keyword filtering with optional external API checks.
    """

    def __init__(
        self,
        enable_external: bool = False,
        external_provider: Optional[str] = None,
        external_api_key: Optional[str] = None,
    ):
        """Initialize moderation service.

        Args:
            enable_external: Enable external content safety API (default: False).
            external_provider: External provider name ("openai", "baidu", "tencent").
            external_api_key: API key for external provider.
        """
        self.enable_external = enable_external

        # Initialize keyword filter (always available)
        self.keyword_filter = KeywordFilter()
        logger.info(f"Keyword filter initialized with {self.keyword_filter.keyword_count} patterns")

        # Initialize external adapter (optional)
        if enable_external:
            provider = external_provider or getattr(settings, 'moderation_provider', None)
            api_key = external_api_key or getattr(settings, 'moderation_api_key', None)

            if provider and api_key:
                self.safety_adapter = ContentSafetyAdapter(provider=provider, api_key=api_key)
                logger.info(f"External content safety enabled: {provider}")
            else:
                logger.warning(
                    f"External moderation requested but not configured "
                    f"(provider={provider}, api_key={'set' if api_key else 'missing'}). "
                    f"Falling back to keyword-only mode."
                )
                self.safety_adapter = ContentSafetyAdapter(provider=None)
                self.enable_external = False
        else:
            self.safety_adapter = ContentSafetyAdapter(provider=None)
            logger.info("External content safety disabled (keyword-only mode)")

    async def moderate(
        self,
        text: str,
        user_id: Optional[str] = None,
        context: Optional[str] = None,
    ) -> ModerationResult:
        """Moderate user-generated content.

        Args:
            text: Text content to moderate.
            user_id: Optional user ID for logging/audit.
            context: Optional context label (e.g., "comment", "review", "chat").

        Returns:
            ModerationResult with moderation decision and details.
        """
        # Empty or whitespace-only text passes
        if not text or not text.strip():
            return ModerationResult(blocked=False, safe=True)

        reasons = []

        # 1. Keyword filter (always runs)
        kw_result = self.keyword_filter.check(text)

        if kw_result.blocked:
            reasons.append(
                f"Keyword filter blocked content (severity {kw_result.highest_severity}, "
                f"{kw_result.match_count} matches)"
            )
            logger.warning(
                f"Content blocked by keyword filter: "
                f"user={user_id}, context={context}, "
                f"severity={kw_result.highest_severity}, matches={kw_result.match_count}"
            )
            return ModerationResult(
                blocked=True,
                safe=False,
                keyword_result=kw_result,
                reasons=reasons,
            )

        # 2. External content safety API (if enabled)
        safety_result = None
        if self.enable_external and self.safety_adapter:
            try:
                safety_result = await self.safety_adapter.check(text)

                if not safety_result.is_safe:
                    flagged_cats = [cat.value for cat in safety_result.flagged_categories]
                    reasons.append(
                        f"External API flagged content: {', '.join(flagged_cats)} "
                        f"(confidence {safety_result.highest_confidence:.2f})"
                    )
                    logger.warning(
                        f"Content flagged by external API: "
                        f"user={user_id}, context={context}, "
                        f"categories={flagged_cats}"
                    )

            except Exception as e:
                logger.error(
                    f"External moderation check failed: {e}. "
                    f"Falling back to keyword-only result."
                )
                safety_result = None

        # 3. Merge results
        blocked = bool(kw_result.blocked or (safety_result and not safety_result.is_safe))
        safe = not blocked

        # Collect all reasons
        if safety_result and safety_result.flags:
            for flag in safety_result.flags:
                if flag.flagged:
                    reasons.append(f"{flag.category.value}: {flag.confidence:.2f}")

        return ModerationResult(
            blocked=blocked,
            safe=safe,
            keyword_result=kw_result,
            safety_result=safety_result,
            reasons=reasons,
        )

    async def moderate_batch(
        self,
        texts: List[str],
        user_id: Optional[str] = None,
        context: Optional[str] = None,
    ) -> List[ModerationResult]:
        """Moderate multiple texts.

        Args:
            texts: List of text contents to moderate.
            user_id: Optional user ID.
            context: Optional context label.

        Returns:
            List of ModerationResult for each text.
        """
        results = []
        for text in texts:
            result = await self.moderate(text, user_id=user_id, context=context)
            results.append(result)
        return results

    def sanitize(self, text: str, replacement: str = "***") -> str:
        """Sanitize text by replacing sensitive keywords.

        Args:
            text: Input text.
            replacement: Replacement string for matches.

        Returns:
            Sanitized text.
        """
        return self.keyword_filter.sanitize(text, replacement=replacement)

    async def close(self):
        """Close external API connections."""
        if self.safety_adapter:
            await self.safety_adapter.close()
            logger.info("External moderation adapter closed")


# Singleton instance (keyword-only mode by default)
moderation_service = ModerationService(enable_external=False)
