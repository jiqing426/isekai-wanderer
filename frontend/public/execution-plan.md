# Corvus-Story-Core 集成执行方案（v3 — 含向量记忆）

> 更新时间：2026-08-06 11:27 CST
> 变更点：1) 所有 UUID v4；2) SSE 流式透传；3) 新增本地 embedding + pgvector 向量记忆写入/召回

---

## 一、已完成的工作

| 项目 | 状态 | 说明 |
|---|---|---|
| Corvus-Story-Core 源码拉取 | ✅ | `/root/code/Corvus-Story-Core`，v1.1.46 |
| npm install + build | ✅ | client 构建成功 |
| LLM 网关配置 | ✅ | thoushub 网关 + deepseek-v4-flash，已通过 Settings API 写入 |
| systemd 服务 | ✅ | `corvus-story.service`，active(running)，开机自启 |
| 防火墙 | ✅ | 8082 仅 127.0.0.1 可访问，公网 DROP |
| 健康检查 | ✅ | `curl 127.0.0.1:8082/api/health` → `{"ok":true}` |

**待解决：** Corvus LLM 调用 ByteString 编码错误，需排查 `lmStudio.ts` 源码。

---

## 二、Corvus 真实 API vs 文档定义差异

| 文档写的 | Corvus 实际 | 差异 |
|---|---|---|
| Python + uvicorn | Node.js + Express + tsx | 部署方式不同 |
| `.env` 配 LLM | `config.json` + Settings API | 配置方式不同 |
| `DISABLE_WEB_UI=true` | 无此环境变量 | Web UI 和 API 同进程 |
| `ENABLE_INTERNAL_MEMORY=true` | 默认开启，无开关 | 内置记忆始终启用 |
| `POST /api/game/create_session` | `POST /api/games` | 创建游戏 |
| `POST /api/game/turn` | `POST /api/games/:gameId/messages` | 发消息（SSE 流式返回） |
| `GET /api/game/player/candidates` | 无此接口 | 需自建 |

---

## 三、数据存储架构

```
┌─────────────────────────────────────────────────────────┐
│ 业务数据库 (PostgreSQL + pgvector)                       │
│                                                         │
│ 现有表:                                                  │
│   users, game_sessions, character_memories(119条,NULL) │
│   characters, scripts, routes, nodes, ...              │
│                                                         │
│ 新增表:                                                  │
│   player_candidates    — 候选角色池(每用户≤3)            │
│   corvus_game_sessions — Corvus 剧本会话                 │
│   session_npcs         — 本局 NPC 实例                   │
│   inventory_items      — 本局道具                        │
│   story_flags          — 剧情标记                        │
│                                                         │
│ 向量记忆:                                                │
│   character_memories (复用)                             │
│   - embedding: vector(512) ← 改为 bge-small-zh 维度     │
│   - 用于跨会话语义召回                                   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Corvus 文件存储 (纯 JSON/JSONL 文件)                     │
│ /root/code/Corvus-Story-Core/corvus-data/games/{id}/    │
│                                                         │
│   game.json              — 游戏元数据                    │
│   world.json             — 世界设定                      │
│   player.json            — 玩家角色                      │
│   characters/{npc}.json  — NPC 卡片(含 memory[] 字段)   │
│   history/chapter-N.jsonl— 对话原文                      │
│   summaries/*.json       — 自动摘要(超50条压缩)          │
│   state/world-state.json — 世界状态事件                  │
│                                                         │
│ Corvus 内置 3 层记忆:                                    │
│   短期: history/ 最近对话原文                            │
│   中期: summaries/ 超阈值后 LLM 压缩                     │
│   NPC: characters/{id}.json 的 memory[] 字段             │
└─────────────────────────────────────────────────────────┘
```

**职责划分：**
- Corvus 存储：会话内剧情对话、事件摘要、NPC 内部记忆 — 用完即弃
- 业务数据库存储：候选角色、会话元数据、NPC好感、道具、剧情标记、**向量记忆（跨会话语义召回）**

---

## 四、向量记忆系统（新增）

### 4.1 Embedding 服务

**方案 A：本地 sentence-transformers + bge-small-zh-v1.5**

