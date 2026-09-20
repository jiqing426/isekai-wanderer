# Architecture Decision Records — Isekai Wanderer

---

## ADR-0001: Backend Framework — Python FastAPI

Status: Accepted  
**Date**: 2026-07-18  
**Decider**: User + Architect

### Context

The project requires a backend framework that supports AI/LLM-intensive operations, async I/O for streaming, and efficient vector database interaction.

### Decision

Use **Python FastAPI** as the backend framework.

### Alternatives Considered

| Dimension | FastAPI (Selected) | NestJS |
|-----------|-------------------|--------|
| AI/LLM ecosystem | Python native; LangChain/LlamaIndex/openai SDK directly usable | Requires HTTP bridge to Python AI services |
| Vector operations | pgvector Python SDK native support | Requires additional adaptation |
| Async performance | asyncio native, ideal for LLM I/O-bound scenarios | Event loop model also suitable |
| Developer efficiency | Type hints + auto docs, less code | TypeScript full-stack type sharing convenient |
| Deployment | Single-process Uvicorn, small Docker image | Node.js image also small |
| Team | Python AI engineers can contribute directly | Requires TypeScript expertise |

### Rationale

AI-intensive project; Python ecosystem is the most natural choice, avoiding cross-language bridge complexity.

### Consequences

- All backend code in Python 3.12
- FastAPI with Uvicorn ASGI server
- SQLAlchemy ORM + Alembic migrations
- pytest + httpx for testing

---

## ADR-0002: Vector Database — pgvector

Status: Accepted  
**Date**: 2026-07-18  
**Decider**: User + Architect

### Context

The memory system requires vector similarity search for character memory recall. Options include embedded vector extensions vs. dedicated vector databases.

### Decision

Use **pgvector** (PostgreSQL extension) for vector storage.

### Alternatives Considered

| Dimension | pgvector (Selected) | Pinecone | Milvus |
|-----------|---------------------|----------|--------|
| Operational complexity | Reuses PostgreSQL, zero extra services | SaaS managed, low | Independent cluster, high |
| MVP data volume | <100K vectors, pgvector performance sufficient | Sufficient | Overkill |
| Cost | No additional cost | $70+/month starting | Self-hosted resource overhead |
| Query flexibility | SQL + vector hybrid queries | Pure vector | Pure vector |
| Migration to dedicated | Can migrate later; embedding column is independent | Vendor lock-in | Vendor lock-in |

### Rationale

MVP phase reuses PostgreSQL to reduce ops and cost; smooth migration path to dedicated vector DB when data grows.

### Consequences

- PostgreSQL with `vector` extension enabled
- 1536-dimension embeddings (text-embedding-3-small)
- IVFFlat index with `lists = 100`
- Similarity threshold 0.8, top-K = 3

---

## ADR-0003: Script Data Format — JSON

Status: Accepted  
**Date**: 2026-07-18  
**Decider**: Architect

### Context

Script/story data (nodes, choices, routes) needs a serialization format for storage and loading.

### Decision

Use **JSON** as the script data format.

### Rationale

- Native to both frontend (JavaScript) and backend (Python `json`)
- Simple structure, no complex nesting requiring YAML
- Easy to validate with JSON Schema
- Seed script imports JSON directly into PostgreSQL

### Consequences

- Script data files stored in `data/` directory as JSON
- Node structure: id, type, text, choices, conditions, next_node references
- Seed script parses JSON and populates `scripts`, `routes`, `nodes`, `node_choices` tables

---

## ADR-0004: Authentication Scheme — JWT

Status: Accepted  
**Date**: 2026-07-18  
**Decider**: Architect

### Context

The system needs stateless, scalable authentication for a SPA/PWA frontend.

### Decision

Use **JWT Bearer Token** authentication (Access Token 15 min + Refresh Token 7 days).

### Rationale

- Stateless: no server-side session storage required
- Scalable: works across multiple backend instances
- SPA-friendly: no cookie CSRF complexity
- Refresh token rotation for security

### Consequences

- Access Token: 15-minute TTL, sent as `Authorization: Bearer <token>`
- Refresh Token: 7-day TTL, used to obtain new Access Tokens
- Passwords hashed with bcrypt (cost factor 12)
- OAuth mock uses same JWT issuance flow
- No CSRF tokens needed (no cookie-based auth)

---

## ADR-0005: Real-time Protocol — SSE

