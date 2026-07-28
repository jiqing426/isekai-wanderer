"""Chat message database model"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class ChatMessage(Base):
    """聊天消息表"""
    __tablename__ = "chat_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    character_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    sender_type = Column(String(10), nullable=False)  # 'npc' or 'user'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index('idx_chat_messages_character_user', 'character_id', 'user_id'),
        Index('idx_chat_messages_created_at', 'created_at'),
    )
    
    def to_dict(self):
        return {
            "message_id": str(self.id),
            "character_id": str(self.character_id),
            "sender_type": self.sender_type,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
