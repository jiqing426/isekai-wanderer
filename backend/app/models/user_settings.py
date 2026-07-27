"""UserSettings SQLAlchemy model."""

import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class UserSettings(Base):
    """User settings model for play preferences and notifications."""

    __tablename__ = "user_settings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Play preferences
    typing_speed: Mapped[str] = mapped_column(String(20), default="normal")
    auto_play: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_play_delay_ms: Mapped[int] = mapped_column(Integer, default=3000)
    bgm_volume: Mapped[int] = mapped_column(Integer, default=80)
    sfx_volume: Mapped[int] = mapped_column(Integer, default=100)
    animation_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    animation_quality: Mapped[str] = mapped_column(String(20), default="high")

    # Notification settings
    notification_cg_unlock: Mapped[bool] = mapped_column(Boolean, default=True)
    notification_affection: Mapped[bool] = mapped_column(Boolean, default=True)
    notification_new_script: Mapped[bool] = mapped_column(Boolean, default=True)
    update_notify: Mapped[bool] = mapped_column(Boolean, default=True)
    activity_reminder: Mapped[bool] = mapped_column(Boolean, default=True)
    checkin_push: Mapped[bool] = mapped_column(Boolean, default=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