Status: Accepted  
**Date**: 2026-07-18  
**Decider**: Architect

### Context

Dialogue streaming requires real-time server-to-client push for LLM-generated text, emotion changes, and scene transitions.

### Decision

Use **Server-Sent Events (SSE)** for real-time dialogue streaming.

### Alternatives Considered

| Protocol | SSE (Selected) | WebSocket |
|----------|----------------|-----------|
| Direction | Server → Client (unidirectional) | Bidirectional |
| Complexity | Low (HTTP-based, auto-reconnect) | Higher (connection management) |
| Fit for use case | Perfect (dialogue is server-push) | Overkill (no client-push needed) |
| Browser support | Native `EventSource` API | Native `WebSocket` API |
| Proxy/CDN | Works through HTTP proxies | May require WebSocket-aware proxies |

### Rationale

Dialogue streaming is unidirectional (server pushes text chunks). SSE is simpler, HTTP-native, and auto-reconnects. Client sends choices via regular POST, not through the streaming channel.

### Consequences

- `GET /api/v1/game/:sessionId/dialogue` returns `text/event-stream`
- Event types: `text`, `emotion`, `scene`, `choice`, `affection_update`, `memory_recall`, `done`
- Frontend uses native `EventSource` API
- Choices submitted via `POST /api/v1/game/:sessionId/choice`

---

## ADR-0006: Frontend UI Framework — Naive UI

Status: Accepted  
**Date**: 2026-07-18  
**Decider**: User

### Context

The frontend needs a Vue 3 component library with strong theming support for anime/game aesthetics.

### Decision

Use **Naive UI** as the component library.

### Alternatives Considered

| Dimension | Naive UI (Selected) | Element Plus |
|-----------|--------------------|---------|
| Theme customization | High flexibility; CSS-in-JS theme override | Moderate; SCSS variables |
| TypeScript | Full TS support | Full TS support |
| Bundle size | Tree-shakeable | Tree-shakeable |
| Game/anime aesthetic | Easier to customize for non-corporate look | More enterprise-oriented |

### Rationale

Naive UI's theme customization flexibility is superior for the anime/game visual style required by the project.

### Consequences

- All UI components from Naive UI
- Custom theme override in `styles/theme.ts`
- Anime-style color palette and typography

---

## ADR-0007: Cache Layer — Redis

Status: Accepted  
**Date**: 2026-07-18  
**Decider**: Architect

### Context

The system needs fast in-memory storage for session state, rate limiting counters, check-in status, and brute force lockout tracking.

### Decision

Use **Redis** as the cache and ephemeral state layer.

### Rationale

- Sub-millisecond latency for cache lookups
- Native support for sliding window rate limiting (sorted sets)
- Key expiration for tokens, lockouts, and session state
- Widely supported, Docker-friendly

### Use Cases

| Use Case | Redis Feature |
|----------|---------------|
| Rate limiting | Sliding window (sorted sets) |
| Brute force lockout | Counter with TTL |
| Session cache | Key-value with expiration |
| Check-in status | Daily key with TTL |

### Consequences

- Redis instance at `:6379`
- `REDIS_URL` environment variable for connection
- RDB snapshot for persistence (cache is reconstructable if lost)

---

## ADR-0008: LLM Provider — GPT-4o-mini Default, Unified Gateway

Status: Accepted  
**Date**: 2026-07-18  
**Decider**: Architect

### Context

The narrative engine requires LLM calls for dialogue generation, memory extraction, and style application. The system must support multi-model switching without business code changes.

### Decision

- **Default model**: OpenAI GPT-4o-mini (low cost, controllable latency)
- **Embedding model**: OpenAI text-embedding-3-small (1536 dimensions)
- **Architecture**: Unified LLM Gateway abstraction layer with pluggable providers

### Gateway Design

```python
class LLMProvider(Protocol):
    async def chat(self, messages: list[Message], **kwargs) -> AsyncIterator[str]: ...
    async def embed(self, text: str) -> list[float]: ...

class OpenAIProvider(LLMProvider): ...
class AnthropicProvider(LLMProvider): ...
class LocalProvider(LLMProvider): ...  # Local models / Ollama
```

### Rationale

- GPT-4o-mini: best cost/quality ratio for MVP
- Gateway pattern: switch providers via `LLM_PROVIDER` env var, no code changes
- Local provider option: enables offline development and future self-hosted models

### Consequences