| 项目 | 说明 |
|---|---|
| 模型 | `BAAI/bge-small-zh-v1.5`（北京智源开源，中文优化） |
| 维度 | 512 维 |
| 模型大小 | ~400MB（一次性下载） |
| 内存占用 | ~500MB 常驻 |
| CPU 推理 | 50-100ms / 次（4 核够用） |
| 费用 | **免费**（开源 Apache 2.0） |
| 安装位置 | isekai 后端容器内 |

**数据库改造：**
```sql
-- 重建 embedding 字段维度: 1536 → 512
ALTER TABLE character_memories ALTER COLUMN embedding TYPE vector(512);
```

现有 119 条 embedding 全为 NULL，不影响。

### 4.2 写入路径（对话结束 → 向量化 → pgvector）

```
Corvus SSE: assistant-complete 事件 (完整对话文本到达)
  ↓
isekai 后端 CorvusAdapter:
  1. 调用现有 MemoryService.extract_and_store()
     - LLM 提取关键记忆(复用现有 prompt)
  2. 对每条提取的记忆文本生成 embedding
     - bge-small-zh 本地推理，50-100ms
  3. 写入 character_memories 表
     (user_id, character_id, memory_text, embedding, source_session_id)
  ↓
异步执行，不阻塞 SSE 文本流
```

### 4.3 读取路径（回合开始 → pgvector 召回 → 注入 Corvus）

```
用户输入文本 → isekai 后端 CorvusAdapter:
  1. 生成用户输入的 embedding (bge-small-zh, 50-100ms)
  2. pgvector KNN 搜索:
     SELECT memory_text FROM character_memories
     WHERE user_id = X AND character_id = Y
       AND 1 - (embedding <=> query_embedding) > 0.7
     ORDER BY embedding <=> query_embedding
     LIMIT 5
  3. 召回 Top-5 相关记忆文本
  ↓
读取 Corvus NPC 的 characters/{npc_id}.json
  ↓
将召回记忆追加到 NPC 的 knownInfo 字段:
  "[相关记忆] 用户曾表达害怕黑暗...
   [相关记忆] 用户和角色约定一起看星星..."
  ↓
POST /api/games/{game_id}/messages
  (Corvus 自动把 NPC knownInfo 带入 LLM 上下文)
  ↓
回合结束后恢复 NPC knownInfo 原始值（避免污染）
```

### 4.4 跨会话记忆能力

| 场景 | 说明 |
|---|---|
| 同一用户同一角色不同剧本 | character_memories 按 user_id+character_id 检索，自然跨会话 |
| 同一用户不同角色 | 不跨（不同 character_id，隔离正确） |
| 新建 Corvus 会话 | 旧会话的对话历史在 Corvus 文件中废弃，但关键记忆已向量存入 pgvector，新会话可召回 |

---

## 五、架构设计（v3）

```
┌─────────────────────────────────────────────────────────┐
│ 前端 (Vue, 微调 ~40 行)                                  │
│  /game?script={game_session_id} (UUID v4)              │
│                                                          │
│  初始化: POST /game/start → {session_id, node_id, ...} │
│  对话流: POST /game/{id}/custom-input (SSE 流式)       │
│    ├─ onText: StoryPanel 逐字渲染                       │
│    ├─ onDone: 更新 currentDialogue + choices([])       │
│    └─ onGmUpdate: 好感度/道具/标记更新                  │
│  读对话: GET /game/{id}/dialogue (非流式, 恢复用)       │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│ isekai-wanderer 后端 (Python FastAPI)                    │
│                                                          │
│  ┌─────────────────────────────────────────┐             │
│  │ Engine Dispatcher (feature flag)        │             │
│  │  engine_type='legacy' → NarrativeEngine│             │
│  │  engine_type='corvus'  → CorvusAdapter  │             │
│  └──────────────┬──────────────────────────┘             │
│                 │                                         │
│  ┌──────────────▼──────────────────────────┐             │
│  │ CorvusAdapter                            │             │
│  │  - CorvusClient (HTTP + SSE 透传)        │             │
│  │  - SSE Event 翻译器                      │             │
│  │  - world_state → DB 异步同步             │             │
│  │  - 向量记忆写入 (对话结束)               │             │
│  │  - 向量记忆召回+注入 (回合开始)          │             │
│  └──────┬──────────────┬───────────────────┘             │
│         │              │                                  │
│  ┌──────▼──────┐ ┌────▼──────────────────┐              │
│  │ EmbeddingSvc│ │ 业务数据库 (PG)        │              │
│  │ bge-small-zh│ │ + pgvector(512维)      │              │
│  │ 本地推理     │ │ + 5张新表              │              │
│  └─────────────┘ └──────────────────────┘              │
└──────────────────────┬──────────────────────────────────┘
                       │ SSE 透传 (127.0.0.1:8082)
┌──────────────────────▼──────────────────────────────────┐
│ Corvus-Story-Core (Node.js Express)                      │
│  POST /api/games/:id/messages → SSE 事件流               │
│  内置 3 层记忆 (短期/摘要/NPC记忆)                       │
│  LLM → thoushub → deepseek-v4-flash                     │
│  数据存储: 纯文件 JSON/JSONL                              │
└──────────────────────────────────────────────────────────┘
```

