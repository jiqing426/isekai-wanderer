"""Unlock record SQLAlchemy model (CR-017)."""

import enum
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSON
from app.core.database import Base


class UnlockType(str, enum.Enum):
    """Types of unlockable content."""
    cg = "cg"
    achievement = "achievement"
    hidden_story = "hidden_story"
    voice = "voice"
    exclusive_script = "exclusive_script"
    reward_float = "reward_float"
    multi_reward = "multi_reward"


class Rarity(str, enum.Enum):
    """Rarity levels for unlock items."""
    R = "R"
    SR = "SR"
    SSR = "SSR"


class UnlockRecord(Base):
    """Record of unlocked content for a user."""

    __tablename__ = "unlock_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    unlock_type: Mapped[str] = mapped_column(
        String(30), nullable=False, index=True
    )
    content_id: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    title: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    image_url: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    rarity: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )
    reward_data: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )
    unlocked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    viewed: Mapped[bool] = mapped_column(
        Boolean, default=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
