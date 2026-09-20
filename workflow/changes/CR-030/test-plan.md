# CR-030 Test Plan

## Test-First Scope

- AC-CHAP-001: DB Migration - routes 表新增 chapter_number 和 chapter_type 字段
- AC-CHAP-002: 数据迁移 - 11 条 route 正确映射到章节
- AC-CHAP-003: API 返回 - GET /game/{session_id}/status 响应包含章节信息
- AC-CHAP-004: 前端展示 - 进度条显示"第X章：章节名"
- AC-CHAP-005: 向后兼容 - 旧 session 返回 null，游戏流程不受影响
- AC-CHAP-006: 剧本章节列表 - GET /scripts/{script_id}/chapters 返回章节数组

## Test Case Artifacts

| 任务编号 | 测试用例产物 | 覆盖验收项 | 状态 |
|----------|--------------|------------|------|
| T-030-01 | tests/db/test_cr030_migration.py | AC-CHAP-001 | Ready |
| T-030-02 | tests/db/test_cr030_data_migration.py | AC-CHAP-002 | Ready |
| T-030-03 | tests/api/test_cr030_chapter_api.py | AC-CHAP-003, AC-CHAP-006 | Ready |
| T-030-04 | tests/e2e/cr030-chapter-display.spec.ts | AC-CHAP-004 | Ready |
| T-030-05 | tests/api/test_cr030_compat.py | AC-CHAP-005 | Ready |

## Red Failure Records

| 任务编号 | 失败 ID | 失败现象 | 失败原因 | 修复状态 |
|----------|---------|----------|----------|----------|
| T-030-01 | RED-001 | 待记录 | 待记录 | Pending |
| T-030-02 | RED-002 | 待记录 | 待记录 | Pending |
| T-030-03 | RED-003 | 待记录 | 待记录 | Pending |
| T-030-04 | RED-004 | 待记录 | 待记录 | Pending |
| T-030-05 | RED-005 | 待记录 | 待记录 | Pending |

## CI/CD Evidence Plan

| 阶段 | 触发时机 | 命令 / Pipeline | 覆盖验收项 | 负责人 | 记录位置 | 状态 |
|------|----------|-----------------|------------|--------|----------|------|
| DEVELOPMENT | 代码提交后 | pytest tests/db/test_cr030_migration.py | AC-CHAP-001 | qa | test-report.md | Planned |
| DEVELOPMENT | 代码提交后 | pytest tests/db/test_cr030_data_migration.py | AC-CHAP-002 | qa | test-report.md | Planned |
| DEVELOPMENT | 代码提交后 | pytest tests/api/test_cr030_chapter_api.py | AC-CHAP-003, AC-CHAP-006 | qa | test-report.md | Planned |
| DEVELOPMENT | 代码提交后 | pytest tests/api/test_cr030_compat.py | AC-CHAP-005 | qa | test-report.md | Planned |
| DEVELOPMENT | 代码提交后 | playwright test tests/e2e/cr030-chapter-display.spec.ts | AC-CHAP-004 | qa | test-report.md | Planned |

## Delivery E2E Plan

| 任务编号 | 命令 / 步骤 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
|----------|-------------|----------|----------|------------------|----------|------------|--------------|------|
| T-030-01 | docker compose exec -T db psql -U isekai -d isekai -c "SELECT column_name FROM information_schema.columns WHERE table_name='routes' AND column_name IN ('chapter_number','chapter_type')" | http://localhost:8081 | http://localhost:8000 | /api/v1/health | no | AC-CHAP-001 | test-report.md | Planned |
| T-030-02 | docker compose exec -T db psql -U isekai -d isekai -c "SELECT COUNT(*) FROM routes WHERE chapter_number IS NOT NULL" | http://localhost:8081 | http://localhost:8000 | /api/v1/health | no | AC-CHAP-002 | test-report.md | Planned |
| T-030-03 | curl -sf http://localhost:8000/api/v1/game/session_id/status | http://localhost:8081 | http://localhost:8000 | /api/v1/game | no | AC-CHAP-003 | test-report.md | Planned |
| T-030-03 | curl -sf http://localhost:8000/api/v1/scripts/script_id/chapters | http://localhost:8081 | http://localhost:8000 | /api/v1/scripts | no | AC-CHAP-006 | test-report.md | Planned |
| T-030-05 | curl -sf http://localhost:8000/api/v1/game/old_session_id/status | http://localhost:8081 | http://localhost:8000 | /api/v1/game | no | AC-CHAP-005 | test-report.md | Planned |