---

## 六、SSE 事件翻译映射

后端收到 Corvus SSE 事件，翻译为前端期望的格式（所有 ID 为 UUID v4）：

| Corvus SSE 事件 | 后端翻译为 | 前端处理 |
|---|---|---|
| `assistant-delta` `{delta: "你"}` | `data: {"type":"text","content":"你"}` | StoryPanel 逐字渲染 |
| `assistant-complete` `{message: {...}}` | `data: {"type":"done","text":"完整文本","character_id":"uuid-v4","character_name":"白夜","node_id":"uuid-v4"}` | 更新 currentDialogue |
| `gm-complete`/`state-changed` | `data: {"type":"gm_update","affection_delta":5,"inventory_changes":[...],"story_flags":[...]}` | 异步写 DB + UI更新 |
| `done` | `data: {"type":"stream_end"}` | 关闭连接 |
| `error` | `data: {"type":"error","message":"..."}` | 显示错误 |

**异步任务（不阻塞 SSE 流）：**
- `assistant-complete` 时：触发向量记忆写入（LLM 提取 + bge embedding + pgvector 存储）
- `gm_update` 时：world_state 同步到 session_npcs / inventory_items / story_flags

---

## 七、数据库建表（全部 UUID v4）

```sql
-- 0. 重建现有 character_memories embedding 维度
ALTER TABLE character_memories ALTER COLUMN embedding TYPE vector(512);

-- 1. 候选角色池
CREATE TABLE player_candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    personality TEXT,
    backstory TEXT,
    appearance TEXT,
    initial_inventory JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Corvus 剧本会话
CREATE TABLE corvus_game_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    selected_player_candidate_id UUID REFERENCES player_candidates(id),
    initial_location_id UUID,
    status VARCHAR(30) DEFAULT 'waiting_select_player',
    corvus_internal_game_id VARCHAR(100),
    engine_type VARCHAR(10) DEFAULT 'corvus',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. 本局 NPC 实例
CREATE TABLE session_npcs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    game_session_id UUID NOT NULL REFERENCES corvus_game_sessions(id) ON DELETE CASCADE,
    npc_template_id UUID,
    name VARCHAR(100),
    affinity INTEGER DEFAULT 0,
    present BOOLEAN DEFAULT TRUE,
    corvus_character_id VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. 本局道具
CREATE TABLE inventory_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    game_session_id UUID NOT NULL REFERENCES corvus_game_sessions(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    quantity INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. 剧情标记
CREATE TABLE story_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    game_session_id UUID NOT NULL REFERENCES corvus_game_sessions(id) ON DELETE CASCADE,
    flag_key VARCHAR(200) NOT NULL,
    flag_value JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(game_session_id, flag_key)
);
```

种子数据：从现有 `characters` 表选白夜、沈星澜、藤原雪转为 `player_candidates`。

---

## 八、后端新增文件

| 文件 | 职责 |
|---|---|
| `backend/app/services/corvus_client.py` | Corvus HTTP 调用 + SSE 流式读取 |
| `backend/app/services/corvus_adapter.py` | SSE 翻译 + world_state DB 同步 + 向量记忆写入/召回 |
| `backend/app/services/embedding_service.py` | bge-small-zh 本地 embedding 服务封装 |
| `backend/app/models/corvus.py` | 5 张新表 SQLAlchemy 模型 |

