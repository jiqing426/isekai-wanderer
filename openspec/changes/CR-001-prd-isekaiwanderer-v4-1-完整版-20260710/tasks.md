# Tasks: CR-001 — Isekai Wanderer MVP

## 实现阶段概览

| 阶段 | 周期 | 范围 | 目标 |
|------|------|------|------|
| Phase 0: 基础设施 | Week 1 | 项目骨架、DB、CI | 前后端脚手架 + Docker Compose + 数据库迁移 + 健康检查 |
| Phase 1: 核心循环 | Week 2-4 | S001+S002+S004 | 叙事引擎 + 剧本系统 + 好感度 → P0 核心游戏循环可跑通 |
| Phase 2: 记忆 + AI | Week 3-5 | S003+S009 | 跨会话记忆 + LLM Gateway + AI 风格化对话 |
| Phase 3: 账户 + 视觉 | Week 4-6 | S007+S006+S005 | 注册/登录/OAuth mock + 视觉呈现 + 首玩保障 |
| Phase 4: 留存 + 商业 | Week 6-8 | S016+S017+S024+S025 | 签到/任务 + mock 内购/订阅 |
| Phase 5: P1 扩展 | Week 8-10 | S008+S010~S015+P1 全部 | 情感节奏 + 社交 + CG + 国际化 + SEO + Discord + 通知 + 邮件 |
| Phase 6: 联调 + QA | Week 10-11 | 全量联调 + E2E | Browser E2E + Delivery E2E + 性能优化 |
| Phase 7: 部署 + 发布 | Week 12 | 部署上线 | Docker 生产配置 + SSL + 监控 |

## 实现任务

