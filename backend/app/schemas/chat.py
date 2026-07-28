"""聊天相关的Pydantic模型"""
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from uuid import UUID


class ChatMessageCreate(BaseModel):
    """创建聊天消息请求"""
    content: str = Field(..., min_length=1, max_length=1000, description="消息内容")


class ChatMessageResponse(BaseModel):
    """聊天消息响应"""
    message_id: str
    character_id: str
    sender_type: str
    content: str
    created_at: str
    
    class Config:
        from_attributes = True


class ChatMessageListResponse(BaseModel):
    """聊天消息列表响应"""
    messages: List[ChatMessageResponse]
    total: int
    page: int
    page_size: int


class ChatTopicResponse(BaseModel):
    """推荐话题响应"""
    topic_id: str
    character_id: str
    topic_text: str
    sort_order: int
    
    class Config:
        from_attributes = True
