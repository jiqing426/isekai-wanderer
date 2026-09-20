# API Design — Isekai Wanderer

## Overview

All API endpoints are served from the FastAPI backend under the base path `/api/v1`. Authentication uses JWT Bearer tokens. Real-time dialogue streaming uses Server-Sent Events (SSE).

---

## API Endpoint Table (67 endpoints)

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
| `gm-complete`/`state-changed` `{"affinity_delta":5,...}` | `{"type":"gm_update","affinity_delta":5,"inventory_changes":[...],"story_flags":[...],"choices":[{"id":"0","text":"...","hint":"..."}]}` | 好感度/道具/标记 UI 更新 + ChoicePanel 选项渲染 (CR-039: playerOptions → choices 映射) |
| `done` `{}` | `{"type":"stream_end"}` | 关闭 SSE 连接 |
| `error` `{"message":"..."}` | `{"type":"error","message":"..."}` | 显示错误提示 |

#### CR-039 SSE Event Extension: playerOptions

`gm_update` 事件增加 `choices` 字段（来源：Corvus `playerOptions`）：

| Corvus Field | Backend Mapping | Frontend Field | Description |
|---|---|---|---|
| `playerOptions[].text` | `choices[].text` | `pendingChoices[].text` | 选项文字 |
| `playerOptions[].hint` | `choices[].hint` (default `""`) | `pendingChoices[].hint` | 简短提示 |
| (generated) | `choices[].id` = index string | `pendingChoices[].id` | 序号 ID |
| `playerOptions` absent/empty | `choices` = `[]` | `pendingChoices` = `[]` | fallback: 纯自由输入 |

No new API endpoints. No new DB tables. `playerOptions` is LLM-generated runtime data, not persisted.

#### CR-039 API / Data / Mock / Runtime Relationships

| Concern | Contract Doc | Runtime Binding |
|---------|-------------|------------------|
| API contract (CR-039) | `docs/api/api.md` (this file, SSE event extension) | No new endpoints; SSE on `/api/v1/game/{id}/custom-input` |
| Database contract (CR-039) | `docs/database/database.md` — Not Required | No DB changes; playerOptions not persisted |
| Mock policy (CR-039) | no mock API for Delivery E2E or Release evidence | `docs/runtime/runtime-contract.md` |
| Runtime contract (CR-039) | `docs/runtime/runtime-contract.md` | No new ports/proxy; CR-039 additions appended |

#### CR-037 API / Data / Mock / Runtime Relationships

| Concern | Contract Doc | Runtime Binding |
|---------|-------------|------------------|
| API contract (CR-037) | `docs/api/api.md` (this file, 4 new + 4 extended + SSE mapping) | `/api/v1` on `:8000`; SSE on `/api/v1/game/{id}/custom-input` |
| Database contract (CR-037) | `docs/database/database.md` | PostgreSQL `:5432` + pgvector 512维; 5 new tables; character_memories embedding 1536→512 |
| Mock policy (CR-037) | **no mock API for Delivery E2E or Release evidence**; unit tests may mock CorvusClient/EmbeddingService | `docs/runtime/runtime-contract.md` |
| Runtime contract (CR-037) | `docs/runtime/runtime-contract.md` | Corvus `127.0.0.1:8082` (systemd, 公网 DROP); SSE proxy_buffering off |
| Corvus internal API | `docs/corvus-integration/execution-plan.md` (v3, 真实 API) | Corvus `127.0.0.1:8082`; POST /api/games, POST /api/games/:id/messages (SSE), GET/PATCH /api/games/:id/characters/:npcId |

---

## CR-038 Additions: Corvus Frontend Entry

### New API Endpoint (1 new, total 67)

| Method | Path | Auth | AC | Purpose |
|---|---|---|---|---|
| POST | /api/v1/game/player/candidates | Bearer | AC-038-003~006 | 创建角色候选 (name 必填, ≤3 限制) |

**Request body (POST /game/player/candidates)**:
```json
{
  "name": "string (≤100, required)",
  "personality": "string (optional)",
  "backstory": "string (optional)",
  "appearance": "string (optional)"
}
```

**Response (create success)**:
```json
{
  "code": 0,
  "data": {
    "id": "uuid-v4",
    "name": "星野",
    "personality": null,
    "backstory": null,
    "appearance": null,
    "initial_inventory": []
  }
}
```

**Error codes**:
- 400 VALIDATION_ERROR: name 缺失或超长
- 400 CANDIDATE_LIMIT_EXCEEDED: 用户已有 3 个候选角色
- 401 AUTH_TOKEN_EXPIRED: 未认证

### Extended API: GET /scripts and GET /scripts/{id}

| Endpoint | CR-038 Behavior Change |
|----------|------------------------|
| `GET /api/v1/scripts` | 每个 script 对象返回 `engine_type: 'corvus'` 字段 (运行时虚拟字段, 不持久化到 DB) |
| `GET /api/v1/scripts/{script_id}` | script 对象返回 `engine_type: 'corvus'` 字段 |

