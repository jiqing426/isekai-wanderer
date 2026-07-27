# Test Plan — CR-004 移动端适配

| 项 | 内容 |
| --- | --- |
| 变更 ID | CR-004 |
| 变更名称 | mobile-responsive |
| 测试状态 | Ready |
| 测试负责人 | qa |
| 创建时间 | 2026-07-19 |
| 前置条件 | DESIGN passed |

---

## Test-First Scope

- 为 28 个前端页面 + 22 个公共组件增加移动端（≤767px）CSS 适配
- 零改动 PC 端（≥1024px），纯 CSS 层改动，不动业务逻辑
- 新建 mobile.css 集中管理所有移动端样式
- 新增底部 TabBar 组件（5 入口）
- Demo 先行：LandingView + HomeView → 用户确认 → P0 → P1 → P2
- 测试类型：Browser Interaction E2E + PC 回归 + CSS 隔离检查 + 触摸目标检查

---

## Test Case Artifacts

| 任务编号 | 测试用例产物 | 覆盖验收项 | 状态 |
|----------|--------------|------------|------|
| TASK-MOB-001 | `tests/e2e/mobile-basic.spec.ts` | AC-MOB-013, AC-MOB-015 | Ready |
| TASK-MOB-002 | `tests/e2e/mobile-tabbar.spec.ts` | AC-MOB-009, AC-MOB-010, AC-MOB-011 | Ready |
| TASK-MOB-003 | `tests/e2e/mobile-landing.spec.ts` | AC-MOB-001 | Ready |
| TASK-MOB-004 | `tests/e2e/mobile-home.spec.ts` | AC-MOB-002 | Ready |
| TASK-MOB-005 | `tests/e2e/mobile-game.spec.ts` | AC-MOB-003, AC-MOB-004 | Ready |
| TASK-MOB-006 | `tests/e2e/mobile-discover.spec.ts` | AC-MOB-005 | Ready |
| TASK-MOB-007 | `tests/e2e/mobile-characters.spec.ts` | AC-MOB-006 | Ready |
| TASK-MOB-008 | `tests/e2e/mobile-character-detail.spec.ts` | AC-MOB-007 | Ready |
| TASK-MOB-009 | `tests/e2e/mobile-community.spec.ts` | AC-MOB-008 | Ready |
| TASK-MOB-010 | `tests/e2e/mobile-touch-targets.spec.ts` | AC-MOB-014 | Ready |
| TASK-MOB-011 | `tests/e2e/mobile-forms.spec.ts` | AC-MOB-016, AC-MOB-017, AC-MOB-032, AC-MOB-033 | Ready |
| TASK-MOB-012 | `tests/e2e/mobile-onboarding.spec.ts` | AC-MOB-018 | Ready |
| TASK-MOB-013 | `tests/e2e/mobile-profile.spec.ts` | AC-MOB-019 | Ready |
| TASK-MOB-014 | `tests/e2e/mobile-settings.spec.ts` | AC-MOB-020 | Ready |
| TASK-MOB-015 | `tests/e2e/mobile-saves.spec.ts` | AC-MOB-021 | Ready |
| TASK-MOB-016 | `tests/e2e/mobile-shards.spec.ts` | AC-MOB-022 | Ready |
| TASK-MOB-017 | `tests/e2e/mobile-achievements.spec.ts` | AC-MOB-023 | Ready |
| TASK-MOB-018 | `tests/e2e/mobile-subscription.spec.ts` | AC-MOB-024 | Ready |
| TASK-MOB-019 | `tests/e2e/mobile-gallery.spec.ts` | AC-MOB-025 | Ready |
| TASK-MOB-020 | `tests/e2e/mobile-gift.spec.ts` | AC-MOB-026 | Ready |
| TASK-MOB-021 | `tests/e2e/mobile-script-detail.spec.ts` | AC-MOB-027 | Ready |
| TASK-MOB-022 | `tests/e2e/mobile-ending.spec.ts` | AC-MOB-028 | Ready |
| TASK-MOB-023 | `tests/e2e/mobile-recap.spec.ts` | AC-MOB-029 | Ready |
| TASK-MOB-024 | `tests/e2e/mobile-routemap.spec.ts` | AC-MOB-030 | Ready |
| TASK-MOB-025 | `tests/e2e/mobile-freechat.spec.ts` | AC-MOB-031 | Ready |
| TASK-MOB-026 | `tests/e2e/mobile-forgot-password.spec.ts` | AC-MOB-032 | Ready |
| TASK-MOB-027 | `tests/e2e/mobile-reset-password.spec.ts` | AC-MOB-033 | Ready |
| TASK-MOB-028 | `tests/e2e/mobile-p2-pages.spec.ts` | AC-MOB-036, AC-MOB-037, AC-MOB-038 | Ready |
| TASK-MOB-029 | `tests/e2e/mobile-components.spec.ts` | AC-MOB-034, AC-MOB-035 | Ready |
| TASK-MOB-030 | `tests/e2e/mobile-pc-regression.spec.ts` | AC-MOB-012 | Ready |

