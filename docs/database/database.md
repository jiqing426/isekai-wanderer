# Database Design — Isekai Wanderer

## Overview

Primary database: **PostgreSQL** with **pgvector** extension for vector similarity search. Cache layer: **Redis**. Migration tool: **Alembic**.

---

## Table List (37 tables)

| Table | Purpose | PK | Key Indexes |
| --- | --- | --- | --- |
| `users` | User accounts | `id (UUID)` | `email (unique)`, `oauth_provider+oauth_id (unique)` |
| `email_verifications` | Email verification tokens | `id` | `user_id`, `token`, `expires_at` |
| `password_resets` | Password reset tokens | `id` | `user_id`, `token`, `expires_at` |
| `scripts` | Script metadata | `id` | `slug (unique)` |
| `routes` | Story routes | `id` | `script_id`, `chapter_number`, `chapter_type`, `script_id+chapter_number` |
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
| `user_character_unlocks` | User unlocked playable characters (CR-028) | `id (UUID)` | `user_id+character_id (unique)` |

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
| Dimensions | 512 (CR-037: changed from 1536 for bge-small-zh) |
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

---

## CR-027 Additions: Lorebook / SceneConfig / Character Extension

### New Table: `lorebook_entries`

World knowledge entries managed by admins, injected into Prompt Layer 2 based on scene tag matching.

```sql
CREATE TABLE lorebook_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    tags JSONB NOT NULL DEFAULT '[]',
    priority INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_lorebook_tags ON lorebook_entries USING gin(tags);
CREATE INDEX idx_lorebook_status ON lorebook_entries(status);
```

| Field | Purpose |
|-------|---------|
| `title` | Entry title (≤200 chars) |
| `content` | Entry content (plain text, ≤5000 chars) |
| `tags` | Scene tags array, e.g. `["森林","白天"]` |
| `priority` | Injection priority (higher = first) |
| `status` | `active` or `deleted` (soft delete) |
| `created_by` | Admin user who created the entry |

### New Table: `scene_configs`

Scene configuration bound to story nodes (1:1), used for Lorebook tag matching and Prompt Layer 2 injection.

```sql
CREATE TABLE scene_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    node_id UUID NOT NULL UNIQUE REFERENCES nodes(id),
    scene_name VARCHAR(200) NOT NULL,
    tags JSONB NOT NULL DEFAULT '[]',
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_scene_configs_node ON scene_configs(node_id);
```

| Field | Purpose |
|-------|---------|
| `node_id` | Bound story node (unique, 1:1) |
| `scene_name` | Scene name, e.g. "月光森林" |
| `tags` | Atmosphere tags, e.g. `["森林","夜晚","神秘"]` |
| `description` | Scene description, injected into Prompt Layer 2 |

### Extended Table: `characters`

Three new nullable fields for NPC internal drive (desire/fear/secret):

```sql
ALTER TABLE characters ADD COLUMN desire TEXT;
ALTER TABLE characters ADD COLUMN fear TEXT;
ALTER TABLE characters ADD COLUMN secret TEXT;
```

| Field | Purpose |
|-------|---------|
| `desire` | Character's inner desire, e.g. "被认可" |
| `fear` | Character's deep fear, e.g. "被遗忘" |
| `secret` | Character's hidden secret, e.g. "其实是异世界人" |

All fields are nullable; existing characters default to NULL. PromptBuilder gracefully degrades when fields are empty.

---

## CR-028 Additions: Character Playable / Multi-Route

### Extended Table: `characters` (playable fields)

Five new fields for playable character configuration:

```sql
ALTER TABLE characters ADD COLUMN playable BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE characters ADD COLUMN playable_route_id UUID REFERENCES routes(id);
ALTER TABLE characters ADD COLUMN play_description TEXT;
ALTER TABLE characters ADD COLUMN unlock_type VARCHAR(20) NOT NULL DEFAULT 'free';
ALTER TABLE characters ADD COLUMN unlock_price INT;
```