**实现方式**: 在 `scripts.py` 的返回逻辑中硬编码 `engine_type: 'corvus'`（C3 约束下所有剧本统一为 Corvus）。不修改 `scripts` 表结构。

### Extended API: Frontend Script Interface

前端 `Script` interface 新增 `engine_type: 'legacy' | 'corvus'` 必填字段（C1/C2 约束）。
前端 `GameSession` interface 的 `engine_type` 从可选 `?` 改为必填（C2 约束）。

### CR-038 API / Data / Mock / Runtime Relationships

| Concern | Contract Doc | Runtime Binding |
|---------|-------------|------------------|
| API contract (CR-038) | `docs/api/api.md` (this file, 1 new + 2 extended) | `/api/v1` on `:8000` |
| Database contract (CR-038) | `docs/database/database.md` | Not Required: 无新增表或列变更。player_candidates 表已在 CR-037 创建。engine_type 为运行时虚拟字段 |
| Mock policy (CR-038) | **no mock API for Delivery E2E or Release evidence**; unit tests may mock CorvusClient | `docs/runtime/runtime-contract.md` |
| Runtime contract (CR-038) | `docs/runtime/runtime-contract.md` | CR-038 Additions: browser_e2e_command 扩展 cr038 测试文件 |

---

## CR-042 Additions: Legacy SSE 流式改造

### New API Endpoint (1 new, total 68)

| Method | Path | Auth | AC | Purpose |
|---|---|---|---|---|
| POST | /api/v1/game/{session_id}/free-chat/stream | Bearer | AC-011, AC-013, AC-014 | 自由对话 SSE 流式端点（新增）；旧端点 POST /game/{id}/free-chat 保留兼容（deprecated） |

**请求体**:
```json
{"message": "string", "topic_id": "string|null"}
```

**响应**: `text/event-stream`，SSE 事件格式见下方。

**响应头**:
| Header | Value |
|-------|-------|
| Content-Type | text/event-stream |
| Cache-Control | no-cache |
| Connection | keep-alive |
| X-Accel-Buffering | no |

### Modified API: Legacy Branch SSE (2 endpoints modified)

| Endpoint | CR-042 Behavior Change |
|----------|------------------------|
| `POST /api/v1/game/{id}/choice` | Legacy 分支：推进节点后检查 next_node.node_type；transition/ai_dialog → 返回 `text/event-stream` SSE；preset/choice → 保持 JSON 响应（不变） |
| `POST /api/v1/game/{id}/custom-input` | Legacy 分支：改为 `text/event-stream` SSE 流式响应（使用 llm_gateway.stream_dialogue() 替代同步 _generate_custom_response()） |

注意：Corvus 分支行为不变。

### Deprecated API

| Method | Path | Status | Note |
|---|---|---|---|
| POST | /api/v1/game/{session_id}/free-chat | Deprecated | CR-042 标记废弃；保留同步 JSON 行为不变；响应头追加 `Deprecation: true`；新端点 `/free-chat/stream` 替代 |

### CR-042 SSE Event Format (Legacy paths)

Legacy SSE 流式端点使用与 Corvus 路径一致的 SSE 事件格式，但不使用 `gm_update` 事件（Legacy 无 GM 循环）。元数据通过 `done` 事件一次性推送：

```
data: {"type":"text","content":"..."}\n\n          ← 逐字/token 推送
data: {"type":"emotion","emotion":"happy","character_id":"..."}\n\n  ← 情绪标签（可选，在 text 之前）
data: {"type":"affection_update","character_id":"...","value":45,"level":"trust"}\n\n  ← 好感度更新（可选）
data: {"type":"done","session_id":"...","node_id":"...","affection_change":{...},"choices":[...]}\n\n  ← 流结束 + 元数据
data: {"type":"error","message":"..."}\n\n           ← 错误事件
```

### CR-042 DB Write Timing

SSE 流期间不执行 `db.commit()`。流结束后在 `finally` 块中通过 `asyncio.create_task()` 异步执行 deferred DB 写入：
- 对话历史写入 `DialogueHistory` 表
- 好感度更新写入 `Affection` 表
- 成就检查和写入
- 收敛检查
Deferred task 使用 `async_session_factory()` 创建独立 DB session，不阻塞 SSE 流。

### CR-042 model_router.stream_with_fallback()

新增方法 `stream_with_fallback(scenario, messages, **kwargs) -> AsyncGenerator[str, None]`：
1. 主模型 `stream_complete()` → 逐 token yield
2. 主模型失败 → 切换 fallback 链下一个模型
3. 所有模型失败 → 一次性 yield 场景特定友好提示文本（非流式 fallback）

Fallback 文本（Q-003 确认）：
- FREE_CHAT: "（微微侧头，轻轻笑了笑）抱歉，我刚才走神了……你说的真有意思，能再和我说说吗？"
- NARRATIVE: "（故事在这一刻仿佛停滞了片刻，随后又缓缓流淌……）"
- 默认: "抱歉，暂时无法回应，请稍后再试。"

