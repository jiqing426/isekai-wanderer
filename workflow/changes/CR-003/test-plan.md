# CR-003 Test Plan

## Test-First Scope

- 剧本发现（CR3-003/004）：Red → Green，先写 pytest 用例（discover 筛选/排序/推荐 fallback），再实现 API
- 角色卡片（CR3-007/008）：Red → Green，先写 pytest 用例（角色列表/详情/好感度排行/关注），再实现 API
- 存档管理（CR3-012/013/014）：Red → Green，先写 pytest 用例（存档 CRUD/快照/fork/结局进度），再实现 API
- 碎片可视化（CR3-018）：Red → Green，先写 pytest 用例（summary API），再实现 API
- 成就系统（CR3-020/021）：Red → Green，先写 pytest 用例（成就触发/领取/防重复），再实现 API
- 每日任务（CR3-023/024）：Red → Green，先写 pytest 用例（活跃度/宝箱/日切割），再实现 API

## Test Case Artifacts

| 任务编号 | 测试用例产物 | 覆盖验收项 | 状态 |
|---------|-------------|-----------|------|
| CR3-003 | backend/tests/test_discover_api.py | AC-DISC-001.1, AC-DISC-001.2, AC-DISC-003.1, AC-DISC-003.2, AC-DISC-003.3, AC-DISC-003.4 | Ready |
| CR3-004 | backend/tests/test_recommendation.py | AC-DISC-002.1, AC-DISC-002.2, AC-DISC-002.3 | Ready |
| CR3-005 | frontend/tests/discover.spec.ts | AC-DISC-001.1, AC-DISC-001.2, AC-DISC-003.1, AC-DISC-003.2, AC-DISC-003.3, AC-DISC-003.4, AC-DISC-004.1, AC-DISC-004.2, AC-DISC-004.3 | Ready |
| CR3-006 | frontend/tests/continue_card.spec.ts | AC-DISC-005.1, AC-DISC-005.2, AC-DISC-005.3, AC-DISC-005.4, AC-DISC-005.5 | Ready |
| CR3-007 | backend/tests/test_character_api.py | AC-CHAR-001.1, AC-CHAR-001.2, AC-CHAR-001.3, AC-CHAR-001.5, AC-CHAR-002.1, AC-CHAR-002.3, AC-CHAR-003.1, AC-CHAR-003.3 | Ready |
| CR3-008 | backend/tests/test_follows_api.py | AC-CHAR-004.1, AC-CHAR-004.2, AC-CHAR-004.5 | Ready |
| CR3-009 | frontend/tests/characters.spec.ts | AC-CHAR-001.1, AC-CHAR-001.2, AC-CHAR-001.3, AC-CHAR-001.4, AC-CHAR-001.5, AC-CHAR-002.1, AC-CHAR-002.2, AC-CHAR-002.3 | Ready |
| CR3-010 | frontend/tests/dialogue_preview.spec.ts | AC-CHAR-003.1, AC-CHAR-003.2, AC-CHAR-003.3 | Ready |
| CR3-011 | frontend/tests/follow_button.spec.ts | AC-CHAR-004.1, AC-CHAR-004.2, AC-CHAR-004.4, AC-CHAR-004.5 | Ready |
| CR3-012 | backend/tests/test_saves_api.py | AC-SAVE-001.1, AC-SAVE-001.2, AC-SAVE-001.3, AC-SAVE-001.5, AC-SAVE-001.7, AC-SAVE-001.8, AC-SAVE-002.1, AC-SAVE-002.2, AC-SAVE-002.3 | Ready |
| CR3-013 | backend/tests/test_snapshot_api.py, backend/tests/test_snapshot_cleanup.py | AC-SAVE-003.1, AC-SAVE-003.2, AC-SAVE-003.3, AC-SAVE-003.4, AC-SAVE-003.5, AC-SAVE-003.6, AC-SAVE-003.7 | Ready |
| CR3-014 | backend/tests/test_ending_progress_api.py | AC-SAVE-004.1, AC-SAVE-004.2, AC-SAVE-004.3, AC-SAVE-004.4, AC-SAVE-004.5 | Ready |
| CR3-015 | frontend/tests/save_manager.spec.ts | AC-SAVE-001.1, AC-SAVE-001.2, AC-SAVE-001.3, AC-SAVE-001.4, AC-SAVE-001.5, AC-SAVE-001.6, AC-SAVE-001.7, AC-SAVE-001.8, AC-SAVE-001.9, AC-SAVE-002.1 | Ready |
| CR3-016 | frontend/tests/snapshot_timeline.spec.ts | AC-SAVE-003.2, AC-SAVE-003.3, AC-SAVE-003.4, AC-SAVE-003.5, AC-SAVE-003.7 | Ready |
| CR3-017 | frontend/tests/ending_progress.spec.ts | AC-SAVE-004.1, AC-SAVE-004.3, AC-SAVE-004.4, AC-SAVE-004.5 | Ready |
| CR3-018 | backend/tests/test_shard_api.py | AC-SHARD-001.1, AC-SHARD-001.4, AC-SHARD-002.1, AC-SHARD-002.2, AC-SHARD-002.3, AC-SHARD-002.5 | Ready |
| CR3-019 | frontend/tests/shard_center.spec.ts | AC-SHARD-001.1, AC-SHARD-001.2, AC-SHARD-001.3, AC-SHARD-001.4, AC-SHARD-002.1, AC-SHARD-002.2, AC-SHARD-002.3, AC-SHARD-002.5, AC-SHARD-003.1, AC-SHARD-003.2, AC-SHARD-003.3, AC-SHARD-003.4, AC-SHARD-003.5 | Ready |
| CR3-020 | backend/tests/test_achievement_api.py, backend/tests/test_achievement_triggers.py | AC-ACH-001.1, AC-ACH-001.2, AC-ACH-001.3, AC-ACH-002.2, AC-ACH-002.3, AC-ACH-002.4, AC-ACH-003.1, AC-ACH-003.2, AC-ACH-003.3, AC-ACH-003.4, AC-ACH-003.5, AC-ACH-003.6 | Ready |
| CR3-021 | backend/tests/test_achievement_claim.py | AC-ACH-004.1, AC-ACH-004.2, AC-ACH-004.3, AC-ACH-004.4, AC-ACH-004.5 | Ready |
| CR3-022 | frontend/tests/achievement.spec.ts | AC-ACH-002.1, AC-ACH-002.2, AC-ACH-002.3, AC-ACH-002.4, AC-ACH-002.5, AC-ACH-004.1, AC-ACH-004.2, AC-ACH-004.3, AC-ACH-004.4 | Ready |
| CR3-023 | backend/tests/test_daily_task_api.py | AC-TASK-001.1, AC-TASK-001.2, AC-TASK-001.3, AC-TASK-001.4, AC-TASK-001.5, AC-TASK-001.6, AC-TASK-002.1, AC-TASK-002.2, AC-TASK-002.3 | Ready |
| CR3-024 | backend/tests/test_activity_api.py | AC-TASK-003.1, AC-TASK-003.2, AC-TASK-003.3, AC-TASK-003.4, AC-TASK-003.5, AC-TASK-003.6, AC-TASK-003.7 | Ready |
| CR3-025 | frontend/tests/task_panel.spec.ts | AC-TASK-001.1, AC-TASK-001.3, AC-TASK-001.4, AC-TASK-001.6, AC-TASK-002.1, AC-TASK-002.2, AC-TASK-002.3 | Ready |
| CR3-026 | frontend/tests/activity_chest.spec.ts | AC-TASK-003.1, AC-TASK-003.3, AC-TASK-003.4, AC-TASK-003.5, AC-TASK-003.6, AC-TASK-003.7, AC-TASK-003.8 | Ready |
| CR3-027 | frontend/tests/animations.spec.ts | AC-TASK-004.4, AC-TASK-004.5 | Ready |
| CR3-028 | frontend/tests/navigation.spec.ts | AC-DISC-001.1, AC-CHAR-001.1, AC-SAVE-001.1, AC-SHARD-001.4, AC-ACH-002.1 | Ready |

