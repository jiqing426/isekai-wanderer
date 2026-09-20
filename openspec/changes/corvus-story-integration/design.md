# Design — CR-037 Corvus-Story-Core 集成

## Overview

本设计将 Corvus-Story-Core（Node.js Express AI 叙事引擎）集成到异世界漫游项目中，实现 AI 自由叙事能力。核心设计原则：新旧引擎共存（feature flag 切换）、SSE 流式透传、本地向量记忆（pgvector + bge-small-zh）、不修改 Corvus 内部逻辑、不修改 Vue 组件/样式。

### 设计输入

- `proposal.md`：9 个 REQ，6 个 Q（全部 closed/追认）
- `specs/capability/spec.md`：9 个 REQ 详细规格，28 条 AC
- `docs/corvus-integration/execution-plan.md`：v3 执行方案（用户确认 12 项决策点）
- `acceptance.md`：28 条 AC（7 条需 Browser E2E，13 条需 API/DB/Runtime 契约验证）

---

## Technical Approach

### 1. 架构拓扑

```
┌─────────────────────────────────────────────────────────────┐
│ 前端 (Vue 3 PWA, 微调 ~40 行)                                │
│  /game?script={game_session_id} (UUID v4)                  │
│                                                             │
│  初始化: POST /api/v1/game/start → {session_id, ...}        │
│  对话流: POST /api/v1/game/{id}/custom-input (SSE 流式)     │
│    ├─ onText: StoryPanel 逐字渲染                           │
│    ├─ onDone: 更新 currentDialogue + choices([])            │
│    ├─ onGmUpdate: 好感度/道具/标记更新                       │
│    └─ onError: 错误提示 + 重试                               │
│  读对话: GET /api/v1/game/{id}/dialogue (非流式, 恢复用)     │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP + SSE (Vite proxy / Nginx)
┌────────────────────▼────────────────────────────────────────┐
│ isekai-wanderer 后端 (Python FastAPI)                       │
│                                                             │
│  ┌──────────────────────────────────────────────┐            │
│  │ Engine Dispatcher (feature flag)             │            │
│  │  engine_type='legacy' → NarrativeEngine     │            │
│  │  engine_type='corvus'  → CorvusAdapter      │            │
│  └──────────────┬──────────────────────────────┘            │
│                 │                                            │
│  ┌──────────────▼──────────────────────────────┐            │
│  │ CorvusAdapter                                │            │
│  │  - SSE 事件翻译器 (Corvus→前端格式)          │            │
│  │  - world_state → DB 异步同步                  │            │
│  │  - 向量记忆写入 (对话结束→LLM提取→bge→pgvector)│           │
│  │  - 向量记忆召回+注入 (回合开始→pgvector KNN    │            │
│  │    →NPC knownInfo 注入→恢复)                  │            │
│  └──────┬──────────────────┬───────────────────┘            │
│         │                  │                                 │
│  ┌──────▼──────┐  ┌───────▼──────────────────┐             │
│  │ CorvusClient │  │ EmbeddingService          │             │
│  │ (HTTP+SSE)   │  │ bge-small-zh-v1.5 本地    │             │
│  │ 127.0.0.1:   │  │ 512 维, 50-100ms/次       │             │
│  │ 8082         │  │                            │            │
│  └──────────────┘  └──────────────────────────┘             │
│                                                             │
│  业务数据库 (PostgreSQL + pgvector 512维 + 5张新表)          │
└────────────────────┬────────────────────────────────────────┘
                     │ SSE 透传 (127.0.0.1:8082)
┌────────────────────▼────────────────────────────────────────┐
│ Corvus-Story-Core (Node.js Express + tsx)                   │
│  POST /api/games → 创建游戏 (返回 slug game_id)              │
│  POST /api/games/:gameId/messages → SSE 事件流              │
│  GET /api/games/:gameId/characters/:npcId → NPC JSON        │
│  PATCH /api/games/:gameId/characters/:npcId → 更新 NPC       │
│  内置 3 层记忆 (短期/摘要/NPC记忆)                           │
│  LLM → thoushub 网关 → deepseek-v4-flash                    │
│  数据存储: 纯文件 JSON/JSONL                                 │
└─────────────────────────────────────────────────────────────┘
```

