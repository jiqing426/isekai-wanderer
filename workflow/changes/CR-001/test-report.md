# Test Report — CR-001 Isekai Wanderer MVP

| 项 | 内容 |
| --- | --- |
| 测试结论 | PASS — 所有 P0 验收项已覆盖，0 阻塞性缺陷，可发布。 |

## CI/CD Execution Results

| 类型 | 命令 / Pipeline | 触发来源 | 覆盖验收项 | Mock API | 结果 | 证据链接 / 日志 | 负责人 |
|------|----------------|----------|-----------|----------|------|-----------------|--------|
| pytest | `cd backend && python -m pytest tests/ -v --tb=short` | local | AC-001, AC-002, AC-003, AC-006, AC-009, AC-010, AC-011, AC-012, AC-013, AC-027, AC-037, AC-042 | no | passed | 180/180 passed | qa |
| vitest | `cd frontend && npx vitest run` | local | AC-020, AC-021, AC-023 | no | passed | 15/15 passed | qa |
| build | `cd frontend && npm run build` | local | AC-004, AC-005, AC-014, AC-025 | no | passed | 0 errors 7.98s | qa |
| security | `python verify_security_fixes.py` | local | AC-020, AC-023, AC-024 | no | passed | 5/5 fixes verified | pl |

## Delivery E2E / Runtime Smoke Results

| 命令 / 步骤 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 结果 | 证据链接 / 日志 | 负责人 |
|-------------|----------|----------|-----------------|----------|-----------|------|-----------------|--------|
| curl /health | http://localhost:3000 | http://localhost:8000 | /health | no | AC-004 | passed | health:ok | qa |
| POST /auth/register then POST /auth/login | http://localhost:3000 | http://localhost:8000 | /api/v1/auth/register, /api/v1/auth/login | no | AC-020, AC-021, AC-023 | passed | 200 plus token returned | qa |
| POST /auth/refresh | http://localhost:3000 | http://localhost:8000 | /api/v1/auth/refresh | no | AC-023 | passed | 200 plus new token | pl |
| GET /scripts then POST /game/start then GET /game/id | http://localhost:3000 | http://localhost:8000 | /api/v1/scripts, /api/v1/game/start, /api/v1/game/id | no | AC-004, AC-005 | passed | 200 plus session_id plus node_id | qa |
| POST /game/id/choice | http://localhost:3000 | http://localhost:8000 | /api/v1/game/id/choice | no | AC-005, AC-006, AC-012 | passed | 201 plus next node plus affection | qa |
| GET /affection plus GET /affection/id | http://localhost:3000 | http://localhost:8000 | /api/v1/affection, /api/v1/affection/id | no | AC-012, AC-013, AC-014 | passed | 200 plus level plus value | qa |
| POST /daily/checkin plus GET /daily/stats plus GET /daily/tasks | http://localhost:3000 | http://localhost:8000 | /api/v1/daily/checkin, /api/v1/daily/stats, /api/v1/daily/tasks | no | AC-026, AC-027, AC-030, AC-031, AC-032 | passed | 200 plus streak plus 3 tasks | qa |
| GET /memories plus GET /memories/recall | http://localhost:3000 | http://localhost:8000 | /api/v1/memories, /api/v1/memories/recall | no | AC-009, AC-010, AC-011 | passed | 200 plus recall results | qa |
| GET /subscription/plans plus POST /subscription/subscribe | http://localhost:3000 | http://localhost:8000 | /api/v1/subscription/plans, /api/v1/subscription/subscribe | no | AC-039, AC-040, AC-042 | passed | 200 plus 4 plans plus subscribe ok | qa |
| GET /gallery/cgs plus GET /gallery/collections plus GET /gallery/achievements | http://localhost:3000 | http://localhost:8000 | /api/v1/gallery/cgs, /api/v1/gallery/collections, /api/v1/gallery/achievements | no | AC-053 | passed | 200 plus items | qa |
| POST /community/posts plus GET /community/posts | http://localhost:3000 | http://localhost:8000 | /api/v1/community/posts | no | AC-051 | passed | 200 plus post created | qa |
| POST /share/generate | http://localhost:3000 | http://localhost:8000 | /api/v1/share/generate | no | AC-050, AC-059 | passed | 200 plus share link | qa |
| POST /moderation/check | http://localhost:3000 | http://localhost:8000 | /api/v1/moderation/check | no | AC-001, AC-002 | passed | 200 plus safe | qa |
| POST /auth/oauth/google | http://localhost:3000 | http://localhost:8000 | /api/v1/auth/oauth/google | no | AC-043, AC-044 | passed | 200 plus OAuth token | qa |
| GET /user/profile plus PUT /user/profile | http://localhost:3000 | http://localhost:8000 | /api/v1/user/profile | no | AC-025 | passed | 200 plus onboarding_completed | qa |

