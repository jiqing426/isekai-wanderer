"""AffectionService - manages affection calculation and level transitions."""

from typing import Optional, Dict, Any
from uuid import UUID
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.affection import Affection, AffectionHistory
from app.models.script import NodeChoice, Character
from app.services.narrative.rule_engine import AFFECTION_LEVELS, get_affection_level


# Max single change clamped to ±5 per spec S004
MAX_DELTA = 5
MIN_AFFECTION = 0
MAX_AFFECTION = 100


@dataclass
class AffectionChange:
    """Result of an affection update."""
    old_value: int
    new_value: int
    old_level: str
    new_level: str
    delta: int
    level_changed: bool


class AffectionService:
    """Manages affection state for user-character pairs."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_affection(self, user_id: UUID, character_id: UUID) -> Affection:
        """Get or create affection record for a user-character pair."""
        stmt = select(Affection).where(
            Affection.user_id == user_id,
            Affection.character_id == character_id,
        )
        result = await self.db.execute(stmt)
        affection = result.scalar_one_or_none()

        if not affection:
            affection = Affection(
                user_id=user_id,
                character_id=character_id,
                value=0,
                level="acquaintance",
            )
            self.db.add(affection)
            await self.db.flush()

        return affection

    async def apply_choice_delta(
        self, user_id: UUID, choice_id: UUID
    ) -> Optional[AffectionChange]:
        """
        Apply affection change from a player choice.

        Reads affection_delta from NodeChoice, clamps to ±5,
        updates value, recalculates level.
        """
        # Load choice to get affection_delta and character context
        stmt = select(NodeChoice).where(NodeChoice.id == choice_id)
        result = await self.db.execute(stmt)
        choice = result.scalar_one_or_none()

        if not choice or choice.affection_delta == 0:
            return None

        # Clamp delta to ±5
        delta = max(-MAX_DELTA, min(MAX_DELTA, choice.affection_delta))

        # We need the character_id - extract from node content or choice metadata
        # For now, get it from the node's content JSON
        from app.models.script import Node
        node_stmt = select(Node).where(Node.id == choice.node_id)
        node_result = await self.db.execute(node_stmt)
        node = node_result.scalar_one_or_none()

        character_id = None
        if node and node.content and "character_id" in node.content:
            character_id = UUID(node.content["character_id"])

        if not character_id:
            return None

        return await self.update_affection(user_id, character_id, delta)

    async def update_affection(
        self, user_id: UUID, character_id: UUID, delta: int
    ) -> AffectionChange:
        """Update affection value and recalculate level."""
        # Clamp delta
        delta = max(-MAX_DELTA, min(MAX_DELTA, delta))

        affection = await self.get_affection(user_id, character_id)
        old_value = affection.value
        old_level = affection.level

        # Apply delta with bounds
        new_value = max(MIN_AFFECTION, min(MAX_AFFECTION, old_value + delta))

        # Recalculate level
        new_level = get_affection_level(new_value)

        # Update record
        affection.value = new_value
        affection.level = new_level
        await self.db.flush()

        # Record history
        history = AffectionHistory(
            user_id=user_id,
            character_id=character_id,
            delta=delta,
            old_value=old_value,
            new_value=new_value,
            old_level=old_level,
            new_level=new_level,
            reason="choice",
        )
        self.db.add(history)
        await self.db.flush()

        return AffectionChange(
            old_value=old_value,
            new_value=new_value,
            old_level=old_level,
            new_level=new_level,
            delta=delta,
            level_changed=(old_level != new_level),
        )

    async def get_all_affections(self, user_id: UUID) -> list[Dict[str, Any]]:
        """Get all affection records for a user, including character_name."""
        stmt = select(Affection).where(Affection.user_id == user_id)
        result = await self.db.execute(stmt)
        affections = list(result.scalars().all())

        # Batch load character names
        if affections:
            char_ids = [a.character_id for a in affections]
            char_stmt = select(Character).where(Character.id.in_(char_ids))
            char_result = await self.db.execute(char_stmt)
            char_map = {c.id: c.name for c in char_result.scalars().all()}
        else:
            char_map = {}

        return [
            {
                "character_id": str(a.character_id),
                "character_name": char_map.get(a.character_id, "Unknown"),
                "value": a.value,
                "level": get_affection_level(a.value),
                "level_label": _level_label(get_affection_level(a.value)),
            }
            for a in affections
        ]

    def get_behavior_hint(self, affection_value: int) -> str:
        """根据好感度值返回角色行为指引（用于 Prompt 注入）
        
        Args:
            affection_value: 好感度值 (0-100)
        
        Returns:
            行为指引文本
        """
        if affection_value < 20:
            return "保持距离，礼貌，有所保留"
        elif affection_value < 40:
            return "态度友好，偶尔关心，但不过分亲密"
        elif affection_value < 60:
            return "主动关心，分享心事，可以开玩笑"
        elif affection_value < 80:
            return "撒娇/吐槽，展现脆弱面，主动找话题"
        else:
            return "深情表达，独占欲，偶尔害羞"

    def calculate_ending(self, affection_value: int, character_id: str) -> str:
        """根据好感度计算结局类型
        
        Args:
            affection_value: 好感度值 (0-100)
            character_id: 角色ID
        
        Returns:
            结局类型: "good_ending" 或 "bad_ending"
        """
        if affection_value >= 60:
            return "good_ending"
        else:
            return "bad_ending"


def _level_label(level: str) -> str:
    """Get display label for affection level."""
    labels = {
        "acquaintance": "相识",
        "ambiguous": "暧昧",
        "trust": "信赖",
        "bond": "羁绊",
        "love": "挚爱",
    }
    return labels.get(level, level)