| Field | Purpose |
|-------|----------|
| `playable` | Whether character can be played as |
| `playable_route_id` | Associated story route for this character's playthrough |
| `play_description` | Description shown to players selecting this character |
| `unlock_type` | Unlock type: `free` / `paid` / `subscription` |
| `unlock_price` | Price in fragments (required when unlock_type='paid') |

Validation: `playable=true` AND `playable_route_id IS NOT NULL` → character appears in playable_characters list. When `unlock_type='paid'`, `unlock_price` must not be NULL (application-level check).

### Extended Table: `game_sessions` (character fields)

Two new nullable fields for tracking player's chosen character:

```sql
ALTER TABLE game_sessions ADD COLUMN character_id UUID REFERENCES characters(id);
ALTER TABLE game_sessions ADD COLUMN character_name VARCHAR(100);
```

| Field | Purpose |
|-------|----------|
| `character_id` | FK to characters table; NULL = default character (backward compatible) |
| `character_name` | Snapshot of character name at session creation; not affected by later renames |

Backward compatible: existing sessions have both fields NULL, display "默认角色".

### New Table: `user_character_unlocks`

Records user's unlocked paid characters:

```sql
CREATE TABLE user_character_unlocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    character_id UUID NOT NULL REFERENCES characters(id),
    unlock_type VARCHAR(20) NOT NULL,  -- paid/subscription/gift
    unlocked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, character_id)
);

CREATE INDEX idx_user_char_unlocks_user ON user_character_unlocks(user_id);
CREATE INDEX idx_user_char_unlocks_char ON user_character_unlocks(character_id);
```

| Field | Purpose |
|-------|----------|
| `user_id` | User who unlocked |
| `character_id` | Character that was unlocked |
| `unlock_type` | How it was unlocked: paid/subscription/gift |
| `unlocked_at` | When it was unlocked |

UNIQUE(user_id, character_id) ensures idempotency.

### CR-028 Data Migration

Existing `is_main=true` characters auto-migrated to playable:

```sql
UPDATE characters
SET playable = true,
    unlock_type = 'free',
    play_description = COALESCE(description, name || ' — 剧本主角'),
    playable_route_id = (SELECT r.id FROM routes r WHERE r.script_id = characters.script_id LIMIT 1)
WHERE is_main = true AND playable = false;
```

Migration is idempotent (WHERE playable = false guard).

### CR-028 Database / API / Mock / Runtime Relationships

| Table | API Consumer | Mock | Runtime |
|-------|-------------|------|----------|
| `characters` (playable fields) | GET /scripts/{id}, POST /game/start, POST /characters/{id}/unlock | No mock; real DB in all tests | `docs/runtime/runtime-contract.md` |
| `game_sessions` (character fields) | POST /game/start, GET /saves | No mock; real DB in all tests | `docs/runtime/runtime-contract.md` |
| `user_character_unlocks` | POST /characters/{id}/unlock, GET /scripts/{id} | No mock; real DB in all tests | `docs/runtime/runtime-contract.md` |

### CR-027 Database / API / Mock / Runtime Relationships

| Table | API Consumer | Mock | Runtime |
|-------|-------------|------|---------|
| `lorebook_entries` | GET/POST/PUT/DELETE /api/v1/lorebook (Admin) | No mock; real DB in all tests | `docs/runtime/runtime-contract.md` |
| `scene_configs` | GET/PUT/DELETE /api/v1/scene-configs (Admin) | No mock; real DB in all tests | `docs/runtime/runtime-contract.md` |
| `characters.desire/fear/secret` | PUT /api/v1/characters/{id} (Admin) | No mock; real DB in all tests | `docs/runtime/runtime-contract.md` |

---

## CR-029 Additions: Node Branch Character Filtering

### Extended Table: `nodes` (character_id field)

One new nullable field for branch-node character visibility:

```sql
ALTER TABLE nodes ADD COLUMN character_id UUID REFERENCES characters(id);
CREATE INDEX ix_nodes_character_id ON nodes(character_id);
```

