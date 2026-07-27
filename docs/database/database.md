# Database Design — Isekai Wanderer

## Overview

Primary database: **PostgreSQL** with **pgvector** extension for vector similarity search. Cache layer: **Redis**. Migration tool: **Alembic**.

---

## Table List (29 tables)

| Table | Purpose | PK | Key Indexes |
| --- | --- | --- | --- |
| `users` | User accounts | `id (UUID)` | `email (unique)`, `oauth_provider+oauth_id (unique)` |
| `email_verifications` | Email verification tokens | `id` | `user_id`, `token`, `expires_at` |
| `password_resets` | Password reset tokens | `id` | `user_id`, `token`, `expires_at` |
| `scripts` | Script metadata | `id` | `slug (unique)` |
| `routes` | Story routes | `id` | `script_id` |
| `nodes` | Plot nodes | `id` | `route_id`, `node_type`, `parent_id` |
| `node_choices` | Choice options | `id` | `node_id` |
| `characters` | Characters | `id` | `script_id` |
| `character_sprites` | Character emotion sprites | `id` | `character_id`, `emotion` |
| `scenes` | Scenes | `id` | `script_id` |
| `game_sessions` | Game sessions | `id (UUID)` | `user_id`, `route_id`, `status` |
| `game_progress` | Game progress (choice history) | `id` | `session_id`, `node_id` |
| `affection` | Affection levels | `id` | `user_id+character_id (unique)` |
| `character_memories` | Character memories (pgvector) | `id` | `user_id+character_id`, `embedding (vector)` |
| `daily_checkins` | Check-in records | `id` | `user_id+date (unique)` |
| `streak_records` | Streak state | `id` | `user_id (unique)` |
| `daily_tasks` | Daily task instances | `id` | `user_id+date+task_type (unique)` |
| `fragments` | Fragment balance | `id` | `user_id (unique)` |
| `fragment_transactions` | Fragment transaction log | `id` | `user_id`, `created_at` |
| `purchases` | IAP transactions | `id` | `user_id`, `created_at` |
| `subscriptions` | Subscription records | `id` | `user_id`, `status` |
| `unlocked_scripts` | Unlocked scripts | `id` | `user_id+script_id (unique)` |
| `unlocked_cgs` | Unlocked CGs | `id` | `user_id+cg_id (unique)` |
| `cg_assets` | CG assets | `id` | `script_id`, `route_id` |
| `share_cards` | Ending share cards | `id (UUID)` | `user_id` |
| `user_preferences` | User preferences | `id` | `user_id (unique)` |
| `discord_configs` | Discord webhook configs (CR-002 AC-055) | `id` | `enabled`, `events` |
| `recall_emails` | Recall email records (CR-002 AC-057) | `id` | `user_id`, `sent_at` |
| `free_chat_sessions` | Free chat history (CR-002 AC-058) | `id (UUID)` | `user_id`, `character_id` |

---

## Key Table Schemas

### users

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),  -- nullable for OAuth-only users
    display_name VARCHAR(100),
    avatar_url TEXT,
    email_verified BOOLEAN DEFAULT FALSE,
    oauth_provider VARCHAR(50),   -- 'google' | 'discord' | NULL
    oauth_id VARCHAR(255),
    subscription_tier VARCHAR(20) DEFAULT 'free',  -- free/basic/standard/premium
    trial_started_at TIMESTAMPTZ,
    trial_ends_at TIMESTAMPTZ,
    onboarding_completed BOOLEAN DEFAULT FALSE,
    preferred_genre VARCHAR(50),
    locale VARCHAR(10) DEFAULT 'en',
    last_login TIMESTAMPTZ,  -- CR-002 AC-057: recall email trigger
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### character_memories (pgvector)

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE character_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    character_id UUID NOT NULL REFERENCES characters(id),
    memory_text TEXT NOT NULL,
    embedding vector(1536) NOT NULL,  -- text-embedding-3-small
    source_session_id UUID,
    confidence DECIMAL(3,2) DEFAULT 1.0,
    is_compressed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_memories_user_char ON character_memories(user_id, character_id);
CREATE INDEX idx_memories_embedding ON character_memories USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

### game_sessions

```sql
CREATE TABLE game_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    script_id UUID NOT NULL REFERENCES scripts(id),
    route_id UUID NOT NULL REFERENCES routes(id),
    current_node_id UUID REFERENCES nodes(id),
    status VARCHAR(20) DEFAULT 'active',  -- active/completed/abandoned
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    ending_type VARCHAR(20),  -- good/normal/bad
    choice_history JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}'
);
```

### password_resets (CR-002 AC-047)

