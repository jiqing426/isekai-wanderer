"""Gift records model"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base


class GiftRecord(Base):
    __tablename__ = "gift_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("game_sessions.id"), nullable=True)
    character_id = Column(UUID(as_uuid=True), ForeignKey("characters.id"), nullable=False)
    gift_id = Column(String(100), nullable=False)
    gift_name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    affection_delta = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_gift_records_user", "user_id"),
        Index("idx_gift_records_session", "session_id"),
    )