| Field | Purpose |
|-------|---------|
| `character_id` | FK to characters table; NULL = public node (all characters visible); non-NULL = branch node (only visible to that character) |

Backward compatible: existing nodes have `character_id = NULL`, visible to all sessions.

### CR-029 Database / API / Mock / Runtime Relationships

| Table | API Consumer | Mock | Runtime |
|-------|-------------|------|----------|
| `nodes.character_id` | GET /game/{sessionId}/dialogue, POST /game/{sessionId}/choice | No mock; real DB in all tests | `docs/runtime/runtime-contract.md` |

---

## CR-030 Additions: Chapter Structure Refactor

### Extended Table: `routes` (chapter fields)

Two new nullable fields for chapter structure:

```sql
ALTER TABLE routes ADD COLUMN chapter_number INTEGER;
ALTER TABLE routes ADD COLUMN chapter_type VARCHAR(50);
CREATE INDEX ix_routes_chapter_number ON routes(chapter_number);
CREATE INDEX ix_routes_chapter_type ON routes(chapter_type);
CREATE INDEX ix_routes_script_chapter ON routes(script_id, chapter_number);
```

| Field | Purpose |
|-------|---------|
| `chapter_number` | Chapter number (1-4); NULL = backward compatible (old route) |
| `chapter_type` | Chapter type enum: `encounter` / `daily` / `conflict` / `convergence`; NULL = backward compatible |

**chapter_type enumeration**:

| Value | Meaning | Chapter |
|-------|---------|----------|
| `encounter` | 相遇 | Chapter 1 |
| `daily` | 日常 | Chapter 2 |
| `conflict` | 冲突 | Chapter 3 |
| `convergence` | 收束 | Chapter 4 |

Backward compatible: existing routes have both fields NULL, API returns `chapter_number: null`.

### CR-030 Data Migration

Map 11 existing routes to chapters by script title + route title:

```sql
-- 星月奇缘 (3 routes)
UPDATE routes SET chapter_number = 1, chapter_type = 'encounter'
WHERE script_id = (SELECT id FROM scripts WHERE title = '星月奇缘')
  AND title = '第一章：月夜邂逅';

UPDATE routes SET chapter_number = 2, chapter_type = 'daily'
WHERE script_id = (SELECT id FROM scripts WHERE title = '星月奇缘')
  AND title = '第二章：星辰之约';

UPDATE routes SET chapter_number = 3, chapter_type = 'conflict'
WHERE script_id = (SELECT id FROM scripts WHERE title = '星月奇缘')
  AND title = '第三章：命运交织';

-- 星辰之约 (4 routes)
UPDATE routes SET chapter_number = 1, chapter_type = 'encounter'
WHERE script_id = (SELECT id FROM scripts WHERE title = '星辰之约')
  AND title = '星夜邂逅';

UPDATE routes SET chapter_number = 2, chapter_type = 'daily'
WHERE script_id = (SELECT id FROM scripts WHERE title = '星辰之约')
  AND title = '林辰线：星光指引';

UPDATE routes SET chapter_number = 3, chapter_type = 'conflict'
WHERE script_id = (SELECT id FROM scripts WHERE title = '星辰之约')
  AND title = '流星线：刹那永恒';

UPDATE routes SET chapter_number = 4, chapter_type = 'convergence'
WHERE script_id = (SELECT id FROM scripts WHERE title = '星辰之约')
  AND title = '银河线：命运交汇';

-- 樱花恋曲 (4 routes)
UPDATE routes SET chapter_number = 1, chapter_type = 'encounter'
WHERE script_id = (SELECT id FROM scripts WHERE title = '樱花恋曲')
  AND title = '樱花树下';

UPDATE routes SET chapter_number = 2, chapter_type = 'daily'
WHERE script_id = (SELECT id FROM scripts WHERE title = '樱花恋曲')
  AND title = '月夜线：静谧之恋';

UPDATE routes SET chapter_number = 3, chapter_type = 'conflict'
WHERE script_id = (SELECT id FROM scripts WHERE title = '樱花恋曲')
  AND title = '阳菜线：夏日恋歌';

UPDATE routes SET chapter_number = 4, chapter_type = 'convergence'
WHERE script_id = (SELECT id FROM scripts WHERE title = '樱花恋曲')
  AND title = '雪乃线：樱花树下的约定';
```

