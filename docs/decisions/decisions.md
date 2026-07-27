# Architecture Decision Records — Isekai Wanderer

---

## ADR-0001: Backend Framework — Python FastAPI

**Status**: Accepted  
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

**Status**: Accepted  
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

**Status**: Accepted  
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

**Status**: Accepted  
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

**Status**: Accepted  
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

**Status**: Accepted  
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

**Status**: Accepted  
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

**Status**: Accepted  
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
