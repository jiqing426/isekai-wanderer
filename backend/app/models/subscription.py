"""Subscription tier, status enums and Subscription SQLAlchemy model.

After CR-044, subscription_plans table is merged into subscriptions table.
This model now maps to the unified 'subscriptions' table with all fields.
"""

import enum
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer, Numeric, Boolean
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
    """Unified subscription record — maps to 'subscriptions' table (merged from subscription_plans in CR-044)."""

    __tablename__ = "subscriptions"

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
    # Fields from legacy payment.Subscription
    plan_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    billing_cycle: Mapped[str] = mapped_column(String(10), default="monthly")
    currency: Mapped[str] = mapped_column(String(3), default="CNY")
    price: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    is_mock: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=False)
    quota_total: Mapped[int] = mapped_column(Integer, default=50)
    quota_used: Mapped[int] = mapped_column(Integer, default=0)
    quota_period: Mapped[str | None] = mapped_column(String(20), default="regular")
    # Fragment grant tracking (from CR-016)
    fragment_quota: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="Monthly fragment quota for this tier"
    )
    last_fragment_grant_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="Last fragment grant time"
    )
    next_fragment_grant_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="Next scheduled fragment grant time"
    )
    # CR-044: Pending downgrade support
    pending_tier: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="Tier to downgrade to after current period ends"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
