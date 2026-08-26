# API Design — Isekai Wanderer

## Overview

All API endpoints are served from the FastAPI backend under the base path `/api/v1`. Authentication uses JWT Bearer tokens. Real-time dialogue streaming uses Server-Sent Events (SSE).

---

## API Endpoint Table (66 endpoints)

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| POST | /api/v1/auth/register | None | Email registration |
| POST | /api/v1/auth/login | None | Email login |
| POST | /api/v1/auth/verify-email | None | Email verification |
| POST | /api/v1/auth/resend-verification | Bearer | Resend verification email |
| POST | /api/v1/auth/forgot-password | None | Password reset request |
| POST | /api/v1/auth/reset-password | None | Password reset |
| POST | /api/v1/auth/refresh | Bearer | Token refresh |
| GET | /api/v1/auth/oauth/:provider | None | OAuth mock login entry |
| GET | /api/v1/auth/oauth/:provider/callback | None | OAuth mock callback |
| GET | /api/v1/scripts | Bearer | Script list |
| GET | /api/v1/scripts/:id | Bearer | Script details (with routes) |
| GET | /api/v1/scripts/:id/routes/:routeId | Bearer | Route details (with node graph) |
| POST | /api/v1/game/start | Bearer | Start game (create session) |
| GET | /api/v1/game/:sessionId | Bearer | Get game session state |
| GET | /api/v1/game/:sessionId/dialogue | Bearer | SSE streaming dialogue |
| POST | /api/v1/game/:sessionId/choice | Bearer | Submit choice |
| POST | /api/v1/game/:sessionId/free-chat | Bearer | Free chat (P1) |
| GET | /api/v1/game/:sessionId/ending | Bearer | Get ending |
| POST | /api/v1/game/:sessionId/restart | Bearer | Restart route |
| GET | /api/v1/affection | Bearer | All character affection levels |
| GET | /api/v1/affection/:characterId | Bearer | Single character affection detail |
| GET | /api/v1/daily/checkin | Bearer | Query today's check-in status |
| POST | /api/v1/daily/checkin | Bearer | Execute check-in |
| GET | /api/v1/daily/tasks | Bearer | Today's task list |
| POST | /api/v1/daily/tasks/:taskId/claim | Bearer | Claim task reward |
| GET | /api/v1/shop | Bearer | IAP item list |
| POST | /api/v1/shop/purchase | Bearer | Mock purchase |
| GET | /api/v1/shop/history | Bearer | Purchase history |
| GET | /api/v1/subscription/plans | Bearer | Subscription plan list |
| POST | /api/v1/subscription/subscribe | Bearer | Mock subscribe |
| POST | /api/v1/subscription/cancel | Bearer | Cancel subscription |
| GET | /api/v1/subscription/status | Bearer | Current subscription status |
| GET | /api/v1/gallery | Bearer | CG gallery (P1) |
| GET | /api/v1/gallery/:cgId | Bearer | CG detail |
| POST | /api/v1/share/ending | Bearer | Generate ending share card (P1) |
| GET | /api/v1/share/:shareId | None | View share card |
| GET | /api/v1/user/profile | Bearer | User profile info |
| PUT | /api/v1/user/profile | Bearer | Update user profile |
| GET | /api/v1/user/preferences | Bearer | User preferences |
| PUT | /api/v1/user/preferences | Bearer | Update preferences |
| GET | /api/v1/game/{scriptId}/route-map | Bearer | Route exploration map (CR-002 AC-045) |
| POST | /api/v1/auth/forgot-password | None | Password reset request (CR-002 AC-047) |
| POST | /api/v1/auth/reset-password | None | Password reset execution (CR-002 AC-047) |
| POST | /api/v1/game/{sessionId}/free-chat | Bearer | Free chat with character (CR-002 AC-058) |
| GET | /api/v1/discover/trending | None | Trending scripts (CR-004) |
| GET | /api/v1/discover/recommendations | Bearer | Personalized recommendations (CR-004) |
| GET | /api/v1/discover/categories | None | Script categories (CR-004) |
| GET | /api/v1/characters | None | Character list (CR-004) |
| GET | /api/v1/saves | Bearer | User save snapshots (CR-004) |
| GET | /api/v1/health | None | Health check |
| GET | /api/v1/scripts/{script_id}/chapters | Bearer | Script chapter list (CR-030) |