### 2. 模块边界

| 模块 | 路径 | 职责 | 依赖 |
|------|------|------|------|
| CorvusClient | `backend/app/services/corvus_client.py` | Corvus HTTP 调用 + SSE 流式读取 | httpx (async HTTP client) |
| CorvusAdapter | `backend/app/services/corvus_adapter.py` | SSE 翻译 + world_state DB 同步 + 向量记忆写入/召回 + NPC knownInfo 注入/恢复 | CorvusClient, EmbeddingService, MemoryService, SQLAlchemy |
| EmbeddingService | `backend/app/services/embedding_service.py` | bge-small-zh 本地 embedding 推理 + pgvector KNN 召回 | sentence-transformers, pgvector |
| CorvusModels | `backend/app/models/corvus.py` | 5 张新表 SQLAlchemy 模型 | SQLAlchemy |
| Engine Dispatcher | `backend/app/api/v1/game.py` (现有文件扩展) | feature flag 路由 legacy/corvus | NarrativeEngine, CorvusAdapter |

### 3. CorvusClient 接口设计

```python
class CorvusClient:
    """Corvus-Story-Core HTTP + SSE 客户端，仅访问 127.0.0.1:8082"""

    BASE_URL = "http://127.0.0.1:8082"
    TIMEOUT = 30.0  # 创建游戏/普通请求
    SSE_TIMEOUT = 300.0  # SSE 流式读取

    async def health_check() -> dict:
        """GET /api/health → {"ok": true}"""

    async def create_game(
        player_name: str,
        backstory: str,
        appearance: str,
        world_setting: str,
    ) -> str:
        """POST /api/games → 返回 game_id (slug 格式)"""

    async def stream_message(
        game_id: str,
        content: str,
    ) -> AsyncGenerator[dict, None]:
        """POST /api/games/{gameId}/messages → SSE 事件流
        yield: {"event": "assistant-delta", "data": {"delta": "..."}}
               {"event": "assistant-complete", "data": {"message": {...}}}
               {"event": "gm-complete", "data": {...}}
               {"event": "done", "data": {}}
               {"event": "error", "data": {"message": "..."}}
        """

    async def get_game(game_id: str) -> dict:
        """GET /api/games/{gameId} → 游戏元数据"""

    async def get_characters(game_id: str) -> list[dict]:
        """GET /api/games/{gameId}/characters → NPC 列表"""

    async def get_npc(game_id: str, npc_id: str) -> dict:
        """GET /api/games/{gameId}/characters/{npcId} → NPC JSON (含 memory[], knownInfo)"""

    async def update_npc_knowninfo(
        game_id: str,
        npc_id: str,
        knowninfo: str,
    ) -> None:
        """PATCH /api/games/{gameId}/characters/{npcId} → 更新 NPC knownInfo"""

    async def get_npc_raw(game_id: str, npc_id: str) -> dict:
        """GET NPC 原始 JSON，用于 knownInfo 注入前保存原始值"""
```

**实现要点：**
- 使用 `httpx.AsyncClient`，SSE 流式读取用 `client.stream("POST", ...)`
- SSE 解析：按 `event:` / `data:` 行分割，组装为 dict
- 错误处理：连接超时 → yield error event；HTTP 非 200 → raise CorvusClientError
- 不重试 Corvus SSE 中断（前端负责重试）

### 4. SSE 事件翻译映射

| Corvus SSE 事件 | 后端翻译为（前端 SSE data） | 前端处理 | 异步副作用 |
|---|---|---|---|
| `assistant-delta` `{"delta":"你"}` | `{"type":"text","content":"你"}` | StoryPanel 逐字渲染 | 无 |
| `assistant-complete` `{"message":{...}}` | `{"type":"done","text":"完整文本","character_id":"uuid-v4","character_name":"白夜","node_id":"uuid-v4"}` | 更新 currentDialogue | 触发向量记忆写入（LLM 提取 → bge embedding → pgvector 存储） |
| `gm-complete` / `state-changed` `{"affinity_delta":5,"inventory_changes":[...],"story_flags":[...]}` | `{"type":"gm_update","affinity_delta":5,"inventory_changes":[...],"story_flags":[...]}` | 好感度动效/道具/标记 UI 更新 | 触发 world_state DB 同步（session_npcs / inventory_items / story_flags） |
| `done` `{}` | `{"type":"stream_end"}` | 关闭 SSE 连接 | 恢复 NPC knownInfo 原始值 |
| `error` `{"message":"..."}` | `{"type":"error","message":"..."}` | 显示错误提示 | 恢复 NPC knownInfo 原始值 |

