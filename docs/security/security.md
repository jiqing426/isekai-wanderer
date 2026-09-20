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

---

## CR-038 Additions: Corvus Frontend Entry

### 角色候选创建安全

| Risk | Mitigation |
|------|------------|
| 角色候选创建无数量限制 | 后端校验每用户 ≤3 个候选，超限返回 400 CANDIDATE_LIMIT_EXCEEDED |
| name 字段注入 | 后端 Pydantic 校验 name: str, max_length=100, required; 前端表单校验 name 非空 |
| 角色候选 XSS | 候选 name/personality/backstory/appearance 存入 DB，前端使用 Vue 模板转义渲染 ({{ }}) 防止 XSS |
| 角色候选数据泄露 | GET /game/player/candidates 需 Bearer 认证，只返回当前用户的候选；无批量枚举端点 |
| POST /game/player/candidates 未认证 | 后端 Bearer Token middleware 校验，401 for unauthenticated |

### localStorage 旧数据兼容安全

| Risk | Mitigation |
|------|------------|
| 旧会话数据无 engine_type | 旧数据默认视为 'legacy'，走 legacy 分支，不影响 Corvus 流程安全 |
| 会话恢复后 engine_type 篡改 | engine_type 从后端 GET /game/{id} 获取或从 localStorage 恢复；不在前端请求中接受外部 engine_type 参数 |

### CR-038 安全检查清单

- [x] POST /game/player/candidates 端点有 Bearer 认证
- [x] 角色候选创建有 ≤3 数量限制
- [x] name 字段有 Pydantic 必填 + 长度校验
- [x] 前端表单 name 为空时不发送 API 请求
- [x] 前端 Vue 模板转义渲染候选字段（防 XSS）
- [x] localStorage 旧数据兼容不影响 Corvus 流程安全
- [x] engine_type 后端硬编码，不接受前端参数（CR-038 安全审查补充）
- [x] SSE 错误事件通用化，不泄露内部细节（CR-038 安全审查补充）
- [x] 会话恢复 engine_type 从后端 API 读取，不可篡改（CR-038 安全审查补充）
- [x] GET /scripts engine_type 为运行时虚拟字段，不持久化（CR-038 安全审查补充）

---

## CR-039 Additions: Corvus 玩家选项功能

### SSE 事件标记过滤安全

| Risk | Mitigation |
|------|------------|
| SSE 事件 [Narrator]/[Character] 标记泄露到前端 | SSETranslator token 级前缀缓冲过滤 + done 级正则双重清理; _MAX_MARKER_LEN 防缓冲溢出 |
| playerOptions → choices 映射注入 | id 服务端生成 (数组索引 str(i)); 字段 get 默认值; isinstance(opt, dict) 类型校验 |
| GM prompt playerOptions 字段注入 | GM 输出限制为 JSON-only; parseGameMasterOutput lenient 解析 fallback 空数组; playerOptions 不持久化 |

### /game/status 越权防护

| Risk | Mitigation |
|------|------------|
| 会话枚举/越权访问 | Bearer Token 认证 + WHERE user_id 所有权校验 (Corvus + Legacy 双路径) |
| character_id 篡改 | character_id 从 CorvusGameSession DB 记录读取, 不从请求参数接受 |

### CR-039 安全检查清单

- [x] SSETranslator 双重过滤 [Narrator]/[Character] 标记
- [x] playerOptions → choices 映射有类型校验和默认值
- [x] GM prompt 输出限制为 JSON-only
- [x] /game/{session_id}/status 有 Bearer Token + 所有权校验
- [x] character_id FK 约束 (DB ForeignKey + 应用层 playable=True 校验)
- [x] 无密钥/token 凭证泄露
- [x] 日志不记录敏感数据 (UUID 级别)
- [x] 发布证据 Mock API=no
- [ ] StoryPanel v-html 增加 DOMPurify (H-1 非阻塞建议, 后续迭代)

---

## CR-042 Additions: Legacy SSE 流式改造

### SSE 流式输出安全

| Risk | Mitigation |
|------|------------|
| SSE 流中敏感信息泄露 | Legacy SSE 仅输出 LLM 生成的对话文本和结构化元数据（好感度、选项）；不输出 token、API key、内部路径 |
| Deferred DB 写入竞争 | Deferred task 使用独立 `async_session_factory()` 创建新 DB session，不复用请求 session，避免连接池耗尽 |
| Fallback 文本注入 | `_get_stream_fallback_text()` 返回硬编码预设文本，不接受外部输入；不存在 prompt injection 风险 |
| 旧端点 deprecation header 信息泄露 | `Deprecation: true` 响应头不泄露后端架构信息，仅标记端点废弃状态 |
| SSE 流中鉴权 | 复用现有 Bearer Token 认证；SSE 流开始前验证 token；deferred DB 写入在信任的内部环境执行 |