- `LLM_PROVIDER` env var selects provider (`openai` | `anthropic` | `local`)
- `OPENAI_API_KEY` required for default provider
- Streaming via SSE for chat responses
- Fallback mechanism: 2 retries → canned fallback dialogue on failure

---

## ADR-0009: Character Playable System — Multi-Route Architecture

Status: Accepted  
**Date**: 2026-08-02  
**Decider**: User + Architect  
**人工确认**: PL 2026-08-02 确认采纳

### Context

Players need to select different characters to experience different story routes within the same script. This requires extending the character and game session models to support playable characters with route associations.

### Decision

Extend the character system with playable flags and route associations:

1. **Character table extension**: Add `playable`, `playable_route_id`, `play_description`, `unlock_type`, `unlock_price` fields
2. **GameSession table extension**: Add `character_id`, `character_name` fields (snapshot)
3. **New table**: `user_character_unlocks` for tracking unlocked paid characters
4. **NarrativeEngine enhancement**: Add L3 Player Identity layer to inject character identity into prompts

### Alternatives Considered

| Dimension | Selected Approach | Alternative: Separate playable_characters table |
|-----------|-------------------|--------------------------------------------------|
| Schema complexity | Extend existing tables | New table with FK to characters |
| Query performance | Single table scan | JOIN required |
| Migration effort | ALTER TABLE + data migration | New table + data copy |
| Backward compatibility | Nullable fields, existing sessions unaffected | Requires view or union query |
| Future extensibility | Fields can be extended | Separate table more flexible |

### Rationale

- **Simplicity**: Extending existing tables avoids JOIN complexity
- **Backward compatibility**: Nullable fields ensure existing GameSessions work unchanged
- **Snapshot pattern**: `character_name` snapshot prevents historical data inconsistency if character is renamed
- **Unlock tracking**: Separate `user_character_unlocks` table allows flexible unlock types (paid/subscription/gift) and audit trail
- **Prompt layer**: L3 Player Identity layer cleanly separates player identity from NPC profile (L4)

### Consequences

- **Database**: 3 schema changes (characters +5 fields, game_sessions +2 fields, new user_character_unlocks table)
- **API**: 1 new endpoint (POST /characters/{id}/unlock), 3 extended endpoints (GET /scripts/{id}, POST /game/start, GET /saves)
- **NarrativeEngine**: PromptBuilder adds L3 layer (100 tok budget), total budget 2400 tokens
- **Frontend**: Script detail page adds character selection, game page shows character info, saves page adds character filter
- **Data migration**: Existing `is_main=true` characters auto-migrated to playable
- **Backward compatibility**: Existing GameSessions (character_id=NULL) display "默认角色", no prompt injection

### Constraints

- `playable=true` AND `playable_route_id IS NOT NULL` required for character to appear in playable list
- `unlock_type='paid'` requires `unlock_price` to be set (application-level validation)
- `character_name` is snapshot at GameSession creation, not affected by later character renames
- L3 Player Identity layer is empty string when `character_id=NULL` (backward compatible)

---

## ADR-0010: Character Name Snapshot Pattern

Status: Accepted  
**Date**: 2026-08-02  
**Decider**: Architect  
**人工确认**: PL 2026-08-02 确认采纳

### Context

When a player starts a game with a character, the character's name should be preserved in the game session even if the character is later renamed by an admin.

### Decision

Store `character_name` as a snapshot in the `game_sessions` table at session creation time.

### Alternatives Considered

| Dimension | Snapshot (Selected) | Alternative: FK lookup at query time |
|-----------|---------------------|--------------------------------------|
| Data consistency | Historical accuracy preserved | Name changes affect all historical sessions |
| Query performance | No JOIN needed | Requires JOIN to characters table |
| Storage overhead | 100 bytes per session | No extra storage |
| Admin workflow | Can rename without affecting history | Must consider historical impact |

### Rationale

- **Historical accuracy**: Players expect to see the character name they chose, not a later rename
- **Performance**: Avoids JOIN on every save list query
- **Simplicity**: Snapshot pattern is well-understood and easy to implement

### Consequences

- `game_sessions.character_name` is VARCHAR(100), nullable
- Set at GameSession creation from `characters.name`
- Not updated if character is renamed
- Existing sessions (NULL) display "默认角色"

---

## ADR-0011: Unlock Type Enumeration

Status: Accepted  
**Date**: 2026-08-02  
**Decider**: Architect  
**人工确认**: PL 2026-08-02 确认采纳

