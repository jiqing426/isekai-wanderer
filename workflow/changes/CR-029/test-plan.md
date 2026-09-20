# CR-029 测试计划

## 测试概述

验证节点分支标记功能：不同角色看到不同分支内容，最终汇合到相同节点。

## Test-First Scope

- AC-BRANCH-001: DB Migration: nodes 表新增 character_id 字段
- AC-BRANCH-002: NarrativeEngine 节点过滤逻辑
- AC-BRANCH-003: 数据填充：MVP 剧本角色分支节点（1 个剧本）
- AC-BRANCH-006: 选择项数量：从 2 个改为 3 个
- AC-BRANCH-007: 向后兼容：现有节点和 session 不受影响

## Test Case Artifacts

| 任务编号 | 测试用例产物 | 覆盖验收项 | 状态 |
|----------|--------------|------------|------|
| T-029-01 | tests/db/test_cr029_migration.py | AC-BRANCH-001 | Ready |
| T-029-02 | tests/api/test_cr029_filter.py | AC-BRANCH-002 | Ready |
| T-029-03 | tests/e2e/cr029-branch.spec.ts | AC-BRANCH-003 | Ready |
| T-029-06 | tests/e2e/cr029-choices.spec.ts | AC-BRANCH-006 | Ready |
| T-029-07 | tests/api/test_cr029_compat.py | AC-BRANCH-007 | Ready |

## Red Failure Records

| 任务编号 | 失败 ID | 失败现象 | 失败原因 | 修复状态 |
|----------|---------|----------|----------|----------|
| T-029-01 | RED-001 | 待记录 | 待记录 | Pending |
| T-029-02 | RED-002 | 待记录 | 待记录 | Pending |
| T-029-03 | RED-003 | 待记录 | 待记录 | Pending |
| T-029-06 | RED-004 | 待记录 | 待记录 | Pending |
| T-029-07 | RED-005 | 待记录 | 待记录 | Pending |

## CI/CD Evidence Plan

| 阶段 | 触发时机 | 命令 / Pipeline | 覆盖验收项 | 负责人 | 记录位置 | 状态 |
|------|----------|-----------------|------------|--------|----------|------|
| DEVELOPMENT | 2026-08-03 18:05 | docker compose exec backend alembic upgrade head | AC-BRANCH-001 | qa | test-report.md | ✅ Executed |
| DEVELOPMENT | 2026-08-03 18:15 | python test_cr029_filter.py | AC-BRANCH-002 | qa | test-report.md | ✅ Executed |
| DEVELOPMENT | 2026-08-03 18:25 | python test_cr029_compat.py | AC-BRANCH-007 | qa | test-report.md | ✅ Executed |

## Delivery E2E Plan

| 任务编号 | 命令 / 步骤 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
|----------|-------------|----------|----------|------------------|----------|------------|--------------|------|
| T-029-02 | curl http://localhost:8081/api/v1/health | http://localhost:8081 | http://localhost:8000 | /api/v1/health | no | AC-BRANCH-002 | test-report.md | ✅ Executed |
| T-029-03 | DB验证分支节点+汇合 | http://localhost:8081 | http://localhost:8000 | /api/v1/game | no | AC-BRANCH-003 | test-report.md | ✅ Executed |
| T-029-07 | curl http://localhost:8000/api/v1/health | http://localhost:8081 | http://localhost:8000 | /api/v1/health | no | AC-BRANCH-007 | test-report.md | ✅ Executed |

## Browser E2E Plan

| 任务编号 | 命令 / 步骤 | Browser / Tool | 用户动作 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
|----------|-------------|----------------|----------|----------|----------|------------------|----------|------------|--------------|------|
| T-029-03 | Playwright cr029-branch.spec.ts | Playwright 1.62 | 选择角色A/B开始游戏→验证不同分支 | http://localhost:8081 | http://localhost:8000 | /api/v1/game | no | AC-BRANCH-003 | test-report.md | ❌ Failed (选择器) |
| T-029-06 | Playwright cr029-choices.spec.ts | Playwright 1.62 | 到达选择节点→验证 3 个选项 | http://localhost:8081 | http://localhost:8000 | /api/v1/game | no | AC-BRANCH-006 | test-report.md | ⏸️ 未执行 |

## 测试执行计划

| 测试项 | 负责人 | 预估工时 | 状态 |
|--------|--------|----------|------|
| 数据库迁移测试 | QA | 0.5h | ✅ passed (5/5) |
| 后端 API 测试 | QA | 1h | ✅ passed (4/4) |
| 数据填充测试 | QA | 1h | ✅ passed (DB验证 + API验证) |
| 选择项数量测试 | QA | 0.5h | ✅ passed (7 nodes × 3 choices) |
| 向后兼容测试 | QA | 0.5h | ✅ passed (4/4) |
| Browser E2E 分支测试 | QA | 1h | ❌ failed (登录选择器问题) |
| Delivery E2E / Runtime Smoke | QA | 0.5h | ✅ passed (proxy + backend health) |

**总工时**：4.5h（含 Browser E2E 调试）

## 测试通过标准

- 数据库迁移成功
- 不同角色看到不同分支内容
- 分支结束后汇合到相同节点
- 选择项数量为 3 个
- 向后兼容（现有节点不受影响）

## 创建时间

2026-08-03 13:26