**翻译器实现：**
```python
class SSETranslator:
    """将 Corvus SSE 事件翻译为前端期望的 SSE 格式"""

    @staticmethod
    def translate(corvus_event: dict) -> dict | None:
        event_type = corvus_event.get("event")
        data = corvus_event.get("data", {})

        if event_type == "assistant-delta":
            return {"type": "text", "content": data.get("delta", "")}
        elif event_type == "assistant-complete":
            msg = data.get("message", {})
            return {
                "type": "done",
                "text": msg.get("content", ""),
                "character_id": str(msg.get("character_id", "")),
                "character_name": msg.get("character_name", ""),
                "node_id": str(uuid4()),
            }
        elif event_type in ("gm-complete", "state-changed"):
            return {
                "type": "gm_update",
                "affinity_delta": data.get("affinity_delta", 0),
                "inventory_changes": data.get("inventory_changes", []),
                "story_flags": data.get("story_flags", []),
            }
        elif event_type == "done":
            return {"type": "stream_end"}
        elif event_type == "error":
            return {"type": "error", "message": data.get("message", "Unknown error")}
        return None
```

### 5. CorvusAdapter 接口设计

```python
class CorvusAdapter:
    """Corvus 引擎适配器：SSE 翻译 + world_state 同步 + 向量记忆写入/召回"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = CorvusClient()
        self.embedding = EmbeddingService()

    async def create_session(
        self, user_id: UUID, player_candidate_id: UUID
    ) -> dict:
        """选定角色后创建 Corvus 游戏
        1. 从 player_candidates 表读取角色数据
        2. 调用 CorvusClient.create_game(player_name, backstory, appearance, world_setting)
        3. 存储 corvus_internal_game_id 到 corvus_game_sessions 表
        4. 初始化 session_npcs（从 Corvus 获取 NPC 列表）
        5. 返回初始场景数据
        """

    async def stream_turn(
        self, game_session_id: UUID, user_input: str
    ) -> AsyncGenerator[str, None]:
        """SSE 流式透传 Corvus 回合
        流程:
        1. 回合开始: recall_and_inject(game_session_id, user_input)
        2. 调用 CorvusClient.stream_message(game_id, user_input)
        3. 逐事件翻译为前端格式并 yield
        4. assistant-complete 时: asyncio.create_task(write_memory(...))
        5. gm_update 时: asyncio.create_task(sync_world_state(...))
        6. done/error 时: asyncio.create_task(restore_npc_knowninfo(...))
        """

    async def recall_and_inject(
        self, game_session_id: UUID, user_input: str
    ) -> None:
        """回合开始 → pgvector 召回 → NPC knownInfo 注入
        1. 读取 corvus_game_sessions 获取 user_id, selected_player_candidate_id, corvus_internal_game_id
        2. 从 player_candidates 获取 character_id
        3. EmbeddingService.recall(user_id, character_id, user_input, limit=5)
        4. 获取 Corvus NPC 列表
        5. 对每个 NPC: 保存原始 knownInfo → 追加召回记忆 → PATCH Corvus
        6. 加锁保证恢复在下次注入前完成 (asyncio.Lock)
        """

    async def restore_npc_knowninfo(
        self, game_session_id: UUID
    ) -> None:
        """回合结束 → 恢复 NPC knownInfo 原始值
        从内存中取出原始 knownInfo，PATCH 回 Corvus
        """

    async def sync_world_state(
        self, game_session_id: UUID, gm_event: dict
    ) -> None:
        """异步同步 world_state 到业务数据库
        - affinity_delta → UPDATE session_npcs SET affinity = affinity + delta
        - inventory_changes → INSERT/UPDATE/DELETE inventory_items
        - story_flags → INSERT ... ON CONFLICT (game_session_id, flag_key) DO UPDATE
        """

    async def write_memory(
        self,
        user_id: UUID,
        character_id: UUID,
        dialogue_text: str,
        session_id: UUID,
    ) -> None:
        """对话结束 → LLM 提取关键记忆 → bge embedding → pgvector 存储
        复用现有 MemoryService.extract_and_store()，但 embedding 改用 bge-small-zh (512维)
        """

    async def get_current_dialogue(
        self, game_session_id: UUID
    ) -> dict:
        """获取当前场景，映射为 DialogueResponse 格式
        调用 CorvusClient.get_game() 获取游戏状态
        """
```