### Context

Characters can have different unlock mechanisms: free for all, paid with fragments, or subscription-tier gated.

### Decision

Use `unlock_type` VARCHAR(20) field with enum values: `free`, `paid`, `subscription`.

### Alternatives Considered

| Dimension | VARCHAR enum (Selected) | Alternative: INTEGER enum |
|-----------|-------------------------|---------------------------|
| Readability | Human-readable in DB | Requires lookup table |
| Extensibility | Easy to add new types | Requires migration |
| Validation | Application-level check | DB-level constraint |
| Query performance | Slightly slower | Faster comparison |

### Rationale

- **Readability**: `unlock_type='paid'` is self-documenting
- **MVP scope**: Only 3 types needed, performance difference negligible
- **Future-proof**: Easy to add new types (e.g., `event`, `achievement`) without migration

### Consequences

- `characters.unlock_type` defaults to `'free'`
- Application validates enum values
- `unlock_price` required when `unlock_type='paid'` (application-level check)
- `user_character_unlocks.unlock_type` records how character was unlocked (paid/subscription/gift)

---

## ADR-0007: Corvus-Story-Core 集成架构 — 新旧引擎共存 + SSE 流式透传

Status: Accepted  
**Date**: 2026-08-06  
**Decider**: User + Architect

### Context

项目需要 AI 自由叙事能力，现有 NarrativeEngine 为规则驱动，无法生成自由文本剧情。用户已自行部署 Corvus-Story-Core (Node.js Express AI 叙事引擎)。

### Decision

采用新旧引擎共存架构，通过 `engine_type` feature flag 切换：

- `engine_type='legacy'` → 现有 NarrativeEngine (规则驱动, 不变)
- `engine_type='corvus'` → CorvusAdapter (SSE 流式透传 Corvus)

后端新增 CorvusClient (HTTP+SSE)、CorvusAdapter (翻译+同步+记忆)、EmbeddingService (bge-small-zh 本地推理)。

### Alternatives Considered

| Dimension | 新旧共存 (Selected) | 替换旧引擎 | 独立微服务 |
|-----------|---------------------|-----------|-----------|
| 风险 | 低 (旧路径不变) | 高 (回归风险) | 中 (部署复杂) |
| 开发量 | 中 (新增模块) | 高 (迁移所有功能) | 高 (新服务+运维) |
| 可回退 | 是 (feature flag) | 否 | 是 |
| 维护 | 两套路径 | 一套 | 跨服务 |

### Rationale

- 旧剧本系统有完整内容和用户，不能废弃
- Corvus 是实验性 AI 引擎，需 feature flag 隔离风险
- SSE 流式透传保证用户体验 (逐字渲染)
- 用户确认了 12 项决策点 (见 execution-plan v3)

### Consequences

- 后端新增 3 个服务模块 + 5 张表 + 4 个 API + 4 个 API 扩展
- 前端仅改 game.ts ~40 行 SSE 读取
- Corvus 127.0.0.1:8082 systemd 守护, 公网不可达

---

## ADR-0008: 向量记忆 Embedding — 本地 bge-small-zh-v1.5

Status: Accepted  
**Date**: 2026-08-06  
**Decider**: User + Architect

### Context

跨会话语义记忆需要 embedding 向量化。现有 `character_memories` 表 embedding 维度 1536 (OpenAI text-embedding-3-small)，但 119 条记录 embedding 全为 NULL。

### Decision

使用 **BAAI/bge-small-zh-v1.5** 本地 sentence-transformers 推理：

| 项目 | 值 |
|---|---|
| 模型 | BAAI/bge-small-zh-v1.5 (北京智源开源, Apache 2.0) |
| 维度 | 512 |
| 模型大小 | ~400MB |
| CPU 推理 | 50-100ms/次 |
| 费用 | 免费 |

`character_memories` embedding 维度 1536→512 (不可逆迁移, Q-001 已追认)。

### Alternatives Considered

| Dimension | bge-small-zh (Selected) | OpenAI text-embedding-3-small | Cohere embed-v3 |
|-----------|-------------------------|-------------------------------|-----------------|
| 费用 | 免费 | $0.02/1M tokens | $0.10/1M tokens |
| 维度 | 512 | 1536 | 1024 |
| 中文优化 | 是 (北京智源) | 通用 | 通用 |
| 隐私 | 本地推理, 数据不出境 | 数据发送 OpenAI | 数据发送 Cohere |
| 延迟 | 50-100ms (本地 CPU) | 100-200ms (网络) | 100-200ms (网络) |
| 运维 | 需下载模型 ~400MB | 无 | 无 |