```sql
CREATE TABLE password_resets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_password_resets_token ON password_resets(token);
CREATE INDEX idx_password_resets_user_id ON password_resets(user_id);
```

### discord_configs (CR-002 AC-055)

```sql
CREATE TABLE discord_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    webhook_url VARCHAR(500) NOT NULL,
    channel_name VARCHAR(100),
    enabled BOOLEAN DEFAULT TRUE,
    events JSONB DEFAULT '["ending_unlocked"]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### recall_emails (CR-002 AC-057)

```sql
CREATE TABLE recall_emails (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    email VARCHAR(255) NOT NULL,
    email_type VARCHAR(50) DEFAULT 'recall_7day',
    game_link TEXT,
    progress_summary JSONB DEFAULT '{}',
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    opened BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_recall_emails_user_id ON recall_emails(user_id);
CREATE INDEX idx_recall_emails_sent_at ON recall_emails(sent_at);
```

### free_chat_sessions (CR-002 AC-058)

```sql
CREATE TABLE free_chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    character_id UUID NOT NULL REFERENCES characters(id),
    topic VARCHAR(50) NOT NULL,
    messages JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_free_chat_user_id ON free_chat_sessions(user_id);
CREATE INDEX idx_free_chat_character_id ON free_chat_sessions(character_id);
```

### affection

```sql
CREATE TABLE affection (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    character_id UUID NOT NULL REFERENCES characters(id),
    value INTEGER NOT NULL DEFAULT 0,  -- 0-100
    level VARCHAR(20) NOT NULL DEFAULT 'acquaintance',  -- acquaintance/ambiguous/trust/bond/love
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, character_id)
);
```

---

## pgvector Setup

| Aspect | Detail |
|--------|--------|
| Extension | `vector` (pgvector) |
| Embedding model | OpenAI `text-embedding-3-small` |
| Dimensions | 1536 |
| Index type | IVFFlat with `vector_cosine_ops` |
| Index parameter | `lists = 100` |
| Similarity threshold | 0.8 |
| Recall limit | 3 (top-K nearest neighbors) |
| Table | `character_memories` |

---

## Migration Strategy

| Aspect | Detail |
|--------|--------|
| Tool | **Alembic** |
| MVP status | Greenfield product, no legacy data migration risk |
| Idempotency | All migration scripts must be idempotent (repeatable) |
| Seed data | Script JSON → seed script import |
| Revision tracking | Alembic `alembic_version` table |

### Migration Workflow

1. Schema change → `alembic revision --autogenerate -m "description"`
2. Review generated migration
3. Apply: `alembic upgrade head`
4. Rollback: `alembic downgrade -1`

---

## Backup Strategy

| Aspect | Detail |
|--------|--------|
| Method | PostgreSQL `pg_dump` |
| Frequency | Daily (cron or managed service backup) |
| Retention | 7-day rolling window (MVP) |
| Vector data | Included in pg_dump (pgvector columns are native) |
| Redis | RDB snapshot + AOF (optional for MVP; cache is reconstructable) |

---

## Database / API / Mock / Runtime Relationships

| Concern | Binding |
|---------|---------|
| ORM | SQLAlchemy async sessions |
| Migrations | Alembic (autogenerate + manual review) |
| Connection | `DATABASE_URL` env var (e.g., `postgresql+asyncpg://user:pass@db:5432/isekai`) |
| Redis | `REDIS_URL` env var (e.g., `redis://redis:6379/0`) |
| Vector ops | pgvector native SQL + SQLAlchemy `Vector` column type |
| Mock policy | No database mocking in Delivery E2E; test fixtures use real PostgreSQL; MockEmailService and MockDiscordService log to files, not to DB tables |
| API 边界 | 数据只能通过 API 边界访问；详见 `docs/api/api.md` 端点列表 |
| Runtime 配置 | 持久化连接串、pgvector 和 Redis 端口通过 `docs/runtime/runtime-contract.md` 统一管理 |

### CR-002 Database / API / Mock / Runtime Relationships

| Table | API Consumer | Mock | Runtime |
|---|---|---|---|
| `password_resets` | POST /auth/forgot-password, POST /auth/reset-password | MockEmailService sends to log | `docs/runtime/runtime-contract.md` |
| `discord_configs` | Internal (DiscordService) | MockDiscordService sends to log | `docs/runtime/runtime-contract.md` |
| `recall_emails` | Internal (RecallService cron) | MockEmailService sends to log | `docs/runtime/runtime-contract.md` |
| `free_chat_sessions` | POST /game/{sessionId}/free-chat | LLM Gateway (mock or real) | `docs/runtime/runtime-contract.md` |
| `users.last_login` | Internal (RecallService query) | N/A | Updated on login success |
