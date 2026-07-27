# CR-008 安全审查报告

**审查时间**: 2026-07-23T12:30:00Z (Asia/Shanghai)
**审查人**: Security Agent
**审查范围**: CR-008 全部变更（26 个后端 API、5 个表新增/扩展、前端页面优化）
**审查结论**: ⚠️ **有条件通过**（1 个 P2 缺陷 + 3 个安全增强建议）

---

## 1. 审查依据

| 文档 | 路径 |
|------|------|
| 安全设计 | `docs/security/security.md` |
| API 契约 | `docs/api/api.md` |
| 数据库契约 | `docs/database/database.md` |
| Runtime 契约 | `docs/runtime/runtime-contract.md` |
| 变更说明 | `workflow/changes/CR-008-post-refactor-optimization/change.md` |
| 测试报告 | `workflow/changes/CR-008-post-refactor-optimization/test-report.md` |
| 后端源码 | `backend/app/api/v1/users.py`, `settings.py`, `auth.py`, `core/security.py` |

---

## 2. 检查清单

### 2.1 密钥/Token/证书/密码泄露

| 检查项 | 结论 | 说明 |
|--------|------|------|
| 代码中是否硬编码密钥 | ✅ PASS | JWT_SECRET 通过 `settings.jwt_secret` 从环境变量读取 |
| 是否提交生产数据 | ✅ PASS | 测试使用 qa-fresh@isekai.dev 测试账号 |
| .env.example 是否安全 | ✅ PASS | 仅含占位符，无真实密钥 |
| 日志是否泄露敏感信息 | ✅ PASS | security.md 规定密码/token 永不记录 |

### 2.2 认证/授权