## Browser E2E Plan

| 任务编号 | 命令 / 步骤 | Browser / Tool | 用户动作 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
|----------|-------------|----------------|----------|----------|----------|------------------|----------|------------|--------------|------|
| T-030-04 | playwright test tests/e2e/cr030-chapter-display.spec.ts | Playwright | 进入游戏页面，查看进度条显示"第X章：章节名" | http://localhost:8081 | http://localhost:8000 | /api/v1/game | no | AC-CHAP-004 | test-report.md | Planned |
| T-030-04 | playwright test tests/e2e/cr030-chapter-switch.spec.ts | Playwright | 从第1章推进到第2章，验证进度条文本实时更新 | http://localhost:8081 | http://localhost:8000 | /api/v1/game | no | AC-CHAP-004 | test-report.md | Planned |
| T-030-05 | playwright test tests/e2e/cr030-compat.spec.ts | Playwright | 使用旧 session 进入游戏，验证降级显示 route.title | http://localhost:8081 | http://localhost:8000 | /api/v1/game | no | AC-CHAP-005 | test-report.md | Planned |
| T-030-03 | playwright test tests/e2e/cr030-chapters-api.spec.ts | Playwright | 调用 GET /scripts/{id}/chapters，验证返回章节数组 | http://localhost:8081 | http://localhost:8000 | /api/v1/scripts | no | AC-CHAP-006 | test-report.md | Planned |
| T-030-01 | playwright test tests/e2e/cr030-migration.spec.ts | Playwright | 验证数据库字段存在（通过 API 间接验证） | http://localhost:8081 | http://localhost:8000 | /api/v1/health | no | AC-CHAP-001 | test-report.md | Planned |
| T-030-02 | playwright test tests/e2e/cr030-data-migration.spec.ts | Playwright | 验证 11 条 route 映射正确（通过 API 间接验证） | http://localhost:8081 | http://localhost:8000 | /api/v1/scripts | no | AC-CHAP-002 | test-report.md | Planned |
| T-030-03 | playwright test tests/e2e/cr030-game-status.spec.ts | Playwright | 验证 game status 返回章节信息 | http://localhost:8081 | http://localhost:8000 | /api/v1/game | no | AC-CHAP-003 | test-report.md | Planned |

## 测试执行计划

| 测试项 | 负责人 | 预估工时 | 状态 |
|--------|--------|----------|------|
| 数据库迁移测试 | QA | 0.5h | pending |
| 数据迁移测试 | QA | 0.5h | pending |
| API 章节信息测试 | QA | 1h | pending |
| 前端进度条测试 | QA | 1h | pending |
| 向后兼容测试 | QA | 0.5h | pending |
| Browser E2E 测试 | QA | 1.5h | pending |

**总工时**: 5h

## 测试通过标准

- routes 表包含 chapter_number 和 chapter_type 字段
- 11 条 route 正确映射到章节（星月奇缘 3 条、星辰之约 4 条、樱花恋曲 4 条）
- GET /game/{session_id}/status 返回 chapter_number、chapter_type、chapter_title
- GET /scripts/{script_id}/chapters 返回章节数组，按 chapter_number 升序
- 前端进度条显示"第X章：章节名"
- 旧 session 返回 null，游戏流程不受影响

## 创建时间

2026-08-04 14:30
