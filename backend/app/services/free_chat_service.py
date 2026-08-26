"""
FreeChatService — 自由对话服务（陪伴Agent）

v4.4 双Agent架构: 重写版本（§3.3）

核心原则：
- 不推进剧情
- 不改好感度
- 不剧透未玩内容
- 注入角色人设
- 用户隔离
"""

import uuid
from datetime import datetime, timezone
from typing import Any, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.model_router import model_router, ScenarioType
from app.llm.prompts.free_chat import build_free_chat_prompt
from app.llm.prompts.character_personas import get_character_persona
from app.models.free_chat import FreeChatSession


class FreeChatService:
    """自由对话服务（陪伴Agent）"""
    
    async def send_message(
        self,
        db: AsyncSession,
        user_id: str,
        character_id: str,
        message: str,
        script_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        发送自由对话消息
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            character_id: 角色ID
            message: 用户消息
            script_id: 剧本ID（可选，提供剧情上下文）
            session_id: 会话ID（可选，复用已有会话）
        
        Returns:
            {
                "reply": "AI回复文本",
                "emotion": "情绪标签",
                "character_id": "角色ID",
                "session_id": "会话ID",
            }
        """
        # 1. 获取或创建会话
        # 优先查找已有的会话（基于 user_id + character_id，不依赖 script_id）
        if not session_id:
            from sqlalchemy import select
            # 查找该用户与该角色的最近会话
            stmt = select(FreeChatSession).where(
                FreeChatSession.user_id == UUID(user_id),
                FreeChatSession.character_id == UUID(character_id) if character_id else True
            ).order_by(FreeChatSession.created_at.desc()).limit(1)
            result = await db.execute(stmt)
            existing_session = result.scalar_one_or_none()
            
            if existing_session:
                # 复用已有会话
                session_id = str(existing_session.id)
                session = existing_session
            else:
                # 创建新会话
                session_id = str(uuid.uuid4())
                session = FreeChatSession(
                    id=uuid.UUID(session_id),
                    user_id=UUID(user_id),
                    topic_id="free_chat",
                    character_id=UUID(character_id) if character_id else None,
                    script_id=UUID(script_id) if script_id else None,
                )
                db.add(session)
                await db.flush()
        
        # 2. 获取角色人设（从数据库读取）
        character_persona = await self._get_character_persona_from_db(db, character_id)
        
        # 3. 获取剧本背景信息（BE-FC-03）
        script_info = None
        if script_id:
            script_info = await self._get_script_info(db, script_id)
        
        # 4. 获取当前好感度
        affection_value = await self._get_affection(db, user_id, character_id)
        
        # 4. 获取最近对话历史（最近20条，确保重要信息不被截断）
        recent_messages = await self._get_recent_messages(db, session_id, limit=20)
        
        # 5. 获取相关记忆（使用向量相似度召回，而不是简单的时间倒序）
        memories = await self._get_relevant_memories(db, user_id, character_id, query=message, limit=10)
        
        # 6. 构建Prompt（包含剧本背景）
        system_prompt = build_free_chat_prompt(
            character_name=character_persona["name"],
            character_persona=character_persona,
            affection_value=affection_value,
            recent_messages=recent_messages,
            memories=memories,
            script_info=script_info,  # 注入剧本背景
        )
        
        # 7. 调用陪伴Agent（deepseek-v4-flash）
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ]
        
        response = await model_router.call_with_fallback(
            scenario=ScenarioType.FREE_CHAT,
            messages=messages,
            max_tokens=300,
            temperature=0.7,
        )
        
        reply_text = response.get("text", "")
        emotion = self._detect_emotion(reply_text)
        
        # 8. 保存对话到数据库
        await self._save_message(db, session_id, user_id, "user", message)
        await self._save_message(db, session_id, user_id, "assistant", reply_text)
        
        # 9. 提取并存储记忆（异步执行，不阻塞响应）
        try:
            from app.services.narrative.memory_service import MemoryService
            memory_service = MemoryService(db)
            # 合并用户消息和 AI 回复作为对话内容
            dialogue_text = f"用户: {message}\n{character_persona["name"]}: {reply_text}"
            await memory_service.extract_and_store(
                user_id=UUID(user_id),
                character_id=UUID(character_id),
                dialogue_text=dialogue_text,
                session_id=UUID(session_id),
            )
        except Exception as e:
            # 记忆提取失败不影响主流程
            import logging
            logging.getLogger(__name__).warning(f"Memory extraction failed: {e}")
        
        await db.commit()
        
        return {
            "reply": reply_text,
            "emotion": emotion,
            "character_id": character_id,
            "session_id": session_id,
        }
    
    async def _get_affection(self, db: AsyncSession, user_id: str, character_id: str) -> int:
        """获取当前好感度"""
        from app.services.narrative.affection_service import AffectionService
        from sqlalchemy import select
        from app.models.affection import Affection
        
        # Try to get from database
        stmt = select(Affection).where(
            Affection.user_id == UUID(user_id),
            Affection.character_id == UUID(character_id)
        )
        result = await db.execute(stmt)
        affection = result.scalar_one_or_none()
        return affection.value if affection else 0
    
    async def _get_recent_messages(self, db: AsyncSession, session_id: str, limit: int = 5) -> List[dict]:
        """获取最近对话历史 - 从用户的所有会话中获取最近消息"""
        from sqlalchemy import select
        from app.models.free_chat import FreeChatSession
        
        # 获取当前会话
        stmt = select(FreeChatSession).where(
            FreeChatSession.id == UUID(session_id)
        )
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()
        
        if session and session.messages:
            return session.messages[-limit:] if len(session.messages) > limit else session.messages
        return []
    
    async def _get_memories(self, db: AsyncSession, user_id: str, character_id: str, limit: int = 10) -> List[dict]:
        """获取相关记忆（按时间倒序，兼容旧代码）"""
        from sqlalchemy import select
        from app.models.memory import CharacterMemory
        
        stmt = select(CharacterMemory).where(
            CharacterMemory.user_id == UUID(user_id),
            CharacterMemory.character_id == UUID(character_id)
        ).order_by(CharacterMemory.created_at.desc()).limit(limit)
        
        result = await db.execute(stmt)
        memories = result.scalars().all()
        
        return [{"content": m.memory_text} for m in memories]
    
    async def _get_relevant_memories(self, db: AsyncSession, user_id: str, character_id: str, query: str, limit: int = 10) -> List[dict]:
        """获取相关记忆（使用向量相似度召回）
        
        通过 pgvector KNN 搜索找到与当前查询最相关的记忆，
        而不是简单按时间排序。
        """
        from app.services.narrative.memory_service import MemoryService
        
        try:
            memory_service = MemoryService(db)
            memories = await memory_service.recall(
                user_id=UUID(user_id),
                character_id=UUID(character_id),
                query_text=query,
                limit=limit,
            )
            return [{"content": m["memory_text"]} for m in memories]
        except Exception as e:
            # 如果向量召回失败，fallback 到时间排序
            import logging
            logging.getLogger(__name__).warning(f"Memory recall failed, falling back to time-based: {e}")
            return await self._get_memories(db, user_id, character_id, limit)
    
    async def _save_message(self, db: AsyncSession, session_id: str, user_id: str, role: str, content: str):
        """保存消息到会话 - 确保持久化到数据库"""
        from sqlalchemy import select
        from app.models.free_chat import FreeChatSession
        
        stmt = select(FreeChatSession).where(
            FreeChatSession.id == UUID(session_id)
        )
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()
        
        # 如果 session 不存在，创建新的
        if not session:
            session = FreeChatSession(
                id=UUID(session_id),
                user_id=UUID(user_id),
                topic_id="free_chat",
                messages=[]
            )
            db.add(session)
            await db.flush()
        
        if not session.messages:
            session.messages = []
        
        # 添加消息
        message_data = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        session.messages.append(message_data)
        
        # 标记对象已修改，确保 SQLAlchemy 检测到 JSON 字段变化
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(session, "messages")
    
    async def _get_character_persona_from_db(self, db: AsyncSession, character_id: str) -> dict:
        """从数据库获取角色人设"""
        from sqlalchemy import select
        from app.models.script import Character
        
        stmt = select(Character).where(Character.id == UUID(character_id))
        result = await db.execute(stmt)
        character = result.scalar_one_or_none()
        
        if character:
            return {
                "name": character.name,
                "description": character.description or "",
                "personality": character.personality or {},
                "dialogue_style": character.dialogue_style or "gentle",
            }
        
        # 如果数据库中没有，返回默认人设
        return {
            "name": "未知角色",
            "description": "",
            "personality": {},
            "dialogue_style": "gentle",
        }
    
    async def _get_script_info(self, db: AsyncSession, script_id: str) -> dict:
        """获取剧本背景信息（BE-FC-03）"""
        from sqlalchemy import select
        from app.models.script import Script
        
        stmt = select(Script).where(Script.id == UUID(script_id))
        result = await db.execute(stmt)
        script = result.scalar_one_or_none()
        
        if script:
            return {
                "title": script.title,
                "description": script.description or "",
                "genre": script.genre or "",
            }
        
        return {
            "title": "未知剧本",
            "description": "",
            "genre": "",
        }
    
    def _detect_emotion(self, text: str) -> str:
        """检测情绪（简单关键词匹配）"""
        emotion_keywords = {
            "happy": ["开心", "高兴", "快乐", "喜欢"],
            "sad": ["难过", "伤心", "遗憾"],
            "excited": ["激动", "兴奋", "太棒了"],
            "contemplative": ["思考", "觉得", "认为"],
        }
        
        for emotion, keywords in emotion_keywords.items():
            if any(kw in text for kw in keywords):
                return emotion
        
        return "neutral"
    
    def get_topics(self) -> List[dict]:
        """获取可用的对话话题列表"""
        return [
            {
                "id": "topic_1",
                "title": "日常寒暄",
                "description": "聊聊今天过得怎么样"
            },
            {
                "id": "topic_2",
                "title": "兴趣爱好",
                "description": "分享彼此的兴趣和爱好"
            },
            {
                "id": "topic_3",
                "title": "回忆往事",
                "description": "回忆一起经历过的故事"
            },
            {
                "id": "topic_4",
                "title": "未来计划",
                "description": "讨论未来的打算和计划"
            }
        ]


# 单例工厂（兼容旧 import）
_free_chat_service_instance: Optional[FreeChatService] = None


def get_free_chat_service() -> FreeChatService:
    """获取 FreeChatService 单例。"""
    global _free_chat_service_instance
    if _free_chat_service_instance is None:
        _free_chat_service_instance = FreeChatService()
    return _free_chat_service_instance


# 模块级实例（兼容 from app.services.free_chat_service import free_chat_service）
free_chat_service = FreeChatService()