| 任务编号 | 阶段 | 模块 | 负责人 Agent | 关联验收项 | 描述 | Consumers | 不覆盖验收项 | 允许写入范围 | 测试用例产物 | 验证方式 | 回滚 / 撤销方案 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEV-001 | P0-Infra | deploy | be | AC-004 | Docker Compose 骨架：PostgreSQL+pgvector、Redis、Nginx 反代配置 | ops, qa | 无 | `deploy/` | docker compose up 全部 healthy | `docker compose up && curl health` | 删除 deploy/ | Ready |
| DEV-002 | P0-Infra | backend | be | AC-004 | FastAPI 骨架 + SQLAlchemy + Alembic + health endpoint `/api/v1/health` | fe, qa | 无 | `backend/` | pytest: GET /api/v1/health 200 | httpx AsyncClient | 删除 backend/app/ | Ready |
| DEV-003 | P0-Infra | frontend | fe | AC-004 | Vue 3 + Vite + Pinia + Vue Router 4 + Naive UI 主题骨架 + PWA manifest | qa | 无 | `frontend/` | `npm run dev` + `npm run build` 通过 | Vitest + 手动 | 删除 frontend/src/ | Ready |
| DEV-004 | P0-Infra | backend | be | AC-004 | Alembic 迁移：users + scripts + routes + nodes + characters + affection + game_sessions 全部表 | ai, fe | 无 | `backend/alembic/versions/` | `alembic upgrade head` 成功 | pytest | `alembic downgrade -1` | Ready |
| DEV-005 | P0-Infra | backend | be | AC-020, AC-023 | JWT 认证中间件 + CORS + 限流 + 错误处理 | fe, ai | 无 | `backend/app/core/security.py`, `middleware.py` | pytest: token 颁发/验证/过期 | pytest | git revert | Ready |
| DEV-006 | P0-Infra | deploy | be | AC-004 | Nginx 配置：前端静态 `/` → 3000，API `/api/v1/*` → 8000，CORS，gzip | ops | 无 | `deploy/nginx/` | 反代通路 curl 测试 | curl + nginx -t | 删除 deploy/nginx/ | Ready |
| DEV-007 | P1-Core | backend | be | AC-001, AC-002, AC-003 | **叙事引擎核心**：ScriptService（状态机 + 节点查询）+ RuleEngine（性格/时间线/好感度校验）+ Fallback（重试2次 + 兜底对话） | ai, fe | 无 | `backend/app/services/narrative_engine.py`, `rule_engine.py`, `fallback.py` | pytest: 预设节点不被修改、违规拦截、兜底触发 | pytest unit + integration | git revert | Ready |
| DEV-008 | P1-Core | backend | ai | AC-001, AC-002, AC-003 | **LLM Gateway**：统一 Provider 接口 + OpenAI Provider + 流式 SSE 输出 + Prompt 模板（角色约束 + 记忆注入 + 情绪标注） | be | 无 | `backend/app/llm/` (gateway.py, providers/, prompts/) | pytest: mock provider + 真实 GPT-4o-mini 调用 | pytest + 真实 LLM | git revert | Ready |
| DEV-009 | P1-Core | backend | be | AC-004, AC-005, AC-006, AC-007, AC-008 | **剧本系统 API**：GET /scripts、GET /scripts/:id、POST /game/start、GET /game/:sessionId/dialogue (SSE)、POST /game/:sessionId/choice、GET /game/:sessionId/ending、POST /game/:sessionId/restart | fe | 无 | `backend/app/api/v1/scripts.py`, `game.py`, `services/script_service.py` | pytest + httpx: 全流程集成测试 | httpx AsyncClient + PostgreSQL | git revert | Ready |
| DEV-010 | P1-Core | backend | be | AC-012, AC-013, AC-014 | **好感度系统 API**：GET /affection、GET /affection/:characterId、好感度计算（±5 限制）、等级阈值升级、持久化 | fe | 无 | `backend/app/services/affection_service.py`, `api/v1/affection.py` | pytest: 数值更新、等级升级、持久化 | pytest | git revert | Ready |
| DEV-011 | P1-Core | data | be | AC-004, AC-007, AC-008 | **剧本数据生产：乙女恋爱**（主力剧本，3 路线 × 2-3 结局），JSON 格式含节点/选择/好感度变化/结局条件/兜底对话 | ai | 无 | `data/scripts/otome/` | seed script 验证 + 游戏流程测试 | seed import + 全流程跑通 | 删除 data/scripts/otome/ | Ready |
| DEV-012 | P1-Core | data | be | AC-004 | **剧本数据生产：奇幻冒险**（轻量剧本，2 路线 × 2 结局） | ai | 无 | `data/scripts/adventure/` | seed script 验证 | seed import | 删除 data/scripts/adventure/ | Ready |
| DEV-013 | P1-Core | data | be | AC-004 | **剧本数据生产：悬疑推理**（轻量剧本，2 路线 × 2 结局） | ai | 无 | `data/scripts/mystery/` | seed script 验证 | seed import | 删除 data/scripts/mystery/ | Ready |
| DEV-014 | P1-Core | frontend | fe | AC-004, AC-005, AC-006, AC-007, AC-008 | **游戏主界面**：GameView（剧本选择 → 路线选择 → 对话界面）+ DialogueBox（SSE 流式文字 ≥30fps + 点击跳过）+ ChoicePanel（选项面板 + 好感度变化反馈）| be | 无 | `frontend/src/views/GameView.vue`, `components/DialogueBox.vue`, `ChoicePanel.vue`, `composables/useSSE.ts` | Playwright E2E: 选择剧本 → 做出选择 → 验证跳转 | Playwright + 真实后端 | git revert | Ready |
| DEV-015 | P1-Core | frontend | fe | AC-012, AC-013, AC-014 | **好感度 UI**：AffectionBar 组件（半隐藏进度条 + 等级标签 + 点击展开精确数值 + 升级动画） | — | 无 | `frontend/src/components/AffectionBar.vue`, `stores/affection.ts` | Playwright E2E: 好感度变化 → 进度条更新 → 展开数值 | Playwright | git revert | Ready |
| DEV-016 | P1-Core | frontend | fe | AC-007, AC-008 | **结局页面**：EndingView（好结局：剧情+独白+CG 展示；坏结局：重新开始按钮 + 进度重置） | — | 无 | `frontend/src/views/EndingView.vue`, `components/EndingCard.vue` | Playwright E2E: 好/坏结局页面展示 | Playwright | git revert | Ready |
| DEV-017 | P2-Memory | backend | ai | AC-009, AC-010, AC-011 | **记忆系统**：MemoryService（记忆提取 LLM prompt + text-embedding-3-small 向量化 + pgvector INSERT/KNN 查询 + 相似度>0.8 阈值 + top-3 召回） | be | 无 | `backend/app/services/memory_service.py`, `llm/prompts/memory_extract.py` | pytest: 存储 → 召回 → 不召回 三场景 | pytest + 真实 pgvector | git revert | Ready |
| DEV-018 | P2-Memory | backend | ai | AC-049 | **AI 风格化对话**：3 种预设风格（温柔/傲娇/冷静）prompt 注入 + 角色 dialogue_style 配置 | be | 无 | `backend/app/llm/prompts/style.py` | pytest: 不同风格输出差异 | pytest | git revert | Ready |
| DEV-019 | P2-Memory | backend | ai | AC-046 | **记忆摘要压缩**：记忆条目超阈值时 LLM 合并为摘要 + 标记已压缩 | be | 无 | `backend/app/services/memory_service.py` (compress) | pytest: 压缩前后检索一致性 | pytest | git revert | Ready |
| DEV-020 | P3-Account | backend | be | AC-020, AC-021, AC-022, AC-023, AC-024 | **用户认证 API**：POST /auth/register + /auth/login + /auth/verify-email + /auth/refresh + bcrypt 密码 + JWT 颁发 + 登录限流（5次/15min） | fe | 无 | `backend/app/api/v1/auth.py`, `core/security.py`, `core/email.py` | pytest + httpx: 注册/登录/验证/限流 | httpx + PostgreSQL + Redis | git revert | Ready |
| DEV-021 | P3-Account | backend | be | AC-043, AC-044 | **OAuth mock API**：GET /auth/oauth/:provider + /auth/oauth/:provider/callback + IOAuthProvider 抽象接口 + Google/Discord mock 实现 | fe | 无 | `backend/app/core/oauth/` | pytest: mock OAuth 流程 + 接口替换验证 | pytest | git revert | Ready |
| DEV-022 | P3-Account | backend | be | AC-047 | **密码找回 API**：POST /auth/forgot-password + /auth/reset-password + 邮件发送 + 1h 过期 | fe | 无 | `backend/app/api/v1/auth.py` (password reset) | pytest: 重置流程 + 过期验证 | pytest | git revert | Ready |
| DEV-023 | P3-Account | frontend | fe | AC-020, AC-021, AC-022, AC-023, AC-024, AC-043, AC-025 | **登录/注册/OAuth 页面**：LoginView（邮箱表单 + 密码强度校验 + Google/Discord mock 按钮 + [Mock] 标识）+ RegisterView + 邮箱验证页面 + 新用户 3 步引导 OnboardingView | be | 无 | `frontend/src/views/LoginView.vue`, `RegisterView.vue`, `OnboardingView.vue`, `stores/auth.ts` | Playwright E2E: 注册 → 验证 → 登录 → 引导 | Playwright + 真实后端 | git revert | Ready |
| DEV-024 | P3-Visual | frontend | fe | AC-015 | **角色立绘组件**：CharacterSprite（≥5 表情 + 情绪标签驱动切换 ≤200ms + 无标签保持当前） | — | 无 | `frontend/src/components/CharacterSprite.vue` | Playwright: 情绪标签 → 表情切换 + 计时 | Playwright + performance.now() | git revert | Ready |
| DEV-025 | P3-Visual | frontend | fe | AC-016 | **场景背景组件**：SceneBackground（≥3 场景 + 节点驱动切换 ≤500ms 淡入） | — | 无 | `frontend/src/components/SceneBackground.vue` | Playwright: 场景切换 + CSS transition 验证 | Playwright | git revert | Ready |
| DEV-026 | P3-Visual | frontend | fe | AC-017 | **BGM 播放器**：AudioPlayer（场景联动 + 淡入淡出 + 静音按钮 + 音量控制） | — | 无 | `frontend/src/components/AudioPlayer.vue`, `composables/useAudio.ts` | Playwright: 场景切换 → BGM 切换 + 静音 | Playwright | git revert | Ready |
| DEV-027 | P3-Visual | frontend | fe | AC-018 | **流式文字动画**：DialogueBox 打字效果（≥30fps + 点击跳过全部显示） | — | 无 | `frontend/src/composables/useTypewriter.ts`, `components/DialogueBox.vue` | Playwright: 文字逐字出现 + requestAnimationFrame 帧率 | Playwright | git revert | Ready |
| DEV-028 | P3-Visual | frontend | fe | AC-019 | **首屏性能优化**：code splitting + 图片懒加载 + 资源预加载 + Service Worker 缓存策略 | — | 无 | `frontend/` (vite.config.ts, lazy imports) | Lighthouse Performance ≥70 (3G Fast) | Lighthouse CI | git revert | Ready |
| DEV-029 | P3-FirstPlay | backend | be | AC-033, AC-034 | **首玩保障后端**：OnboardingService（引导对话脚本 + AI 失败自动兜底 + 首玩完成率埋点记录） | fe, ai | 无 | `backend/app/services/onboarding_service.py` | pytest: 引导触发 + 兜底 + 完成率统计 | pytest | git revert | Ready |
| DEV-030 | P3-FirstPlay | frontend | fe | AC-033, AC-034 | **首玩引导 UI**：GameView onboarding mode（3-5 句引导对话 + 自动进入正常流程 + 埋点上报） | be | 无 | `frontend/src/views/GameView.vue` (onboarding mode) | Playwright: 新用户引导触发 + 老用户跳过 | Playwright | git revert | Ready |
| DEV-031 | P4-Retention | backend | be | AC-026, AC-027, AC-028, AC-029 | **签到系统 API**：GET/POST /daily/checkin + streak 计算（UTC 0:00 + 断签重置）+ Day 3/7/14/30 阶梯奖励 + 碎片发放 | fe | 无 | `backend/app/services/daily_service.py`, `api/v1/daily.py` | pytest: 签到/streak/断签/奖励 | pytest + PostgreSQL + Redis | git revert | Ready |
| DEV-032 | P4-Retention | backend | be | AC-030, AC-031, AC-032 | **每日任务 API**：GET /daily/tasks + POST /daily/tasks/:taskId/claim + 3 任务进度追踪（对话/选择/角色）+ 全完成奖励 + Streak 延续 | fe | 无 | `backend/app/services/task_service.py`, `api/v1/daily.py` | pytest: 任务进度/完成/奖励/streak延续 | pytest | git revert | Ready |
| DEV-033 | P4-Retention | frontend | fe | AC-026, AC-027, AC-028, AC-029, AC-030, AC-031, AC-032 | **签到+任务 UI**：DailyView（签到日历 StreakCalendar + 任务面板 + 进度条 + 奖励弹窗 + toast） | be | 无 | `frontend/src/views/DailyView.vue`, `components/StreakCalendar.vue`, `stores/daily.ts` | Playwright E2E: 签到 + 任务进度 + 奖励弹窗 | Playwright + 真实后端 | git revert | Ready |
| DEV-034 | P4-Monetize | backend | be | AC-035, AC-036, AC-037, AC-038 | **内购系统 API**：GET /shop + POST /shop/purchase + GET /shop/history + IPaymentProvider 抽象接口 + mock 实现（碎片包/装饰包/剧情包 × 多 SKU）+ 交易流水 | fe | 无 | `backend/app/services/payment_service.py`, `api/v1/shop.py` | pytest: 商品列表/mock购买/余额更新/历史/接口替换 | pytest | git revert | Ready |
| DEV-035 | P4-Monetize | backend | be | AC-039, AC-040, AC-041, AC-042 | **订阅系统 API**：GET /subscription/plans + POST /subscription/subscribe + /cancel + GET /status + ISubscriptionProvider 抽象 + 4档×月/年×4货币 mock + 到期降级 + 权益管理 | fe | 无 | `backend/app/services/subscription_service.py`, `api/v1/subscription.py` | pytest: 方案/订阅/取消/到期/降级/接口替换 | pytest | git revert | Ready |
| DEV-036 | P4-Monetize | frontend | fe | AC-035, AC-036, AC-038, AC-039, AC-040 | **商店+订阅 UI**：ShopView（3类商品 + [Mock] 标识 + mock 支付弹窗 + 购买历史）+ SubscriptionView（4档卡片 + 月/年切换 + 4 货币 + [Mock] 标识） | be | 无 | `frontend/src/views/ShopView.vue`, `SubscriptionView.vue` | Playwright E2E: 浏览商品 + mock 购买 + 订阅流程 | Playwright + 真实后端 | git revert | Ready |
| DEV-037 | P5-P1 | backend | ai | AC-048 | **情感节奏**：节点 JSON 增加 emotion_tag（紧张/温馨/悲伤/高潮/平静）+ LLM prompt 注入情绪节奏 + 打字速度和 BGM 音量联动 | fe | 无 | `backend/app/llm/prompts/narrative.py`, `data/scripts/*/emotion_tags.json` | pytest: emotion_tag 解析 + SSE 推送 | pytest | git revert | Ready |
| DEV-038 | P5-P1 | frontend | fe | AC-048 | **情感节奏前端**：解析 SSE emotion_tag → 打字速度变化 + BGM 音量渐变 | be | 无 | `frontend/src/views/GameView.vue`, `composables/useTypewriter.ts` | Playwright: 情绪标签 → 速度/音量变化 | Playwright | git revert | Ready |
| DEV-039 | P5-P1 | backend | be | AC-050, AC-059 | **社交分享+结局卡片**：POST /share/ending（Canvas/sharp 生成 PNG 卡片）+ GET /share/:shareId（公开查看） | fe | 无 | `backend/app/services/share_service.py`, `card_generator.py`, `api/v1/share.py` | pytest: 卡片生成 + 链接可访问 | pytest + 图片校验 | git revert | Ready |
| DEV-040 | P5-P1 | frontend | fe | AC-050, AC-059 | **分享 UI**：结局页面分享按钮 + ShareCard 组件（图片+文字）+ 复制链接 + 保存图片 | be | 无 | `frontend/src/components/ShareCard.vue`, `EndingCard.vue` | Playwright: 分享按钮 → 卡片生成 → 复制/保存 | Playwright | git revert | Ready |
| DEV-041 | P5-P1 | backend | be | AC-051 | **UGC**：game_sessions 增加 custom_name + avatar_choice 字段 + 创建时自定义 | fe | 无 | `backend/app/api/v1/game.py` | pytest: 自定义名称存储和读取 | pytest | git revert | Ready |
| DEV-042 | P5-P1 | frontend | fe | AC-051 | **UGC UI**：开始游戏前角色名称输入（2-12字符）+ 3种预设头像选择 | be | 无 | `frontend/src/views/GameView.vue` (character creation) | Playwright: 输入名称 + 选择头像 | Playwright | git revert | Ready |
| DEV-043 | P5-P1 | frontend | fe | AC-052 | **国际化**：vue-i18n 集成 + en.json 英文翻译 + 设置页语言切换（中/英） | — | 无 | `frontend/src/i18n/`, `views/SettingsView.vue` | Vitest: 切换后 UI 文本变化 | Vitest | git revert | Ready |
| DEV-044 | P5-P1 | backend | be | AC-053 | **CG 画廊 API**：GET /gallery + GET /gallery/:cgId + 解锁状态查询 | fe | 无 | `backend/app/api/v1/gallery.py` | pytest: CG 列表/详情/解锁 | pytest | git revert | Ready |
| DEV-045 | P5-P1 | frontend | fe | AC-053 | **CG 画廊页面**：GalleryView（grid 布局 + 缩略图 + 锁定灰色 + 解锁时间） | be | 无 | `frontend/src/views/GalleryView.vue` | Playwright: 画廊展示 + 锁定/解锁状态 | Playwright | git revert | Ready |
| DEV-046 | P5-P1 | frontend | fe | AC-054 | **SEO**：@vueuse/head meta 标签（title/description/og:image）+ sitemap.xml 生成 + robots.txt | — | 无 | `frontend/public/sitemap.xml`, `robots.txt`, `src/App.vue` | Lighthouse SEO audit ≥90 | Lighthouse | git revert | Ready |
| DEV-047 | P5-P1 | backend | be | AC-055 | **Discord 集成**：DiscordService webhook 通知（新注册/达成结局）+ 配置 Discord webhook URL | fe | 无 | `backend/app/services/discord_service.py` | pytest: webhook 发送（mock server） | pytest | git revert | Ready |
| DEV-048 | P5-P1 | backend | ai | AC-058 | **自由对话 API**：POST /game/:sessionId/free-chat + 5 预设话题配置 + LLM 角色约束生成 | fe | 无 | `backend/app/api/v1/game.py` (free-chat endpoint) | pytest: 话题选择 + LLM 生成 + 角色约束 | pytest + 真实 LLM | git revert | Ready |
| DEV-049 | P5-P1 | frontend | fe | AC-058 | **自由对话 UI**：FreeChatView（5 话题按钮 + 对话展示 + SSE 流式） | be | 无 | `frontend/src/views/FreeChatView.vue` | Playwright: 选择话题 + 对话展示 | Playwright | git revert | Ready |
| DEV-050 | P5-P1 | backend | be | AC-057 | **邮件召回**：RecallService cron job（查询 last_login_at > 7天 + 模板邮件发送） | — | 无 | `backend/app/services/recall_service.py` | pytest: 7天未登录触发 + 邮件发送 | pytest + mock email | git revert | Ready |
| DEV-051 | P5-P1 | frontend | fe | AC-056 | **Push 通知**：Service Worker 通知权限提示 + Notification API | — | 无 | `frontend/src/pwa/notifications.ts` | 手动测试: 浏览器弹出权限请求 | 手动 | git revert | Ready |
| DEV-052 | P5-P1 | frontend | fe | AC-045 | **路线探索图**：剧本详情页路线图（已探索高亮 + 未探索灰色 + 解锁条件提示） | — | 无 | `frontend/src/components/RouteMap.vue` | Playwright: 路线图展示 | Playwright | git revert | Ready |
| DEV-053 | Integration | tests | qa | AC-004, AC-005, AC-012, AC-020, AC-026, AC-035 | **Delivery E2E**：从真实前端入口穿过 Nginx 代理访问真实后端 + health check + 全链路冒烟 | ops | 无 | `tests/e2e/delivery-smoke.spec.ts` | `tests/e2e/delivery-smoke.spec.ts` | Playwright + docker compose | 重跑 pipeline | Ready |
| DEV-054 | Integration | tests | qa | AC-004, AC-005, AC-012, AC-015, AC-020, AC-023, AC-026, AC-030, AC-035, AC-039 | **Browser Interaction E2E**：真实浏览器执行完整用户旅程（注册→登录→选剧本→游戏→选择→好感度→签到→任务→商店→订阅） | — | 无 | `tests/e2e/user-journey.spec.ts` | Playwright: 全流程截图 + trace | Playwright + 真实后端 | 重跑 pipeline | Ready |
| DEV-055 | Integration | frontend | fe | AC-019 | **性能优化迭代**：Lighthouse 全量审计 + 图片压缩 + 字体优化 + 关键 CSS 内联 | — | 无 | `frontend/` | Lighthouse Performance ≥70 | Lighthouse CI | git revert | Ready |
| DEV-056 | Deploy | deploy | ops | AC-004 | **生产 Docker 配置**：multi-stage build + Nginx SSL termination + 环境变量注入 + 健康检查 + 日志 | ops | 无 | `deploy/` | `deploy/docker-compose.prod.yml` | docker compose -f deploy/docker-compose.prod.yml up | docker compose down | Ready |
| DEV-057 | Deploy | deploy | ops | AC-004 | **监控 + 告警**：健康检查 cron + 错误日志收集 + LLM 调用成本监控 | ops | 无 | `deploy/monitoring/` | `deploy/monitoring/healthcheck.sh` | 健康检查脚本通过 | 删除 deploy/monitoring/ | Ready |

