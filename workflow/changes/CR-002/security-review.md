# Security Review — CR-002

> **Review Date**: 2026-07-22T18:00:00Z
> **Reviewer**: PL (coordinated with Security Agent)
> **Scope**: CR-002 Phase 1 (9 P1 features + 11 Bug fixes)

| 项 | 内容 |
|---|------|
| 审查结论 | passed — 无 P0/P1 安全风险。CR-002 Phase 1 安全审查通过，可进入 RELEASE_GATE。P2 风险记录在案，建议后续 CR 处理。 |

---

## 1. 认证与授权

| 检查项 | 状态 | 说明 |
|-------|------|------|
| Token 有效期合理 | 通过 | access 24h + refresh 30d |
| Token refresh 防循环 | 通过 | _isRetry flag + singleton promise guard |
| 密码重置 token 有效期 | 通过 | 1 小时过期，一次性使用 |
| 密码重置速率限制 | 通过 | forgot-password 有速率限制 |
| 公开接口无 auth 要求 | 通过 | /scripts, /subscription/plans 免登录 |
| 受保护接口需 Bearer | 通过 | 401 + AUTH_TOKEN_EXPIRED 错误码 |

## 2. 输入验证

| 检查项 | 状态 | 说明 |
|-------|------|------|
| API 请求参数验证 | 通过 | Pydantic schema 验证 |
| SQL 注入防护 | 通过 | SQLAlchemy ORM，无原始 SQL |
| XSS 防护 | 通过 | Vue 模板自动转义 |
| 邮箱格式验证 | 通过 | Pydantic EmailStr |

## 3. 数据存储

| 检查项 | 状态 | 说明 |
|-------|------|------|
| 密码哈希存储 | 通过 | bcrypt/passlib |
| 敏感数据不日志 | 通过 | MockEmailService 只写 JSONL 文件 |
| Token 不存数据库 | 通过 | 无状态 JWT |

## 4. Mock 服务安全

| 检查项 | 状态 | 说明 |
|-------|------|------|
| MockEmailService 无真实外部调用 | 通过 | 只写本地 JSONL |
| MockDiscordService 无真实外部调用 | 通过 | 只写本地 JSONL |
| MockLLMProvider 无真实外部调用 | 通过 | 关键词匹配本地响应 |

## 5. 已知风险（P2，不阻塞发布）

| # | 风险 | 级别 | 缓解 |
|---|------|------|------|
| 1 | datetime.utcnow deprecation | P2 | Python 3.12 废弃，建议后续 CR 修复 |
| 2 | forgot-password 无邮件枚举保护 | P2 | 始终返回 200，可被枚举邮箱是否存在 |
| 3 | Mock 服务生产替换 | P2 | 生产需替换为真实 SMTP/Discord/LLM |