---

## Authentication Scheme

| Aspect | Detail |
|--------|--------|
| Protocol | JWT Bearer Token |
| Access Token TTL | 15 minutes |
| Refresh Token TTL | 7 days |
| OAuth Mock | Google/Discord buttons → mock callback → create/link account → issue JWT |
| Provider Abstraction | `IOAuthProvider` interface; mock and real implementations share the contract |
| API Auth Middleware | Bearer Token middleware validates every protected request |
| Rate Limiting | Redis sliding window: general API 60/min, LLM calls 10/min |

---

## Error Codes

| Error Code | HTTP Status | Meaning |
| --- | --- | --- |
| AUTH_INVALID_CREDENTIALS | 401 | Email or password incorrect |
| AUTH_EMAIL_NOT_VERIFIED | 403 | Email not verified |
| AUTH_TOKEN_EXPIRED | 401 | Token expired |
| AUTH_FORBIDDEN | 403 | Insufficient permissions |
| SCRIPT_NOT_FOUND | 404 | Script not found |
| SCRIPT_LOCKED | 403 | Script not unlocked (requires purchase) |
| GAME_SESSION_EXPIRED | 410 | Game session expired |
| GAME_INVALID_CHOICE | 400 | Invalid choice |
| LLM_GENERATION_FAILED | 503 | AI generation failed (fallback triggered) |
| LLM_RATE_LIMITED | 429 | LLM call rate limited |
| PAYMENT_FAILED | 402 | Mock payment failed |
| SUBSCRIPTION_ACTIVE | 409 | Active subscription already exists |
| DAILY_ALREADY_CHECKED_IN | 409 | Already checked in today |
| CHARACTER_NOT_FOUND | 404 | Character not found (CR-002) |
| AUTH_RESET_TOKEN_INVALID | 400 | Reset token invalid or already used (CR-002) |
| AUTH_RESET_TOKEN_EXPIRED | 400 | Reset token expired (CR-002) |
| VALIDATION_ERROR | 422 | Request parameter validation failed |
| INTERNAL_ERROR | 500 | Internal server error |
| CHAPTER_NOT_FOUND | 404 | Chapter not found for script (CR-030) |

---

## SSE Protocol — Streaming Dialogue

### Client Connection

```typescript
const eventSource = new EventSource('/api/v1/game/dialogue?session_id=xxx');
```

### Server Push Format

```typescript
// Text chunk
event: message
data: {"type": "text", "content": "Hello, I am...", "character_id": "char_a"}

// Emotion change
event: message
data: {"type": "emotion", "emotion": "happy", "character_id": "char_a"}

// Scene change
event: message
data: {"type": "scene", "scene_id": "forest_01", "bgm": "battle_theme"}

// Choice prompt
event: message
data: {"type": "choice", "options": [{"id": "c1", "text": "...", "affection_delta": 3}]}

// Affection update
event: message
data: {"type": "affection_update", "character_id": "char_a", "value": 45, "level": "trust"}

// Memory recall
event: message
data: {"type": "memory_recall", "text": "I remember you said you liked sunflowers..."}

// Session complete
event: done
data: {"session_id": "xxx", "node_id": "n015"}
```

### SSE Event Types

| Event Type | Description | Payload Fields |
|------------|-------------|----------------|
| `text` | Dialogue text chunk | `content`, `character_id` |
| `emotion` | Character emotion change | `emotion`, `character_id` |
| `scene` | Scene/background switch | `scene_id`, `bgm` |
| `choice` | Present choices to player | `options[]` (id, text, affection_delta) |
| `affection_update` | Real-time affection change | `character_id`, `value`, `level` |
| `memory_recall` | Memory injected into dialogue | `text` |
| `done` | Dialogue round complete | `session_id`, `node_id` |

---

## Frontend Consumer Matrix

