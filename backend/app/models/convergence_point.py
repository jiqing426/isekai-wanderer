"""Convergence point SQLAlchemy model — v4.4 dual-agent architecture."""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String, DateTime, ForeignKey, Integer, Text, Boolean, JSON,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class ConvergencePoint(Base):
    """Story convergence point — where branching narratives rejoin."""

    __tablename__ = "convergence_points"
    __table_args__ = (
        UniqueConstraint("script_id", "chapter", name="uq_convergence_script_chapter"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    script_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scripts.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    chapter: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    required_rounds: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)
    scene_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scenes.id"), nullable=True,
    )
    content: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    is_final: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow,
    )
