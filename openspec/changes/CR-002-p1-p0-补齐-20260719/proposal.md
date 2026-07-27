# Proposal: CR-002 — P1-P0 补齐

## Why

- CR-001 MVP 已通过全流程 13 阶段并部署上线，但 59 项验收项中 16 项标记为 deferred_with_approval
- 9 项 P1 功能未开发（路线图、密码重置、i18n、SEO 等缺失导致产品不完整）
- 10 项 P0 测试未运行（已有功能缺乏自动化验证）
- CEO 指令启动 CR-002 补齐，将产品从 MVP 提升到完整可用状态

## What Changes

### Phase 1：P1 功能开发（9 项，全部完成后再进 Phase 2）

- AC-045 路线图探索：FE 新增 RouteMap.vue + GET /game/{id}/route-map
- AC-047 密码重置：BE POST /auth/forgot-password + POST /auth/reset-password + mock 邮件
- AC-048 情绪节奏：FE TypewriterSpeed + BGMVolume 联动情绪标签
- AC-052 国际化 i18n：vue-i18n + zh.json + en.json + SettingsView 语言切换
- AC-054 SEO：@vueuse/head meta + sitemap.xml + robots.txt
- AC-055 Discord 集成：DiscordService mock webhook + 设置页链接
- AC-056 PWA 通知：Service Worker + Notification API 权限提示
- AC-057 召回邮件：RecallService cron + MockEmailService（7 天未登录）
- AC-058 自由对话模式：POST /free-chat + 5 话题 + LLM 角色约束

### Phase 2：P0 测试补齐（10 项）

- AC-008 坏结局重新开始：Playwright E2E
- AC-015 立绘表情切换 ≤200ms：Performance.now()
- AC-016 背景图淡入 ≤500ms：CSS transition
- AC-017 BGM 跟随切换：Playwright E2E
- AC-018 打字效果 ≥30fps：rAF 帧率
- AC-019 Lighthouse CI 3G Fast <3s：Lighthouse
- AC-028 签到阶梯奖励：pytest + Delivery
- AC-029 签到月历 UI：Playwright E2E
- AC-034 首玩 AI 失败兜底：pytest MockProvider
- AC-041 订阅到期降级：pytest + Delivery

## Non-Goals

- 不接入真实邮件 SMTP（AC-047/AC-057 使用 mock）
- 不接入真实 Discord Bot（AC-055 使用 mock webhook）
- 不做邮箱验证链接（AC-022 排除）
- 不做真实支付网关（后续 CR-003）
- 不做真实 OAuth（后续 CR-003）
- 不做管理后台（CEO 明确排除）

## Success Criteria

- Phase 1 全部 9 项 P1 功能开发完成，通过 QA 验证
- Phase 2 全部 10 项 P0 测试补齐，测试通过
- CI/CD 全绿：pytest + vitest + build + E2E
- Delivery E2E Mock API=no
- Browser E2E Mock API=no
- 无 P0/P1 阻塞缺陷
- 部署后冒烟测试通过

## Impact

- 前端：8 项新功能/增强（RouteMap, ForgotPassword, TypewriterSpeed, vue-i18n, meta, SW, FreeChatView, SettingsView）
- 后端：4 新 API + 1 cron + MockEmailService + DiscordService + RecallService
- 数据库：3 新表（password_resets, free_chat_sessions, recall_emails）
- 部署：无新增基础设施依赖（全部 mock 实现）
- 测试：新增 10 项 P0 测试用例 + 9 项 P1 功能测试
- 架构：不变（FastAPI + Vue3 + PostgreSQL + Redis）