---

## Red Failure Records

| 任务编号 | 失败描述 | 根因 | 修复措施 | 状态 |
|----------|----------|------|----------|------|
| TASK-MOB-001 | 待 DEVELOPMENT 阶段补充 | 待补充 | 待补充 | Pending |

---

## CI/CD Evidence Plan

| 阶段 | 触发时机 | 命令 / Pipeline | 覆盖验收项 | 负责人 | 记录位置 | 状态 |
|------|----------|-----------------|------------|--------|----------|------|
| Demo | PR 提交 | `APP_BASE=http://localhost:8081 npx playwright test tests/e2e/mobile-responsive.spec.ts --project=mobile --trace on` | AC-MOB-001, AC-MOB-002, AC-MOB-009, AC-MOB-010, AC-MOB-013, AC-MOB-015 | qa | `test-results/demo/` | Ready |
| GameView | Demo 通过后 | `APP_BASE=http://localhost:8081 npx playwright test tests/e2e/mobile-game.spec.ts --project=mobile --trace on` | AC-MOB-003, AC-MOB-004 | qa | `test-results/gameview/` | Ready |
| P0 全面 | GameView 通过后 | `APP_BASE=http://localhost:8081 npx playwright test tests/e2e/mobile-*.spec.ts --project=mobile --trace on` | AC-MOB-005~008, AC-MOB-014 | qa | `test-results/p0/` | Ready |
| P1 | P0 通过后 | `APP_BASE=http://localhost:8081 npx playwright test tests/e2e/mobile-*.spec.ts --project=mobile --trace on` | AC-MOB-016~033 | qa | `test-results/p1/` | Ready |
| P2 + 最终 | P1 通过后 | `APP_BASE=http://localhost:8081 npx playwright test tests/e2e/mobile-*.spec.ts --project=mobile --trace on && git diff frontend/src/styles/global.css` | AC-MOB-034~038, AC-MOB-012 | qa | `test-results/final/` | Ready |
| RELEASE_GATE | 所有阶段通过后 | `docker compose up -d && sleep 5 && curl -f http://localhost:8000/api/v1/health && APP_BASE=http://localhost:8081 npx playwright test tests/e2e/mobile-*.spec.ts --trace on` | AC-MOB-001~038 | qa | `test-results/release/` | Ready |

---

## Delivery E2E / Runtime Smoke Plan

| 任务编号 | 命令 / 步骤 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
|----------|-------------|----------|----------|------------------|----------|------------|--------------|------|
| TASK-MOB-001 | `docker compose up -d && sleep 5 && curl -f http://localhost:8081/` | http://localhost:8081 | http://localhost:8000 | /api/v1 | no | AC-MOB-001, AC-MOB-013 | `test-results/delivery/` | Ready |
| TASK-MOB-002 | `curl -f http://localhost:8000/api/v1/health` | http://localhost:8081 | http://localhost:8000 | /api/v1 | no | AC-MOB-009, AC-MOB-010 | `test-results/delivery/` | Ready |
| TASK-MOB-003 | `curl -f http://localhost:8081/home` | http://localhost:8081 | http://localhost:8000 | /api/v1 | no | AC-MOB-002 | `test-results/delivery/` | Ready |
| TASK-MOB-004 | `curl -f http://localhost:8081/discover` | http://localhost:8081 | http://localhost:8000 | /api/v1 | no | AC-MOB-005 | `test-results/delivery/` | Ready |

