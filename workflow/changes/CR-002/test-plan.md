# Test Plan — CR-002

## 测试策略

| 层级 | 范围 | 工具 | Mock 允许 |
| --- | --- | --- | --- |
| 单元测试 | 纯逻辑、组件 | pytest (BE), Vitest (FE) | 是 (mock DB, mock LLM, mock services) |
| 集成测试 | API + DB + service | pytest + httpx + real PostgreSQL | 否 (real DB, real API routes) |
| Browser E2E | 用户流程 | Playwright | 否 (real frontend + real backend + real proxy) |
| Delivery E2E / Runtime Smoke | 全栈健康检查 | curl + Playwright | 否 (Mock API=no) |
| 性能测试 | 时序、fps、Lighthouse | Playwright + performance.now() + Lighthouse CI | 否 |

**关键原则**：Delivery E2E / Release evidence 禁止 mock API。mock 只允许用于支付/订阅/OAuth/邮件/Discord 的 Provider 实现层。

## Test-First Scope

- 密码重置 (DEV-CR2-002)：Red → Green，先写 pytest 用例（token 生成/验证/过期/rate limit），再实现 auth endpoints
- 自由对话 (DEV-CR2-009)：Red → Green，先写 pytest 用例（话题验证/session 创建/LLM 调用），再实现 free_chat_service
- 召回邮件 (DEV-CR2-008)：Red → Green，先写 pytest 用例（7 天判断/进度摘要/mock email 调用），再实现 recall_service
- 路线图探索 (DEV-CR2-001)：Red → Green，先写 pytest 用例（聚合查询），再实现 route-map endpoint
- Discord 集成 (DEV-CR2-006)：Red → Green，先写 pytest 用例（mock webhook 日志），再实现 discord_service
- 情绪节奏 (DEV-CR2-003)：Red → Green，先写 Vitest 用例（emotion multiplier），再实现 useTypewriter/AudioPlayer 增强
- i18n (DEV-CR2-004)：Red → Green，先写 Vitest 用例（翻译完整性），再实现 vue-i18n 集成
- PWA 通知 (DEV-CR2-007)：Red → Green，先写 Vitest 用例（权限请求逻辑），再实现 useNotification
- E2E (DEV-CR2-012)：先写 Playwright spec，再联调验证

## Test Case Artifacts

| Task ID | Test Case Artifact | Acceptance IDs | Status |
|---------|-------------------|----------------|--------|
| DEV-CR2-001 | `tests/unit/test_route_map.py` | AC-045 | Ready |
| DEV-CR2-002 | `tests/unit/test_password_reset.py` | AC-047 | Ready |
| DEV-CR2-002 | `tests/integration/test_auth_reset.py` | AC-047 | Ready |
| DEV-CR2-003 | `tests/unit/fe/useTypewriter.test.ts` | AC-048 | Ready |
| DEV-CR2-003 | `tests/unit/fe/AudioPlayer.test.ts` | AC-048 | Ready |
| DEV-CR2-004 | `tests/unit/fe/i18n.test.ts` | AC-052 | Ready |
| DEV-CR2-005 | `tests/e2e/cr002-features.spec.ts#seo` | AC-054 | Ready |
| DEV-CR2-006 | `tests/unit/test_discord_service.py` | AC-055 | Ready |
| DEV-CR2-006 | `tests/integration/test_ending_discord.py` | AC-055 | Ready |
| DEV-CR2-007 | `tests/unit/fe/useNotification.test.ts` | AC-056 | Ready |
| DEV-CR2-008 | `tests/unit/test_recall_service.py` | AC-057 | Ready |
| DEV-CR2-008 | `tests/integration/test_recall_cron.py` | AC-057 | Ready |
| DEV-CR2-009 | `tests/unit/test_free_chat_service.py` | AC-058 | Ready |
| DEV-CR2-009 | `tests/integration/test_free_chat_api.py` | AC-058 | Ready |
| DEV-CR2-009 | `tests/unit/fe/FreeChatView.test.ts` | AC-058 | Ready |
| DEV-CR2-010 | `tests/unit/fe/SettingsView.test.ts` | AC-052, AC-055 | Ready |
| DEV-CR2-011 | `tests/unit/test_mock_email_service.py` | AC-047, AC-057 | Ready |
| DEV-CR2-012 | `tests/e2e/cr002-features.spec.ts` | AC-045, AC-047, AC-048, AC-052, AC-054, AC-055, AC-056, AC-058 | Ready |
| DEV-CR2-012 | `tests/integration/test_cr002_apis.py` | AC-045, AC-047, AC-048, AC-052, AC-055, AC-057, AC-058 | Ready |
| DEV-CR2-013 | alembic upgrade head 验证 | AC-047, AC-055, AC-057, AC-058 | Ready |

## Red Failure Records

> Red 失败记录属于 DEVELOPMENT 阶段写业务代码前的 code readiness，不属于 DESIGN 关口必须完成项。
> 以下表格在 DEVELOPMENT 阶段、写业务代码前由开发补齐。

