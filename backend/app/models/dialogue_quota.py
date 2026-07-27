"""Dialogue quota model and lifecycle stage enum (CR-016)."""

import enum
import uuid
from datetime import datetime, date
from sqlalchemy import String, DateTime, ForeignKey, Integer, Date, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class LifecycleStage(str, enum.Enum):
    """User lifecycle stage for dynamic quota calculation."""
    honeymoon = "honeymoon"   # registration day 1-3
    growth = "growth"         # registration day 4-7
    regular = "regular"       # registration day 8+
    returnee = "returnee"     # 7+ days inactive, returns for 3 days


class DialogueQuota(Base):
    """Daily dialogue quota per user — base + fragment extra."""

    __tablename__ = "dialogue_quotas"
    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_dialogue_quota_user_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    base_quota: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    consumed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    fragment_extra: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    fragment_consumed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