## Red Failure Records

| 任务编号 | 测试用例产物 | 预期 Red 场景 | 状态 |
|---------|-------------|-------------|------|
| CR3-003 | backend/tests/test_discover_api.py | discover API 未实现时返回 404 | Recorded |
| CR3-004 | backend/tests/test_recommendation.py | recommendations API 未实现时返回 404 | Recorded |
| CR3-007 | backend/tests/test_character_api.py | characters API 未实现时返回 404 | Recorded |
| CR3-008 | backend/tests/test_follows_api.py | follows API 未实现时返回 404 | Recorded |
| CR3-012 | backend/tests/test_saves_api.py | saves API 未实现时返回 404 | Recorded |
| CR3-013 | backend/tests/test_snapshot_api.py | snapshot API 未实现时返回 404 | Recorded |
| CR3-018 | backend/tests/test_shard_api.py | shards API 未实现时返回 404 | Recorded |
| CR3-020 | backend/tests/test_achievement_api.py | achievements API 未实现时返回 404 | Recorded |
| CR3-023 | backend/tests/test_daily_task_api.py | daily tasks 扩展 API 未实现时返回 404 | Recorded |
| CR3-024 | backend/tests/test_activity_api.py | activity API 未实现时返回 404 | Recorded |

## CI/CD Evidence Plan