### CorvusClient 接口

```python
class CorvusClient:
    async def create_game(player_name, backstory, appearance, world_setting) -> str
    async def stream_message(game_id, content) -> AsyncGenerator[dict, None]
    async def get_game(game_id) -> dict
    async def get_characters(game_id) -> list[dict]
    async def update_npc_knowninfo(game_id, npc_id, knowninfo) -> None
    async def get_npc(game_id, npc_id) -> dict
```

### EmbeddingService 接口

```python
class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer('BAAI/bge-small-zh-v1.5')

    def embed(self, text: str) -> list[float]:
        """生成 512 维 embedding，50-100ms"""

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """批量生成"""

    def recall(self, user_id, character_id, query_text, limit=5) -> list[str]:
        """pgvector KNN 召回相关记忆文本"""
```

### CorvusAdapter 接口

```python
class CorvusAdapter:
    async def create_session(user_id, player_candidate) -> dict:
        """创建 Corvus 游戏，返回 session 数据"""

    async def stream_turn(game_session_id, user_input) -> AsyncGenerator[str, None]:
        """SSE 流式透传 Corvus 回合
        回合开始前: 向量召回 → 注入 NPC knownInfo
        回合结束后: 恢复 NPC knownInfo + 向量写入记忆
        """

    async def get_current_dialogue(game_session_id) -> dict:
        """获取当前场景，映射为 DialogueResponse"""

    async def sync_world_state(game_session_id, gm_event, db) -> None:
        """异步同步 world_state 到业务数据库"""

    async def write_memory(user_id, character_id, dialogue_text, session_id) -> None:
        """对话结束 → LLM 提取记忆 → bge embedding → pgvector 存储"""

    async def recall_and_inject(game_session_id, user_input) -> None:
        """回合开始 → pgvector 召回 → 写入 NPC knownInfo"""

    async def restore_npc_knowninfo(game_session_id, npc_id, original_value) -> None:
        """恢复 NPC knownInfo 原始值"""
```

---

## 九、现有 API 改造（feature flag）

| API | 旧引擎 (legacy) | Corvus 引擎 |
|---|---|---|
| `POST /game/start` | 不变 | 创建 corvus_game_sessions, 返回 `{session_id, node_id: uuid4, message}` |
| `GET /game/{id}/dialogue` | 不变 | 调 CorvusClient.get_game(), 映射为 DialogueResponse |
| `POST /game/{id}/custom-input` | 不变 (同步 JSON) | **SSE 流式透传**（含向量召回注入） |
| `POST /game/{id}/choice` | 不变 (同步 JSON) | **SSE 流式透传** (choice_text 作为 input) |

## 十、新增 API

| 路由 | 方法 | 说明 |
|---|---|---|
| `/api/game/session/create` | POST | 创建剧本会话 |
| `/api/game/player/candidates` | GET | 获取候选角色（最多 3 个） |
| `/api/game/session/select-player` | POST | 选定角色, 调 Corvus 创建游戏 |
| `/api/game/game-turn` | POST | 游戏回合（同步版, 供 API 调用） |

---

## 十一、前端改造（~40 行）

### 改动 1：`game.ts` — `submitCustomInput` 改为 SSE 流式

```typescript
async function submitCustomInput(text: string) {
    if (!currentSession.value) return;
    loading.value = true;

    const isCorvus = currentSession.value.engine_type === 'corvus';

    if (isCorvus) {
        // SSE 流式读取
        const token = getCookie('isekai_access_token');
        const response = await fetch(`/api/v1/game/${currentSession.value.id}/custom-input`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ text })
        });

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let fullText = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = JSON.parse(line.slice(6));
                    if (data.type === 'text') {
                        fullText += data.content;
                        currentDialogue.value = {
                            ...currentDialogue.value!,
                            text: fullText,
                            type: 'dialogue',
                        };
                    } else if (data.type === 'done') {
                        currentDialogue.value = {
                            ...currentDialogue.value!,
                            text: data.text || fullText,
                            character_id: data.character_id,
                            node_id: data.node_id,
                            type: 'dialogue',
                        };
                        pendingChoices.value = []; // Corvus 无 choices
                    } else if (data.type === 'gm_update') {
                        // 好感度动效等
                    }
                }
            }
        }

        loading.value = false;
        return { new_achievements: [], chapter_transition: null };
    }

    // 旧引擎路径不变
    // ... existing code ...
}
```