### Rationale

- 免费 (无新增基础设施费用)
- 中文优化 (项目为中文叙事)
- 隐私 (用户对话数据不出境)
- 现有 119 条 embedding 全为 NULL，维度变更无损

### Consequences

- 服务启动时预加载模型 (~400MB 内存常驻)
- `character_memories` embedding 维度 1536→512 (不可逆)
- 上线后跑批量补量脚本为 119 条旧记忆补 embedding

---

## ADR-0009: 新旧引擎共存 Feature Flag — engine_type 字段

Status: Accepted  
**Date**: 2026-08-06  
**Decider**: User + Architect

### Context

需要在不废弃旧剧本系统的前提下集成 Corvus 引擎，降低风险并支持回退。

### Decision

使用 `engine_type` 字段在 `corvus_game_sessions` 表区分引擎类型：

- `engine_type='legacy'` → NarrativeEngine 路径 (完全不变)
- `engine_type='corvus'` → CorvusAdapter 路径 (SSE 流式)

### Alternatives Considered

| Dimension | feature flag (Selected) | 独立路由 | 环境变量 |
|-----------|----------------------|---------|---------|
| 粒度 | 每会话级 | 全局级 | 全局级 |
| 回退 | 改字段即可 | 切路由 | 改 env 重启 |
| 旧路径影响 | 无 | 无 | 无 |
| 用户感知 | 无 | 无 | 无 |

### Rationale

- 每会话级粒度，可逐用户灰度
- 旧路径完全不变，零回归风险
- 回退只需改 `engine_type` 字段

### Consequences

- Engine Dispatcher 在 `game.py` 中按 `engine_type` 分支路由
- 旧 API 入参/返回格式完全兼容 (非破坏性变更)
- 两种引擎互不干扰

---

## ADR-0012: Legacy 代码保留策略 — 条件分支保留

Status: Accepted  
**Date**: 2026-08-27  
**Decider**: Architect (SA)  
**人工确认**: INIT 附条件 2 委托 SA 在 DESIGN 阶段决定

### Context

CR-038 需要在前端激活 Corvus 引擎，但 C3 约束下所有剧本统一走 Corvus。Legacy 代码路径（POST /game/start、节点式对话、submitChoice/submitCustomInput 的 legacy 分支）需要决定保留方式。

### Decision

采用**条件分支保留**策略：
- `submitChoice()` 和 `submitCustomInput()` 中的 `if (isCorvus) { SSE 分支 } else { legacy 分支 }` 原样保留
- Legacy 分支代码不被删除、不被注释、不被标记为 deprecated
- C3 约束下所有剧本 `engine_type = 'corvus'`，legacy 分支自然不被执行

### Alternatives Considered

| Dimension | 条件分支保留 (Selected) | 注释 | 删除标记 | 删除 |
|-----------|---------------------|------|---------|------|
| 可读性 | 保留 (最佳) | 注释降低可读性 | 标记增加噪音 | 丢失代码 |
| 可回退 | 改 engine_type 即可 | 取消注释易出错 | 移除标记 | 需 git revert |
| 可测试 | legacy 分支可被测试 | 注释无法测试 | 标记无法测试 | 不可测试 |
| 未来恢复 | 只需 engine_type='legacy' | 需取消注释 | 需移除标记 | 需 git revert |
| 代码整洁 | 条件分支是正常代码结构 | 注释块不整洁 | 墓碑注释不整洁 | 最整洁但风险高 |

### Rationale

- 条件分支是正常的代码结构，不是需要清理的技术债
- CR-037 已实现完整的 Corvus SSE 分支，CR-038 只是激活它（设置 engine_type）
- 注释和删除标记都会降低可读性和可测试性
- 未来如需恢复 legacy 引擎，只需将 engine_type 改回 'legacy'

### Consequences

- `submitChoice()` 和 `submitCustomInput()` 的条件分支代码原样保留
- `startGame()` 中新增 Corvus 会话创建流程分支，原 legacy POST /game/start 路径保留
- `resumeSession()` 新增 engine_type 写入，旧数据兼容处理
- Legacy 代码保留在代码库中，但不被 Corvus 剧本激活

---