## Browser Interaction E2E Results

| 命令 / 步骤 | Browser / Tool | 用户动作 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 结果 | 证据链接 / 日志 | 负责人 |
|-------------|---------------|----------|----------|----------|-----------------|----------|-----------|------|-----------------|--------|
| node tests/integration-e2e.cjs path1 | Chromium Playwright | 填写邮箱密码点击注册，填写邮箱密码点击登录，完成3步引导，进入首页 | http://localhost:3000 | http://localhost:8000 | /api/v1/auth/register, /api/v1/auth/login, /api/v1/user/profile | no | AC-020, AC-021, AC-023, AC-025 | passed | e2e-screens/integration/01-login.png, 02-register.png, 03-onboarding.png, 04-home.png | qa |
| node tests/integration-e2e.cjs path2 | Chromium Playwright | 浏览剧本列表，点击开始游戏，阅读对话内容，点击继续 | http://localhost:3000 | http://localhost:8000 | /api/v1/scripts, /api/v1/game/start, /api/v1/game/id | no | AC-004, AC-005 | passed | e2e-screens/integration/05-game-dialogue.png, 06-game-choice.png | qa |
| node tests/integration-e2e.cjs path3 | Chromium Playwright | 选择对话选项，查看好感度侧栏变化，点击好感度进度条展开数值 | http://localhost:3000 | http://localhost:8000 | /api/v1/game/id/choice, /api/v1/affection | no | AC-005, AC-006, AC-012, AC-013, AC-014 | passed | e2e-screens/integration/07-affection.png | qa |
| node tests/integration-e2e.cjs path4 | Chromium Playwright | 点击签到按钮，查看签到结果弹窗，查看连续签到天数 | http://localhost:3000 | http://localhost:8000 | /api/v1/daily/checkin, /api/v1/daily/stats | no | AC-026, AC-027 | passed | e2e-screens/integration/08-checkin.png, 09-checkin-result.png | qa |
| node tests/integration-e2e.cjs path5 | Chromium Playwright | 浏览订阅方案卡片，切换月付年付，查看功能对比表，进入商店页面 | http://localhost:3000 | http://localhost:8000 | /api/v1/subscription/plans, /api/v1/payment/plans | no | AC-035, AC-036, AC-038, AC-039 | passed | e2e-screens/integration/10-subscription.png, 11-shop.png | qa |
| node tests/integration-e2e.cjs path6 | Chromium Playwright | 浏览画廊CG图鉴，切换角色图鉴标签，查看成就墙，进入社区帖子列表，点击分享按钮 | http://localhost:3000 | http://localhost:8000 | /api/v1/gallery/cgs, /api/v1/community/posts, /api/v1/share/generate | no | AC-050, AC-051, AC-053, AC-059 | passed | e2e-screens/integration/12-gallery.png, 13-community.png, 14-share.png | qa |

## 安全修复验证

| 安全修复 | 验证命令 | 结果 |
|----------|----------|------|
| CRIT-001 OAuth 限速 | 15 次连续 OAuth 请求 | 第 11 次返回 429 |
| CRIT-002 登录锁定 | 6 次错误密码登录 | 第 6 次返回 429 |
| CRIT-003 游戏会话 IDOR | User B 访问 User A 会话 | 返回 403 |
| HIGH-001 Refresh Token | POST /auth/refresh | 返回 200 加新 token |
| HIGH-003 JWT 密钥警告 | uvicorn 启动日志 | 打印安全警告 |

## 未覆盖项（已批准暂缓）

| AC | 原因 | 处理方式 |
|----|------|----------|
| AC-015, AC-016, AC-017, AC-018 | 视觉性能需浏览器手动验证 | deferred_with_approval |
| AC-019 | Lighthouse CI 需 ops 配置 | deferred_with_approval |
| AC-022 | 邮件服务不在 MVP 范围 | deferred_with_approval |
| AC-034 | k6 压测需独立环境 | deferred_with_approval |
| AC-028, AC-029 | 签到奖励日历需种子数据 | deferred_with_approval |
| AC-041 | 订阅到期需时间测试 | deferred_with_approval |
