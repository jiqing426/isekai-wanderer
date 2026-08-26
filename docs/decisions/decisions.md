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
