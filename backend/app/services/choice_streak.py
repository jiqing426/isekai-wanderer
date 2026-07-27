"""Choice Streak Service (CR3-049 / AC-GAME-008).

Tracks cumulative choice patterns (streaks) per user/session.
When a streak reaches a threshold, triggers special events
(e.g., bonus dialogue, hidden CG unlock, achievement trigger).
"""

from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.game import GameSession, GameProgress
from app.models.script import NodeChoice


# Streak thresholds that trigger special events
STREAK_THRESHOLDS: Dict[int, Dict[str, Any]] = {
    3: {"event": "minor_bonus", "fragments": 10, "description": "连续选择同一倾向 3 次"},
    5: {"event": "medium_bonus", "fragments": 30, "description": "连续选择同一倾向 5 次"},
    10: {"event": "major_bonus", "fragments": 100, "description": "连续选择同一倾向 10 次"},
    20: {"event": "legendary_bonus", "fragments": 300, "description": "连续选择同一倾向 20 次"},
}

# Choice affinity categories for streak detection
AFFINITY_CATEGORIES = {
    "positive": ["kind", "gentle", "support", "help", "encourage", "protect", "care"],
    "negative": ["angry", "reject", "ignore", "cold", "hostile", "dismiss", "rude"],
    "bold": ["brave", "risk", "fight", "charge", "attack", "bold", "dare"],
    "cautious": ["wait", "observe", "hide", "careful", "plan", "think", "retreat"],
}


def _classify_choice(choice: NodeChoice) -> str:
    """Classify a choice's affinity based on its text and affection_delta."""
    text_lower = choice.text.lower()

    # First try text-based classification
    for category, keywords in AFFINITY_CATEGORIES.items():
        for kw in keywords:
            if kw in text_lower:
                return category

    # Fallback: use affection_delta
    if choice.affection_delta > 0:
        return "positive"
    elif choice.affection_delta < 0:
        return "negative"
    return "neutral"


class ChoiceStreakService:
    """Tracks cumulative choice patterns and triggers streak events."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_and_check(
        self,
        user_id: UUID,
        session_id: UUID,
        choice: NodeChoice,
    ) -> Optional[Dict[str, Any]]:
        """
        Record a choice and check if it triggers a streak event.

        Returns streak event info if triggered, None otherwise.
        """
        affinity = _classify_choice(choice)

        # Get current streak from session metadata
        session = await self._get_session(session_id)
        if not session:
            return None

        metadata = dict(session.metadata_json or {})
        streak_data = metadata.get("choice_streak", {})

        current_affinity = streak_data.get("affinity", "")
        current_count = streak_data.get("count", 0)

        if affinity == current_affinity:
            new_count = current_count + 1
        else:
            new_count = 1

        # Update streak in session metadata
        streak_data = {
            "affinity": affinity,
            "count": new_count,
            "last_choice_id": str(choice.id),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        metadata["choice_streak"] = streak_data
        session.metadata_json = metadata
        await self.db.flush()

        # Check if streak hits a threshold
        if new_count in STREAK_THRESHOLDS:
            threshold = STREAK_THRESHOLDS[new_count]
            return {
                "event": threshold["event"],
                "affinity": affinity,
                "streak_count": new_count,
                "fragments_reward": threshold["fragments"],
                "description": threshold["description"],
            }

        return None

    async def get_streak(self, session_id: UUID) -> Dict[str, Any]:
        """Get current streak state for a session."""
        session = await self._get_session(session_id)
        if not session:
            return {"affinity": "", "count": 0}

        metadata = session.metadata_json or {}
        streak = metadata.get("choice_streak", {})
        return {
            "affinity": streak.get("affinity", ""),
            "count": streak.get("count", 0),
            "last_choice_id": streak.get("last_choice_id"),
            "updated_at": streak.get("updated_at"),
        }

    async def _get_session(self, session_id: UUID) -> Optional[GameSession]:
        """Fetch a game session."""
        stmt = select(GameSession).where(GameSession.id == session_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


# Module-level singleton-style factory
def get_choice_streak_service(db: AsyncSession) -> ChoiceStreakService:
    return ChoiceStreakService(db)
