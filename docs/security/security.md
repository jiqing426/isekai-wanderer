# Security Design — Isekai Wanderer

## Overview

Security is enforced at multiple layers: transport (HTTPS/TLS), authentication (JWT), authorization (Bearer middleware), input validation (Pydantic + ORM parameterization), and rate limiting (Redis sliding window).

---

## Authentication & Authorization

| Scenario | Scheme |
|----------|--------|
| User authentication | JWT (Access Token 15 min + Refresh Token 7 days) |
| Password storage | bcrypt (cost factor 12) |
| OAuth mock | Abstract `IOAuthProvider` interface; mock implementation returns fixed user |
| API authorization | Bearer Token middleware on all protected endpoints |
| Rate limiting | Redis sliding window: general API 60 req/min, LLM calls 10 req/min |
| Brute force protection | Login locked for 15 minutes after 5 failed attempts (Redis counter) |

---

## Sensitive Data Handling

| Data | Storage | Transport | Logging |
|------|---------|-----------|---------|
| Passwords | bcrypt hash | HTTPS only | Never logged |
| JWT tokens | In-memory / cookie | HTTPS only | Never logged |
| Email | Plaintext (queryable) | HTTPS only | Masked |
| Dialogue records | Plaintext storage | HTTPS only | Masked |
| Memory vectors | Vector storage | Internal calls only | Never logged |
| Mock payment data | Plaintext with mock flag | HTTPS only | Log mock flag only |

---

## Security Constraints

| Constraint | Implementation |
|------------|----------------|
| **HTTPS** | All API traffic over HTTPS; Nginx SSL termination in production |
| **CORS** | Whitelist only: frontend origin (`http://localhost:3000` dev, production domain prod) |
| **SQL Injection** | SQLAlchemy ORM parameterized queries; no raw SQL string concatenation |
| **XSS** | Vue default template escaping + Content-Security-Policy (CSP) headers |
| **CSRF** | JWT mode does not require CSRF tokens (no cookie-based auth) |
| **Brute Force** | Login: 5 failed attempts → 15-minute lockout (Redis counter) |
| **Input Validation** | Pydantic schemas on all request bodies; FastAPI auto-validation (422 on failure) |
| **Dependency Security** | Pinned versions in `pyproject.toml`; regular `pip-audit` scans |

---

## Token Lifecycle

1. User registers → email verification token (expires 24h)
2. User logs in → Access Token (15 min) + Refresh Token (7 days)
3. Access Token expires → client calls `/auth/refresh` with Refresh Token → new Access Token issued
4. Refresh Token expires → user must re-login
5. Password reset → reset token (expires 1h), single-use, invalidated after use (CR-002 AC-047: implemented)

---

## OAuth Mock Architecture

```txt
Frontend "Login with Google" button
    │
    ▼
GET /api/v1/auth/oauth/google
    │
    ▼
IOAuthProvider.authenticate()
    │ (mock: returns deterministic test user)
    │ (real: redirects to Google OAuth consent)
    │
    ▼
GET /api/v1/auth/oauth/google/callback?code=xxx
    │
    ▼
IOAuthProvider.get_user_info()
    │
    ▼
Create or link user account → Issue JWT pair
```

The `IOAuthProvider` abstraction ensures mock and real OAuth providers share the same contract, enabling seamless transition from mock to production without business code changes.

---

## CR-002 Security Additions

### Password Reset Security (AC-047)

| Risk | Mitigation |
|---|---|
| Email enumeration | forgot-password returns 200 for non-existent emails |
| Token brute force | `secrets.token_urlsafe(32)` (256-bit entropy) |
| Token reuse | Single-use: `used=TRUE` after first use |
| Token expiry | 1 hour TTL, rejected after expiry |
| Rate limiting | 3 requests/hour/email (Redis counter) |
| Password strength | Pydantic validation: min 8 chars + digit + letter |

### Free Chat Security (AC-058)

| Risk | Mitigation |
|---|---|
| Prompt injection | User input separated from system prompt |
| LLM output unpredictability | RuleEngine validation + max length + emotion tag format |
| Data privacy | Stored in DB, accessible only by owning user |

### Mock Service Security (AC-055/AC-057)

- Mock services do not send real HTTP requests (no external attack surface)
- Webhook URLs stored in DB, not exposed to frontend
- Log files contain no sensitive user data (emails masked)
- Recall cron runs internally, no public API exposure

### CR-027 Security (Lorebook / SceneConfig / NPC Extension)

