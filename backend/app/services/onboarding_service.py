"""
OnboardingService — AC-034: First-play AI failure guarantee.

When a new user's first AI dialogue fails (timeout / quality below threshold),
the system automatically uses a preset guided script to complete the conversation.
Target: first-play failure rate < 5%.

Production: track failure counts in DB. Current MVP: in-memory + MockProvider fallback.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


# Preset guided scripts for first-play onboarding
ONBOARDING_SCRIPTS: Dict[str, Dict[str, Any]] = {
    "default": {
        "id": "onboarding_default",
        "title": "欢迎来到异世界",
        "steps": [
            {
                "text": "你好，冒险者！欢迎来到异世界。我是你的向导艾拉。",
                "emotion": "happy",
                "pause_seconds": 2,
            },
            {
                "text": "在这里，你将经历各种奇幻冒险，做出影响命运的选择。",
                "emotion": "neutral",
                "pause_seconds": 2,
            },
            {
                "text": "首先，请告诉我——你想成为什么样的冒险者？",
                "emotion": "thoughtful",
                "choices": [
                    {"id": "warrior", "text": "勇猛的战士"},
                    {"id": "mage", "text": "睿智的法师"},
                    {"id": "explorer", "text": "好奇的探险家"},
                ],
            },
        ],
    },
    "warrior": {
        "id": "onboarding_warrior",
        "title": "战士之路",
        "steps": [
            {
                "text": "战士！你的勇气令人敬佩。前方的路虽险，但你会成为最强的存在。",
                "emotion": "excited",
            },
        ],
    },
    "mage": {
        "id": "onboarding_mage",
        "title": "法师之路",
        "steps": [
            {
                "text": "法师……智慧是最强大的武器。让我们一起探索这个世界的奥秘吧。",
                "emotion": "thoughtful",
            },
        ],
    },
    "explorer": {
        "id": "onboarding_explorer",
        "title": "探险家之路",
        "steps": [
            {
                "text": "探险家！这个世界有太多未知等待你去发现。准备好了吗？",
                "emotion": "excited",
            },
        ],
    },
}


class OnboardingService:
    """
    Manages first-play experience with AI fallback guarantee.

    Features:
    - Detect if user is first-play (no prior completed sessions)
    - Try AI dialogue; if fails (timeout/error), use preset script
    - Track success/failure rates
    """

    def __init__(self):
        # In-memory tracking. Production: use DB counters.
        self._stats = {"total_first_plays": 0, "ai_success": 0, "fallback_used": 0}

    async def is_first_play(self, user_id: str, db=None) -> bool:
        """
        Check if this is the user's first play session.

        Uses game_sessions table: if user has 0 completed sessions, it's first play.
        """
        if db is None:
            return True  # Assume first play if no DB

        from sqlalchemy import select, func
        from app.models.game import GameSession

        stmt = (
            select(func.count())
            .select_from(GameSession)
            .where(
                GameSession.user_id == uuid.UUID(user_id),
                GameSession.status == "completed",
            )
        )
        result = await db.execute(stmt)
        completed = result.scalar() or 0
        return completed == 0

    async def generate_first_dialogue(
        self,
        user_id: str,
        llm_provider=None,
        prompt: str = "",
        timeout_seconds: float = 5.0,
        db=None,
    ) -> Dict[str, Any]:
        """
        Generate first-play dialogue with guaranteed fallback.

        Flow:
        1. If first play and LLM available → try AI with timeout
        2. If AI succeeds → return AI response
        3. If AI fails (timeout/error/quality) → return preset script
        4. Track success/failure

        Returns:
            {
                "text": str,
                "emotion": str,
                "source": "ai" | "fallback",
                "is_first_play": bool,
                "onboarding_step": int | None,
            }
        """
        first_play = await self.is_first_play(user_id, db)

        if not first_play:
            # Not first play — normal flow, no fallback needed
            return {
                "text": "",
                "emotion": "neutral",
                "source": "normal",
                "is_first_play": False,
                "onboarding_step": None,
            }

        self._stats["total_first_plays"] += 1

        # Try AI generation with timeout
        if llm_provider:
            try:
                result = await asyncio.wait_for(
                    self._try_ai_generate(llm_provider, prompt),
                    timeout=timeout_seconds,
                )
                # Quality check: response must be non-empty and > 10 chars
                if result and len(result.get("text", "")) > 10:
                    self._stats["ai_success"] += 1
                    return {
                        "text": result["text"],
                        "emotion": result.get("emotion", "neutral"),
                        "source": "ai",
                        "is_first_play": True,
                        "onboarding_step": 0,
                    }
                else:
                    logger.warning(f"AI response quality too low for first-play user {user_id}")
            except asyncio.TimeoutError:
                logger.warning(f"AI timeout for first-play user {user_id}, using fallback")
            except Exception as e:
                logger.error(f"AI generation failed for first-play user {user_id}: {e}")

        # Fallback: use preset onboarding script
        self._stats["fallback_used"] += 1
        script = ONBOARDING_SCRIPTS["default"]
        step = script["steps"][0]

        return {
            "text": step["text"],
            "emotion": step.get("emotion", "neutral"),
            "source": "fallback",
            "is_first_play": True,
            "onboarding_step": 0,
            "onboarding_script_id": script["id"],
        }

    async def get_onboarding_step(
        self, script_id: str, step_index: int
    ) -> Optional[Dict[str, Any]]:
        """Get a specific step from an onboarding script."""
        script = ONBOARDING_SCRIPTS.get(script_id)
        if not script:
            return None
        if step_index >= len(script["steps"]):
            return None
        step = script["steps"][step_index]
        return {
            "text": step["text"],
            "emotion": step.get("emotion", "neutral"),
            "choices": step.get("choices"),
            "step_index": step_index,
            "total_steps": len(script["steps"]),
            "is_last": step_index == len(script["steps"]) - 1,
        }

    async def _try_ai_generate(
        self, llm_provider, prompt: str
    ) -> Dict[str, Any]:
        """Attempt AI generation. Raises on failure."""
        text = await llm_provider.generate(prompt or "Generate onboarding dialogue")
        return {"text": text, "emotion": "happy"}

    def get_stats(self) -> Dict[str, Any]:
        """Get first-play success/failure statistics."""
        total = self._stats["total_first_plays"]
        fallback = self._stats["fallback_used"]
        success = self._stats["ai_success"]
        failure_rate = (fallback / total * 100) if total > 0 else 0.0
        return {
            "total_first_plays": total,
            "ai_success_count": success,
            "fallback_used_count": fallback,
            "ai_success_rate": round(100 - failure_rate, 1),
            "failure_rate": round(failure_rate, 1),
            "target_failure_rate": 5.0,
            "within_target": failure_rate < 5.0,
        }

    def reset_stats(self) -> None:
        """Reset tracking stats (for testing)."""
        self._stats = {"total_first_plays": 0, "ai_success": 0, "fallback_used": 0}


# Module-level singleton
onboarding_service: OnboardingService = OnboardingService()


def get_onboarding_service() -> OnboardingService:
    return onboarding_service