| 阶段 | 触发时机 | 命令 / Pipeline | 覆盖验收项 | 负责人 | 记录位置 | 状态 |
|------|---------|----------------|-----------|--------|---------|------|
| Lint | PR push | `cd backend && ruff check . && cd ../frontend && npm run lint` | AC-DISC-001.1, AC-CHAR-001.1, AC-SAVE-001.1, AC-SHARD-001.1, AC-ACH-001.1, AC-TASK-001.1 | QA | CI log | Ready |
| BE Unit | PR push | `cd backend && pytest tests/ -v --tb=short` | AC-DISC-001.1, AC-DISC-002.1, AC-DISC-003.1, AC-CHAR-001.1, AC-CHAR-002.1, AC-CHAR-003.1, AC-CHAR-004.1, AC-SAVE-001.1, AC-SAVE-002.1, AC-SAVE-003.1, AC-SAVE-004.1, AC-SHARD-001.1, AC-SHARD-002.1, AC-SHARD-003.1, AC-ACH-001.1, AC-ACH-002.1, AC-ACH-003.1, AC-ACH-004.1, AC-TASK-001.1, AC-TASK-002.1, AC-TASK-003.1 | QA | CI log | Ready |
| FE Unit | PR push | `cd frontend && npx vitest run --reporter=verbose` | AC-DISC-001.1, AC-DISC-005.1, AC-CHAR-001.1, AC-CHAR-003.1, AC-CHAR-004.1, AC-SAVE-001.1, AC-SAVE-003.1, AC-SAVE-004.1, AC-SHARD-001.1, AC-ACH-002.1, AC-TASK-001.1, AC-TASK-002.1, AC-TASK-003.1, AC-TASK-004.1 | QA | CI log | Ready |

## Delivery E2E / Runtime Smoke Plan