| Risk | Mitigation |
|------|------------|
| Non-admin accessing admin APIs | All Lorebook/SceneConfig endpoints require `users.is_admin=True`; 403 for non-admin |
| Lorebook content XSS | Input validation: content ≤5000 chars, `<script>` tag rejection; frontend renders with template escaping |
| Tag injection | Tags array validated: ≤20 items, each ≤50 chars |
| NPC secret field exposure | `desire/fear/secret` only readable/writable via Admin API; never exposed in player-facing endpoints |
| Soft delete bypass | Lorebook DELETE sets `status='deleted'`; all queries filter `status='active'` |

### CR-028 Security (Character Playable / Multi-Route)

| Risk | Mitigation |
|------|------------|
| Unauthorized character unlock | POST /characters/{id}/unlock requires Bearer token; 401 for unauthenticated |
| Unlock free characters | Server validates unlock_type='paid'; returns 400 for free characters |
| Idempotency abuse | UNIQUE(user_id, character_id) constraint prevents duplicate unlock records |
| Playable character spoofing | Server validates character.playable=true before creating GameSession; returns 400 CHARACTER_NOT_PLAYABLE |
| unlock_price manipulation | Price stored server-side in characters table; not accepted from client input |
| SQL injection in migration | Alembic uses parameterized DDL; no raw string concatenation |
| user_character_unlocks data leak | Table only accessible by owning user via API; no bulk enumeration endpoint |

### CR-029 Security (Node Branch Character Filtering)

| Risk | Mitigation |
|------|------------|
| Cross-character node access | Backend filters nodes by `session.character_id`; 403 `NARRATIVE_NODE_NOT_VISIBLE` on mismatch |
| Direct node ID enumeration | `get_node_with_choices` applies character filter; even knowing node ID doesn't bypass visibility |
| Old session privilege escalation | `session.character_id=NULL` → only public nodes visible; no branch access |
| FK integrity | `nodes.character_id` references `characters(id)`; DB-level constraint prevents orphan references |
| Migration safety | `IF NOT EXISTS` / `IF EXISTS` idempotent DDL; no data loss on re-run |

---

## Production Security Checklist

- [ ] Nginx SSL termination with modern cipher suite
- [ ] CORS whitelist restricted to production frontend domain
- [ ] Rate limiting active on all public endpoints
- [ ] Brute force lockout active on login endpoint
- [ ] No sensitive data in application logs
- [ ] Database credentials via environment variables (not hardcoded)
- [ ] Redis AUTH enabled (if exposed beyond localhost)
- [ ] Docker secrets or equivalent for production credentials
- [ ] Regular dependency vulnerability scanning (`pip-audit`, `npm audit`)

---

## CR-037 Additions: Corvus-Story-Core 集成

### Corvus 服务安全隔离

| 约束 | 实现 |
|------|------|
| Corvus 仅本机访问 | systemd 服务绑定 127.0.0.1:8082；iptables 8082 公网 DROP |
| 前端不可直接请求 Corvus | 前端只通过后端 SSE 代理访问；Corvus 8082 不在 Nginx/Vite proxy 中暴露 |
| LLM API-Key 不经后端 | Corvus config.json 自行管理 thoushub 网关 API-Key；后端不存储、不转发 |
| Corvus 内部数据不可枚举 | Corvus API 仅通过后端 CorvusClient 调用，不对外暴露 |

### 向量记忆数据隔离

| 约束 | 实现 |
|------|------|
| 跨用户记忆隔离 | pgvector KNN 查询 WHERE user_id = ? 隔离；不同用户记忆不可互相检索 |
| 跨角色记忆隔离 | pgvector KNN 查询 WHERE character_id = ? 隔离；不同角色记忆不可互相检索 |
| NPC knownInfo 恢复 | 回合结束后恢复 NPC knownInfo 原始值，防止记忆注入污染后续会话 |
| embedding 数据不泄露 | embedding 向量仅用于 KNN 计算，不通过 API 返回给前端 |

### CR-037 安全检查清单

- [x] Corvus systemd 服务仅绑定 127.0.0.1:8082
- [x] iptables 规则：8082 公网 DROP
- [x] Corvus LLM API-Key 存储在 Corvus config.json，不经后端
- [x] 向量记忆 KNN 查询按 user_id + character_id 隔离
- [x] NPC knownInfo 注入/恢复加锁 (asyncio.Lock)
- [x] embedding 向量不通过 API 返回前端
