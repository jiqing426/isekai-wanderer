"""Subscription tier, status enums and Subscription SQLAlchemy model (CR-016)."""

import enum
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class SubscriptionTier(str, enum.Enum):
    """Subscription tier levels."""
    free = "free"
    basic = "basic"
    standard = "standard"
    premium = "premium"


class SubscriptionStatus(str, enum.Enum):
    """Subscription lifecycle status."""
    active = "active"
    cancelled = "cancelled"
    expired = "expired"


class Subscription(Base):
    """Subscription record — tracks user tier, status, and validity window."""

    __tablename__ = "subscription_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    tier: Mapped[str] = mapped_column(
        String(20), nullable=False, default=SubscriptionTier.free.value, index=True
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=SubscriptionStatus.active.value, index=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Fragment grant tracking
    fragment_quota: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Monthly fragment quota for this tier"
    )
    last_fragment_grant_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="Last fragment grant time"
    )
    next_fragment_grant_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="Next scheduled fragment grant time"
    )