---

## Browser Interaction E2E Plan

| 任务编号 | 命令 / 步骤 | Browser / Tool | 用户动作 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
|----------|-------------|----------------|----------|----------|----------|------------------|----------|------------|--------------|------|
| TASK-MOB-001 | 访问 /，检查布局和按钮尺寸 | Playwright (mobile) | 打开页面，滚动查看，点击CTA按钮 | http://localhost:8081 | http://localhost:8000 | /api/v1 | no | AC-MOB-001, AC-MOB-013 | `test-results/browser/` | Ready |
| TASK-MOB-002 | 访问 /home，检查卡片和 TabBar | Playwright (mobile) | 打开页面，点击TabBar导航 | http://localhost:8081 | http://localhost:8000 | /api/v1 | no | AC-MOB-002, AC-MOB-009, AC-MOB-010 | `test-results/browser/` | Ready |
| TASK-MOB-003 | 进入游戏，点击选项 | Playwright (mobile) | 打开游戏，点击选择按钮 | http://localhost:8081 | http://localhost:8000 | /api/v1 | no | AC-MOB-003, AC-MOB-004 | `test-results/browser/` | Ready |
| TASK-MOB-004 | 检查所有 28 个页面 | Playwright (desktop) | 逐页访问，截图对比 | http://localhost:8081 | http://localhost:8000 | /api/v1 | no | AC-MOB-012 | `test-results/browser/` | Ready |
| TASK-MOB-005 | 检查所有页面无横向滚动 | Playwright (mobile) | 逐页访问，检查滚动条 | http://localhost:8081 | http://localhost:8000 | /api/v1 | no | AC-MOB-013 | `test-results/browser/` | Ready |
| TASK-MOB-006 | 测量交互元素尺寸 | Playwright (mobile) | 检查按钮/输入框尺寸 | http://localhost:8081 | http://localhost:8000 | /api/v1 | no | AC-MOB-014 | `test-results/browser/` | Ready |
| TASK-MOB-007 | `git diff frontend/src/styles/global.css` | git diff | 执行命令检查输出 | N/A | N/A | N/A | no | AC-MOB-015 | `test-results/browser/` | Ready |
| TASK-MOB-008 | 检查 TabBar iOS 安全区域 | Playwright (webkit) | 访问页面，检查底部间距 | http://localhost:8081 | http://localhost:8000 | /api/v1 | no | AC-MOB-011 | `test-results/browser/` | Ready |

---

## 测试通过标准

| 阶段 | 通过条件 |
|------|----------|
| Demo | AC-MOB-001, 002, 009, 010, 013, 015 全部 covered |
| GameView | AC-MOB-003, 004 全部 covered |
| P0 全面 | AC-MOB-005~008, 014 全部 covered |
| P1 | AC-MOB-016~033 全部 covered |
| P2 + 最终 | AC-MOB-034~038, 011, 012 全部 covered |
| RELEASE_GATE | 38 项 AC 全部 covered + CI/CD 通过 + Mock API=no |

---

## 测试风险

| # | 风险 | 影响 | 缓解 |
|---|------|------|------|
| T1 | iOS 设备/模拟器不可用 | AC-MOB-011 无法验证 | 使用 WebKit 浏览器模拟 |
| T2 | 截图对比基线缺失 | PC 回归无法自动对比 | 首次适配前截图作为基线 |
| T3 | Naive UI 组件内部结构变化 | `:deep()` 覆盖失效 | 逐个组件验证 |
