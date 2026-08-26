"""Chat API routes"""
import asyncio
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc
from sqlalchemy.sql import func
from uuid import UUID
from typing import List, Optional, AsyncIterator
from datetime import datetime

from app.core.database import get_db
from app.models.chat_message import ChatMessage
from app.models.chat_topic import ChatTopic
from app.models.script import Character
from app.schemas.chat import (
    ChatMessageResponse,
    ChatMessageListResponse,
    ChatMessageCreate,
    ChatTopicResponse,
    ChatTopicListResponse,
    ChatSendResponse
)
from app.api.v1.auth import get_current_user_id

logger = logging.getLogger(__name__)

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


@router.post("/{character_id}/messages", response_model=ChatSendResponse, status_code=status.HTTP_201_CREATED)
async def send_chat_message(
    character_id: UUID,
    message: ChatMessageCreate,
    current_user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    发送聊天消息（含 NPC 自动回复）

    流程：
    1. 保存用户消息
    2. 查询角色人设 + 最近对话历史
    3. 调用 LLM 生成 NPC 回复
    4. 保存 NPC 回复
    5. 同时返回用户消息与 NPC 回复
    """
    # 1. 保存用户消息
    user_message = ChatMessage(
        character_id=character_id,
        user_id=current_user_id,
        sender_type="user",
        content=message.content,
        created_at=datetime.utcnow()
    )
    db.add(user_message)
    await db.flush()
    await db.refresh(user_message)

    # 2. 生成 NPC 回复（失败不影响用户消息保存）
    npc_message: Optional[ChatMessage] = None
    try:
        npc_content = await _generate_npc_reply(db, character_id, current_user_id, message.content)
        if npc_content:
            npc_message = ChatMessage(
                character_id=character_id,
                user_id=current_user_id,
                sender_type="npc",
                content=npc_content,
                created_at=datetime.utcnow()
            )
            db.add(npc_message)
            await db.flush()
            await db.refresh(npc_message)
    except Exception as e:
        logger.error(f"NPC reply generation failed for character={character_id}: {e}")
        # 不抛出，仍然返回用户消息

    await db.commit()

    # 3. 提取并保存记忆（异步执行，不阻塞响应）
    try:
        from app.services.narrative.memory_service import MemoryService
        memory_service = MemoryService(db)
        # 查询角色名称
        char_result = await db.execute(select(Character).where(Character.id == character_id))
        character = char_result.scalar_one_or_none()
        char_name = character.name if character else "角色"
        dialogue_text = f"用户: {message.content}\n{char_name}: {npc_content if npc_content else ''}"
        await memory_service.extract_and_store(
            user_id=current_user_id,
            character_id=character_id,
            dialogue_text=dialogue_text,
            session_id=None
        )
        await db.commit()
    except Exception as e:
        logger.debug(f"Memory extraction skipped: {e}")

    # 4. 更新每日任务进度（对话达人）
    try:
        from app.api.v1.daily_tasks import update_progress, ProgressUpdateRequest
        await update_progress(
            request=ProgressUpdateRequest(task_type="task_dialogue", increment=1),
            user_id=str(current_user_id),
            db=db
        )
    except Exception as e:
        logger.debug(f"Daily task progress update skipped: {e}")

    # 4. 组装响应
    user_msg_dict = user_message.to_dict()
    npc_msg_dict = npc_message.to_dict() if npc_message else None

    return ChatSendResponse(
        message=ChatMessageResponse(**user_msg_dict),
        npc_message=ChatMessageResponse(**npc_msg_dict) if npc_msg_dict else None,
    )


@router.post("/{character_id}/stream")
async def stream_chat_message(
    character_id: UUID,
    message: ChatMessageCreate,
    current_user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    发送聊天消息并流式返回 NPC 回复（SSE）

    使用完整 prompt（参考 free_chat_service）：
    - 角色完整人设（personality, likes, dialogue_style）
    - 剧本背景信息
    - 当前游戏进度（防剧透）
    - 好感度等级
    - 最近对话历史 + 记忆

    SSE 事件格式：
    - event: message, data: {"type": "text", "content": "..."}
    - event: done, data: {"type": "done", "message_id": "..."}
    """
    # 1. 保存用户消息
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

    # 2. 获取角色完整信息
    char_result = await db.execute(select(Character).where(Character.id == character_id))
    character = char_result.scalar_one_or_none()
    character_name = character.name if character else "角色"

    # 构建完整角色人设（参考 free_chat_service._get_character_persona_from_db）
    personality = character.personality or {} if character else {}
    character_persona = {
        "name": character_name,
        "description": character.description or "" if character else "",
        "dialogue_style": character.dialogue_style or "gentle" if character else "gentle",
        "traits": personality.get("traits", ""),
        "likes": personality.get("likes", ""),
        "dislikes": personality.get("dislikes", ""),
        "speak_style": personality.get("speak_style", character.dialogue_style or "" if character else ""),
        "example_sentences": personality.get("example_sentences", []),
        "title": personality.get("title", ""),
    }

    # 3. 获取剧本背景信息
    script_info = None
    if character and character.script_id:
        from app.models.script import Script
        script_result = await db.execute(select(Script).where(Script.id == character.script_id))
        script = script_result.scalar_one_or_none()
        if script:
            script_info = {
                "title": script.title,
                "description": script.description or "",
                "genre": script.genre or "",
            }

    # 4. 获取用户当前游戏进度（防剧透）
    game_progress_info = None
    if character and character.script_id:
        from app.models.game import GameSession
        session_result = await db.execute(
            select(GameSession)
            .where(
                GameSession.user_id == current_user_id,
                GameSession.script_id == character.script_id,
                GameSession.status == "active",
            )
            .order_by(desc(GameSession.started_at))
            .limit(1)
        )
        game_session = session_result.scalar_one_or_none()
        if game_session:
            game_progress_info = {
                "session_id": str(game_session.id),
                "route_id": str(game_session.route_id),
                "current_node_id": str(game_session.current_node_id) if game_session.current_node_id else None,
                "status": game_session.status,
            }

    # 5. 获取好感度
    from app.models.affection import Affection
    affection_result = await db.execute(
        select(Affection).where(
            Affection.user_id == current_user_id,
            Affection.character_id == character_id,
        )
    )
    affection = affection_result.scalar_one_or_none()
    affection_value = affection.value if affection else 0

    # 6. 获取最近对话历史（最近 5 条）
    history_result = await db.execute(
        select(ChatMessage)
        .where(
            ChatMessage.character_id == character_id,
            ChatMessage.user_id == current_user_id,
        )
        .order_by(desc(ChatMessage.created_at))
        .limit(5)
    )
    history_msgs = list(history_result.scalars().all())
    history_msgs.reverse()
    recent_messages = [
        {"role": "assistant" if m.sender_type == "npc" else "user", "content": m.content}
        for m in history_msgs
    ]

    # 7. 获取相关记忆（使用向量相似度召回）
    memories = []
    try:
        from app.services.narrative.memory_service import MemoryService
        memory_service = MemoryService(db)
        # 使用当前用户消息作为查询，召回相关记忆
        recalled = await memory_service.recall(
            user_id=current_user_id,
            character_id=character_id,
            query_text=message.content,
            limit=5
        )
        memories = [{"content": m["memory_text"]} for m in recalled]
    except Exception as e:
        logger.debug(f"Memory recall skipped: {e}")

    # 8. 构建完整 system prompt（使用 build_free_chat_prompt）
    from app.llm.prompts.free_chat import build_free_chat_prompt
    system_prompt = build_free_chat_prompt(
        character_name=character_name,
        character_persona=character_persona,
        affection_value=affection_value,
        recent_messages=recent_messages,
        memories=memories,
        script_info=script_info,
    )

    # 追加游戏进度上下文（防剧透指导）
    if game_progress_info:
        system_prompt += f"""

## 当前游戏进度
玩家正在进行的游戏会话：
- 路线 ID：{game_progress_info['route_id']}
- 当前节点 ID：{game_progress_info['current_node_id'] or '未知'}
- 状态：{game_progress_info['status']}

重要：玩家只玩到了这个进度。绝对不要透露此节点之后的任何剧情、选择或结局。
如果玩家询问后续剧情，用角色口吻回避。
"""

    # 用户 prompt
    user_prompt = message.content

    # 9. 创建流式响应生成器
    async def event_generator() -> AsyncIterator[str]:
        """生成 SSE 事件流（使用 model_router，和自由对话完全一致）"""
        from app.llm.model_router import model_router, ScenarioType
        from app.core.database import async_session_factory

        full_reply = ""
        npc_message_id = None

        try:
            # 构建 messages（和自由对话完全一致）
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            # 使用 model_router.call_with_fallback()（和自由对话完全一致）
            # ScenarioType.FREE_CHAT 对应 deepseek-v4-flash，有降级链
            response = await model_router.call_with_fallback(
                scenario=ScenarioType.FREE_CHAT,
                messages=messages,
                max_tokens=800,  # 支持 50-500 字回复（500 字中文约需 600-800 tokens）
                temperature=0.7,
            )

            full_reply = response.get("text", "")

            # 流式返回完整回复（模拟流式效果，逐块发送）
            if full_reply.strip():
                # 将完整回复分成小块发送（模拟流式效果）
                chunk_size = 10  # 每次发送10个字符
                for i in range(0, len(full_reply), chunk_size):
                    chunk_text = full_reply[i:i+chunk_size]
                    chunk = {"type": "text", "content": chunk_text, "character_id": str(character_id)}
                    yield f"event: message\ndata: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                    await asyncio.sleep(0.05)  # 模拟流式延迟

            # 立即发送 done 事件，让前端可以立即恢复输入
            done_event = {
                "type": "done",
                "message_id": None,  # 稍后更新
                "character_id": str(character_id)
            }
            yield f"event: done\ndata: {json.dumps(done_event, ensure_ascii=False)}\n\n"

            # 异步执行后续操作（不阻塞前端）
            async def post_stream_tasks():
                nonlocal npc_message_id
                try:
                    # 保存 NPC 回复到数据库
                    if full_reply.strip():
                        async with async_session_factory() as session:
                            npc_message = ChatMessage(
                                character_id=character_id,
                                user_id=current_user_id,
                                sender_type="npc",
                                content=full_reply.strip(),
                                created_at=datetime.utcnow()
                            )
                            session.add(npc_message)
                            await session.commit()
                            await session.refresh(npc_message)
                            npc_message_id = str(npc_message.id)

                    # 提取并保存记忆
                    if full_reply.strip():
                        try:
                            from app.services.narrative.memory_service import MemoryService
                            async with async_session_factory() as mem_session:
                                memory_service = MemoryService(mem_session)
                                # 查询角色名称
                                char_result = await mem_session.execute(select(Character).where(Character.id == character_id))
                                character = char_result.scalar_one_or_none()
                                char_name = character.name if character else "角色"
                                dialogue_text = f"用户: {user_prompt}\n{char_name}: {full_reply.strip()}"
                                await memory_service.extract_and_store(
                                    user_id=current_user_id,
                                    character_id=character_id,
                                    dialogue_text=dialogue_text,
                                    session_id=None
                                )
                                await mem_session.commit()
                        except Exception as e:
                            logger.debug(f"Memory extraction skipped: {e}")
                except Exception as e:
                    logger.error(f"Post-stream task failed: {e}")

            # 启动后台任务
            asyncio.create_task(post_stream_tasks())

        except Exception as e:
            logger.error(f"LLM call failed for character={character_id}: {e}")
            # 使用 model_router 的 fallback 回复（和自由对话一致）
            fallback_text = "（微微侧头）嗯……我好像有点记不清了，也许我们还需要多相处一段时间？"
            yield f"event: message\ndata: {json.dumps({'type': 'text', 'content': fallback_text, 'character_id': str(character_id)}, ensure_ascii=False)}\n\n"

            async with async_session_factory() as session:
                npc_msg = ChatMessage(
                    character_id=character_id, user_id=current_user_id,
                    sender_type="npc", content=fallback_text, created_at=datetime.utcnow()
                )
                session.add(npc_msg)
                await session.commit()
                await session.refresh(npc_msg)
            yield f"event: done\ndata: {json.dumps({'type': 'done', 'message_id': str(npc_msg.id), 'character_id': str(character_id)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


async def _generate_npc_reply(
    db: AsyncSession,
    character_id: UUID,
    user_id: UUID,
    user_message: str,
) -> str:
    """调用 LLM 生成 NPC 回复。"""
    # 获取角色信息
    char_result = await db.execute(select(Character).where(Character.id == character_id))
    character = char_result.scalar_one_or_none()
    character_name = character.name if character else "角色"
    personality = character.personality if character else {}
    description = character.description if character else ""

    # 获取最近对话历史（最近 10 条，包含本次用户消息）
    history_result = await db.execute(
        select(ChatMessage)
        .where(
            ChatMessage.character_id == character_id,
            ChatMessage.user_id == user_id,
        )
        .order_by(desc(ChatMessage.created_at))
        .limit(10)
    )
    history_msgs = list(history_result.scalars().all())
    history_msgs.reverse()  # 按时间正序

    conversation_history = [
        {"role": "assistant" if m.sender_type == "npc" else "user", "content": m.content}
        for m in history_msgs
    ]

    # 构建角色人设描述
    persona_parts = []
    if description:
        persona_parts.append(description)
    if personality:
        traits = personality.get("traits") or personality.get("性格")
        speak_style = personality.get("speak_style") or personality.get("说话风格")
        if traits:
            persona_parts.append(f"性格：{traits}")
        if speak_style:
            persona_parts.append(f"说话风格：{speak_style}")
    character_personality = "\n".join(persona_parts) if persona_parts else "温柔、友善"

    # 调用 LLM（带超时保护，避免阻塞用户）
    import asyncio
    from app.llm.gateway import llm_gateway
    try:
        reply = await asyncio.wait_for(
            llm_gateway.generate_dialogue(
                character_name=character_name,
                character_personality=character_personality,
                user_input=user_message,
                conversation_history=conversation_history[:-1],
            ),
            timeout=5.0  # 5秒超时，避免 LLM 不可用时阻塞
        )
        if reply and reply.strip():
            return reply.strip()
    except asyncio.TimeoutError:
        logger.warning("LLM generation timed out (5s), using fallback")
    except Exception as e:
        logger.warning(f"LLM generation failed, using fallback: {e}")

    # Fallback: 如果 LLM 调用失败，返回基于角色的简单回复
    return _fallback_npc_reply(character_name, user_message)


def _fallback_npc_reply(character_name: str, user_message: str) -> str:
    """Fallback NPC reply when LLM is unavailable."""
    import random

    greetings = ["你好", "嗨", "hi", "hello", "早上好", "下午好", "晚上好"]
    farewells = ["再见", "拜拜", "bye", "晚安"]
    questions = ["？", "?", "怎么", "为什么", "什么", "如何", "吗"]

    msg = user_message.lower()

    if any(g in msg for g in greetings):
        replies = [
            f"你好呀～很高兴见到你！",
            f"嗨！今天过得怎么样？",
            f"你好！有什么想聊的吗？",
        ]
    elif any(f in msg for f in farewells):
        replies = [
            f"再见！期待下次和你聊天～",
            f"拜拜～路上小心哦！",
            f"晚安，做个好梦！",
        ]
    elif any(q in msg for q in questions):
        replies = [
            f"嗯……让我想想……",
            f"这是个好问题呢！",
            f"我觉得……可以慢慢聊。",
        ]
    else:
        replies = [
            f"嗯嗯，我懂你的意思。",
            f"是这样啊，继续说下去？",
            f"听起来很有趣呢！",
            f"我也这么觉得。",
            f"谢谢你跟我分享这些。",
        ]

    return random.choice(replies)


@router.get("/{character_id}/topics", response_model=ChatTopicListResponse)
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
    
    return {"topics": [topic.to_dict() for topic in topics]}