### 改动 2：`game.ts` — `GameSession` interface 新增 `engine_type`

```typescript
export interface GameSession {
    id: string;
    script_id: string;
    current_node_id: string;
    status: 'active' | 'completed' | 'abandoned';
    character_id?: string;
    route_id?: string;
    affection_value?: number;
    engine_type?: 'legacy' | 'corvus';  // 新增
}
```

### 改动 3：`GameView.vue` — `initGame` 支持 Corvus 会话

约 5 行分支逻辑。

### 改动 4：choices 为空时降级

现有 `ChoicePanel` 的 `v-if="game.hasChoices || game.loading"` 已处理空数组。`FreeChatInput` 的 `v-if="!game.isEnded"` 始终显示。**无需改。**

---

## 十二、风险和待解决项

| 风险 | 影响 | 缓解 |
|---|---|---|
| Corvus LLM ByteString 编码错误 | 阶段 1 收尾 | 调试 lmStudio.ts 源码 |
| SSE 透传中断断连 | 用户体验 | 前端 onError 回调 + 重试 |
| Corvus game_id 是 slug 不是 UUID | DB 设计 | corvus_internal_game_id 用 VARCHAR |
| gm_update 异步写 DB 可能阻塞 SSE | 流式延迟 | asyncio.create_task 异步写 |
| knownInfo 注入+恢复 可能竞争 | 记忆污染 | 每回合前后加锁，保证恢复 |
| bge-small-zh 首次加载慢 | 服务启动 | 预热模型，启动时加载 |
| 现有 119 条记忆无 embedding | 召回失效 | 上线后跑批量补量脚本 |

---

## 十三、执行顺序和时间估计

| 步骤 | 内容 | 预计 | 依赖 |
|---|---|---|---|
| 1.1 | 修复 Corvus LLM 编码错误 | 0.5h | — |
| 1.2 | 验证 Corvus 端到端（创建→发消息→收 SSE 流） | 0.5h | 1.1 |
| 2.1 | 建表 + ALTER embedding 维度 + SQLAlchemy 模型 | 1h | — |
| 2.2 | 种子数据（3 个候选角色） | 0.5h | 2.1 |
| 2.3 | 安装 sentence-transformers + 下载 bge-small-zh | 1h | — |
| 2.4 | EmbeddingService 实现 | 1h | 2.3 |
| 2.5 | 批量补量 119 条旧记忆的 embedding | 0.5h | 2.4 |
| 3.1 | CorvusClient 实现（HTTP + SSE 流式读取） | 2h | 1.2 |
| 3.2 | CorvusAdapter 实现（SSE 翻译 + DB 同步 + 向量写入 + 召回注入） | 4h | 3.1, 2.4 |
| 3.3 | 现有 API feature flag + SSE 透传改造 | 2h | 3.2 |
| 3.4 | 新增 4 个 API 端点 | 1h | 3.2 |
| 4.1 | 前端 game.ts submitCustomInput SSE 改造（~40 行） | 1.5h | 3.3 |
| 5.1 | 联调测试 | 2h | 全部 |
| **合计** | | **~18h** | |

---

## 十四、用户确认的决策点

1. ✅ Node.js 方式部署
2. ✅ config.json + Settings API 配置 LLM
3. ✅ 前端小改 ~40 行
4. ✅ 新旧剧本系统共存 + feature flag
5. ✅ 候选角色用现有 characters 表
6. ✅ 使用 thoushub 网关
7. ✅ 所有 UUID v4
8. ✅ SSE 流式透传
9. ✅ 方案 A：本地 sentence-transformers + bge-small-zh-v1.5（免费）
10. ✅ 向量记忆写入（对话结束 → pgvector）
11. ✅ 向量记忆召回（回合开始 → NPC knownInfo 注入 + 回合结束恢复）
12. ✅ 重建 character_memories embedding 维度 1536→512
