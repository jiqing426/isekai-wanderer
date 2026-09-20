"""CR-037 Corvus-Story-Core SQLAlchemy models.

5 new tables for the Corvus engine integration:
- player_candidates: per-user character candidates (max 3)
- corvus_game_sessions: Corvus game sessions (separate from legacy game_sessions)
- session_npcs: NPC state per game session (affinity, presence, corvus character id)
- inventory_items: items held in a game session
- story_flags: key-value flags per game session (unique constraint on session+key)

All primary keys are UUID v4 (default=uuid.uuid4).
corvus_internal_game_id is VARCHAR(100), not UUID — stores Corvus slug format.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, Boolean, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class PlayerCandidate(Base):
    """Player character candidates for Corvus game sessions (max 3 per user)."""

    __tablename__ = "player_candidates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    personality: Mapped[str | None] = mapped_column(Text, nullable=True)
    backstory: Mapped[str | None] = mapped_column(Text, nullable=True)
    appearance: Mapped[str | None] = mapped_column(Text, nullable=True)
    initial_inventory: Mapped[dict] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )


class CorvusGameSession(Base):
    """Corvus game sessions — distinct from legacy game_sessions table.

    corvus_internal_game_id stores the Corvus slug (VARCHAR(100), not UUID).
    """

    __tablename__ = "corvus_game_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    selected_player_candidate_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("player_candidates.id"), nullable=True
    )
    # CR-039 D6: Store character_id from select-player for /game/status
    character_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("characters.id"), nullable=True
    )
    initial_location_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(30), default="waiting_select_player", index=True
    )
    corvus_internal_game_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True  # VARCHAR(100) — Corvus slug, not UUID
    )
    engine_type: Mapped[str] = mapped_column(
        String(10), default="corvus"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )


class SessionNpc(Base):
    """NPC state per Corvus game session (affinity, presence, etc.)."""

    __tablename__ = "session_npcs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    game_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("corvus_game_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    npc_template_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    affinity: Mapped[int] = mapped_column(Integer, default=0)
    present: Mapped[bool] = mapped_column(Boolean, default=True)
    corvus_character_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )


class InventoryItem(Base):
    """Items held in a Corvus game session."""

    __tablename__ = "inventory_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    game_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("corvus_game_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )


class StoryFlag(Base):
    """Story flags per Corvus game session.

    Unique constraint on (game_session_id, flag_key) — duplicate keys update
    instead of inserting (ON CONFLICT).
    """

    __tablename__ = "story_flags"

    __table_args__ = (
        UniqueConstraint("game_session_id", "flag_key", name="story_flags_game_session_id_flag_key_key"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    game_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("corvus_game_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    flag_key: Mapped[str] = mapped_column(String(200), nullable=False)
    flag_value: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