## ADR-0013: 选角 UI 形态 — 模态弹窗

Status: Accepted  
**Date**: 2026-08-27  
**Decider**: Architect (SA)  
**人工确认**: Q-003 暂缓到设计阶段，SA 决定

### Context

CR-038 需要选角 UI，用户在开始 Corvus 游戏前选择或创建角色候选。Q-003 暂缓决定选角 UI 是模态弹窗还是独立页面。

### Decision

采用**模态弹窗 (Modal Dialog)**。

### Alternatives Considered

| Dimension | 模态弹窗 (Selected) | 独立页面 |
|-----------|---------------------|---------|
| 用户体验 | 聚焦注意力，不离开当前页面 | 需要导航到新路由 |
| 实现复杂度 | 中 (Naive UI n-modal) | 中 (新增路由+视图) |
| 流程连贯性 | 高 (弹窗关闭即进入游戏) | 中 (需路由跳转) |
| 与现有架构 | 一致 (Naive UI 组件) | 需新增路由配置 |

### Rationale

- 选角是进入游戏前的必要步骤，模态弹窗聚焦用户注意力
- 不需要独立路由页面，选角完成后自动进入游戏界面
- 与现有 Naive UI 的 `n-modal` 组件一致
- 触发时机：startGame() 创建会话成功后 → 弹出选角 Modal → 用户选择/创建角色 → 确认 → 进入游戏

### Consequences

- 新增 `PlayerCandidateModal.vue` 组件，使用 Naive UI `n-modal`
- 选角 Modal 嵌入 startGame 流程，创建会话成功后弹出
- 角色候选创建表单嵌入 Modal 内，支持切换选择/创建模式

---

## ADR-042-01: Legacy SSE 在端点层组装

**Date**: 2026-09-15
**Status**: Accepted
**CR**: CR-042

### Context

Legacy `submit_choice` 和 `submit_custom_input` 已有 `process_choice()` / `process_custom_input()` 方法处理节点推进、好感度、对话历史、成就和收敛检查。SSE 流式输出需要在这之上增加 LLM 流式调用和 SSE 事件包装。需要决定流式逻辑放在哪一层。

### Decision

在 `game.py` 端点层新建 `_stream_legacy_turn()` 和 `_stream_legacy_custom_input()` 函数，调用 `llm_gateway.stream_dialogue()` 获取流式输出并包装为 SSE 事件。不修改 `narrative_engine` 内部方法。

### Alternatives Considered

| Dimension | 端点层组装 (Selected) | narrative_engine 内部 |
|-----------|----------------------|----------------------|
| 职责清晰 | ✅ narrative_engine 负责状态，game.py 负责传输 | ❌ 混合状态和传输 |
| 一致性 | ✅ 与 Corvus `_stream_corvus_turn()` 模式一致 | ❌ 引入新模式 |
| 改动范围 | ✅ 只改 game.py + 新增函数 | ❌ 需改 narrative_engine 多个方法 |
| 测试 | ✅ 端点测试覆盖 | ❌ 需要引擎层 + 端点层双重测试 |

### Rationale

与 Corvus 路径的 `_stream_corvus_turn()` 保持架构一致；`narrative_engine` 继续专注节点推进和状态变更；流式传输是端点层关注点。

### Consequences

- `game.py` 新增 4 个函数：`_stream_legacy_turn()`, `_stream_legacy_custom_input()`, `_run_legacy_deferred()`, `_run_legacy_custom_input_deferred()`
- `narrative_engine` 不被修改（`generate_dialogue_stream()` 保持不变）
- BE 开发者只需在端点层处理 SSE 组装

---

## ADR-042-02: Legacy done 事件一次性推送元数据

**Date**: 2026-09-15
**Status**: Accepted
**CR**: CR-042

### Context

Corvus 路径使用 `gm_update` 事件从 GM 输出流中解析元数据（好感度、道具、选项）。Legacy 路径的 `process_choice()` 返回值中已有结构化的 `affection_change`、`choices` 等字段，不需要从 LLM 输出流中解析。

### Decision

Legacy SSE 流在 `done` 事件中一次性推送所有元数据（好感度变化、下一节点选项），不使用 `gm_update` 事件。

### Rationale

Legacy 路径的元数据来源是结构化的（DB 查询 + affection_service），不需要从 LLM 输出流中解析。`done` 事件一次性推送更简洁、更可靠，前端处理逻辑更简单。

### Consequences

