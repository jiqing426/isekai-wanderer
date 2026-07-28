# CR-018 安全审查报告

**审查时间**: 2026-07-26  
**审查人**: Security Agent  
**审查结论**: ✅ 通过（附遗留项说明）

---

## 1. 审查范围

| 维度 | 范围 |
|------|------|
| 变更文件 | P0: `gift.py`, `chat.ts`, `user.ts`, `users.py`；P1: `narrative_engine.py`, `free_chat_service.py`, `script_service.py`, `migrate_uuid_v4.sql`, `users.py`, `sign.py`, `quota_service.py`；二次复测: `fragment.py`, `community.py`, `settings.py`, `FragmentMallView.vue`, `SettingsView.vue`, `zh-CN.ts` |
| UUID v4 迁移 | `backend/scripts/migrate_uuid_v4.sql` — 临时映射表 + 外键重建，事务包裹 |
| 文件上传 | `backend/app/api/v1/users.py` 头像上传 — 5MB 限制、MIME 白名单、路径规范化 |
| 鉴权修复 | 自由对话 401（`frontend/src/api/chat.ts` 改用统一 api 实例携带 token）；头像 AUTH_TOKEN_EXPIRED（`frontend/src/api/user.ts` token 刷新） |

---

## 2. 安全审查结论

### 2.1 无新增安全漏洞 ✅
- 未发现新增真实密钥、token、证书、密码或生产数据提交。
- `.env` 中 `DISABLE_MOCK=1` 已禁用 mock 路由，生产环境不加载 mock 数据。

### 2.2 鉴权修复已正确实现 ✅
- 自由对话 `/api/v1/chat/free` 前端改用统一 `api.post` 实例，自动附加 Authorization header，修复 401。
- 头像上传改用统一 `api` 实例，token 过期时走刷新流程，修复 AUTH_TOKEN_EXPIRED。
- 后端 `get_current_user_id` 依赖链未变更，鉴权中间件逻辑完整。

### 2.3 文件上传路径已规范化 ✅
- `AVATAR_UPLOAD_DIR` 使用 `Path.resolve()` 规范化到 `static/avatars/`，防止路径穿越。
- 文件大小限制 5MB，MIME 白名单 `image/jpeg, image/png, image/gif, image/webp`。
- 文件名使用安全生成（UUID/哈希），不接受用户指定文件名。

### 2.4 数据迁移无数据泄露风险 ✅
- `migrate_uuid_v4.sql` 使用 `CREATE TEMPORARY TABLE` + `BEGIN/COMMIT` 事务。
- 映射表仅存在于当前事务会话，不暴露给外部连接。
- 迁移仅更新 ID 引用，不涉及数据导出或删除，无数据泄露路径。
- 外键约束先删后建，保证引用完整性。

---

## 3. 检查清单逐项结果

| # | 检查项 | 结果 | 说明 |
|---|--------|------|------|
| 1 | 是否提交真实密钥/token/证书/密码/生产数据 | ✅ 通过 | 未发现 |
| 2 | 鉴权、授权、审计和敏感操作确认 | ✅ 通过 | 鉴权修复已验证，敏感操作（送礼、签到）有余额校验和事务保护 |
| 3 | 敏感字段、隐私、日志脱敏和数据保留 | ✅ 通过 | 用户密码 bcrypt 哈希，日志中未见明文 token |
| 4 | API/DB/Runtime/Mock 策略一致性 | ⚠️ 遗留项 | mock_router.py 和 mock_middleware.py 存在硬编码 UUID，但 `DISABLE_MOCK=1` 已禁用，不影响生产 |
| 5 | test-report.md 区分 CI/CD、Delivery E2E、Browser Interaction E2E | ⚠️ 部分 | 当前 test-report 以 API 级别验证为主，Browser Interaction E2E 证据有限 |
| 6 | 依赖、容器和部署配置风险 | ✅ 通过 | Docker Compose 配置未见特权容器或暴露多余端口 |
| 7 | 安全相关验收项在 acceptance.md 有验证结论 | ⚠️ 缺失 | acceptance.md 尚未创建，安全相关 AC 待补 |
| 8 | 高风险事项是否需要人工确认 | ✅ 否 | 无高风险阻塞项 |

---

## 4. 遗留项

### 4.1 Mock 数据文件中的硬编码 UUID [低风险]
- **文件**: `backend/app/api/v1/mock_router.py`, `backend/app/api/v1/mock_middleware.py`
- **现象**: 包含 `a1111111-...`, `66666666-...`, `22222222-...` 等硬编码 UUID
- **缓解**: `.env` 中 `DISABLE_MOCK=1` 已禁用 mock 路由，生产环境不加载
- **建议**: 后续 CR 中清理 mock 文件或将其移至独立 dev-only 模块
- **责任**: be（后端）

### 4.2 acceptance.md 待补齐 [流程项]
- 安全相关 AC 需在 acceptance.md 中有明确验证结论
- **责任**: PL

### 4.3 Browser Interaction E2E 证据 [流程项]
- 当前测试报告以 API 级别为主，权限拒绝、敏感操作的浏览器交互证据有限
- **责任**: QA

---

## 5. 总结

| 项 | 值 |
|---|---|
| 结论 | ✅ 通过 |
| 阻塞项 | 0 |
| 遗留项 | 3（均为低风险/流程项） |
| 退回 | 无 |
| 高风险人工确认 | 不需要 |

CR-018 安全审查通过，可发布。遗留项不影响生产安全，建议在后续 CR 中逐步解决。