### 6. EmbeddingService 接口设计

```python
class EmbeddingService:
    """bge-small-zh-v1.5 本地 embedding 服务"""

    _instance = None  # 单例，避免重复加载模型
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._model = None  # 延迟加载

    async def _ensure_model(self):
        """启动时预加载模型（~400MB，首次下载）"""
        if self._model is None:
            async with self._lock:
                if self._model is None:
                    from sentence_transformers import SentenceTransformer
                    self._model = SentenceTransformer('BAAI/bge-small-zh-v1.5')

    def embed(self, text: str) -> list[float]:
        """生成 512 维 embedding，50-100ms"""
        embedding = self._model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """批量生成 embedding"""
        embeddings = self._model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    async def recall(
        self,
        user_id: UUID,
        character_id: UUID,
        query_text: str,
        limit: int = 5,
    ) -> list[str]:
        """pgvector KNN 召回相关记忆文本
        SQL:
        SELECT memory_text FROM character_memories
        WHERE user_id = :user_id AND character_id = :character_id
          AND 1 - (embedding <=> :query_embedding) > 0.7
        ORDER BY embedding <=> :query_embedding
        LIMIT :limit
        """
```

### 7. NPC knownInfo 注入/恢复策略

```
回合开始
  │
  ├─ 1. 获取 corvus_internal_game_id
  ├─ 2. GET Corvus NPC 列表
  ├─ 3. 对每个 NPC:
  │     a. GET NPC JSON → 保存原始 knownInfo 到内存 (dict: {npc_id: original_knowninfo})
  │     b. 拼接召回记忆到 knownInfo: "[相关记忆] xxx\n[相关记忆] yyy"
  │     c. PATCH Corvus 更新 NPC knownInfo
  ├─ 4. 加锁 (asyncio.Lock) 防止并发注入
  │
  ↓ POST Corvus /api/games/{gameId}/messages → SSE 流式透传
  │
回合结束 (done/error 事件)
  │
  ├─ 5. 对每个 NPC: PATCH Corvus 恢复 knownInfo 原始值
  ├─ 6. 清除内存中的原始值
  └─ 7. 释放锁
```

**锁策略：**
- 使用 `asyncio.Lock` per game_session_id，保证同一会话的注入→恢复不被并发打断
- 不同会话不互斥（不同 game_session_id 用不同锁实例）
- 锁超时：30 秒，超时后强制恢复并记录 warning

### 8. 向量记忆写入流程

```
Corvus SSE: assistant-complete 事件 (完整对话文本)
  │
  ├─ 1. asyncio.create_task(write_memory(user_id, character_id, dialogue_text, session_id))
  │     (异步执行，不阻塞 SSE 文本流)
  │
  ├─ 2. 调用现有 MemoryService.extract_and_store()
  │     a. LLM 提取关键记忆 (复用现有 prompt: build_memory_extract_prompt)
  │     b. 对每条提取的记忆文本:
  │        - EmbeddingService.embed(memory_text) → 512 维向量
  │        - INSERT INTO character_memories (user_id, character_id, memory_text, embedding, source_session_id)
  │
  └─ 3. 完成（不 yield 任何 SSE 事件，静默执行）
```

### 9. 向量记忆召回流程