- Legacy SSE 事件类型：`text`, `emotion`, `affection_update`, `done`, `error`（不包含 `gm_update`）
- 前端 `useSSEStream()` composable 的 `onGmUpdate` callback 仅 Corvus 路径使用
- 前端在 `onDone` callback 中处理 `affection_change` 和 `choices`

---

## ADR-042-03: Fallback 文本按场景区分设计

**Date**: 2026-09-15
**Status**: Accepted
**CR**: CR-042

### Context

Q-003 暂缓到 DESIGN 阶段确认 AC-019 fallback 文本内容。所有 fallback 模型均流式失败时需要返回友好提示文本。

### Decision

按场景类型预设不同 fallback 文本，保持角色人设口吻（第一人称、含动作描述括号），不让用户感觉是系统错误。

### Fallback Texts

| Scenario | Text |
|----------|------|
| FREE_CHAT | （微微侧头，轻轻笑了笑）抱歉，我刚才走神了……你说的真有意思，能再和我说说吗？ |
| NARRATIVE | （故事在这一刻仿佛停滞了片刻，随后又缓缓流淌……） |
| CHOICE_GENERATION | 选项似乎暂时无法生成，请稍后再试。 |
| Default | 抱歉，暂时无法回应，请稍后再试。 |

### Rationale

不同场景的 fallback 文本应该匹配上下文；使用角色口吻比 "系统错误" 更友好，用户不会感觉是技术故障。Fallback 文本为硬编码，不接受外部输入，不存在注入风险。

### Consequences

- `model_router._get_stream_fallback_text(scenario)` 方法返回场景特定文本
- fallback 文本作为单个 chunk 一次性 yield（非流式）
- 不影响正常流式输出路径

---

## ADR-043-01: 权限检查放在 API 端点层

**Date**: 2026-09-16
**Status**: Accepted
**CR**: CR-043

### Context

Q-005 暂缓到 DESIGN 阶段确认权限检查放在 API 层还是中间件层。CG 画廊和剧本访问的权限检查逻辑各不相同，需要决定放置位置。

### Decision

放在 API 端点层，不使用中间件。

### Alternatives Considered

| Dimension | API 端点层 (Selected) | 中间件层 |
|-----------|----------------------|---------|
| 灵活性 | ✅ 每个端点可定制检查逻辑 | ❌ 通用中间件难以覆盖不同权限场景 |
| 与现有代码一致 | ✅ 端点层调用 Service 层 | ❌ 需新增中间件层 |
| 代码可读性 | ✅ 权限检查在端点内可见 | ❌ 中间件隐式拦截 |
| 维护成本 | ✅ 低 | ❌ 需维护中间件配置 |

### Rationale

CG 画廊检查订阅等级（standard+ 可访问全部），剧本检查 `script_access`（三档映射），`game.py` 检查 `script_access` + 剧本分类。三种场景逻辑不同，不适合统一中间件。端点层调用 `SubscriptionService` 的方式与现有代码风格一致。

### Consequences

- `gallery.py`、`game.py`、`scripts.py` 各自调用 `SubscriptionService` 进行权限检查
- 不新增中间件
- 权限检查逻辑在端点代码中可见

---

## ADR-043-02: script_access 映射采用运行时虚拟判定

**Date**: 2026-09-16
**Status**: Accepted
**CR**: CR-043

### Context

Q-002/C2 要求确认 `script_access` 三档如何映射到剧本表结构。PRD Non-Goals 明确“不修改数据库结构”。

### Decision

通过运行时虚拟字段判定，不修改 `scripts` 表。

### 判定规则

- `trial_only` (free)：`genre == 'romance' AND hot_value >= 50`
- `all_normal` (basic/standard)：所有剧本（当前无独家剧本）
- `all_including_exclusive` (premium)：所有剧本

### Rationale

- PRD 明确不修改数据库结构
- 当前系统无独家剧本，不需要 `is_exclusive` 字段
- 运行时判定函数可随业务调整，不触发数据库迁移
- 试用剧本范围采用 PRD 建议默认值（Q-003 确认）

### Consequences

- `scripts.py` 和 `game.py` 中新增 `_compute_script_accessible()` 辅助函数
- 未来如需新增独家剧本，可在 `scripts` 表增加 `is_exclusive` 字段，届时 `all_normal` 档追加 `AND NOT is_exclusive` 条件
- 试用剧本范围调整只需修改判定函数