| 模块 | Red 用例 | 预期失败 | 实际结果 | 记录人 | 日期 |
|------|---------|---------|---------|--------|------|
| DEV-CR2-003 useTypewriter | emotion speed multiplier (8 cases) | `setEmotionMultiplier` / `speedMultiplier` not found on useTypewriter | ✅ Red confirmed — TypeError: setEmotionMultiplier is not a function | fe | 2026-07-19 |
| DEV-CR2-003 AudioPlayer | emotion volume multiplier (8 cases) + mute | AudioPlayer.vue does not exist | ✅ Red confirmed — Cannot find module '@/components/AudioPlayer.vue' | fe | 2026-07-19 |
| DEV-CR2-004 i18n | translation completeness (8 cases) | settings.* and notification.* keys missing from zh-CN/en-US | ✅ Red confirmed — Expected [settings.title, ...] to equal [] (missing keys) | fe | 2026-07-19 |
| DEV-CR2-007 useNotification | permission request logic (10 cases) | useNotification.ts does not exist | ✅ Red confirmed — Cannot find module '@/composables/useNotification' | fe | 2026-07-19 |

## CI/CD Evidence Plan

| Stage | Trigger | Command / Pipeline | Acceptance IDs | Owner | Record Location | Status |
|-------|---------|-------------------|----------------|-------|-----------------|--------|
| Lint (BE) | push/PR | `cd backend && ruff check .` | AC-045, AC-047, AC-055, AC-057, AC-058 | be | stdout | Planned |
| Lint (FE) | push/PR | `cd frontend && npx eslint src/` | AC-045, AC-048, AC-052, AC-054, AC-056 | fe | stdout | Planned |
| Unit Test (BE) | push/PR | `cd backend && pytest tests/unit/ -v --tb=short` | AC-045, AC-047, AC-055, AC-057, AC-058 | be | `backend/tests/unit/` | Planned |
| Unit Test (FE) | push/PR | `cd frontend && npx vitest run --reporter=verbose` | AC-048, AC-052, AC-056 | fe | `frontend/src/__tests__/` | Planned |
| Integration Test | push/PR | `cd backend && pytest tests/integration/ -v --tb=short` | AC-047, AC-055, AC-057, AC-058 | be | `backend/tests/integration/` | Planned |
| Build Check | push/PR | `cd frontend && npm run build && cd ../backend && docker build -f Dockerfile -t backend .` | AC-045, AC-047, AC-048, AC-052, AC-054, AC-055, AC-056, AC-057, AC-058 | ops | `docker-compose.yml` | Planned |
| Delivery E2E | push/PR | `docker compose up -d && sleep 5 && curl -f http://localhost/api/v1/health && APP_BASE=http://localhost npx playwright test tests/e2e/delivery-smoke.spec.ts` | AC-045, AC-047, AC-052, AC-058 | qa | `tests/e2e/screenshots/` | Planned |
| Browser E2E | push/PR | `APP_BASE=http://localhost:3000 npx playwright test tests/e2e/cr002-features.spec.ts --headed --trace on` | AC-045, AC-047, AC-048, AC-052, AC-054, AC-055, AC-056, AC-058 | qa | `tests/e2e/traces/` | Planned |

## Delivery E2E / Runtime Smoke Plan

| 任务编号 | 命令 / 步骤 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
|---------|------------|---------|---------|-----------------|---------|-----------|-------------|------|
| DEL-CR2-001 | `docker compose up -d && sleep 5 && curl -f http://localhost/api/v1/health` | `http://localhost:3000` | `http://localhost:8000` | `/api/v1/health` | no | AC-045, AC-047, AC-048, AC-052, AC-054, AC-055, AC-056, AC-057, AC-058 | `logs/e2e/del-cr2-001-health.log` | Planned |
| DEL-CR2-002 | `APP_BASE=http://localhost npx playwright test tests/e2e/delivery-smoke.spec.ts -g "cr002-password-reset"` | `http://localhost:3000` | `http://localhost:8000` | `/api/v1/auth/forgot-password, /api/v1/auth/reset-password` | no | AC-047 | `logs/e2e/del-cr2-002.png` | Planned |
| DEL-CR2-003 | `APP_BASE=http://localhost npx playwright test tests/e2e/delivery-smoke.spec.ts -g "cr002-free-chat"` | `http://localhost:3000` | `http://localhost:8000` | `/api/v1/game/*/free-chat` | no | AC-058 | `logs/e2e/del-cr2-003.png` | Planned |
| DEL-CR2-004 | `APP_BASE=http://localhost npx playwright test tests/e2e/delivery-smoke.spec.ts -g "cr002-route-map"` | `http://localhost:3000` | `http://localhost:8000` | `/api/v1/game/*/route-map` | no | AC-045 | `logs/e2e/del-cr2-004.png` | Planned |

## Browser Interaction E2E Plan