| 检查项 | 结论 | 说明 |
|--------|------|------|
| /users/me/* 全部需要 Bearer Token | ✅ PASS | 所有端点均使用 `Depends(get_current_user_id)` |
| JWT 验证逻辑 | ✅ PASS | `decode_token(token, expected_type="access")` 验证签名+过期+类型 |
| 用户隔离 | ✅ PASS | 所有查询均以 `user_id` (从 JWT 提取) 为条件，无 IDOR 风险 |
| /users/me/memory/full 会员限制 | ✅ PASS | 检查 `subscription_tier in ["standard", "premium"]`，free 用户返回 403 |

### 2.3 输入校验

| 检查项 | 结论 | 说明 |
|--------|------|------|
| PATCH /users/me | ✅ PASS | Pydantic: display_name 2-100 字符, signature ≤200 字符 |
| POST /users/me/change-password | ✅ PASS | Pydantic: new_password min_length=8 |
| PATCH /users/me/play-setting | ✅ PASS | Pydantic: typing_speed 正则, volume 0-100, delay 1000-10000 |
| PATCH /users/me/notify-setting | ✅ PASS | Pydantic: 全部 Optional[bool] |
| POST /users/me/devices/{id}/logout | ❌ **FAIL** | UUID 格式未预校验，无效 UUID 导致 500（BUG-001） |

### 2.4 SQL 注入

| 检查项 | 结论 | 说明 |
|--------|------|------|
| 数据库查询方式 | ✅ PASS | 全部使用 SQLAlchemy ORM（`select().where()`），参数化查询 |
| 原始 SQL | ✅ PASS | 未发现字符串拼接 SQL |

### 2.5 敏感操作安全

| 检查项 | 结论 | 说明 |
|--------|------|------|
| 密码修改 — 验证旧密码 | ✅ PASS | `verify_password(body.old_password, user.password_hash)` |
| 密码修改 — 新密码强度 | ⚠️ WARN | 仅 min_length=8，无复杂度要求（字母+数字），建议增强 |
| 密码修改 — Token 失效 | ⚠️ WARN | 修改密码后旧 JWT 仍有效（15 分钟内），建议清除所有 refresh token |
| 账号删除 — 确认机制 | ⚠️ WARN | DELETE /users/me 无二次确认或重新验证，直接硬删除 |
| 账号删除 — 级联清理 | ⚠️ WARN | 依赖 ORM 级联，需确认所有关联表有 ON DELETE CASCADE |
| 审计日志 | ⚠️ WARN | 密码修改、账号删除等敏感操作无审计日志记录 |

### 2.6 Mock 策略与发布证据

| 检查项 | 结论 | 说明 |
|--------|------|------|
| Mock API 使用 | ✅ PASS | test-report 明确记录 Mock API=no |
| Browser E2E | ✅ PASS | 10/10 通过，真实前端入口 → 真实后端 |
| Delivery E2E / Runtime Smoke | ✅ PASS | curl 通过前端 proxy 访问真实后端，200 OK |
| Mock 中间件干扰 | ✅ PASS | Mock 仅用于 Payment/OAuth/Email/Discord 外部服务 |

### 2.7 依赖/容器/部署

| 检查项 | 结论 | 说明 |
|--------|------|------|
| 依赖版本固定 | ✅ PASS | pyproject.toml 固定版本 |
| 数据库凭据 | ✅ PASS | 通过 DATABASE_URL 环境变量 |
| 手动建表风险 | ⚠️ WARN | posts/collections 表手动创建未走 Alembic（test-report 已记录） |

---

## 3. 缺陷与风险

### 3.1 阻塞缺陷（必须修复）

| ID | 严重度 | 接口 | 问题 | 责任人 |
|----|--------|------|------|--------|
| SEC-001 (=BUG-001) | P2 | POST /users/me/devices/{id}/logout | 无效 UUID 返回 500 而非 400，输入校验缺失 | BE |

**修复方案**: 在 `settings.py` 的 `logout_device` 中增加 UUID 解析 try/except，或依赖 SQLAlchemy asyncpg 的自动转换并在外层捕获 `ValueError`。

### 3.2 安全增强建议（不阻塞发布，建议后续迭代处理）

| ID | 严重度 | 问题 | 建议 |
|----|--------|------|------|
| SEC-002 | 中 | 密码修改后旧 Token 仍有效 | 修改密码后清除该用户所有 refresh token（Redis 黑名单或 DB token 版本号） |
| SEC-003 | 低 | 新密码无复杂度要求 | Pydantic 增加正则校验：至少含字母+数字 |
| SEC-004 | 低 | 敏感操作无审计日志 | 密码修改、账号删除写入 audit_log 表 |
| SEC-005 | 低 | 账号删除无二次确认 | 前端增加确认弹窗 + 后端要求传入确认 token 或密码 |

### 3.3 已确认低风险项

| 项 | 说明 |
|----|------|
| 登录暴力破解防护 | ✅ Redis 计数器，5 次失败 → 15 分钟锁定 |
| 密码存储 | ✅ bcrypt cost 12 |
| CORS | ✅ 白名单配置 |
| Rate Limiting | ✅ Redis 滑动窗口 |
| 权限拒绝证据 | ✅ /users/me/memory/full 对 free 用户返回 403 + SUBSCRIPTION_REQUIRED |

---

## 4. 验收项追踪

| AC 相关 | 安全验证 | 证据来源 |
|---------|----------|----------|
| JWT 验证 | 所有 26 个接口均需 Bearer | test-report §1.1, §1.2 |
| 权限控制 | /users/me/memory/full 返回 403 | test-report #18 |
| 密码安全 | 旧密码验证正确 | 源码 `users.py` L117-123 |
| 输入校验 | Pydantic schema 覆盖所有 POST/PATCH | 源码 schema 定义 |
| Mock 策略 | Mock API=no | test-report §3, §4 |

---

## 5. 结论

### 审查结果: ⚠️ 有条件通过

**通过条件**:
1. **必须修复**: SEC-001（设备下线 UUID 校验，P2）— 修复后发布
2. **建议修复**: SEC-002 ~ SEC-005 在后续迭代中处理

**发布建议**:
- SEC-001 修复工作量约 10 分钟，建议发布前修复
- 其余为安全增强，不阻塞本次发布
- 核心安全机制（JWT 认证、ORM 参数化、权限控制、输入校验）均已到位

**退回项**: 无（SEC-001 为 P2，QA 已记录为 BUG-001，BE 修复后即可通过）

---

## 6. 签字

**审查人**: Security Agent
**审查时间**: 2026-07-23
**审查结论**: ⚠️ 有条件通过（1 个 P2 安全缺陷待修复 + 4 个增强建议）