Migration is idempotent (UPDATE by title is repeatable). Unmatched routes remain NULL.

### CR-030 Rollback

**Schema rollback**: `alembic downgrade -1` removes chapter_number and chapter_type columns.

**Data rollback**: Downgrade automatically removes fields; no separate data rollback script needed.

**Code rollback**: `git revert <commit-hash>`

### CR-030 Database / API / Mock / Runtime Relationships

| Table | API Consumer | Mock | Runtime |
|-------|-------------|------|----------|
| `routes.chapter_number` | GET /game/{sessionId}/status, GET /game/{sessionId}/dialogue, GET /scripts/{id}/chapters | No mock; real DB in all tests | `docs/runtime/runtime-contract.md` |
| `routes.chapter_type` | GET /game/{sessionId}/status, GET /game/{sessionId}/dialogue, GET /scripts/{id}/chapters | No mock; real DB in all tests | `docs/runtime/runtime-contract.md` |

### CR-037 Additions: Corvus-Story-Core 集成

#### New Tables (5 tables, total 37)

| Table | Purpose | PK | Key Indexes |
| --- | --- | --- | --- |
| `player_candidates` | 候选角色池 (每用户≤3) | `id (UUID v4)` | `user_id` |
| `corvus_game_sessions` | Corvus 剧本会话 | `id (UUID v4)` | `user_id`, `status`, `corvus_internal_game_id` |
| `session_npcs` | 本局 NPC 实例 | `id (UUID v4)` | `game_session_id`, `corvus_character_id` |
| `inventory_items` | 本局道具 | `id (UUID v4)` | `game_session_id` |
| `story_flags` | 剧情标记 | `id (UUID v4)` | `game_session_id`, `flag_key (unique per session)` |

#### New Table Schemas

```sql
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
    corvus_internal_game_id VARCHAR(100),  -- Corvus slug 格式, 非 UUID
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

#### Modified Table: character_memories

```sql
-- 重建 embedding 维度: 1536 → 512 (适配 bge-small-zh-v1.5)
ALTER TABLE character_memories ALTER COLUMN embedding TYPE vector(512);
```

**迁移说明**: 现有 119 条记录 embedding 全为 NULL，不影响迁移。此为不可逆迁移，Q-001 已追认。

**回滚方案**: `ALTER TABLE character_memories ALTER COLUMN embedding TYPE vector(1536);` 可恢复维度（NULL 数据无损）。

#### Seed Data

从现有 `characters` 表选 3 个角色转为 `player_candidates` 种子数据：
- 白夜、沈星澜、藤原雪

#### CR-037 Database / API / Mock / Runtime Relationships

| Table | API Consumer | Mock | Runtime |
|-------|-------------|------|----------|
| `player_candidates` | GET /api/v1/game/player/candidates, POST /api/v1/game/session/select-player | No mock; real DB | `docs/runtime/runtime-contract.md` |
| `corvus_game_sessions` | POST /api/v1/game/session/create, POST /api/v1/game/session/select-player, POST /api/v1/game/start (feature flag) | No mock; real DB | `docs/runtime/runtime-contract.md` |
| `session_npcs` | CorvusAdapter.sync_world_state (affinity 同步) | No mock; real DB | `docs/runtime/runtime-contract.md` |
| `inventory_items` | CorvusAdapter.sync_world_state (道具同步) | No mock; real DB | `docs/runtime/runtime-contract.md` |
| `story_flags` | CorvusAdapter.sync_world_state (标记同步) | No mock; real DB | `docs/runtime/runtime-contract.md` |
| `character_memories` (modified) | CorvusAdapter.write_memory / recall_and_inject, EmbeddingService.recall | No mock; real pgvector 512维 | `docs/runtime/runtime-contract.md` |
