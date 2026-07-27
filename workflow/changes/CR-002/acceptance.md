# Acceptance — CR-002

| 验收编号 | 需求编号 | 优先级 | 来源规格 | 验收标准 | 设计落点 | OpenSpec Task | 实现证据 | 测试用例 / 验证命令 | 状态 | 覆盖状态 | 未覆盖原因 | PL 处理 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AC-045 | REQ-002 | P1 | `openspec/changes/CR-002-p1-p0-补齐-20260719/specs/capability/script-system.md` | 剧本完成后，用户在剧本详情页点击路线探索可查看路线图，已探索分支高亮，未探索灰色 | RouteMap.vue + GET /api/v1/game/{scriptId}/route-map + script_service.get_route_map | DEV-CR2-001 | ✅ RouteMap.vue + game.py L259 | Playwright BR-CR2-001 passed | Verified | covered | — | — | Phase 1 完成 |
| AC-047 | REQ-006 | P1 | `openspec/changes/CR-002-p1-p0-补齐-20260719/specs/capability/user-account.md` | 用户在登录页点击忘记密码并输入邮箱后，收到密码重置链接（有效期 1 小时，mock 邮件） | POST /auth/forgot-password + POST /auth/reset-password + ForgotPasswordView + ResetPasswordView + MockEmailService + password_resets 表 | DEV-CR2-002 | ✅ auth.py + ForgotPasswordView + ResetPasswordView | pytest 12 passed + Playwright BR-CR2-002 passed | Verified | covered | — | — | mock 邮件 |
| AC-048 | REQ-012 | P1 | `openspec/changes/CR-002-p1-p0-补齐-20260719/specs/capability/emotional-rhythm.md` | 剧本关键节点有情绪标签时，对话打字速度跟随调整，BGM 音量跟随调整 | useTypewriter.setEmotionMultiplier + AudioPlayer.emotionVolumeMultiplier + emotion mapping table | DEV-CR2-003 | ✅ useTypewriter.ts + AudioPlayer.vue | Vitest 17 passed + Playwright BR-CR2-003 passed | Verified | covered | — | — | FE 增强 |
| AC-052 | REQ-016 | P1 | `openspec/changes/CR-002-p1-p0-补齐-20260719/specs/capability/internationalization.md` | 游戏 UI 文本支持英文翻译；用户在设置页可切换语言（中文/英文） | vue-i18n + i18n/zh.json + i18n/en.json + SettingsView NSelect 语言切换 + localStorage 持久化 | DEV-CR2-004 | ✅ i18n.ts + zh-CN.ts + en-US.ts + SettingsView | Vitest 8 passed + Playwright BR-CR2-004 passed | Verified | covered | — | — | FE 新功能 |
| AC-054 | REQ-018 | P1 | `openspec/changes/CR-002-p1-p0-补齐-20260719/specs/capability/seo.md` | 游戏首页和各剧本页面的 HTML 包含基础 meta 标签（title/description/og:image）；网站根目录有 sitemap.xml | @vueuse/head useHead() 每页 meta + public/sitemap.xml + public/robots.txt | DEV-CR2-005 | ✅ sitemap.xml + robots.txt + 各 View useHead | Playwright BR-CR2-005 passed | Verified | covered | — | — | FE 配置 |
| AC-055 | REQ-019 | P1 | `openspec/changes/CR-002-p1-p0-补齐-20260719/specs/capability/discord-integration.md` | 游戏设置页展示官方 Discord 链接；新结局解锁时 Discord Bot 发送通知到指定频道 | MockDiscordService + discord_configs 表 + SettingsView Discord 链接 | DEV-CR2-006 | ✅ discord_service.py + SettingsView | pytest 7 passed + Playwright BR-CR2-006 passed | Verified | covered | — | — | mock webhook |
| AC-056 | REQ-020 | P1 | `openspec/changes/CR-002-p1-p0-补齐-20260719/specs/capability/push-notification.md` | 用户首次进入游戏时，浏览器弹出 PWA 通知权限提示；用户授权后系统可发送通知 | useNotification composable + NotificationPrompt.vue + sw.js | DEV-CR2-007 | ✅ useNotification.ts + NotificationPrompt.vue | Vitest 10 passed + Playwright BR-CR2-007 passed | Verified | covered | — | — | FE 新功能 |
| AC-057 | REQ-021 | P1 | `openspec/changes/CR-002-p1-p0-补齐-20260719/specs/capability/email-recall.md` | 用户连续 7 天未登录时，系统自动发送召回邮件（含游戏链接和最近游玩进度摘要，mock 实现） | RecallService cron + users.last_login + MockEmailService + recall_emails 表 | DEV-CR2-008 | ✅ recall_service.py + recall.py | pytest 5 passed + Delivery E2E cron 验证 | Verified | covered | — | — | mock 邮件 |
| AC-058 | REQ-022 | P1 | `openspec/changes/CR-002-p1-p0-补齐-20260719/specs/capability/free-conversation.md` | 用户在剧本间可进入自由对话模式，从 5 个预设话题中选择，角色根据话题和记忆生成对话 | POST /game/{sessionId}/free-chat + 5 topics + free_chat_service + free_chat_sessions 表 + FreeChatView.vue | DEV-CR2-009 | ✅ free_chat_service.py + FreeChatView.vue | pytest 8 passed + Playwright BR-CR2-008 passed | Verified | covered | — | — | BE API + FE |
| AC-008 | REQ-002 | P0 | `openspec/changes/CR-002-p1-p0-补齐-20260719/specs/capability/script-system.md` | 用户达成坏结局时，结局页面提供重新开始本路线按钮，点击后进度重置到路线起始 | POST /restart 已实现 | DEV-CR2-010 | 待测试 | Playwright: 坏结局→重新开始→进度重置 | Blocked | deferred_with_approval | Phase 2 P0 测试补齐，CR-003 执行 | Phase 2 | Browser E2E |
| AC-015 | REQ-005 | P0 | `openspec/changes/CR-002-p1-p0-补齐-20260719/specs/capability/visual-presentation.md` | 对话中 AI 输出带情绪标签时，角色立绘在 200ms 内切换到对应表情 | CharacterSprite CSS transition 已实现 | DEV-CR2-011 | 待测试 | Playwright + performance.now() ≤200ms | Blocked | deferred_with_approval | Phase 2 P0 测试补齐，CR-003 执行 | Phase 2 | Performance |
| AC-016 | REQ-005 | P0 | `openspec/changes/CR-002-p1-p0-补齐-20260719/specs/capability/visual-presentation.md` | 剧情推进到不同场景时，背景图在 500ms 内完成淡入切换 | SceneBackground CSS transition 已实现 | DEV-CR2-012 | 待测试 | Playwright + CSS transition ≤500ms | Blocked | deferred_with_approval | Phase 2 P0 测试补齐，CR-003 执行 | Phase 2 | Performance |
| AC-017 | REQ-005 | P0 | `openspec/changes/CR-002-p1-p0-补齐-20260719/specs/capability/visual-presentation.md` | 场景切换时 BGM 跟随切换（淡出旧曲+淡入新曲）；用户点击静音按钮后 BGM 停止 | AudioPlayer 已实现 | DEV-CR2-013 | 待测试 | Playwright: BGM 切换验证 | Blocked | deferred_with_approval | Phase 2 P0 测试补齐，CR-003 执行 | Phase 2 | Browser E2E |
| AC-018 | REQ-005 | P0 | `openspec/changes/CR-002-p1-p0-补齐-20260719/specs/capability/visual-presentation.md` | 对话文本以流式打字效果展示（≥30fps）；用户点击对话区域后全部文本立即显示 | useTypewriter 已实现 | DEV-CR2-014 | 待测试 | Playwright + rAF 帧率 ≥30fps | Blocked | deferred_with_approval | Phase 2 P0 测试补齐，CR-003 执行 | Phase 2 | Performance |
| AC-019 | REQ-005 | P0 | `openspec/changes/CR-002-p1-p0-补齐-20260719/specs/capability/visual-presentation.md` | 3G Fast 网络条件下，页面首次加载（URL 到可交互）小于 3s | Vite code splitting 已实现 | DEV-CR2-015 | 待测试 | Lighthouse CI 或本地 Lighthouse | Blocked | deferred_with_approval | Phase 2 P0 测试补齐，CR-003 执行 | Phase 2 | Performance |
| AC-028 | REQ-007 | P0 | `openspec/changes/CR-002-p1-p0-补齐-20260719/specs/capability/daily-streak.md` | streak 达到 Day 3/7/14/30 时，系统发放对应阶梯奖励（碎片+特殊内容），展示奖励弹窗 | daily_service 已实现 | DEV-CR2-016 | 待测试 | pytest + Delivery: 种子数据驱动奖励测试 | Blocked | deferred_with_approval | Phase 2 P0 测试补齐，CR-003 执行 | Phase 2 | Unit + Delivery |
| AC-029 | REQ-007 | P0 | `openspec/changes/CR-002-p1-p0-补齐-20260719/specs/capability/daily-streak.md` | 用户进入签到页面可查看当月签到日历，已签到日期标记，当前 streak 天数和下一阶梯进度 | StreakCalendar 已实现 | DEV-CR2-017 | 待测试 | Playwright: 签到日历展示 | Blocked | deferred_with_approval | Phase 2 P0 测试补齐，CR-003 执行 | Phase 2 | Browser E2E |
| AC-034 | REQ-009 | P0 | `openspec/changes/CR-002-p1-p0-补齐-20260719/specs/capability/first-play-guarantee.md` | 新用户首次 AI 对话失败时（超时/质量不达标），系统自动使用预设引导脚本完成对话，首玩失败率小于 5% | onboarding_service 已实现 | DEV-CR2-018 | 待测试 | pytest: MockProvider 失败率统计 <5% | Blocked | deferred_with_approval | Phase 2 P0 测试补齐，CR-003 执行 | Phase 2 | Unit |
| AC-041 | REQ-011 | P0 | `openspec/changes/CR-002-p1-p0-补齐-20260719/specs/capability/subscription-system.md` | 订阅到期后状态变为过期，用户权益降级为免费档；用户可取消订阅，当前周期结束前权益不变 | subscription_service 已实现 | DEV-CR2-019 | 待测试 | pytest + Delivery: 时间模拟到期/取消 | Blocked | deferred_with_approval | Phase 2 P0 测试补齐，CR-003 执行 | Phase 2 | Unit + Delivery |

## Phase 划分

- **Phase 1（P1 功能开发）**：AC-045, AC-047, AC-048, AC-052, AC-054, AC-055, AC-056, AC-057, AC-058（9 项）
- **Phase 2（P0 测试补齐）**：AC-008, AC-015, AC-016, AC-017, AC-018, AC-019, AC-028, AC-029, AC-034, AC-041（10 项）
- **Phase 2 依赖 Phase 1**：Phase 1 全部完成并通过 QA 后才进入 Phase 2

## 排除项

| AC | 内容 | 排除原因 |
| --- | --- | --- |
| AC-022 | 邮箱验证链接 | 无真实邮件服务，CR-001 已标记 auto-verify enabled |

## 状态规则

- `状态`：`Pending`、`Designed`、`Implemented`、`Verified`、`Blocked`
- `覆盖状态`：`covered` / `not_covered` / `manual_pending` / `deferred_with_approval` / `out_of_scope_with_reason`
