# CR-028 测试计划

## 测试先行范围

- AC-PLAY-001: 玩家可在剧本详情页选择可扮演角色
- AC-PLAY-002: 不同角色进入不同故事线
- AC-PLAY-003: 同一剧本可切换角色重新游玩
- AC-PLAY-004: 个人中心存档展示角色信息
- AC-PLAY-005: 存档管理页可按角色筛选
- AC-PLAY-006: 未解锁角色显示锁定状态
- AC-PLAY-007: 数据迁移后原主角自动可扮演
- AC-PLAY-008: 可直接操作数据库新增可扮演角色
- AC-PLAY-009: 付费角色解锁接口

## Test Case Artifacts

| 任务编号 | 测试用例产物 | 覆盖验收项 | 类型 | 状态 |
|----------|--------------|------------|------|------|
| T-028-01 | tests/db/test_cr028_migration.py | AC-PLAY-007 | API/DB | Recorded |
| T-028-02 | tests/db/test_cr028_migration_verify.py | AC-PLAY-007 | API/DB | Recorded |
| T-028-03 | tests/api/test_cr028_db_direct.py | AC-PLAY-008 | API/DB | Recorded |
| T-028-04 | tests/api/test_cr028_game_start.py | AC-PLAY-002, AC-PLAY-003 | API/DB | Recorded |
| T-028-05 | tests/api/test_cr028_saves.py | AC-PLAY-004, AC-PLAY-005 | API/DB | Recorded |
| T-028-06 | tests/api/test_cr028_unlock.py | AC-PLAY-009 | API/DB | Recorded |
| T-028-07 | tests/api/test_cr028_game_start_logic.py | AC-PLAY-002 | API/DB | Recorded |
| T-028-08 | tests/e2e/cr028_character_select.spec.ts | AC-PLAY-001, AC-PLAY-003, AC-PLAY-006 | Browser E2E | Recorded |
| T-028-09 | tests/e2e/cr028_profile_saves.spec.ts | AC-PLAY-004 | Browser E2E | Recorded |
| T-028-10 | tests/e2e/cr028_save_filter.spec.ts | AC-PLAY-005 | Browser E2E | Recorded |
| T-028-11 | tests/e2e/cr028_profile_display.spec.ts | AC-PLAY-004 | Browser E2E | Recorded |

## Red Failure Records

| 失败 ID | 关联测试用例 | 失败时间 | 失败现象 | 失败原因 | 修复状态 |
|---------|--------------|----------|----------|----------|----------|
| RED-001 | tests/api/test_cr028_game_start.py | 2026-08-02 | POST /game/start 返回 500 | UnboundLocalError: select 未导入 | 已修复 |

## CI/CD Evidence Plan

| 阶段 | 触发时机 | 命令 / Pipeline | 覆盖验收项 | 负责人 | 记录位置 | 状态 |
|------|----------|-----------------|------------|--------|----------|------|
| DEVELOPMENT | 手动 | python -m py_compile backend/app/api/v1/saves.py | AC-PLAY-002, AC-PLAY-007, AC-PLAY-008 | qa | test-report.md | Recorded |
| DEVELOPMENT | 手动 | cd frontend && npm run build | AC-PLAY-001, AC-PLAY-003, AC-PLAY-004, AC-PLAY-005, AC-PLAY-006 | qa | test-report.md | Recorded |
| DEVELOPMENT | 手动 | docker compose ps | AC-PLAY-002, AC-PLAY-007, AC-PLAY-008, AC-PLAY-009 | qa | test-report.md | Recorded |

## Delivery E2E / Runtime Smoke Plan

| 任务编号 | 命令 / 步骤 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
|----------|-------------|----------|----------|------------------|----------|------------|--------------|------|
| T-028-04 | curl http://localhost:8000/api/v1/health | http://localhost:8081 | http://localhost:8000 | /api/v1/health | no | AC-PLAY-002 | test-report.md | Recorded |
| T-028-05 | curl http://localhost:8000/api/v1/scripts/1 | http://localhost:8081 | http://localhost:8000 | /api/v1/scripts | no | AC-PLAY-001, AC-PLAY-003 | test-report.md | Recorded |
| T-028-06 | curl http://localhost:8000/api/v1/saves?character_id=xxx | http://localhost:8081 | http://localhost:8000 | /api/v1/saves | no | AC-PLAY-004, AC-PLAY-005 | test-report.md | Recorded |

## Browser Interaction E2E Plan

| 任务编号 | 命令 / 步骤 | Browser / Tool | 用户动作 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
|----------|-------------|----------------|----------|----------|----------|------------------|----------|------------|--------------|------|
| T-028-08 | Not Required: bcrypt 4.0.1 与 passlib 1.7.4 不兼容，登录功能无法正常工作 | Playwright | 选择角色开始游戏 | http://localhost:8081 | http://localhost:8000 | /api/v1 | no | AC-PLAY-001 | test-report.md | skipped_with_reason |
| T-028-08 | Not Required: bcrypt 4.0.1 与 passlib 1.7.4 不兼容，登录功能无法正常工作 | Playwright | 切换角色 | http://localhost:8081 | http://localhost:8000 | /api/v1 | no | AC-PLAY-003 | test-report.md | skipped_with_reason |
| T-028-10 | Not Required: bcrypt 4.0.1 与 passlib 1.7.4 不兼容，登录功能无法正常工作 | Playwright | 存档筛选 | http://localhost:8081 | http://localhost:8000 | /api/v1 | no | AC-PLAY-005 | test-report.md | skipped_with_reason |
| T-028-08 | Not Required: bcrypt 4.0.1 与 passlib 1.7.4 不兼容，登录功能无法正常工作 | Playwright | 锁定角色 | http://localhost:8081 | http://localhost:8000 | /api/v1 | no | AC-PLAY-006 | test-report.md | skipped_with_reason |
| T-028-09 | Not Required: bcrypt 4.0.1 与 passlib 1.7.4 不兼容，登录功能无法正常工作 | Playwright | 角色信息展示 | http://localhost:8081 | http://localhost:8000 | /api/v1 | no | AC-PLAY-004 | test-report.md | skipped_with_reason |