| Feature | Frontend Component | API Endpoint(s) | State Store |
|---------|-------------------|-----------------|-------------|
| Script list | HomeView | GET /api/v1/scripts | script store |
| Game dialogue | GameView + DialogueBox | SSE /api/v1/game/dialogue | game store |
| Choice actions | ChoicePanel | POST /api/v1/game/choice | game store |
| Emotion switching | CharacterSprite | Parse SSE emotion tags | game store |
| Background switching | SceneBackground | Parse node `scene` field | game store |
| Affection display | AffectionBar | GET /api/v1/affection/:charId | affection store |
| Check-in | StreakCalendar | GET/POST /api/v1/daily/checkin | daily store |
| Tasks | DailyView | GET /api/v1/daily/tasks | daily store |
| Shop | ShopView | GET/POST /api/v1/payment/* | auth store |
| Subscription | SubscriptionView | GET/POST /api/v1/subscription/* | auth store |

---

## API / Data / Mock / Runtime Relationships

| Concern | Contract Doc | Runtime Binding |
|---------|-------------|-----------------|
| API contract | `docs/api/api.md` (this file, 61 endpoints) | All endpoints served at `/api/v1` on `:8000` |
| Database contract | `docs/database/database.md` | PostgreSQL `:5432` + pgvector; Redis `:6379` |
| Mock policy | Mock only for payment/OAuth providers; **no mock API for Delivery E2E or Release evidence** |
| Runtime contract | `docs/runtime/runtime-contract.md` | Vite dev proxy `→ localhost:8000`; Nginx reverse proxy in prod |

### Mock Boundaries

| What is mocked | What is NOT mocked |
|----------------|-------------------|
| Payment providers (Stripe/Apple IAP) | All 45 API endpoints |
| OAuth providers (Google/Discord) | Database operations |
| Email delivery (MockEmailService -> log file) | LLM Gateway (uses real or stub LLM, not mocked API) |
| Discord webhook (MockDiscordService -> log file) | SSE streaming |
| | Browser/Delivery E2E (Mock API=no) |

### CR-002 API / Data / Mock / Runtime Relationships

| Concern | Contract Doc | Runtime Binding |
|---------|-------------|------------------|
| API contract (CR-002 new endpoints) | `docs/api/api.md` (this file, 45 endpoints) | `/api/v1` on `:8000` |
| Database contract (CR-002 new tables) | `docs/database/database.md` | PostgreSQL `:5432` + pgvector |
| Mock policy (CR-002) | MockEmailService (AC-047/057), MockDiscordService (AC-055); **no mock API for Delivery E2E** | `docs/runtime/runtime-contract.md` |
| Runtime contract | `docs/runtime/runtime-contract.md` | Vite dev proxy, Nginx prod proxy |

---

## CR-027 Additions: Lorebook / SceneConfig / Character Extension

### New Endpoints (8 endpoints, total 58)

#### Lorebook Management (Admin only)

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | /api/v1/lorebook | Bearer + Admin | Lorebook entry list (supports `?tag=` filter, `?page=&pageSize=` pagination) |
| POST | /api/v1/lorebook | Bearer + Admin | Create Lorebook entry |
| GET | /api/v1/lorebook/{id} | Bearer + Admin | Lorebook entry detail |
| PUT | /api/v1/lorebook/{id} | Bearer + Admin | Update Lorebook entry |
| DELETE | /api/v1/lorebook/{id} | Bearer + Admin | Soft delete Lorebook entry (status → 'deleted') |

**Request body (create/update)**:
```json
{
  "title": "string (≤200 chars)",
  "content": "string (≤5000 chars, plain text)",
  "tags": ["string (≤50 chars each, ≤20 items)"],
  "priority": 0
}
```

**Response (list item)**:
```json
{
  "id": "uuid",
  "title": "string",
  "tags": ["string"],
  "priority": 0,
  "status": "active",
  "updated_at": "2026-07-31T00:00:00Z"
}
```

**Error codes**:
- 400: title/content/tags validation failed
- 403: non-admin user
- 404: entry not found

#### Scene Config Management (Admin only)

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | /api/v1/scene-configs | Bearer + Admin | List scene configs (supports `?script_id=&route_id=` filter) |
| PUT | /api/v1/scene-configs/node/{node_id} | Bearer + Admin | Create or update scene config for a Node |
| DELETE | /api/v1/scene-configs/node/{node_id} | Bearer + Admin | Delete scene config for a Node |

**Request body (PUT)**:
```json
{
  "scene_name": "string (≤200 chars)",
  "tags": ["string (≤50 chars each, ≤20 items)"],
  "description": "string (optional)"
}
```

**Response (list item)**:
```json
{
  "id": "uuid",
  "node_id": "uuid",
  "scene_name": "string",
  "tags": ["string"],
  "description": "string",
  "created_at": "2026-07-31T00:00:00Z",
  "updated_at": "2026-07-31T00:00:00Z"
}
```

**Error codes**:
- 400: validation failed
- 403: non-admin user
- 404: node not found

#### Character Extension

**Extended endpoint**: `PUT /api/v1/characters/{id}` (existing, now accepts new optional fields)

**New optional fields in request body**:
```json
{
  "desire": "string (TEXT, nullable) — 内在渴望",
  "fear": "string (TEXT, nullable) — 深层恐惧",
  "secret": "string (TEXT, nullable) — 隐藏秘密"
}
```

Backward compatible: omitting these fields does not update them.

---

## CR-028 Additions: Character Playable / Multi-Route

### Extended Endpoint: GET /api/v1/scripts/{id}

Response adds `playable_characters` array:

```json
{
  "playable_characters": [
    {
      "id": "uuid",
      "name": "爱丽丝",
      "avatar_url": "/assets/alice.png",
      "play_description": "你是爱丽丝...",
      "unlock_type": "free",
      "unlock_price": null,
      "is_unlocked": true
    }
  ]
}
```

Filter: only characters with `playable=true` AND `playable_route_id IS NOT NULL`.

is_unlocked logic:
- `unlock_type='free'` → always true
- `unlock_type='paid'` → check user_character_unlocks table
- `unlock_type='subscription'` → check user subscription_tier
- Unauthenticated → free=true, others=false

### Extended Endpoint: POST /api/v1/game/start

Request body adds optional field:
```json
{
  "script_id": "uuid",
  "character_id": "uuid"  // optional, backward compatible
}
```

When character_id is provided:
- Validate character playable=true
- Use character's playable_route_id as session route_id
- Write character_id and character_name (snapshot)

When character_id is NULL: use default route (existing logic).

### Extended Endpoint: GET /api/v1/saves

Response adds per-record fields: `character_id`, `character_name`.
New query parameter: `character_id` (UUID, optional) for filtering.

character_name returns "默认角色" when NULL.

### New Endpoint: POST /api/v1/characters/{character_id}/unlock

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | /api/v1/characters/{character_id}/unlock | Bearer | Unlock paid character (no payment this phase) |

Response: `{"success": true, "message": "角色解锁成功"}`

Idempotent: repeated calls return 200 without duplicate records.

Error codes:
- 400 CHARACTER_NOT_PAID: free character doesn't need unlock
- 401 AUTH_TOKEN_EXPIRED: not authenticated
- 404 CHARACTER_NOT_FOUND: character not found

### CR-028 New Error Codes

| Error Code | HTTP Status | Meaning |
|------------|-------------|----------|
| CHARACTER_NOT_PLAYABLE | 400 | Character not playable (playable=false or playable_route_id=NULL) |
| CHARACTER_NOT_PAID | 400 | Free character doesn't need unlock |

### CR-028 API / Data / Mock / Runtime Relationships

| Concern | Contract Doc | Runtime Binding |
|---------|-------------|------------------|
| API contract (CR-028) | `docs/api/api.md` (this file, 61 endpoints) | `/api/v1` on `:8000` |
| Database contract (CR-028) | `docs/database/database.md` | PostgreSQL `:5432`; new table: `user_character_unlocks`; extended: `characters`, `game_sessions` |
| Mock policy (CR-028) | **no mock API for Delivery E2E or Release evidence** | `docs/runtime/runtime-contract.md` |
| Runtime contract | `docs/runtime/runtime-contract.md` | Vite dev proxy, Nginx prod proxy |

---

### CR-027 API / Data / Mock / Runtime Relationships

| Concern | Contract Doc | Runtime Binding |
|---------|-------------|------------------|
| API contract (CR-027 new endpoints) | `docs/api/api.md` (this file, 58 endpoints) | `/api/v1` on `:8000` |
| Database contract (CR-027 new tables) | `docs/database/database.md` | PostgreSQL `:5432`; new tables: `lorebook_entries`, `scene_configs`; extended: `characters` |
| Mock policy (CR-027) | **no mock API for Delivery E2E or Release evidence**; LLM Gateway mock allowed in dev/test | `docs/runtime/runtime-contract.md` |
| Runtime contract | `docs/runtime/runtime-contract.md` | Vite dev proxy, Nginx prod proxy |

---

## CR-029 Additions: Node Branch Character Filtering

### No New Endpoints

CR-029 does not add new API endpoints. It extends the behavior of existing endpoints:
- `GET /api/v1/game/{sessionId}/dialogue` — now filters nodes by `session.character_id`
- `POST /api/v1/game/{sessionId}/choice` — validates next node visibility for current character

### New Error Code

| Error Code | HTTP Status | Meaning |
|------------|-------------|----------|
| NARRATIVE_NODE_NOT_VISIBLE | 403 | Node not visible for current character (character_id mismatch) |

### CR-029 API / Data / Mock / Runtime Relationships

| Concern | Contract Doc | Runtime Binding |
|---------|-------------|------------------|
| API contract (CR-029 behavior extension) | `docs/api/api.md` (this file, 61 endpoints, 0 new) | `/api/v1` on `:8000` |
| Database contract (CR-029) | `docs/database/database.md` | PostgreSQL `:5432`; extended: `nodes.character_id` |
| Mock policy (CR-029) | **no mock API for Delivery E2E or Release evidence** | `docs/runtime/runtime-contract.md` |
| Runtime contract | `docs/runtime/runtime-contract.md` | Vite dev proxy, Nginx prod proxy |

---

## CR-030 Additions: Chapter Structure Refactor

### New Endpoint: GET /api/v1/scripts/{script_id}/chapters

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | /api/v1/scripts/{script_id}/chapters | Bearer | Script chapter list (CR-030) |

**Response**:
```json
{
  "chapters": [
    {
      "chapter_number": 1,
      "chapter_type": "encounter",
      "title": "相遇",
      "routes": [
        {
          "id": "uuid",
          "title": "第一章：月夜邂逅",
          "description": "..."
        }
      ]
    },
    {
      "chapter_number": 2,
      "chapter_type": "daily",
      "title": "日常",
      "routes": [...]
    }
  ]
}
```

**Logic**:
1. Query `routes` table where `script_id` matches and `chapter_number IS NOT NULL`
2. Group by `chapter_number` ascending
3. Each chapter contains all routes with that chapter_number
4. If script has no chapter data (old script), return empty array `[]`

**Error codes**:
- 404 `SCRIPT_NOT_FOUND`: script_id does not exist

### Extended Endpoint: GET /api/v1/game/{session_id}/status

Response adds chapter information fields:

```json
{
  "session_id": "uuid",
  "status": "active",
  "current_node_id": "uuid",
  "current_node": {...},
  "is_ended": false,
  "ending_type": null,
  "chapter_number": 2,
  "chapter_type": "daily",
  "chapter_title": "日常"
}
```

**New fields**:

| Field | Source | Old session behavior |
|-------|--------|---------------------|
| `chapter_number` | `routes.chapter_number` (via session.route_id → route) | `null` |
| `chapter_type` | `routes.chapter_type` (via session.route_id → route) | `null` |
| `chapter_title` | Mapped from chapter_type to Chinese name | `null` |

**chapter_title mapping**:

| chapter_type | chapter_title |
|--------------|---------------|
| `encounter` | `相遇` |
| `daily` | `日常` |
| `conflict` | `冲突` |
| `convergence` | `收束` |
| `null` | `null` |

**Backward compatibility**:
- Old session's route has no chapter_number/chapter_type → three fields return null
- Frontend detects null → fallback to display route.title (existing behavior)

### Extended Endpoint: GET /api/v1/game/{session_id}/dialogue

Response adds chapter information fields (same as game status):

```json
{
  "dialogue": "...",
  "chapter": "第一章：月夜邂逅",
  "chapter_id": "uuid",
  "chapter_number": 1,
  "chapter_type": "encounter",
  "chapter_title": "相遇"
}
```

**Logic**: Read from current route's chapter_number/chapter_type, consistent with game status.

### CR-030 Browser E2E User Actions

| Action | AC | Description |
|--------|----|----|
| 章节进度显示 | AC-CHAP-004 | 进入游戏界面→查看进度条→显示"第X章：章节名" |
| 章节切换更新 | AC-CHAP-004 | 从第1章推进到第2章→进度条文本实时更新为"第2章：日常" |

### CR-030 API / Data / Mock / Runtime Relationships

| Concern | Contract Doc | Runtime Binding |
|---------|-------------|------------------|
| API contract (CR-030) | `docs/api/api.md` (this file, 62 endpoints, 1 new + 2 extended) | `/api/v1` on `:8000` |
| Database contract (CR-030) | `docs/database/database.md` | PostgreSQL `:5432`; extended: `routes.chapter_number`, `routes.chapter_type` |
| Mock policy (CR-030) | **no mock API for Delivery E2E or Release evidence** | `docs/runtime/runtime-contract.md` |
| Runtime contract | `docs/runtime/runtime-contract.md` | Vite dev proxy, Nginx prod proxy |

### CR-037 Additions: Corvus-Story-Core 集成

#### New API Endpoints (4 new, total 66)

| Method | Path | Auth | AC | Purpose |
|---|---|---|---|---|
| POST | /api/v1/game/session/create | Bearer | AC-006 | 创建剧本会话 (返回 game_session_id UUID v4, status=waiting_select_player) |
| GET | /api/v1/game/player/candidates | Bearer | AC-005 | 获取候选角色 (最多 3 个, 含 name/personality/backstory/appearance/initial_inventory) |
| POST | /api/v1/game/session/select-player | Bearer | AC-007 | 选定角色 + 调 Corvus POST /api/games 创建游戏, 返回初始场景 |
| POST | /api/v1/game/game-turn | Bearer | (备用) | 游戏回合同步版 (供 API 调用, 非 SSE) |

#### Extended API: Feature Flag (4 existing endpoints)

| Endpoint | CR-037 Behavior Change |
|----------|------------------------|
| `POST /api/v1/game/start` | 新增可选 engine_type 参数; engine_type=corvus 时创建 corvus_game_sessions 记录 |
| `GET /api/v1/game/{id}/dialogue` | engine_type=corvus 时调 CorvusClient.get_game() 映射为 DialogueResponse |
| `POST /api/v1/game/{id}/custom-input` | engine_type=corvus 时返回 SSE 流式响应 (Content-Type: text/event-stream) |
| `POST /api/v1/game/{id}/choice` | engine_type=corvus 时返回 SSE 流式响应 (choice_text 作为 user input) |

#### SSE Event Mapping (Corvus → Frontend)

| Corvus SSE Event | Backend Translation | Frontend Handler |
|---|---|---|
| `assistant-delta` `{"delta":"你"}` | `{"type":"text","content":"你"}` | StoryPanel 逐字渲染 |
| `assistant-complete` `{"message":{...}}` | `{"type":"done","text":"完整文本","character_id":"uuid-v4","character_name":"白夜","node_id":"uuid-v4"}` | 更新 currentDialogue |
| `gm-complete`/`state-changed` `{"affinity_delta":5,...}` | `{"type":"gm_update","affinity_delta":5,"inventory_changes":[...],"story_flags":[...]}` | 好感度/道具/标记 UI 更新 |
| `done` `{}` | `{"type":"stream_end"}` | 关闭 SSE 连接 |
| `error` `{"message":"..."}` | `{"type":"error","message":"..."}` | 显示错误提示 |

#### CR-037 API / Data / Mock / Runtime Relationships

| Concern | Contract Doc | Runtime Binding |
|---------|-------------|------------------|
| API contract (CR-037) | `docs/api/api.md` (this file, 4 new + 4 extended + SSE mapping) | `/api/v1` on `:8000`; SSE on `/api/v1/game/{id}/custom-input` |
| Database contract (CR-037) | `docs/database/database.md` | PostgreSQL `:5432` + pgvector 512维; 5 new tables; character_memories embedding 1536→512 |
| Mock policy (CR-037) | **no mock API for Delivery E2E or Release evidence**; unit tests may mock CorvusClient/EmbeddingService | `docs/runtime/runtime-contract.md` |
| Runtime contract (CR-037) | `docs/runtime/runtime-contract.md` | Corvus `127.0.0.1:8082` (systemd, 公网 DROP); SSE proxy_buffering off |
| Corvus internal API | `docs/corvus-integration/execution-plan.md` (v3, 真实 API) | Corvus `127.0.0.1:8082`; POST /api/games, POST /api/games/:id/messages (SSE), GET/PATCH /api/games/:id/characters/:npcId |
