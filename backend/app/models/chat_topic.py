"""推荐话题数据模型"""
from sqlalchemy import Column, String, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid


class ChatTopic(Base):
    """推荐话题表"""
    __tablename__ = "chat_topics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    character_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    topic_text = Column(Text, nullable=False)
    sort_order = Column(Integer, default=0)
    
    def to_dict(self):
        return {
            "topic_id": str(self.id),
            "character_id": str(self.character_id),
            "topic_text": self.topic_text,
            "sort_order": self.sort_order
        }