### CR-042 安全检查清单

- [x] SSE 流式输出无新增鉴权需求（复用现有 Bearer Token）
- [x] Deferred DB 写入使用独立 session 不阻塞流
- [x] Fallback 文本为硬编码预设，不接受外部输入
- [x] 旧端点 deprecation header 不泄露后端架构信息
- [x] SSE 流中不输出敏感信息（token、API key、内部路径）
- [x] Legacy SSE 事件格式与 Corvus 一致，已有安全审查覆盖
- [x] 无新增权限边界（Legacy 路径已有所有权校验）
- [x] 无新增数据库表或字段（复用现有表）
- [x] 发布证据 Mock API=no

---

## CR-043 Additions: 订阅权益区分与 CG 画廊权限控制

### 权限边界变更安全（CEO 附条件 C3）

| Risk | Mitigation |
|------|------------|
| API 层面伪造 tier 绕过权限 | 后端通过 `SubscriptionService.get_user_tier(user_id)` 从服务端数据库获取用户 tier，不接受客户端请求中的 tier 参数 |
| Gallery API 权限绕过 | `GET /gallery/collections/{script_id}` 返回的 `is_accessible` 字段由后端基于服务端 tier 计算，前端不可篡改 |
| Game start API 权限绕过 | `POST /game/start` 在创建 GameSession 前检查 `script_access`，基于服务端 tier，不信任客户端任何 tier/script_access 字段 |
| Scripts API 权限绕过 | `GET /scripts` 和 `GET /scripts/{script_id}` 返回的 `is_accessible` 字段由后端计算 |
| 权限拒绝无审计 | 403 权限拒绝必须记录审计日志（user_id, script_id, tier, timestamp） |
| 前端硬编码权限映射 | 前端不得本地硬编码 tier→permissions 映射；权限判断以后端 API 返回的 `is_accessible` 为权威值 |
| member-info tier 数据不一致 | `get_member_info()` 的 `tier` 从 `SubscriptionService.get_user_tier()` 获取，与 `subscription/status` API 统一数据源 |

### CR-043 安全检查清单

- [ ] 后端 `get_user_tier()` 从服务端数据库读取，不接受客户端 tier 参数
- [ ] `POST /game/start` 在创建 GameSession 前检查 script_access
- [ ] Gallery API `is_accessible` 字段由后端计算
- [ ] Scripts API `is_accessible` 字段由后端计算
- [ ] 403 权限拒绝记录审计日志
- [ ] 前端不硬编码 tier→permissions 映射
- [ ] Security 阶段审查 API 层面绕过风险（CEO 附条件 C3）

---

## CR-043 Additions: 订阅权益区分与 CG 画廊权限控制

### 权限边界变更安全（CEO 附条件 C3）

| Risk | Mitigation |
|------|------------|
| API 层面伪造 tier 绕过权限 | 后端通过 `SubscriptionService.get_user_tier(user_id)` 从服务端数据库获取用户 tier，不接受客户端请求中的 tier 参数 |
| Gallery API 权限绕过 | `GET /gallery/collections/{script_id}` 返回的 `is_accessible` 字段由后端基于服务端 tier 计算，前端不可篡改 |
| Game start API 权限绕过 | `POST /game/start` 在创建 GameSession 前检查 `script_access`，基于服务端 tier，不信任客户端任何 tier/script_access 字段 |
| Scripts API 权限绕过 | `GET /scripts` 和 `GET /scripts/{script_id}` 返回的 `is_accessible` 字段由后端计算 |
| 权限拒绝无审计 | 403 权限拒绝必须记录审计日志（user_id, script_id, tier, timestamp） |
| 前端硬编码权限映射 | 前端不得本地硬编码 tier→permissions 映射；权限判断以后端 API 返回的 `is_accessible` 为权威值 |

### CR-043 安全检查清单

- [ ] 后端 `get_user_tier()` 从服务端数据库读取，不接受客户端 tier 参数
- [ ] `POST /game/start` 在创建 GameSession 前检查 script_access
- [ ] Gallery API `is_accessible` 字段由后端计算
- [ ] Scripts API `is_accessible` 字段由后端计算
- [ ] 403 权限拒绝记录审计日志
- [ ] 前端不硬编码 tier→permissions 映射
- [ ] Security 阶段审查 API 层面绕过风险（CEO 附条件 C3）