### CR-042 Frontend Composable

新增 `composables/useSSEStream.ts`，封装 `fetch` + `ReadableStream` reader + SSE 事件解析。三条 Legacy 路径和 Corvus 路径均使用该 composable。

接口：
```typescript
function useSSEStream(options: SSEStreamOptions, callbacks: SSEStreamCallbacks): SSEStreamResult
```

Callbacks: `onText`, `onDone`, `onError`, `onEmotion`, `onAffectionUpdate`, `onGmUpdate`（Corvus 路径使用）

### CR-042 API / Data / Mock / Runtime Relationships

| Concern | Contract Doc | Runtime Binding |
|---------|-------------|------------------|
| API contract (CR-042) | `docs/api/api.md` (this file, 1 new + 2 modified + 1 deprecated) | `/api/v1` on `:8000`; SSE on `/api/v1/game/{id}/choice` (Legacy), `/api/v1/game/{id}/custom-input` (Legacy), `/api/v1/game/{id}/free-chat/stream` |
| Database contract (CR-042) | `docs/database/database.md` — Not Required | No DB changes; deferred writes reuse existing DialogueHistory, Affection, FreeChatSession tables |
| Mock policy (CR-042) | **no mock API for Delivery E2E or Release evidence**; unit tests may mock LLM Gateway / Provider stream | `docs/runtime/runtime-contract.md` |
| Runtime contract (CR-042) | `docs/runtime/runtime-contract.md` | No new ports/proxy; CR-042 additions appended |

---

## CR-043 Additions: 订阅权益区分与 CG 画廊权限控制

### Extended API: Gallery / Scripts / Game / Settings

CR-043 不新增 API 端点，扩展现有端点行为：

| Endpoint | CR-043 Behavior Change |
|----------|------------------------|
| `GET /api/v1/gallery/collections/{script_id}` | 每个 CG 项新增 `is_accessible: boolean` 字段，基于用户 tier + CG 解锁状态计算 |
| `GET /api/v1/scripts` | 每个剧本项新增 `is_accessible: boolean` 字段（已认证用户）；未认证用户不返回该字段 |
| `GET /api/v1/scripts/{script_id}` | 剧本对象新增 `is_accessible: boolean` 字段 |
| `POST /api/v1/game/start` | 创建 GameSession 前检查 `script_access`，权限不足返回 403 `SCRIPT_ACCESS_DENIED` |
| `GET /api/v1/users/me/member-info` | `tier` 从 `SubscriptionService.get_user_tier()` 获取；`status`/`expires_at` 从 Subscription 表获取 |

### is_accessible 字段契约

**Gallery API** (`GET /api/v1/gallery/collections/{script_id}`)：
```json
{
  "items": [{
    "id": "uuid",
    "is_accessible": true,
    "unlock_status": "unlocked"
  }]
}
```

计算逻辑：`is_accessible = is_unlocked OR tier in ('standard', 'premium')`

**Scripts API** (`GET /api/v1/scripts`, `GET /api/v1/scripts/{id}`)：
```json
{
  "scripts": [{
    "id": "uuid",
    "is_accessible": true
  }]
}
```

计算逻辑（运行时虚拟判定，见 ADR-043-02）：
- `trial_only` (free): `genre == 'romance' AND hot_value >= 50`
- `all_normal` (basic/standard): 所有剧本
- `all_including_exclusive` (premium): 所有剧本

### New Error Code

| Error Code | HTTP Status | Meaning |
|---|---|---|
| SCRIPT_ACCESS_DENIED | 403 | 订阅等级不足以游玩此剧本 |

### member-info 数据源修复

`get_member_info()` 修复前后的数据源对比：

| 字段 | 修复前（数据源） | 修复后（数据源） |
|---|---|---|
| `tier` | `User.subscription_tier` | `SubscriptionService.get_user_tier()` |
| `status` | `User.trial_started_at` / `trial_ends_at` | `SubscriptionService.get_user_subscription().status` |
| `expires_at` | `User.trial_ends_at` | `SubscriptionService.get_user_subscription().expires_at` |

修复后 `member-info` 和 `subscription/status` 两个 API 的 `tier` 值一致，都基于 `SubscriptionService.get_user_tier()`。

### CR-043 API / Data / Mock / Runtime Relationships

| Concern | Contract Doc | Runtime Binding |
|---------|-------------|------------------|
| API contract (CR-043) | `docs/api/api.md` (this file, 0 new + 5 extended) | `/api/v1` on `:8000` |
| Database contract (CR-043) | `docs/database/database.md` — Not Required | 无 DB 表结构变更；is_accessible 为运行时计算字段 |
| Mock policy (CR-043) | **no mock API for Delivery E2E or Release evidence** | `docs/runtime/runtime-contract.md` |
| Runtime contract (CR-043) | `docs/runtime/runtime-contract.md` | No new ports/proxy; CR-043 additions appended |
