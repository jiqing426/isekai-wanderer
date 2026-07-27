"""Recap Service (CR3-053 / AC-GAME-012).

Generates adventure recap for a completed game session:
- Key choices made
- AI-generated summary
- Ending info
- Duration stats
"""

from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.game import GameSession, GameProgress
from app.models.script import NodeChoice, Node


class RecapService:
    """Generates adventure recap for completed sessions."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_recap(
        self,
        session_id: UUID,
        user_id: UUID,
    ) -> Dict[str, Any]:
        """
        Generate a complete recap for a game session.

        Returns:
            {
                "session_id": str,
                "key_choices": [...],
                "summary": str,
                "ending_type": str,
                "duration_minutes": int,
                "choice_count": int,
            }
        """
        # 1. Fetch session
        session = await self._get_session(session_id)
        if not session:
            return {"session_id": str(session_id), "error": "Session not found"}

        # Ownership check (CRIT-003)
        if session.user_id != user_id:
            return {"session_id": str(session_id), "error": "Access denied"}

        # 2. Collect key choices
        key_choices = await self._get_key_choices(session_id)

        # 3. Calculate duration
        duration_minutes = self._calculate_duration(session)

        # 4. Generate summary text
        summary = await self._generate_summary(session, key_choices)

        return {
            "session_id": str(session_id),
            "key_choices": key_choices,
            "summary": summary,
            "ending_type": session.ending_type or "unknown",
            "duration_minutes": duration_minutes,
            "choice_count": len(key_choices),
        }

    async def _get_session(self, session_id: UUID) -> Optional[GameSession]:
        stmt = select(GameSession).where(GameSession.id == session_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_key_choices(self, session_id: UUID) -> List[Dict[str, Any]]:
        """Get all meaningful choices made during the session."""
        stmt = select(GameProgress).where(GameProgress.session_id == session_id).order_by(GameProgress.created_at)
        result = await self.db.execute(stmt)
        progress_entries = result.scalars().all()

        key_choices = []
        for entry in progress_entries:
            if not entry.choice_id:
                continue

            # Fetch choice details
            choice_stmt = select(NodeChoice).where(NodeChoice.id == entry.choice_id)
            choice_result = await self.db.execute(choice_stmt)
            choice = choice_result.scalar_one_or_none()
            if not choice:
                continue

            # Fetch node for context
            node_stmt = select(Node).where(Node.id == choice.node_id)
            node_result = await self.db.execute(node_stmt)
            node = node_result.scalar_one_or_none()

            key_choices.append({
                "choice_id": str(choice.id),
                "text": choice.text,
                "affection_delta": choice.affection_delta,
                "node_text": (node.content or {}).get("text", "") if node else "",
                "created_at": entry.created_at.isoformat() if entry.created_at else None,
            })

        return key_choices

    def _calculate_duration(self, session: GameSession) -> int:
        """Calculate session duration in minutes."""
        if not session.started_at:
            return 0
        end_time = session.completed_at or datetime.now(timezone.utc)
        if session.started_at.tzinfo is None:
            # Make naive datetime timezone-aware
            started = session.started_at.replace(tzinfo=timezone.utc)
        else:
            started = session.started_at
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)
        delta = end_time - started
        return max(1, int(delta.total_seconds() / 60))

    async def _generate_summary(
        self, session: GameSession, key_choices: List[Dict[str, Any]]
    ) -> str:
        """Generate a text summary of the adventure."""
        # Try AI-generated summary via LLM gateway
        try:
            from app.services.llm.gateway import llm_gateway
            prompt = self._build_summary_prompt(session, key_choices)
            from app.services.llm.gateway import LLMMessage
            messages = [
                LLMMessage(role="system", content="You are a narrative writer for an interactive story game."),
                LLMMessage(role="user", content=prompt),
            ]
            provider = llm_gateway.provider
            response = await provider.complete(messages, temperature=0.7, max_tokens=300)
            summary = response.content
            if summary and len(summary) > 20:
                return summary
        except Exception:
            pass

        # Fallback: template-based summary
        return self._template_summary(session, key_choices)

    def _build_summary_prompt(
        self, session: GameSession, key_choices: List[Dict[str, Any]]
    ) -> str:
        """Build LLM prompt for generating adventure summary."""
        choice_texts = [c["text"] for c in key_choices[:10]]
        ending = session.ending_type or "unknown"
        return (
            f"Generate a brief adventure summary (2-3 sentences) for a completed visual novel session.\n"
            f"Ending type: {ending}\n"
            f"Total choices made: {len(key_choices)}\n"
            f"Key decisions: {'; '.join(choice_texts[:5])}\n"
            f"Write in a narrative, story-telling tone. Keep it under 100 words."
        )

    def _template_summary(
        self, session: GameSession, key_choices: List[Dict[str, Any]]
    ) -> str:
        """Generate template-based summary when LLM is unavailable."""
        ending = session.ending_type or "unknown"
        count = len(key_choices)
        duration = self._calculate_duration(session)

        ending_desc = {
            "good": "a heartwarming conclusion",
            "bad": "a bittersweet ending",
            "neutral": "a quiet resolution",
            "secret": "a mysterious revelation",
            "true_end": "the true ending — all secrets unveiled",
        }.get(ending, "an unexpected conclusion")

        if count == 0:
            return f"This brief adventure led to {ending_desc}."

        return (
            f"Over {duration} minutes, you made {count} choices that shaped your journey, "
            f"leading to {ending_desc}."
        )


def get_recap_service(db: AsyncSession) -> RecapService:
    return RecapService(db)