| 任务编号 | 命令 / 步骤 | Browser / Tool | 用户动作 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
|---------|------------|---------------|---------|---------|---------|-----------------|---------|-----------|-------------|------|
| BR-CR2-001 | `APP_BASE=http://localhost:3000 npx playwright test tests/e2e/cr002-features.spec.ts --headed --trace on -g "route-map"` | Chromium (Playwright) | 剧本详情页 → 点击路线探索 → 查看高亮/灰色分支 | `http://localhost:3000` | `http://localhost:8000` | `/api/v1/game/*/route-map` | no | AC-045 | `tests/e2e/traces/br-cr2-001.zip` | Ready |
| BR-CR2-002 | `APP_BASE=http://localhost:3000 npx playwright test tests/e2e/cr002-features.spec.ts --headed --trace on -g "password-reset"` | Chromium (Playwright) | 登录页 → 忘记密码 → 输入邮箱 → 提交 → 重置页 → 输入新密码 → 提交 → 验证登录 | `http://localhost:3000` | `http://localhost:8000` | `/api/v1/auth/forgot-password, /api/v1/auth/reset-password` | no | AC-047 | `tests/e2e/traces/br-cr2-002.zip` | Ready |
| BR-CR2-003 | `APP_BASE=http://localhost:3000 npx playwright test tests/e2e/cr002-features.spec.ts --headed --trace on -g "emotional-rhythm"` | Chromium (Playwright) | 游戏中 → 观察 SSE emotion 事件 → 验证打字速度变化 → 验证 BGM 音量变化 | `http://localhost:3000` | `http://localhost:8000` | `/api/v1/game/*/dialogue (SSE)` | no | AC-048 | `tests/e2e/traces/br-cr2-003.zip` | Ready |
| BR-CR2-004 | `APP_BASE=http://localhost:3000 npx playwright test tests/e2e/cr002-features.spec.ts --headed --trace on -g "i18n"` | Chromium (Playwright) | 设置页 → 选择 English → 验证 UI 文本变化 → 切换回中文 | `http://localhost:3000` | `http://localhost:8000` | `/api/v1/user/preferences` | no | AC-052 | `tests/e2e/traces/br-cr2-004.zip` | Ready |
| BR-CR2-005 | `APP_BASE=http://localhost:3000 npx playwright test tests/e2e/cr002-features.spec.ts --headed --trace on -g "seo"` | Chromium (Playwright) | 查看页面源码 → 验证 title/description/og:image meta 标签 → 访问 sitemap.xml → 访问 robots.txt | `http://localhost:3000` | `http://localhost:8000` | `/sitemap.xml, /robots.txt` | no | AC-054 | `tests/e2e/traces/br-cr2-005.zip` | Ready |
| BR-CR2-006 | `APP_BASE=http://localhost:3000 npx playwright test tests/e2e/cr002-features.spec.ts --headed --trace on -g "discord"` | Chromium (Playwright) | 设置页 → 查看 Discord 链接存在且可点击 | `http://localhost:3000` | `http://localhost:8000` | `/api/v1/user/preferences` | no | AC-055 | `tests/e2e/traces/br-cr2-006.zip` | Ready |
| BR-CR2-007 | `APP_BASE=http://localhost:3000 npx playwright test tests/e2e/cr002-features.spec.ts --headed --trace on -g "pwa-notification"` | Chromium (Playwright) | 首次进入游戏 → 查看通知提示 → 点击启用 → 验证 Notification.permission | `http://localhost:3000` | `http://localhost:8000` | N/A (frontend only) | no | AC-056 | `tests/e2e/traces/br-cr2-007.zip` | Ready |
| BR-CR2-008 | `APP_BASE=http://localhost:3000 npx playwright test tests/e2e/cr002-features.spec.ts --headed --trace on -g "free-chat"` | Chromium (Playwright) | 首页 → 自由对话 → 选角色 → 选话题 → 发消息 → 查看流式回复 + 情绪标签 | `http://localhost:3000` | `http://localhost:8000` | `/api/v1/game/*/free-chat` | no | AC-058 | `tests/e2e/traces/br-cr2-008.zip` | Ready |

## 状态规则

- 测试用例产物状态：`Draft`、`Ready`、`Approved`、`Recorded`。
- 测试证据状态：`pending`、`pass`、`fail`、`manual_pending`。
- P0/P1 验收项必须有测试证据；只有 `manual_pending` 或 `out_of_scope_with_reason` 可例外。
- 每个 P0/P1 AC 必须记录至少一条用户动作或验证命令。

## 维护规则

- QA 在 Architect 和 PL 确认验收矩阵、运行契约和测试要求后，补齐测试用例和执行证据。
- QA 必须独立复核测试证据和覆盖结论，不直接采纳开发自测结论。
- 测试用例和证据必须可在仓库或制品中追溯。
- 发布关口前，所有测试证据应达到 `pass` 或 `manual_pending`。
