"""Keyword-based content filter with regex support.

Maintains a configurable sensitive word library and applies pattern matching
to detect prohibited content in user-generated text.
"""

import re
import logging
from typing import List, Optional, Set, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class FilterMatch:
    """Represents a single filter match."""
    keyword: str
    category: str  # e.g., "profanity", "violence", "sexual", "political", "spam"
    severity: int  # 1 (low) to 5 (critical)
    position: int  # start index in text
    matched_text: str


@dataclass
class FilterResult:
    """Result of keyword filtering."""
    is_safe: bool
    matches: List[FilterMatch] = field(default_factory=list)
    blocked: bool = False  # True if severity >= block_threshold
    highest_severity: int = 0

    @property
    def match_count(self) -> int:
        return len(self.matches)


class KeywordFilter:
    """Keyword and regex-based content filter.

    Supports:
    - Exact keyword matching (case-insensitive)
    - Regex pattern matching
    - Severity levels (1-5)
    - Category classification
    - Configurable block threshold
    """

    # Default sensitive word library — extend via load_keywords() or constructor
    DEFAULT_KEYWORDS: List[Tuple[str, str, int]] = [
        # (keyword/regex, category, severity)
        # Profanity (severity 2-3)
        (r"操你", "profanity", 3),
        (r"妈的", "profanity", 2),
        (r"他妈的", "profanity", 3),
        (r"我操", "profanity", 3),
        (r"傻[逼比]", "profanity", 3),
        (r"去死", "profanity", 2),
        # Violence (severity 3-4)
        (r"杀[了掉你]", "violence", 3),
        (r"砍[死你了]", "violence", 4),
        (r"自[杀残]", "violence", 4),
        (r"炸弹", "violence", 3),
        (r"枪[击支]", "violence", 3),
        # Sexual (severity 3-4)
        (r"色情", "sexual", 3),
        (r"裸[体聊]", "sexual", 3),
        (r"约[炮]", "sexual", 4),
        # Spam (severity 1-2)
        (r"加[微wx]", "spam", 2),
        (r"扫码领[红奖]", "spam", 2),
        (r"免费领[取]", "spam", 1),
        (r"https?://[^\s]*\.(cn|top|xyz|buzz)", "spam", 2),
    ]

    def __init__(
        self,
        keywords: Optional[List[Tuple[str, str, int]]] = None,
        block_threshold: int = 3,
    ):
        """Initialize keyword filter.

        Args:
            keywords: List of (pattern, category, severity) tuples.
                      If None, uses DEFAULT_KEYWORDS.
            block_threshold: Minimum severity to trigger block (default 3).
        """
        self._keywords = list(keywords) if keywords is not None else list(self.DEFAULT_KEYWORDS)
        self.block_threshold = block_threshold
        self._compiled_patterns: List[Tuple[re.Pattern, str, int]] = []
        self._compile_patterns()

    def _compile_patterns(self):
        """Pre-compile regex patterns for performance."""
        self._compiled_patterns = []
        for pattern, category, severity in self._keywords:
            try:
                compiled = re.compile(pattern, re.IGNORECASE)
                self._compiled_patterns.append((compiled, category, severity))
            except re.error as e:
                logger.warning(f"Invalid regex pattern '{pattern}': {e}")

    def add_keyword(self, pattern: str, category: str, severity: int):
        """Add a new keyword/pattern to the filter.

        Args:
            pattern: Regex pattern string.
            category: Category label (profanity, violence, sexual, spam, political).
            severity: Severity level 1-5.
        """
        self._keywords.append((pattern, category, severity))
        try:
            compiled = re.compile(pattern, re.IGNORECASE)
            self._compiled_patterns.append((compiled, category, severity))
        except re.error as e:
            logger.warning(f"Failed to compile added pattern '{pattern}': {e}")

    def remove_keyword(self, pattern: str):
        """Remove a keyword pattern by exact match."""
        self._keywords = [(p, c, s) for p, c, s in self._keywords if p != pattern]
        self._compiled_patterns = [
            (pat, cat, sev) for pat, cat, sev in self._compiled_patterns
            if pat.pattern != pattern
        ]

    def check(self, text: str) -> FilterResult:
        """Check text against all keyword patterns.

        Args:
            text: User-generated text to check.

        Returns:
            FilterResult with matches and safety status.
        """
        if not text or not text.strip():
            return FilterResult(is_safe=True)

        matches: List[FilterMatch] = []
        highest_severity = 0

        for pattern, category, severity in self._compiled_patterns:
            for match in pattern.finditer(text):
                matches.append(FilterMatch(
                    keyword=pattern.pattern,
                    category=category,
                    severity=severity,
                    position=match.start(),
                    matched_text=match.group(),
                ))
                highest_severity = max(highest_severity, severity)

        blocked = highest_severity >= self.block_threshold
        is_safe = not blocked

        return FilterResult(
            is_safe=is_safe,
            matches=matches,
            blocked=blocked,
            highest_severity=highest_severity,
        )

    def sanitize(self, text: str, replacement: str = "***") -> str:
        """Replace matched keywords with replacement string.

        Args:
            text: Input text.
            replacement: Replacement string for matches.

        Returns:
            Sanitized text with matches replaced.
        """
        if not text:
            return text

        result = text
        # Sort matches by position (reverse) to avoid offset issues
        all_matches = []
        for pattern, category, severity in self._compiled_patterns:
            for match in pattern.finditer(text):
                all_matches.append((match.start(), match.end(), match.group()))

        # Sort by start position descending so replacements don't shift offsets
        all_matches.sort(key=lambda m: m[0], reverse=True)

        # Deduplicate overlapping matches
        seen_ranges: Set[Tuple[int, int]] = set()
        for start, end, matched in all_matches:
            overlaps = False
            for s, e in seen_ranges:
                if start < e and end > s:
                    overlaps = True
                    break
            if not overlaps:
                seen_ranges.add((start, end))
                result = result[:start] + replacement + result[end:]

        return result

    @property
    def keyword_count(self) -> int:
        """Number of active keyword patterns."""
        return len(self._compiled_patterns)