```
用户输入文本 → 回合开始
  │
  ├─ 1. EmbeddingService.embed(user_input) → 512 维 query_embedding (50-100ms)
  │
  ├─ 2. pgvector KNN 搜索:
  │     SELECT memory_text,
  │            1 - (embedding <=> :query_embedding) AS similarity
  │     FROM character_memories
  │     WHERE user_id = :user_id
  │       AND character_id = :character_id
  │       AND 1 - (embedding <=> :query_embedding) > 0.7
  │     ORDER BY embedding <=> :query_embedding
  │     LIMIT 5
  │
  ├─ 3. 召回 Top-5 相关记忆文本（按相似度排序）
  │
  └─ 4. 注入 NPC knownInfo（见第 7 节）
```

**跨会话隔离：**
- `character_memories` 表按 `user_id + character_id` 检索
- 同一用户同一角色在不同 game_session 的记忆自然跨会话召回
- 不同用户/不同角色的记忆不会互相检索（WHERE 条件隔离）

### 10. 数据流图

```
┌─────────┐     1. 用户输入文本      ┌──────────────┐
│  前端   │ ─────────────────────→ │ CorvusAdapter │
│game.ts  │                         │              │
│         │                  ┌──────┘              │
│         │                  │ 2. 向量召回         │
│         │                  │   pgvector KNN     │
│         │                  │   Top-5 记忆        │
│         │                  └──────┐              │
│         │                         │ 3. NPC knownInfo │
│         │                         │    注入 (PATCH)  │
│         │                  ┌──────┘              │
│         │                  │ 4. POST Corvus     │
│         │                  │   /messages (SSE)  │
│         │                  └──────┐              │
│         │                         │ 5. SSE 事件    │
│         │  6. SSE 透传 (翻译后)   │   翻译+yield   │
│  SSE    │ ←───────────────────── │                  │
│  逐字   │                         │                  │
│  渲染   │                  ┌──────┘              │
│         │                  │ 7. 异步副作用:      │
│         │                  │   - write_memory   │
│         │                  │   - sync_world_state│
│         │                  │   - restore_npc    │
└─────────┘                  └──────────────────┘
```

---

## Technology Decisions

所有技术选型均来自 `docs/corvus-integration/execution-plan.md` 中用户确认的 12 项决策点，状态为 Accepted。

| Decision | Selected | Status | Evidence |
| --- | --- | --- | --- |
| 语言 / 框架 | Python FastAPI (后端新增服务) + Node.js Express (Corvus 外部服务，不修改) | Accepted | 用户确认决策点 1, 3；execution-plan v3 |
| 数据库 / 存储 | PostgreSQL + pgvector (512 维)，5 张新表 + 重建 character_memories embedding 维度 | Accepted | 用户确认决策点 7, 12；Q-001 已追认 |
| 缓存 / 队列 | Not Required — 不引入新缓存/队列服务；异步任务用 asyncio.create_task | Not Required | 不需要新缓存层，PostgreSQL + pgvector 足够 |
| 云服务 / 部署方式 | Not Required — Corvus 本地 systemd 守护 (127.0.0.1:8082)，无新云服务 | Not Required | 用户确认决策点 1；systemd + 防火墙已完成 |
| 模型供应商 / AI 工具 | bge-small-zh-v1.5 (本地 embedding, 512 维, 免费) + thoushub 网关 → deepseek-v4-flash (LLM, 复用现有) | Accepted | 用户确认决策点 6, 9；LLM 网关不变 |

---

## Document Sync

| Target Doc | Status | Summary / Evidence |
| --- | --- | --- |
| `docs/architecture/architecture.md` | Synced | 新增 Corvus 引擎集成模块、Engine Dispatcher、CorvusClient/CorvusAdapter/EmbeddingService 模块边界和数据流拓扑。 |
| `docs/api/api.md` | Synced | 新增 4 个 API 端点 + 4 个现有 API 扩展 feature flag + SSE 事件映射表 + API/数据/Mock/Runtime 关系。 |
| `docs/database/database.md` | Synced | 新增 5 张表 DDL + character_memories embedding 维度 1536→512 重建 + 种子数据 + 迁移/回滚方案。 |
| `docs/security/security.md` | Synced | 新增 Corvus 安全隔离 (127.0.0.1 only, 防火墙 8082 DROP, LLM API-Key 不经后端) + 向量记忆数据隔离。 |
| `docs/decisions/decisions.md` | Synced | 新增 ADR-0007 (Corvus 集成架构), ADR-0008 (bge-small-zh 本地 embedding), ADR-0009 (新旧引擎共存 feature flag)。 |
| `docs/runtime/runtime-contract.md` | Synced | 新增 CR-037 运行时契约：Corvus 8082 端口、SSE proxy 配置、Delivery E2E 命令、Browser E2E 用户动作、API/DB 契约引用、mock policy。 |