| 任务编号 | 命令 / 步骤 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
|---------|------------|---------|---------|-----------------|---------|-----------|-------------|------|
| CR3-003 | `docker compose up -d && curl -s http://localhost:8000/health && curl -s http://localhost:3000/discover` | http://localhost:3000 | http://localhost:8000 | /api/v1/scripts/discover | no | AC-DISC-001.1, AC-DISC-003.1 | workflow/changes/CR-003/test-report.md | Ready |
| CR3-007 | `curl -s http://localhost:8000/api/v1/characters && curl -s http://localhost:3000/characters` | http://localhost:3000 | http://localhost:8000 | /api/v1/characters | no | AC-CHAR-001.1, AC-CHAR-002.1 | workflow/changes/CR-003/test-report.md | Ready |
| CR3-012 | `curl -s http://localhost:8000/api/v1/saves -H "Authorization: Bearer $TOKEN" && curl -s http://localhost:3000/saves` | http://localhost:3000 | http://localhost:8000 | /api/v1/saves | no | AC-SAVE-001.1, AC-SAVE-002.1 | workflow/changes/CR-003/test-report.md | Ready |
| CR3-018 | `curl -s http://localhost:8000/api/v1/shards/summary -H "Authorization: Bearer $TOKEN" && curl -s http://localhost:3000/shards` | http://localhost:3000 | http://localhost:8000 | /api/v1/shards/summary | no | AC-SHARD-001.1, AC-SHARD-002.1 | workflow/changes/CR-003/test-report.md | Ready |
| CR3-020 | `curl -s http://localhost:8000/api/v1/achievements -H "Authorization: Bearer $TOKEN" && curl -s http://localhost:3000/achievements` | http://localhost:3000 | http://localhost:8000 | /api/v1/achievements | no | AC-ACH-001.1, AC-ACH-002.1 | workflow/changes/CR-003/test-report.md | Ready |
| CR3-024 | `curl -s http://localhost:8000/api/v1/daily/activity -H "Authorization: Bearer $TOKEN"` | http://localhost:3000 | http://localhost:8000 | /api/v1/daily/activity | no | AC-TASK-001.1, AC-TASK-003.1 | workflow/changes/CR-003/test-report.md | Ready |

## Browser Interaction E2E Plan

