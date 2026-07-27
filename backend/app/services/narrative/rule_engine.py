"""RuleEngine - validates LLM output against character personality, timeline, and affection constraints."""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.script import Node, Character
from app.models.affection import Affection


@dataclass
class RuleViolation:
    """A single rule violation found in LLM output."""
    rule: str
    detail: str
    severity: str = "error"  # "error" | "warning"


@dataclass
class ValidationResult:
    """Result of rule validation."""
    passed: bool
    violations: List[RuleViolation] = field(default_factory=list)

    def add_violation(self, rule: str, detail: str, severity: str = "error"):
        self.violations.append(RuleViolation(rule=rule, detail=detail, severity=severity))
        if severity == "error":
            self.passed = False


# Affection level thresholds (matching FE 5-level system)
AFFECTION_LEVELS = {
    "acquaintance": (0, 19),
    "ambiguous": (20, 39),
    "trust": (40, 59),
    "bond": (60, 79),
    "love": (80, 100),
}

# Intimate terms that should only appear at high affection
INTIMATE_TERMS = ["亲爱的", "宝贝", "darling", "honey", "my love", "sweetheart"]
WARM_TERMS = ["朋友", "friend", "trust", "信赖"]


def get_affection_level(value: int) -> str:
    """Get affection level label from numeric value."""
    if value >= 80:
        return "love"
    if value >= 60:
        return "bond"
    if value >= 40:
        return "trust"
    if value >= 20:
        return "ambiguous"
    return "acquaintance"


def get_level_threshold(level: str) -> int:
    """Get minimum value for a level."""
    if level in AFFECTION_LEVELS:
        return AFFECTION_LEVELS[level][0]
    return 0


class RuleEngine:
    """Validates LLM-generated content against story rules."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def validate_dialogue(
        self,
        text: str,
        character: Character,
        affection_value: int,
        current_node: Optional[Node] = None,
        completed_node_ids: Optional[List[UUID]] = None,
    ) -> ValidationResult:
        """
        Validate LLM-generated dialogue against all rules.

        Rules checked:
        1. Character personality consistency
        2. Affection-level appropriate terms
        3. Timeline consistency (no references to unreached events)
        """
        result = ValidationResult(passed=True)

        # Rule 1: Affection-level term check
        self._check_affection_terms(text, affection_value, result)

        # Rule 2: Character personality consistency
        self._check_personality(text, character, result)

        # Rule 3: Timeline consistency
        if current_node and completed_node_ids:
            self._check_timeline(text, current_node, completed_node_ids, result)

        return result

    def _check_affection_terms(
        self, text: str, affection_value: int, result: ValidationResult
    ):
        """Check that intimate terms match affection level."""
        text_lower = text.lower()

        # Intimate terms require bond (60+) level
        if affection_value < 60:
            for term in INTIMATE_TERMS:
                if term.lower() in text_lower:
                    result.add_violation(
                        rule="affection_intimate_term",
                        detail=f"Intimate term '{term}' used at affection {affection_value} (requires 60+)",
                    )

        # Warm terms require trust (40+) level
        if affection_value < 40:
            for term in WARM_TERMS:
                if term.lower() in text_lower:
                    result.add_violation(
                        rule="affection_warm_term",
                        detail=f"Warm term '{term}' used at affection {affection_value} (requires 40+)",
                        severity="warning",
                    )

    def _check_personality(
        self, text: str, character: Character, result: ValidationResult
    ):
        """Check dialogue matches character personality style."""
        style = character.dialogue_style or "neutral"
        text_lower = text.lower()

        # Cold/rational characters shouldn't use overly emotional language
        if style in ("cold", "rational", "冷淡", "理性"):
            overly_emotional = ["呜呜", "哇哇", "太开心了", "好激动", "sob", "so excited"]
            for term in overly_emotional:
                if term in text_lower:
                    result.add_violation(
                        rule="personality_mismatch",
                        detail=f"Cold/rational character used emotional term '{term}'",
                        severity="warning",
                    )

        # Gentle characters shouldn't use aggressive language
        if style in ("gentle", "温柔"):
            aggressive = ["滚", "闭嘴", "shut up", "get lost", "fuck"]
            for term in aggressive:
                if term in text_lower:
                    result.add_violation(
                        rule="personality_mismatch",
                        detail=f"Gentle character used aggressive term '{term}'",
                    )

    def _check_timeline(
        self,
        text: str,
        current_node: Node,
        completed_node_ids: List[UUID],
        result: ValidationResult,
    ):
        """Check that dialogue doesn't reference events that haven't happened yet."""
        # Extract spoiler keywords from node content
        if not current_node.content:
            return

        # Check if node content has spoiler_keywords for unreached nodes
        spoiler_keywords = current_node.content.get("spoiler_keywords", [])
        text_lower = text.lower()

        for keyword in spoiler_keywords:
            if keyword.lower() in text_lower:
                result.add_violation(
                    rule="timeline_spoiler",
                    detail=f"Reference to spoiler keyword '{keyword}' before it's revealed",
                )

    async def get_affection_for_character(
        self, user_id: UUID, character_id: UUID
    ) -> int:
        """Get current affection value for a user-character pair."""
        stmt = select(Affection).where(
            Affection.user_id == user_id,
            Affection.character_id == character_id,
        )
        db_result = await self.db.execute(stmt)
        affection = db_result.scalar_one_or_none()
        return affection.value if affection else 0