## 任务规则

- 每个任务必须关联至少一个 AC 编号。
- 每个涉及 API、页面、管理端或用户动作的任务必须填写 `Consumers`，明确哪个页面、组件、菜单、按钮、调用方或脚本会消费这项能力。
- 不覆盖的 AC 必须显式写入 `不覆盖验收项`；无不覆盖项时写 `无`。
- 声明任务完成前，必须在 `workflow/changes/CR-001/review.md` 写开发覆盖声明。
- Red 失败记录在 DEVELOPMENT 阶段、写业务代码前补齐，不属于 DESIGN 关口必须完成项。

## AC → Task 映射表

> 确保每个 AC 都被至少一个任务覆盖，无遗漏。

| AC 编号 | 优先级 | 覆盖任务 | 备注 |
|---------|--------|---------|------|
| AC-001 | P0 | DEV-007, DEV-008 | 叙事引擎 + LLM |
| AC-002 | P0 | DEV-007, DEV-008 | 规则引擎拦截 |
| AC-003 | P0 | DEV-007, DEV-008 | 兜底机制 |
| AC-004 | P0 | DEV-009, DEV-011, DEV-012, DEV-013, DEV-014 | 剧本全流程 |
| AC-005 | P0 | DEV-009, DEV-014 | 选择+进度持久化 |
| AC-006 | P0 | DEV-009, DEV-014 | 收敛节点 |
| AC-007 | P0 | DEV-009, DEV-014, DEV-016 | 好结局 |
| AC-008 | P0 | DEV-009, DEV-014, DEV-016 | 坏结局+重新开始 |
| AC-009 | P0 | DEV-017 | 记忆存储 |
| AC-010 | P0 | DEV-017 | 跨会话召回 |
| AC-011 | P0 | DEV-017 | 不误召回 |
| AC-012 | P0 | DEV-010, DEV-015 | 好感度更新 |
| AC-013 | P0 | DEV-010, DEV-015 | 等级升级 |
| AC-014 | P0 | DEV-010, DEV-015 | 半隐藏进度条 |
| AC-015 | P0 | DEV-024 | 表情切换 |
| AC-016 | P0 | DEV-025 | 背景切换 |
| AC-017 | P0 | DEV-026 | BGM 切换 |
| AC-018 | P0 | DEV-014, DEV-027 | 流式文字 |
| AC-019 | P0 | DEV-028, DEV-055 | 首屏性能 |
| AC-020 | P0 | DEV-020, DEV-023 | 邮箱注册 |
| AC-021 | P0 | DEV-020, DEV-023 | 重复注册 |
| AC-022 | P0 | DEV-020, DEV-023 | 邮箱验证 |
| AC-023 | P0 | DEV-020, DEV-023 | 登录 |
| AC-024 | P0 | DEV-020, DEV-023 | 密码错误 |
| AC-025 | P0 | DEV-023 | 新用户引导 |
| AC-026 | P0 | DEV-031, DEV-033 | 签到 |
| AC-027 | P0 | DEV-031, DEV-033 | 断签 |
| AC-028 | P0 | DEV-031, DEV-033 | 阶梯奖励 |
| AC-029 | P0 | DEV-031, DEV-033 | 签到日历 |
| AC-030 | P0 | DEV-032, DEV-033 | 任务面板 |
| AC-031 | P0 | DEV-032, DEV-033 | 任务进度 |
| AC-032 | P0 | DEV-032, DEV-033 | 全完成奖励 |
| AC-033 | P0 | DEV-029, DEV-030 | 首玩引导对话 |
| AC-034 | P0 | DEV-029, DEV-030 | 首玩兜底 |
| AC-035 | P0 | DEV-034, DEV-036 | 内购商店 |
| AC-036 | P0 | DEV-034, DEV-036 | mock 购买 |
| AC-037 | P0 | DEV-034 | IPaymentProvider 抽象 |
| AC-038 | P0 | DEV-034, DEV-036 | 购买历史 |
| AC-039 | P0 | DEV-035, DEV-036 | 订阅页面 |
| AC-040 | P0 | DEV-035, DEV-036 | mock 订阅 |
| AC-041 | P0 | DEV-035 | 到期/取消 |
| AC-042 | P0 | DEV-035 | ISubscriptionProvider 抽象 |
| AC-043 | P0 | DEV-021, DEV-023 | OAuth mock |
| AC-044 | P0 | DEV-021 | IOAuthProvider 抽象 |
| AC-045 | P1 | DEV-052 | 路线探索图 |
| AC-046 | P1 | DEV-019 | 记忆压缩 |
| AC-047 | P1 | DEV-022 | 密码找回 |
| AC-048 | P1 | DEV-037, DEV-038 | 情感节奏 |
| AC-049 | P1 | DEV-018 | AI 风格化 |
| AC-050 | P1 | DEV-039, DEV-040 | 社交分享 |
| AC-051 | P1 | DEV-041, DEV-042 | UGC |
| AC-052 | P1 | DEV-043 | 国际化 |
| AC-053 | P1 | DEV-044, DEV-045 | CG 画廊 |
| AC-054 | P1 | DEV-046 | SEO |
| AC-055 | P1 | DEV-047 | Discord |
| AC-056 | P1 | DEV-051 | Push 通知 |
| AC-057 | P1 | DEV-050 | 邮件召回 |
| AC-058 | P1 | DEV-048, DEV-049 | 自由对话 |
| AC-059 | P1 | DEV-039, DEV-040 | 结局分享卡片 |