| 任务编号 | 命令 / 步骤 | Browser / Tool | 用户动作 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
|---------|------------|---------------|---------|---------|---------|-----------------|---------|-----------|-------------|------|
| CR3-005 | `cd frontend && npx playwright test discover.spec.ts` | Playwright Chromium | 1. 导航到 /discover 2. 点击筛选栏选择"恋爱" 3. 验证列表过滤 4. 点击排序选择"最多人玩" 5. 验证排行 | http://localhost:3000 | http://localhost:8000 | /api/v1/scripts/discover | no | AC-DISC-001.1, AC-DISC-001.2, AC-DISC-003.1, AC-DISC-003.2, AC-DISC-003.3, AC-DISC-003.4, AC-DISC-004.1 | workflow/changes/CR-003/test-report.md | Ready |
| CR3-006 | `cd frontend && npx playwright test continue_card.spec.ts` | Playwright Chromium | 1. 登录有未完成 session 的账号 2. 访问首页 3. 验证继续玩卡片显示 4. 点击继续游戏 5. 验证跳转 | http://localhost:3000 | http://localhost:8000 | /api/v1/game/continue | no | AC-DISC-005.1, AC-DISC-005.2, AC-DISC-005.3, AC-DISC-005.5 | workflow/changes/CR-003/test-report.md | Ready |
| CR3-009 | `cd frontend && npx playwright test characters.spec.ts` | Playwright Chromium | 1. 导航到 /characters 2. 验证角色卡片网格 3. 点击已解锁角色 4. 验证详情页 5. 搜索角色 | http://localhost:3000 | http://localhost:8000 | /api/v1/characters | no | AC-CHAR-001.1, AC-CHAR-001.2, AC-CHAR-001.3, AC-CHAR-001.5, AC-CHAR-002.1 | workflow/changes/CR-003/test-report.md | Ready |
| CR3-011 | `cd frontend && npx playwright test follow_button.spec.ts` | Playwright Chromium | 1. 进入角色详情页 2. 点击关注按钮 3. 验证状态切换 4. 再次点击取消关注 | http://localhost:3000 | http://localhost:8000 | /api/v1/follows | no | AC-CHAR-004.1, AC-CHAR-004.2, AC-CHAR-004.5 | workflow/changes/CR-003/test-report.md | Ready |
| CR3-015 | `cd frontend && npx playwright test save_manager.spec.ts` | Playwright Chromium | 1. 导航到 /saves 2. 验证存档列表 3. 重命名存档 4. 删除存档（确认弹窗） 5. 点击继续游戏 | http://localhost:3000 | http://localhost:8000 | /api/v1/saves | no | AC-SAVE-001.1, AC-SAVE-001.2, AC-SAVE-001.3, AC-SAVE-001.5, AC-SAVE-001.6, AC-SAVE-001.7 | workflow/changes/CR-003/test-report.md | Ready |
| CR3-016 | `cd frontend && npx playwright test snapshot_timeline.spec.ts` | Playwright Chromium | 1. 展开快照时间线 2. 验证快照列表 3. 点击"从这里重新开始" 4. 验证 fork | http://localhost:3000 | http://localhost:8000 | /api/v1/game/:sessionId/fork | no | AC-SAVE-003.3, AC-SAVE-003.4 | workflow/changes/CR-003/test-report.md | Ready |
| CR3-017 | `cd frontend && npx playwright test ending_progress.spec.ts` | Playwright Chromium | 1. 查看结局进度 2. 验证进度条 3. 查看未解锁结局提示 | http://localhost:3000 | http://localhost:8000 | /api/v1/scripts/:id/ending-progress | no | AC-SAVE-004.1, AC-SAVE-004.3, AC-SAVE-004.4 | workflow/changes/CR-003/test-report.md | Ready |
| CR3-019 | `cd frontend && npx playwright test shard_center.spec.ts` | Playwright Chromium | 1. 导航到 /shards 2. 验证余额显示 3. 点击用途卡片 4. 验证跳转 5. 查看消费记录 | http://localhost:3000 | http://localhost:8000 | /api/v1/shards/summary | no | AC-SHARD-001.1, AC-SHARD-001.2, AC-SHARD-001.3, AC-SHARD-002.1, AC-SHARD-003.1 | workflow/changes/CR-003/test-report.md | Ready |
| CR3-022 | `cd frontend && npx playwright test achievement.spec.ts` | Playwright Chromium | 1. 导航到 /achievements 2. 切换分类 tab 3. 验证成就卡片 4. 点击领取奖励 | http://localhost:3000 | http://localhost:8000 | /api/v1/achievements | no | AC-ACH-002.1, AC-ACH-002.2, AC-ACH-002.4, AC-ACH-002.5, AC-ACH-004.1 | workflow/changes/CR-003/test-report.md | Ready |
| CR3-025 | `cd frontend && npx playwright test task_panel.spec.ts` | Playwright Chromium | 1. 访问首页 2. 展开任务面板 3. 验证任务列表 4. 领取任务奖励 5. 验证进度条更新 | http://localhost:3000 | http://localhost:8000 | /api/v1/daily/tasks | no | AC-TASK-001.1, AC-TASK-001.3, AC-TASK-001.4, AC-TASK-002.1, AC-TASK-002.2 | workflow/changes/CR-003/test-report.md | Ready |
| CR3-026 | `cd frontend && npx playwright test activity_chest.spec.ts` | Playwright Chromium | 1. 完成任务获得活跃度 2. 验证宝箱亮起 3. 点击宝箱 4. 验证开箱动画+奖励 | http://localhost:3000 | http://localhost:8000 | /api/v1/daily/chest/claim | no | AC-TASK-003.3, AC-TASK-003.4, AC-TASK-003.5 | workflow/changes/CR-003/test-report.md | Ready |
| CR3-028 | `cd frontend && npx playwright test navigation.spec.ts` | Playwright Chromium | 1. 验证底部 Tab Bar 导航 2. 点击发现/角色/我的 3. 验证路由跳转 | http://localhost:3000 | http://localhost:8000 | /api/v1/health | no | AC-DISC-001.1, AC-CHAR-001.1, AC-SAVE-001.1 | workflow/changes/CR-003/test-report.md | Ready |
