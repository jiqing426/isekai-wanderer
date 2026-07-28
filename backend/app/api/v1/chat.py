"""Chat API routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc
from sqlalchemy.sql import func
from uuid import UUID
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.models.chat_message import ChatMessage
from app.models.chat_topic import ChatTopic
from app.schemas.chat import (
    ChatMessageResponse,
    ChatMessageListResponse,
    ChatMessageCreate,
    ChatTopicResponse
)
from app.api.v1.auth import get_current_user_id

router = APIRouter(prefix="/character-chat", tags=["character-chat"])


@router.get("/{character_id}/messages", response_model=ChatMessageListResponse)
async def get_chat_messages(
    character_id: UUID,
    page: int = 1,
    page_size: int = 20,
    current_user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取与指定角色的聊天消息列表
    
    Args:
        character_id: 角色ID
        page: 页码，默认1
        page_size: 每页数量，默认20
        current_user_id: 当前用户ID（从认证中获取）
        db: 数据库会话
    
    Returns:
        消息列表，包含分页信息
    """
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 查询消息，按创建时间倒序
    query = (
        select(ChatMessage)
        .where(
            ChatMessage.character_id == character_id,
            ChatMessage.user_id == current_user_id
        )
        .order_by(desc(ChatMessage.created_at))
        .offset(offset)
        .limit(page_size)
    )
    
    result = await db.execute(query)
    messages = result.scalars().all()
    
    # 查询总数
    count_query = (
        select(func.count())
        .select_from(ChatMessage)
        .where(
            ChatMessage.character_id == character_id,
            ChatMessage.user_id == current_user_id
        )
    )
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    # 转换为响应格式（按时间正序）
    messages.reverse()
    
    return ChatMessageListResponse(
        messages=[msg.to_dict() for msg in messages],
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/{character_id}/messages", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
async def send_chat_message(
    character_id: UUID,
    message: ChatMessageCreate,
    current_user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    发送聊天消息
    
    Args:
        character_id: 角色ID
        message: 消息内容
        current_user_id: 当前用户ID（从认证中获取）
        db: 数据库会话
    
    Returns:
        创建的消息对象
    """
    # 创建用户消息
    user_message = ChatMessage(
        character_id=character_id,
        user_id=current_user_id,
        sender_type="user",
        content=message.content,
        created_at=datetime.utcnow()
    )
    
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)
    
    # TODO: 这里可以添加NPC自动回复逻辑
    # 暂时只返回用户消息
    
    return ChatMessageResponse(**user_message.to_dict())


@router.get("/{character_id}/topics", response_model=List[ChatTopicResponse])
async def get_chat_topics(
    character_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    获取与指定角色的推荐话题列表
    
    Args:
        character_id: 角色ID
        current_user_id: 当前用户ID（从认证中获取）
        db: 数据库会话
    
    Returns:
        话题列表
    """
    query = (
        select(ChatTopic)
        .where(ChatTopic.character_id == character_id)
        .order_by(ChatTopic.sort_order)
        .limit(5)
    )
    
    result = await db.execute(query)
    topics = result.scalars().all()
    
    return [topic.to_dict() for topic in topics]