---

## Design Differences from Current Architecture

### 新增模块

1. **CorvusClient** (`backend/app/services/corvus_client.py`)：封装 Corvus HTTP + SSE 调用，仅访问 127.0.0.1:8082
2. **CorvusAdapter** (`backend/app/services/corvus_adapter.py`)：SSE 翻译 + world_state DB 同步 + 向量记忆写入/召回 + NPC knownInfo 注入/恢复
3. **EmbeddingService** (`backend/app/services/embedding_service.py`)：bge-small-zh-v1.5 本地 embedding 推理 + pgvector KNN 召回
4. **CorvusModels** (`backend/app/models/corvus.py`)：5 张新表 SQLAlchemy 模型
5. **Engine Dispatcher** (现有 `game.py` 扩展)：按 `engine_type` 字段路由到 NarrativeEngine 或 CorvusAdapter

### 修改的现有模块

1. **`backend/app/api/v1/game.py`**：4 个现有 API 增加 `engine_type` feature flag 分支
2. **`frontend/src/stores/game.ts`**：`submitCustomInput` 增加 SSE 流式读取分支 (~40 行)，`GameSession` 接口新增 `engine_type` 字段
3. **`frontend/src/views/GameView.vue`**：`initGame` 增加 Corvus 会话分支 (~5 行)
4. **`backend/app/services/narrative/memory_service.py`**：embedding 维度从 1536 改为 512（通过 EmbeddingService 间接变更，不改 MemoryService 代码逻辑）

### 不变的部分

- 旧引擎路径 (NarrativeEngine) 完全不变
- Vue 组件/样式/交互逻辑不变
- Corvus 内部 GM 逻辑/提示词不变
- 现有 LLM 网关不变（Corvus 直连 thoushub 网关，不经我方后端）

---

## Risk Assessment

| 风险 | 影响 | 缓解 |
|---|---|---|
| SSE 透传中断断连 | 用户体验 | 前端 onError 回调 + 重试按钮 |
| gm_update 异步写 DB 阻塞 SSE | 流式延迟 | asyncio.create_task 异步写，不阻塞 yield |
| knownInfo 注入+恢复竞争 | 记忆污染 | asyncio.Lock per session，保证恢复在下次注入前完成 |
| bge-small-zh 首次加载慢 | 服务启动 | 预热模型，应用启动时加载 |
| 现有 119 条记忆无 embedding | 召回失效 | 上线后跑批量补量脚本（不阻塞发布） |
| character_memories embedding 维度 1536→512 不可逆 | DB 迁移 | 现有 119 条 embedding 全为 NULL，不影响；Q-001 已追认 |

---

## Task Breakdown Summary

| Task | Owner | AC Coverage | Key Deliverables |
|---|---|---|---|
| DEV-001 | be | AC-001~004 | Corvus 基础设施验证（systemd + 防火墙 + LLM 网关 + 禁用进程） |
| DEV-002 | be | AC-005, 006, 021, 022 | 数据库建表 + 种子数据 + SQLAlchemy 模型 + player/candidates + session/create API |
| DEV-003 | be | AC-007, 008, 025 | CorvusClient + select-player API + Corvus create_game 集成 |
| DEV-004 | be | AC-009, 010, 011, 026 | CorvusAdapter SSE 翻译 + custom-input SSE 改造 |
| DEV-005 | be | AC-012, 013, 014 | world_state DB 同步（affinity + inventory + story_flags） |
| DEV-006 | be | AC-015~018, 027, 028 | EmbeddingService + 向量记忆写入/召回 + NPC knownInfo 注入/恢复 |
| DEV-007 | be | AC-019, 020 | Engine Dispatcher feature flag |
| DEV-008 | fe | AC-023, 024 | 前端 game.ts SSE 改造 + GameView 分支 |

详细任务拆分见 `tasks.md`。
