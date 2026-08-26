# AI 记忆存储方案 — 角色聊天 & 自由对话

> 版本: v1.0 | 日期: 2026-07-30 | 项目: Isekai Wanderer

---

## 目录

1. [记忆分层模型](#一记忆分层模型)
2. [数据模型设计](#二数据模型设计)
3. [记忆提取流程](#三记忆提取流程)
4. [角色聊天记忆策略](#四角色聊天-characterchatview)
5. [自由对话记忆策略](#五自由对话-freechatview)
6. [记忆注入 Prompt 结构](#六记忆注入-prompt-结构)
7. [性能优化策略](#七性能优化策略)
8. [前端集成点](#八前端集成点)
9. [API 设计](#九api-设计)
10. [记忆生命周期管理](#十记忆生命周期管理)

---

## 一、记忆分层模型

```
┌─────────────────────────────────────────────────────────┐
│                    记忆层级架构                           │
├─────────────────────────────────────────────────────────┤
│  L1: 工作记忆 (Working Memory)                          │
│      ├─ 当前对话上下文 (最近 N 轮)                       │
│      ├─ 存储: Redis (TTL: 会话时长)                     │
│      └─ 用途: 即时对话连贯性                             │
├─────────────────────────────────────────────────────────┤
│  L2: 短期记忆 (Short-term Memory)                       │
│      ├─ 本次会话提取的关键事实                           │
│      ├─ 存储: PostgreSQL + pgvector                     │
│      └─ 用途: 本次会话内的记忆召回                       │
├─────────────────────────────────────────────────────────┤
│  L3: 长期记忆 (Long-term Memory)                        │
│      ├─ 跨会话持久化的用户偏好/关系/事件                 │
│      ├─ 存储: PostgreSQL + pgvector                     │
│      └─ 用途: 跨会话的角色一致性                         │
├─────────────────────────────────────────────────────────┤
│  L4: 核心记忆 (Core Memory)                             │
│      ├─ 角色设定、世界观、关键剧情节点                   │
│      ├─ 存储: PostgreSQL (非向量)                       │
│      └─ 用途: 角色人格一致性保障                         │
└─────────────────────────────────────────────────────────┘
```

### 各层详细说明

| 层级 | 存储介质 | TTL | 容量上限 | 写入时机 | 读取时机 |
|------|----------|-----|----------|----------|----------|
| L1 工作记忆 | Redis Hash | 会话结束 + 30min | 最近 20 轮 | 每轮对话 | 每次 LLM 调用 |
| L2 短期记忆 | pgvector | 会话结束归档到 L3 | 50 条/会话 | 异步提取 | 同会话内召回 |
| L3 长期记忆 | pgvector | 永久 (定期清理) | 500 条/用户/角色 | 会话结束时合并 | 跨会话召回 |
| L4 核心记忆 | PostgreSQL | 永久 | 由剧本/角色决定 | 角色创建时 | 始终注入 |

---

## 二、数据模型设计

### 2.1 记忆主表

```sql
-- 扩展 pgvector (如未安装)
CREATE EXTENSION IF NOT EXISTS vector;

-- 记忆主表
CREATE TABLE memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    character_id UUID NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    session_id UUID REFERENCES game_sessions(id) ON DELETE SET NULL,

    -- 记忆内容
    content TEXT NOT NULL,                    -- 原始记忆文本
    summary TEXT,                             -- LLM 生成的摘要
    memory_type VARCHAR(50) NOT NULL,         -- 记忆类型 (见下方枚举)

    -- 向量化
    embedding vector(1536),                   -- text-embedding-3-small 维度

    -- 元数据
    importance FLOAT DEFAULT 0.5,             -- 重要性权重 (0-1)
    access_count INT DEFAULT 0,               -- 被召回次数
    last_accessed_at TIMESTAMPTZ,             -- 最后召回时间
    decay_rate FLOAT DEFAULT 0.01,            -- 记忆衰减速率

    -- 时间戳
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,                   -- 可选过期时间

    -- 来源追踪
    source_message_id UUID,                   -- 触发提取的原始消息 ID
    source_context TEXT,                      -- 提取时的上下文片段

    -- 合并关系
    merged_from UUID[],                       -- 被合并的旧记忆 ID 列表
    merged_into UUID REFERENCES memories(id), -- 合并到的新记忆 ID

    -- 约束
    CONSTRAINT valid_memory_type CHECK (memory_type IN (
        'user_preference',     -- 用户偏好 (喜欢/讨厌)
        'user_fact',           -- 用户事实 (名字/职业/背景)
        'relationship_event',  -- 关系事件 (第一次见面/告白)
        'character_emotion',   -- 角色情感状态
        'plot_point',         -- 剧情关键点
        'conversation_topic',  -- 对话主题
        'promise',             -- 承诺/约定
        'secret'               -- 秘密信息
    ))
);

-- 索引
CREATE INDEX idx_memories_user_char ON memories(user_id, character_id);
CREATE INDEX idx_memories_type ON memories(memory_type);
CREATE INDEX idx_memories_importance ON memories(importance DESC);
CREATE INDEX idx_memories_access ON memories(access_count DESC);
CREATE INDEX idx_memories_created ON memories(created_at DESC);
CREATE INDEX idx_memories_embedding ON memories
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- 记忆关联表 (多角色共享记忆)
CREATE TABLE memory_shares (
    memory_id UUID REFERENCES memories(id) ON DELETE CASCADE,
    shared_with_character_id UUID REFERENCES characters(id) ON DELETE CASCADE,
    PRIMARY KEY (memory_id, shared_with_character_id)
);

-- 记忆合并日志 (审计用)
CREATE TABLE memory_merge_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    old_memory_ids UUID[] NOT NULL,
    new_memory_id UUID REFERENCES memories(id),
    merge_reason TEXT,
    merged_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 2.2 记忆类型说明

| 类型 | 说明 | 示例 | 默认重要性 | 衰减速度 |
|------|------|------|-----------|----------|
| `user_preference` | 用户偏好 | "用户喜欢猫" | 0.7 | 慢 |
| `user_fact` | 用户事实 | "用户叫小明" | 0.8 | 极慢 |
| `relationship_event` | 关系事件 | "第一次牵手" | 0.9 | 不衰减 |
| `character_emotion` | 角色情感 | "角色对用户产生好感" | 0.6 | 中 |
| `plot_point` | 剧情关键点 | "发现了秘密通道" | 0.85 | 不衰减 |
| `conversation_topic` | 对话主题 | "讨论了旅行计划" | 0.4 | 快 |
| `promise` | 承诺/约定 | "约定明天再见" | 0.95 | 不衰减 |
| `secret` | 秘密信息 | "角色隐藏身份" | 0.9 | 不衰减 |

### 2.3 Redis 工作记忆结构

```
# 工作记忆 Key 设计
# Hash: memory:working:{user_id}:{character_id}
# Field: msg_{sequence_number}
# Value: JSON { role, content, timestamp, emotion }

# 示例
HSET memory:working:u123:c456 msg_001 '{"role":"user","content":"我喜欢猫","timestamp":"2026-07-30T09:00:00Z"}'
HSET memory:working:u123:c456 msg_002 '{"role":"assistant","content":"真的吗？我也喜欢猫！","timestamp":"2026-07-30T09:00:05Z"}'
EXPIRE memory:working:u123:c456 7200  # 2小时过期
```

---

## 三、记忆提取流程

### 3.1 整体流程

```
用户发送消息
      │
      ▼
┌─────────────────────┐
│ 1. 即时响应          │ ← 使用工作记忆 (Redis) 生成回复
│    延迟 < 500ms      │
└────┬────────────────┘
     │ 异步 (不阻塞响应)
     ▼
┌─────────────────────┐
│ 2. 记忆提取判断      │ ← 规则引擎 + LLM 判断是否需要提取
└────┬────────────────┘
     │ 需要提取
     ▼
┌─────────────────────┐
│ 3. LLM 提取记忆      │ ← 小模型 (gpt-4o-mini) 分析对话
└────┬────────────────┘
     │
     ▼
┌─────────────────────┐
│ 4. 去重 & 合并       │ ← 与已有记忆对比，避免重复
└────┬────────────────┘
     │
     ▼
┌─────────────────────┐
│ 5. 向量化存储        │ ← text-embedding-3-small → pgvector
└────┬────────────────┘
     │
     ▼
┌─────────────────────┐
│ 6. 更新工作记忆      │ ← 写入 Redis
└─────────────────────┘
```

### 3.2 提取 Prompt 模板

```python
# backend/app/llm/prompts/memory_extract.py

MEMORY_EXTRACTION_PROMPT = """
你是一个记忆提取器。分析以下对话，提取需要长期记忆的关键信息。

## 角色设定
- 角色名: {character_name}
- 角色性格: {character_personality}
- 与用户关系: {relationship_level}

## 已有记忆 (避免重复)
{existing_memories}

## 当前对话
{conversation_context}

## 提取规则
1. 只提取对后续对话有实质影响的信息
2. 区分事实 vs 观点 vs 情感
3. 标记重要性 (0.0-1.0)
4. 不要提取与已有记忆重复的内容
5. 如果新信息与旧记忆冲突，标记为 "update" 类型

## 输出格式 (JSON)
{{
  "memories": [
    {{
      "content": "记忆内容",
      "memory_type": "user_preference|user_fact|relationship_event|character_emotion|plot_point|conversation_topic|promise|secret",
      "importance": 0.8,
      "summary": "简短摘要 (≤20字)",
      "action": "create|update|delete",
      "update_target_id": "如果是 update，指定要更新的记忆 ID"
    }}
  ]
}}

如果没有需要记忆的内容，返回 {{"memories": []}}。
"""

# 记忆合并 Prompt
MEMORY_MERGE_PROMPT = """
以下两条记忆描述的是同一件事，请合并为一条更完整的记忆。

记忆 A: {memory_a}
记忆 B: {memory_b}

请输出一条合并后的记忆，保留所有关键细节:
"""
```

### 3.3 提取服务实现

```python
# backend/app/services/memory_service.py

import json
import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, func, delete
from pgvector.sqlalchemy import Vector

from app.models.memory import Memory, MemoryShare, MemoryMergeLog
from app.llm.prompts.memory_extract import MEMORY_EXTRACTION_PROMPT, MEMORY_MERGE_PROMPT

logger = logging.getLogger(__name__)


class MemoryService:
    """记忆系统核心服务"""

    def __init__(self, db, llm_gateway, embedding_service, redis_client):
        self.db = db
        self.llm = llm_gateway
        self.embedder = embedding_service
        self.redis = redis_client

    # ─── 提取 ─────────────────────────────────────────────

    async def extract_and_store(
        self,
        user_id: str,
        character_id: str,
        session_id: Optional[str],
        messages: list[dict],
    ) -> list[str]:
        """从对话中提取记忆并存储，返回新记忆 ID 列表"""

        # 1. 获取已有记忆 (去重用)
        existing = await self._get_recent_memories(user_id, character_id, limit=20)
        existing_text = "\n".join(
            f"- [{m.memory_type}] {m.content} (id={m.id})" for m in existing
        ) or "无"

        # 2. 构建提取 prompt
        character = await self._get_character(character_id)
        relationship = await self._get_affection(user_id, character_id)

        prompt = MEMORY_EXTRACTION_PROMPT.format(
            character_name=character.name,
            character_personality=character.personality,
            relationship_level=relationship.level,
            existing_memories=existing_text,
            conversation_context=self._format_messages(messages),
        )

        # 3. LLM 提取 (使用小模型降低成本)
        try:
            response = await self.llm.generate(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "请提取需要记忆的内容"},
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
            )
        except Exception as e:
            logger.error(f"Memory extraction failed: {e}")
            return []

        # 4. 解析结果
        result = json.loads(response.content)
        extracted = result.get("memories", [])

        # 5. 处理每条记忆
        memory_ids = []
        for mem in extracted:
            action = mem.get("action", "create")

            if action == "update" and mem.get("update_target_id"):
                mid = await self._update_memory(
                    mem["update_target_id"], mem["content"], mem.get("summary")
                )
            elif action == "create":
                mid = await self._create_memory(
                    user_id, character_id, session_id, mem, messages
                )
            else:
                continue

            if mid:
                memory_ids.append(mid)

        return memory_ids

    async def _create_memory(
        self,
        user_id: str,
        character_id: str,
        session_id: Optional[str],
        mem: dict,
        messages: list[dict],
    ) -> Optional[str]:
        """创建单条记忆"""
        try:
            embedding = await self.embedder.embed(mem["content"])
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            return None

        memory = Memory(
            user_id=user_id,
            character_id=character_id,
            session_id=session_id,
            content=mem["content"],
            summary=mem.get("summary", ""),
            memory_type=mem["memory_type"],
            importance=min(max(mem.get("importance", 0.5), 0.0), 1.0),
            embedding=embedding,
            source_context=self._format_messages(messages[-3:]),
        )
        self.db.add(memory)
        await self.db.flush()
        return memory.id

    async def _update_memory(
        self, memory_id: str, new_content: str, summary: Optional[str]
    ) -> Optional[str]:
        """更新已有记忆"""
        stmt = select(Memory).where(Memory.id == memory_id)
        result = await self.db.execute(stmt)
        memory = result.scalar_one_or_none()
        if not memory:
            return None

        try:
            embedding = await self.embedder.embed(new_content)
            memory.content = new_content
            memory.embedding = embedding
            if summary:
                memory.summary = summary
            memory.updated_at = func.now()
            return memory.id
        except Exception as e:
            logger.error(f"Memory update failed: {e}")
            return None

    # ─── 召回 ─────────────────────────────────────────────

    async def recall(
        self,
        user_id: str,
        character_id: str,
        current_message: str,
        max_memories: int = 5,
        similarity_threshold: float = 0.75,
    ) -> list[Memory]:
        """根据当前消息召回相关记忆"""

        # 1. 当前消息向量化
        query_embedding = await self.embedder.embed(current_message)

        # 2. 向量相似度搜索 + 综合排序
        distance_col = Memory.embedding.cosine_distance(query_embedding)

        stmt = (
            select(Memory)
            .where(Memory.user_id == user_id)
            .where(Memory.character_id == character_id)
            .where(distance_col < (1 - similarity_threshold))
            .where(Memory.merged_into.is_(None))  # 排除已合并的旧记忆
            .order_by(
                # 综合排序: 相似度×0.5 + 重要性×0.3 + 新鲜度×0.2
                (distance_col * 0.5
                 + (1 - Memory.importance) * 0.3
                 + func.extract("epoch", func.now() - Memory.created_at) / 86400 * 0.2)
            )
            .limit(max_memories)
        )

        result = await self.db.execute(stmt)
        memories = list(result.scalars().all())

        # 3. 更新访问统计 (异步，不阻塞)
        for mem in memories:
            mem.access_count += 1
            mem.last_accessed_at = func.now()
        await self.db.commit()

        return memories

    async def recall_by_topic(
        self,
        user_id: str,
        character_id: str,
        topic: str,
        max_memories: int = 5,
    ) -> list[Memory]:
        """按话题召回记忆 (conversation_topic 类型优先)"""
        query_embedding = await self.embedder.embed(topic)
        distance_col = Memory.embedding.cosine_distance(query_embedding)

        stmt = (
            select(Memory)
            .where(Memory.user_id == user_id)
            .where(Memory.character_id == character_id)
            .where(Memory.merged_into.is_(None))
            .order_by(
                # 话题类型优先，然后按相似度
                (Memory.memory_type == "conversation_topic").desc(),
                distance_col,
            )
            .limit(max_memories)
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # ─── 格式化 ───────────────────────────────────────────

    def format_for_prompt(self, memories: list[Memory]) -> str:
        """将记忆格式化为 prompt 注入文本"""
        if not memories:
            return ""

        type_prefix = {
            "user_preference": "🎯 偏好",
            "user_fact": "📋 事实",
            "relationship_event": "💕 关系事件",
            "character_emotion": "💭 情感",
            "plot_point": "📖 剧情",
            "conversation_topic": "💬 话题",
            "promise": "🤝 约定",
            "secret": "🤫 秘密",
        }

        lines = ["## 你记得的事情："]
        for mem in memories:
            prefix = type_prefix.get(mem.memory_type, "📌")
            lines.append(f"- {prefix} {mem.content}")

        return "\n".join(lines)

    # ─── 工作记忆 (Redis) ─────────────────────────────────

    async def push_working_memory(
        self,
        user_id: str,
        character_id: str,
        role: str,
        content: str,
        emotion: Optional[str] = None,
        max_turns: int = 20,
    ):
        """推入一条工作记忆到 Redis"""
        key = f"memory:working:{user_id}:{character_id}"
        seq = await self.redis.hlen(key)
        msg = json.dumps({
            "role": role,
            "content": content,
            "emotion": emotion,
            "timestamp": datetime.utcnow().isoformat(),
        })
        await self.redis.hset(key, f"msg_{seq:04d}", msg)
        await self.redis.expire(key, 7200)  # 2h TTL

        # 超出上限时移除最早的
        total = await self.redis.hlen(key)
        if total > max_turns:
            keys_to_remove = sorted(await self.redis.hkeys(key))[: total - max_turns]
            await self.redis.hdel(key, *keys_to_remove)

    async def get_working_memory(
        self, user_id: str, character_id: str
    ) -> list[dict]:
        """获取当前工作记忆"""
        key = f"memory:working:{user_id}:{character_id}"
        raw = await self.redis.hgetall(key)
        messages = []
        for field, value in sorted(raw.items()):
            messages.append(json.loads(value))
        return messages

    # ─── 辅助 ─────────────────────────────────────────────

    async def _get_recent_memories(
        self, user_id: str, character_id: str, limit: int = 20
    ) -> list[Memory]:
        stmt = (
            select(Memory)
            .where(Memory.user_id == user_id)
            .where(Memory.character_id == character_id)
            .where(Memory.merged_into.is_(None))
            .order_by(Memory.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    def _format_messages(self, messages: list[dict]) -> str:
        lines = []
        for m in messages:
            role = "用户" if m["role"] == "user" else "角色"
            lines.append(f"{role}: {m['content']}")
        return "\n".join(lines)
```

---

## 四、角色聊天 (CharacterChatView)

### 场景特点

- 用户与特定角色 1v1 对话
- 角色有固定设定和剧情线
- 好感度系统影响关系
- 对话有明确的角色扮演需求

### 记忆策略

```python
class CharacterChatMemoryService(MemoryService):
    """角色聊天专用记忆服务"""

    async def build_context(
        self,
        user_id: str,
        character_id: str,
        affection_level: str,
        current_message: str,
    ) -> str:
        """构建角色聊天的记忆上下文"""

        # 1. 召回相关记忆
        memories = await self.recall(user_id, character_id, current_message)

        # 2. 根据好感度调整记忆范围
        if affection_level == "acquaintance":
            # 陌生阶段: 只用高重要性记忆
            memories = [m for m in memories if m.importance > 0.8]
        elif affection_level in ("bond", "love"):
            # 亲密阶段: 加入情感记忆
            emotion_memories = await self._get_emotion_memories(
                user_id, character_id
            )
            memories = list({m.id: m for m in memories + emotion_memories}.values())

        # 3. 获取工作记忆 (最近对话)
        working = await self.get_working_memory(user_id, character_id)

        # 4. 注入角色设定
        character = await self._get_character(character_id)
        core_memory = f"""
## 你是 {character.name}
- 性格: {character.personality}
- 说话风格: {character.dialogue_style}
- 与用户关系: {affection_level}
"""

        # 5. 组合完整上下文
        memory_text = self.format_for_prompt(memories)
        history_text = self._format_messages(working[-10:])

        return f"""
{core_memory}

{memory_text}

## 最近对话
{history_text}

## 回复要求
1. 保持 {character.name} 的角色一致性
2. 如果记得相关信息，自然地引用（不要生硬复述）
3. 根据好感度调整亲密度和语气
"""

    async def _get_emotion_memories(
        self, user_id: str, character_id: str, limit: int = 5
    ) -> list[Memory]:
        """获取情感相关记忆"""
        stmt = (
            select(Memory)
            .where(Memory.user_id == user_id)
            .where(Memory.character_id == character_id)
            .where(Memory.memory_type.in_(["relationship_event", "character_emotion", "promise"]))
            .where(Memory.merged_into.is_(None))
            .order_by(Memory.importance.desc(), Memory.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
```

### 好感度与记忆的关系

```
好感度等级    可用记忆范围                    记忆提取阈值
─────────────────────────────────────────────────────────
acquaintance  仅 user_fact, plot_point       importance > 0.8
ambiguous     + user_preference              importance > 0.6
trust         + conversation_topic           importance > 0.4
bond          + character_emotion, promise   importance > 0.3
love          全部类型                        importance > 0.2
```

---

## 五、自由对话 (FreeChatView)

### 场景特点

- 用户与角色自由聊天，无剧情约束
- 话题可能跳跃
- 需要更灵活的记忆召回
- 无 session 绑定

### 记忆策略

```python
class FreeChatMemoryService(MemoryService):
    """自由对话专用记忆服务"""

    async def build_context(
        self,
        user_id: str,
        character_id: str,
        topic_history: list[str],
        current_message: str,
    ) -> str:
        """构建自由对话的记忆上下文"""

        # 1. 话题切换检测
        topic_shift = await self._detect_topic_shift(
            current_message, topic_history
        )

        # 2. 根据话题选择记忆策略
        if topic_shift:
            # 新话题: 召回相关主题记忆
            memories = await self.recall_by_topic(
                user_id, character_id, current_message
            )
        else:
            # 延续话题: 使用工作记忆 + 少量长期记忆
            memories = await self.recall(
                user_id, character_id, current_message,
                max_memories=3,
                similarity_threshold=0.8,  # 更严格的阈值
            )

        # 3. 自由对话更宽松的记忆提取
        await self.extract_and_store(
            user_id=user_id,
            character_id=character_id,
            session_id=None,  # 自由对话无 session
            messages=[{"role": "user", "content": current_message}],
        )

        return self.format_for_prompt(memories)

    async def _detect_topic_shift(
        self,
        current: str,
        history: list[str],
    ) -> bool:
        """检测是否发生话题切换"""
        if not history:
            return True

        # 用 embedding 相似度判断
        current_emb = await self.embedder.embed(current)
        last_emb = await self.embedder.embed(history[-1])

        similarity = self._cosine_similarity(current_emb, last_emb)
        return similarity < 0.6  # 阈值可调

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """计算余弦相似度"""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(y * y for y in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
```

### 角色聊天 vs 自由对话对比

| 维度 | 角色聊天 | 自由对话 |
|------|----------|----------|
| session 绑定 | 有 (game_session) | 无 |
| 记忆提取阈值 | importance > 0.5 | importance > 0.3 |
| 话题切换 | 不常见 (剧情驱动) | 频繁 |
| 情感记忆 | 根据好感度开放 | 始终可用 |
| 工作记忆 TTL | 会话时长 | 2 小时 |
| 核心记忆注入 | 始终注入角色设定 | 注入角色基础设定 |

---

## 六、记忆注入 Prompt 结构

### 6.1 角色聊天 Prompt

```python
CHARACTER_CHAT_PROMPT = """
## 角色核心设定
你是 {character_name}。
{character_core_settings}

## 记忆上下文
{memory_context}

## 当前状态
- 好感度: {affection_level} ({affection_value}/100)
- 当前场景: {scene_description}
- 时间: {in_game_time}

## 对话历史 (最近 10 轮)
{conversation_history}

## 用户最新消息
{current_message}

## 回复要求
1. 保持角色一致性，使用角色特有的说话风格
2. 如果记得相关信息，自然地引用（不要生硬复述记忆）
3. 根据好感度调整亲密度和语气
4. 回复长度适中 (50-200字)
5. 可以包含动作描写 (用 *星号* 包裹)

请回复:
"""
```

### 6.2 自由对话 Prompt

```python
FREE_CHAT_PROMPT = """
## 角色设定
你是 {character_name}，一个 {personality_summary} 的角色。

## 记忆上下文
{memory_context}

## 当前状态
- 与用户关系: {relationship_description}

## 对话历史 (最近 5 轮)
{conversation_history}

## 用户最新消息
{current_message}

## 回复要求
1. 以 {character_name} 的身份自然回复
2. 如果记得相关话题，自然引用
3. 保持对话轻松自然
4. 回复长度适中 (30-150字)

请回复:
"""
```

---

## 七、性能优化策略

| 策略 | 实现方式 | 效果 | 注意事项 |
|------|----------|------|----------|
| 异步提取 | 消息发送后立即返回，后台 Celery/ARQ 任务提取记忆 | 响应延迟 < 100ms | 需要任务队列 |
| 批量向量化 | 多条记忆合并 embedding 请求 | 减少 API 调用 50%+ | 注意 token 上限 |
| 记忆缓存 | Redis 缓存高频访问记忆 (LRU) | 减少 DB 查询 | 缓存一致性 |
| 增量更新 | 只向量化新增/修改的记忆 | 节省 embedding token | - |
| 过期清理 | Cron 定期清理低重要性旧记忆 | 控制存储增长 | 保留 relationship_event |
| 连接池 | pgvector 查询使用连接池 | 减少连接开销 | 配置 pool_size |
| 预计算 | 用户进入聊天页时预加载记忆 | 首次回复更快 | 预加载量可控 |

### 异步提取架构

```
POST /character-chat/message
      │
      ▼
┌─────────────────┐     ┌──────────────────┐
│ API Handler      │────>│ 即时返回回复      │
│                  │     │ (使用工作记忆)    │
└────┬─────────────┘     └──────────────────┘
     │ enqueue
     ▼
┌─────────────────┐
│ Redis Queue      │
│ (memory_extract) │
└────┬─────────────┘
     │ worker
     ▼
┌─────────────────┐
│ Memory Worker    │
│ ├─ LLM 提取     │
│ ├─ Embedding    │
│ └─ DB 写入      │
└─────────────────┘
```

---

## 八、前端集成点

| 组件 | API | 用途 |
|------|-----|------|
| CharacterChatView | POST /api/v1/character-chat/{characterId}/message | 发送消息，触发记忆提取 |
| FreeChatView | POST /api/v1/game/{sessionId}/free-chat | 自由对话，触发记忆提取 |
| DialogueBox | SSE `memory_recall` 事件 | 显示"我记得..."提示 |
| ProfileView | GET /api/v1/user/memories/{characterId} | 查看与角色的记忆列表 |
| SettingsView | PUT /api/v1/user/memory-preferences | 管理记忆偏好设置 |

### SSE 记忆召回事件

```typescript
// 当 AI 回复中使用了记忆时，通过 SSE 通知前端
event: message
data: {"type": "memory_recall", "memories": [
  {"id": "xxx", "content": "用户喜欢猫", "type": "user_preference"}
]}
```

前端可以在对话气泡旁显示一个小的 💡 图标，hover 时展示"我记得你说过喜欢猫"。

---

## 九、API 设计

### 9.1 新增 API 端点

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | /api/v1/user/memories | Bearer | 获取用户所有记忆概览 |
| GET | /api/v1/user/memories/{characterId} | Bearer | 获取与特定角色的记忆列表 |
| DELETE | /api/v1/user/memories/{memoryId} | Bearer | 删除特定记忆 (用户主动遗忘) |
| PUT | /api/v1/user/memory-preferences | Bearer | 更新记忆偏好设置 |
| GET | /api/v1/character-chat/{characterId}/memory-summary | Bearer | 获取角色记忆摘要 |

### 9.2 请求/响应示例

#### 获取记忆列表

```
GET /api/v1/user/memories/{characterId}?type=user_preference&limit=20

Response 200:
{
  "memories": [
    {
      "id": "uuid",
      "content": "用户喜欢猫",
      "summary": "喜欢猫",
      "memory_type": "user_preference",
      "importance": 0.7,
      "created_at": "2026-07-30T09:00:00Z",
      "access_count": 5,
      "last_accessed_at": "2026-07-30T10:00:00Z"
    }
  ],
  "total": 42,
  "types_summary": {
    "user_preference": 10,
    "user_fact": 5,
    "relationship_event": 3,
    ...
  }
}
```

#### 删除记忆

```
DELETE /api/v1/user/memories/{memoryId}

Response 200:
{
  "success": true,
  "deleted_memory_id": "uuid",
  "message": "记忆已删除"
}
```

#### 更新记忆偏好

```
PUT /api/v1/user/memory-preferences

Request Body:
{
  "enable_memory_extraction": true,
  "max_memories_per_chat": 5,
  "auto_forget_after_days": 90,
  "excluded_types": ["conversation_topic"]
}

Response 200:
{
  "preferences": {
    "enable_memory_extraction": true,
    "max_memories_per_chat": 5,
    "auto_forget_after_days": 90,
    "excluded_types": ["conversation_topic"]
  },
  "updated_at": "2026-07-30T10:00:00Z"
}
```

---

## 十、记忆生命周期管理

### 10.1 记忆状态流转

```
创建 (Created)
    │
    ├─ 活跃 (Active) ← 被频繁召回
    │   │
    │   ├─ 衰减 (Decaying) ← 长时间未被召回
    │   │   │
    │   │   ├─ 归档 (Archived) ← 重要性降至阈值以下
    │   │   │   │
    │   │   │   └─ 删除 (Deleted) ← 用户主动删除或过期清理
    │   │   │
    │   │   └─ 合并 (Merged) ← 与相似记忆合并
    │   │
    │   └─ 强化 (Reinforced) ← 被召回后重要性提升
    │
    └─ 核心 (Core) ← importance > 0.9，永不衰减
```

### 10.2 记忆衰减机制

```python
# 记忆衰减计算公式
def calculate_effective_importance(memory: Memory) -> float:
    """计算记忆的当前有效重要性"""
    
    # 核心记忆不衰减
    if memory.importance >= 0.9:
        return memory.importance
    
    # 计算距今天数
    days_since_creation = (datetime.utcnow() - memory.created_at).days
    days_since_access = (
        (datetime.utcnow() - memory.last_accessed_at).days
        if memory.last_accessed_at
        else days_since_creation
    )
    
    # 衰减因子
    decay_rate = memory.decay_rate  # 默认 0.01
    
    # 被访问过的记忆衰减更慢
    access_bonus = min(memory.access_count * 0.05, 0.3)
    
    # 有效重要性 = 原始重要性 × (1 - 衰减率 × 未访问天数) + 访问奖励
    effective = memory.importance * (1 - decay_rate * days_since_access) + access_bonus
    
    return max(0.0, min(1.0, effective))
```

### 10.3 记忆合并策略

```python
async def merge_similar_memories(
    user_id: str,
    character_id: str,
    similarity_threshold: float = 0.92
) -> int:
    """合并相似记忆，返回合并数量"""
    
    # 获取用户-角色的所有记忆
    memories = await get_all_memories(user_id, character_id)
    
    merged_count = 0
    processed = set()
    
    for i, mem_a in enumerate(memories):
        if mem_a.id in processed:
            continue
            
        for mem_b in memories[i+1:]:
            if mem_b.id in processed:
                continue
            
            # 计算相似度
            sim = cosine_similarity(mem_a.embedding, mem_b.embedding)
            
            if sim >= similarity_threshold:
                # 合并：保留重要性更高的
                keeper = mem_a if mem_a.importance >= mem_b.importance else mem_b
                loser = mem_b if keeper == mem_a else mem_a
                
                # 使用 LLM 合并内容
                merged_content = await llm.generate(
                    MEMORY_MERGE_PROMPT.format(
                        memory_a=keeper.content,
                        memory_b=loser.content
                    )
                )
                
                # 更新 keeper
                keeper.content = merged_content.content
                keeper.embedding = await embedder.embed(merged_content.content)
                keeper.merged_from = (keeper.merged_from or []) + [loser.id]
                keeper.updated_at = func.now()
                
                # 标记 loser 为已合并
                loser.merged_into = keeper.id
                
                processed.add(loser.id)
                merged_count += 1
    
    await db.commit()
    return merged_count
```

### 10.4 定期清理任务

```python
# backend/app/tasks/memory_cleanup.py

from datetime import datetime, timedelta
from sqlalchemy import delete, select
from app.models.memory import Memory
from app.core.celery import celery_app

@celery_app.task(name="memory.cleanup_decayed")
def cleanup_decayed_memories():
    """清理衰减到阈值以下的记忆"""
    
    # 配置
    DECAY_THRESHOLD = 0.1  # 有效重要性低于此值则删除
    PRESERVE_TYPES = ["relationship_event", "promise", "secret"]  # 这些类型不自动删除
    
    # 获取所有衰减记忆
    stmt = select(Memory).where(
        Memory.memory_type.not_in(PRESERVE_TYPES),
        Memory.merged_into.is_(None)
    )
    
    memories = db.execute(stmt).scalars().all()
    
    to_delete = []
    for mem in memories:
        effective = calculate_effective_importance(mem)
        if effective < DECAY_THRESHOLD:
            to_delete.append(mem.id)
    
    if to_delete:
        db.execute(delete(Memory).where(Memory.id.in_(to_delete)))
        db.commit()
    
    return {"deleted_count": len(to_delete)}

@celery_app.task(name="memory.merge_similar")
def merge_similar_memories_task():
    """定期合并相似记忆"""
    
    # 获取所有用户-角色组合
    user_char_pairs = db.execute(
        select(Memory.user_id, Memory.character_id).distinct()
    ).all()
    
    total_merged = 0
    for user_id, character_id in user_char_pairs:
        merged = await merge_similar_memories(user_id, character_id)
        total_merged += merged
    
    return {"merged_count": total_merged}

# Celery Beat 调度配置
CELERY_BEAT_SCHEDULE = {
    "memory-cleanup-daily": {
        "task": "memory.cleanup_decayed",
        "schedule": crontab(hour=3, minute=0),  # 每天凌晨 3 点
    },
    "memory-merge-weekly": {
        "task": "memory.merge_similar",
        "schedule": crontab(hour=4, minute=0, day_of_week=0),  # 每周日凌晨 4 点
    },
}
```

### 10.5 用户主动遗忘

```python
# 用户可以主动删除特定记忆
async def user_forget_memory(user_id: str, memory_id: str) -> bool:
    """用户主动遗忘记忆"""
    
    # 验证记忆属于该用户
    memory = await db.get(Memory, memory_id)
    if not memory or memory.user_id != user_id:
        return False
    
    # 记录删除日志 (审计)
    await db.execute(
        MemoryDeleteLog(
            memory_id=memory_id,
            user_id=user_id,
            reason="user_requested",
            deleted_at=func.now()
        )
    )
    
    # 软删除 (保留审计痕迹)
    memory.deleted_at = func.now()
    memory.deleted_by = user_id
    
    await db.commit()
    return True
```

---

## 附录：成本估算

### Embedding 成本

| 场景 | 估算 | 成本/月 |
|------|------|---------|
| 记忆提取 | 1000 用户 × 10 条/天 × 30 天 = 300,000 条 | ~$30 |
| 记忆召回 | 1000 用户 × 50 次/天 × 5 条 = 250,000 次 | ~$25 |
| **总计** | | **~$55/月** |

### LLM 提取成本 (gpt-4o-mini)

| 场景 | Token 估算 | 成本/月 |
|------|-----------|---------|
| 记忆提取 | 300,000 条 × 500 tokens = 150M tokens | ~$45 |
| **总计** | | **~$45/月** |

### 存储成本 (PostgreSQL + pgvector)

| 指标 | 估算 |
|------|------|
| 每条记忆大小 | ~2 KB (含 1536 维向量) |
| 100 万条记忆 | ~2 GB |
| 存储成本 (RDS) | ~$0.23/GB/月 = ~$0.46/月 |

---

## 总结

本方案提供了一个完整的 AI 记忆存储架构，核心特点：

1. **分层记忆模型**：工作记忆 → 短期记忆 → 长期记忆 → 核心记忆，平衡性能与持久性
2. **向量化检索**：基于 pgvector 的语义搜索，支持相似性召回
3. **智能提取**：LLM 异步提取关键信息，避免冗余
4. **差异化策略**：角色聊天和自由对话采用不同的记忆策略
5. **生命周期管理**：衰减、合并、清理机制控制存储增长
6. **用户可控**：支持主动遗忘和偏好设置

该方案可直接基于项目现有的 PostgreSQL + pgvector + Redis 技术栈实现，无需引入新的基础设施。

---

*文档版本: v1.0*  
*最后更新: 2026-07-30*