## AC 覆盖完整性检查

- **P0 AC 数量**：44 项（AC-001 ~ AC-044），全部有任务覆盖 ✅
- **P1 AC 数量**：15 项（AC-045 ~ AC-059），全部有任务覆盖 ✅
- **总 AC 数量**：59 项
- **总任务数量**：57 项（DEV-001 ~ DEV-057）
- **无覆盖 AC**：0
- **任务与 AC 覆盖完整，可进入 DESIGN_GATE 审查。**

## 工期评估

### 方案 A：3 人团队（1 BE + 1 FE + 1 AI/BE）

| 阶段 | 周期 | 并行度 | 风险 |
|------|------|--------|------|
| 基础设施 (DEV-001~006) | Week 1 | BE+FE 并行 | 低 |
| 核心循环 (DEV-007~016) | Week 2-5 | BE 叙事+好感度，AI LLM+记忆，FE 游戏UI | 高（叙事引擎复杂，1人串行） |
| 账户+视觉 (DEV-020~030) | Week 5-7 | FE 页面+组件，BE 认证 | 中（美术资源依赖） |
| 留存+商业 (DEV-031~036) | Week 7-9 | BE API + FE 页面 | 低 |
| P1 扩展 (DEV-037~052) | Week 9-13 | 全栈 | 高（16 个 P1 任务串行） |
| 联调+QA (DEV-053~055) | Week 13-15 | QA 主导 | 中 |
| 部署+发布 (DEV-056~057) | Week 15-16 | Ops | 低 |
| **总计** | **16 周（4 月）** | | **超出 Q3 目标，需裁剪 P1** |

