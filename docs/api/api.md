# API Design — Isekai Wanderer

## Overview

All API endpoints are served from the FastAPI backend under the base path `/api/v1`. Authentication uses JWT Bearer tokens. Real-time dialogue streaming uses Server-Sent Events (SSE).

---

## API Endpoint Table (50 endpoints)

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
| API contract | `docs/api/api.md` (this file) | All endpoints served at `/api/v1` on `:8000` |
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
