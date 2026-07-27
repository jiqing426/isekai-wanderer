"""Ending Calculator Service (CR3-050 / AC-GAME-009).

Determines the ending type for a completed game session based on
accumulated affection, choice patterns, and streak history.

5 Ending Types:
  - good:       High affection + mostly positive choices
  - neutral:    Average affection + mixed choices
  - bad:        Low affection + mostly negative choices
  - secret:     Specific hidden choice combinations
  - true_end:   All conditions maxed + secret unlocked
"""

from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.game import GameSession, GameProgress
from app.models.script import NodeChoice, Node
from app.models.affection import Affection  # if exists, else fallback


# Ending type definitions
ENDING_TYPES = {
    "good": {
        "name": "Good Ending",
        "description": "幸福的结局",
        "min_affection": 60,
        "min_positive_ratio": 0.6,
        "requires_secret": False,
        "fragments_reward": 50,
    },
    "neutral": {
        "name": "Neutral Ending",
        "description": "平淡的结局",
        "min_affection": 30,
        "min_positive_ratio": 0.3,
        "requires_secret": False,
        "fragments_reward": 20,
    },
    "bad": {
        "name": "Bad Ending",
        "description": "遗憾的结局",
        "min_affection": 0,
        "min_positive_ratio": 0.0,
        "requires_secret": False,
        "fragments_reward": 10,
    },
    "secret": {
        "name": "Secret Ending",
        "description": "隐藏的真相",
        "min_affection": 50,
        "min_positive_ratio": 0.4,
        "requires_secret": True,
        "fragments_reward": 150,
    },
    "true_end": {
        "name": "True Ending",
        "description": "真正的结局",
        "min_affection": 90,
        "min_positive_ratio": 0.7,
        "requires_secret": True,
        "fragments_reward": 500,
    },
}

# Choices that count as "secret path" triggers
SECRET_CHOICE_KEYWORDS = ["真相", "secret", "truth", "hidden", "隐藏", "命运", "fate"]


class EndingCalculator:
    """Calculates the ending type for a completed game session."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate(
        self,
        session_id: UUID,
        user_id: UUID,
        character_id: UUID = None,
    ) -> Dict[str, Any]:
        """
        Calculate ending type based on session state.

        Returns:
            {
                "ending_type": "good" | "neutral" | "bad" | "secret" | "true_end",
                "ending_name": str,
                "description": str,
                "fragments_reward": int,
                "stats": {
                    "final_affection": int,
                    "positive_ratio": float,
                    "total_choices": int,
                    "secret_path_triggered": bool,
                },
            }
        """
        # 1. Get session and its choice history
        session = await self._get_session(session_id)
        if not session:
            return self._default_ending()

        # 2. Compute metrics
        affection_value = await self._get_affection(user_id, character_id)
        choice_stats = await self._analyze_choices(session_id)

        total_choices = choice_stats["total"]
        positive_ratio = choice_stats["positive_ratio"]
        secret_triggered = choice_stats["secret_triggered"]

        # 3. Determine ending type (check best → worst)
        ending_type = self._determine_ending(
            affection_value, positive_ratio, secret_triggered
        )

        ending_def = ENDING_TYPES[ending_type]

        return {
            "ending_type": ending_type,
            "ending_name": ending_def["name"],
            "description": ending_def["description"],
            "fragments_reward": ending_def["fragments_reward"],
            "stats": {
                "final_affection": affection_value,
                "positive_ratio": round(positive_ratio, 2),
                "total_choices": total_choices,
                "secret_path_triggered": secret_triggered,
            },
        }

    def _determine_ending(
        self,
        affection: int,
        positive_ratio: float,
        secret_triggered: bool,
    ) -> str:
        """Determine ending type by checking conditions from best to worst."""
        # True ending: max affection + secret + high positive
        te = ENDING_TYPES["true_end"]
        if (
            affection >= te["min_affection"]
            and positive_ratio >= te["min_positive_ratio"]
            and secret_triggered
        ):
            return "true_end"

        # Secret ending: moderate affection + secret path
        se = ENDING_TYPES["secret"]
        if (
            affection >= se["min_affection"]
            and positive_ratio >= se["min_positive_ratio"]
            and secret_triggered
        ):
            return "secret"

        # Good ending: high affection + positive choices
        ge = ENDING_TYPES["good"]
        if (
            affection >= ge["min_affection"]
            and positive_ratio >= ge["min_positive_ratio"]
        ):
            return "good"

        # Neutral ending: moderate affection + mixed choices
        ne = ENDING_TYPES["neutral"]
        if (
            affection >= ne["min_affection"]
            and positive_ratio >= ne["min_positive_ratio"]
        ):
            return "neutral"

        # Fallback: bad ending
        return "bad"

    async def _get_session(self, session_id: UUID) -> Optional[GameSession]:
        stmt = select(GameSession).where(GameSession.id == session_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_affection(self, user_id: UUID, character_id: UUID = None) -> int:
        """Get affection value for user-character pair."""
        if not character_id:
            return 50  # Default middle value if no character
        try:
            from app.services.narrative.affection_service import AffectionService
            svc = AffectionService(self.db)
            aff = await svc.get_affection(user_id, character_id)
            return aff.value
        except Exception:
            return 50

    async def _analyze_choices(self, session_id: UUID) -> Dict[str, Any]:
        """Analyze choice history for a session."""
        stmt = select(GameProgress).where(GameProgress.session_id == session_id)
        result = await self.db.execute(stmt)
        progress_entries = result.scalars().all()

        total = 0
        positive = 0
        secret_triggered = False

        for entry in progress_entries:
            if not entry.choice_id:
                continue
            # Fetch the choice
            choice_stmt = select(NodeChoice).where(NodeChoice.id == entry.choice_id)
            choice_result = await self.db.execute(choice_stmt)
            choice = choice_result.scalar_one_or_none()
            if not choice:
                continue

            total += 1
            if choice.affection_delta > 0:
                positive += 1

            # Check for secret path keywords
            text_lower = choice.text.lower()
            for kw in SECRET_CHOICE_KEYWORDS:
                if kw in text_lower:
                    secret_triggered = True
                    break

        positive_ratio = positive / total if total > 0 else 0.0

        return {
            "total": total,
            "positive": positive,
            "positive_ratio": positive_ratio,
            "secret_triggered": secret_triggered,
        }

    def _default_ending(self) -> Dict[str, Any]:
        """Return default neutral ending when session data is unavailable."""
        return {
            "ending_type": "neutral",
            "ending_name": ENDING_TYPES["neutral"]["name"],
            "description": ENDING_TYPES["neutral"]["description"],
            "fragments_reward": ENDING_TYPES["neutral"]["fragments_reward"],
            "stats": {
                "final_affection": 50,
                "positive_ratio": 0.5,
                "total_choices": 0,
                "secret_path_triggered": False,
            },
        }


def get_ending_calculator(db: AsyncSession) -> EndingCalculator:
    return EndingCalculator(db)