**3 人团队裁剪方案**：P1 只保留 DEV-037/038（情感节奏）+ DEV-043（国际化）+ DEV-044/045（CG 画廊），砍掉其余 P1 → **12 周（3 月）** 可达 P0 发布。

### 方案 B：5 人团队（2 BE + 1 FE + 1 AI + 1 QA）— 推荐

| 阶段 | 周期 | 并行度 | 风险 |
|------|------|--------|------|
| 基础设施 (DEV-001~006) | Week 1 | BE1 infra + BE2 auth + FE 骨架 + AI LLM 调研 | 低 |
| 核心循环 (DEV-007~016) | Week 2-4 | BE1 叙事引擎 + BE2 剧本API + AI LLM Gateway + FE 游戏UI | 中 |
| 记忆+账户 (DEV-017~023) | Week 3-5 | AI 记忆系统 + BE2 认证 + FE 登录/引导 | 低 |
| 视觉+留存 (DEV-024~033) | Week 5-7 | FE 全部组件 + BE1 签到/任务 | 低 |
| 商业+P1 (DEV-034~052) | Week 7-10 | BE1 支付/订阅 + BE2 P1后端 + AI P1 + FE P1 | 中 |
| 联调+QA (DEV-053~055) | Week 10-11 | QA 全量 E2E + 性能优化 | 低 |
| 部署+发布 (DEV-056~057) | Week 12 | Ops 主导 | 低 |
| **总计** | **12 周（3 月）** | | **符合 Q3 上线目标** ✅ |

