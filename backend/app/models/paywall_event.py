"""Paywall scene enum and event model (CR-016)."""

import enum
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class PaywallScene(str, enum.Enum):
    """Paywall trigger scenes."""
    T1_quota = "T1_quota"
    T2_archive = "T2_archive"
    T3_premium = "T3_premium"
    T4_trial = "T4_trial"
    T5_gallery = "T5_gallery"
    T6_voice = "T6_voice"
    T7_rewind = "T7_rewind"
    T8_fragment = "T8_fragment"


class PaywallDisplayType(str, enum.Enum):
    """Display type for paywall UI."""
    modal = "modal"
    banner = "banner"
    toast = "toast"


class PaywallEvent(Base):
    """Record of paywall trigger events."""

    __tablename__ = "paywall_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    scene: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    display_type: Mapped[str] = mapped_column(String(10), nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