**关键路径**：DEV-007(叙事引擎) → DEV-009(剧本API) → DEV-014(游戏UI) → DEV-017(记忆) → DEV-053(联调)

### 方案 C：7 人团队（2 BE + 2 FE + 1 AI + 1 QA + 1 内容/美术）

| 阶段 | 周期 | 并行度 | 风险 |
|------|------|--------|------|
| 基础设施 (DEV-001~006) | Week 1 | 全员并行 | 低 |
| 核心循环 (DEV-007~016) | Week 2-3 | BE1+BE2+AI+FE1+FE2 全并行 + 内容生产3剧本 | 低 |
| 记忆+账户+视觉 (DEV-017~030) | Week 3-5 | AI 记忆 + BE 认证 + FE1 组件 + FE2 页面 | 低 |
| 留存+商业+P1 (DEV-031~052) | Week 5-8 | 全员并行 | 中 |
| 联调+QA (DEV-053~055) | Week 8-9 | QA 全量 | 低 |
| 部署+发布 (DEV-056~057) | Week 10 | Ops | 低 |
| **总计** | **10 周（2.5 月）** | | 提前完成，需美术/内容提前到位 |

### 推荐方案与预计完成时间

**推荐方案 B（5 人团队）**：

- 设计关口通过（本周）→ **立即进入 DEVELOPMENT**
- Phase 0 基础设施：Week 1（5 个工作日）
- Phase 1-5 功能开发：Week 2-10（9 周）
- Phase 6 联调 QA：Week 10-11（2 周）
- Phase 7 部署发布：Week 12（1 周）
- **预计完成时间：设计关口通过后 12 周**
- 如果今天是 Week 0，则 **Week 12 可交付**

**3 人团队备选**：P0 全量 + P1 精简（3 个模块）→ 12 周；P1 全量 → 16 周。

### 关键风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| 美术资源产出慢（3 剧本 × 多角色 × 5 表情） | 阻塞 DEV-024~026 | Week 1 启动外包/AI 生成；优先乙女恋爱 |
| LLM 质量不达标 | 核心体验降级 | 关键节点 100% 人工预设；兜底对话全覆盖 |
| 叙事引擎复杂度超预期 | 阻塞核心循环 | 状态机 + JSON 剧本数据，不做运行时编辑器 |
| P1 模块超期 | 影响发布 | 严格按 MAS 执行；超期砍 P1 不追加时间 |
| pgvector 性能瓶颈 | 记忆召回慢 | MVP <100K 向量足够；后续可迁移专用向量库 |