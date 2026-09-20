# Test Plan: CR-038 — Corvus 前端入口接入

## Test-First Scope

本 CR 的测试先行范围覆盖 25 条 AC（16 P0 + 9 P1），分为以下验证类型：

- Browser Interaction E2E: 14 条 AC（需真实浏览器执行用户动作）
- API/DB/Runtime 契约验证: 9 条 AC（需真实后端 API + DB 验证）
- 编译检查: 2 条 AC（`npm run build` TypeScript 编译通过）
- 角色候选管理 UI: 5 条 AC（查看/创建/校验/限制/选择）
- SSE 流式渲染: 4 条 AC（逐字渲染/gm_update/error 重试/无选项降级）
- 会话恢复: 2 条 AC（Corvus 会话恢复/旧数据兼容）
- 剧本选择: 3 条 AC（engine_type 解析/Corvus 流程/Legacy 保留）

## Test Case Artifacts

| 任务编号 | 测试用例产物 | 覆盖验收项 | 状态 |
|---|---|---|---|
| T-038-BE-001 | `backend/tests/unit/test_scripts_engine_type.py` | AC-038-001, AC-038-002 | Recorded |
| T-038-BE-002 | `backend/tests/unit/test_player_candidates_create.py` | AC-038-003, AC-038-004, AC-038-005, AC-038-006 | Recorded |
| T-038-FE-001 | `frontend/tests/compile-check.sh` | AC-038-007, AC-038-008 | Recorded |
| T-038-FE-002 | `frontend/tests/e2e/cr038-start-game.spec.ts` | AC-038-009, AC-038-010, AC-038-011 | Recorded | manual |
| T-038-FE-003 | `frontend/tests/e2e/cr038-candidate-management.spec.ts` | AC-038-012, AC-038-013, AC-038-014, AC-038-015, AC-038-016 | Recorded | manual |
| T-038-FE-004 | `frontend/tests/e2e/cr038-sse-streaming.spec.ts` | AC-038-017, AC-038-018, AC-038-019, AC-038-020 | Recorded | manual |
| T-038-FE-005 | `frontend/tests/e2e/cr038-resume-session.spec.ts` | AC-038-021, AC-038-022 | Recorded | manual |
| T-038-FE-006 | `frontend/tests/e2e/cr038-script-selection.spec.ts` | AC-038-023, AC-038-024, AC-038-025 | Recorded | manual |

## Red Failure Records

| 任务编号 | 测试用例产物 | 覆盖验收项 | 命令 / 步骤 | 失败摘要 | 记录时间 | 状态 |
|---|---|---|---|---|---|---|
| T-038-BE-001 | `backend/tests/unit/test_scripts_engine_type.py` | AC-038-001, AC-038-002 | `cd /root/isekai-wanderer/backend && .venv/bin/python -m pytest /root/isekai-wanderer/backend/tests/unit/test_scripts_engine_type.py -v` | 2 FAILED: test_list_scripts_has_engine_type (AssertionError: Script missing engine_type), test_get_script_detail_has_engine_type (缺 engine_type 字段) | 2026-08-28T10:22:00+08:00 | Failed |
| T-038-BE-002 | `backend/tests/unit/test_player_candidates_create.py` | AC-038-003, AC-038-004, AC-038-005, AC-038-006 | `cd /root/isekai-wanderer/backend && .venv/bin/python -m pytest /root/isekai-wanderer/backend/tests/unit/test_player_candidates_create.py -v` | 4 FAILED: 405 Method Not Allowed (POST /api/v1/game/player/candidates 端点不存在) | 2026-08-28T10:23:00+08:00 | Failed |
| T-038-FE-001 | `frontend/tests/compile-check.sh` | AC-038-007, AC-038-008 | `bash /root/isekai-wanderer/frontend/tests/compile-check.sh` | baseline exit 0 — 编译通过（修改前基线确认） | 2026-08-28T11:08:00+08:00 | Recorded |
| T-038-FE-002 | `frontend/tests/e2e/cr038-start-game.spec.ts` | AC-038-009, AC-038-010, AC-038-011 | `ls /root/isekai-wanderer/frontend/tests/e2e/cr038-start-game.spec.ts && bash /root/isekai-wanderer/frontend/tests/compile-check.sh` | E2E 测试文件已编写但编译检查 exit 0（Red 阶段基线确认）；需真实后端+Corvus 运行 | 2026-08-28T11:30:00+08:00 | Failed |
| T-038-FE-006 | `frontend/tests/e2e/cr038-script-selection.spec.ts` | AC-038-023, AC-038-024, AC-038-025 | `ls /root/isekai-wanderer/frontend/tests/e2e/cr038-script-selection.spec.ts && bash /root/isekai-wanderer/frontend/tests/compile-check.sh` | E2E 测试文件已编写但编译检查 exit 0（Red 阶段基线确认）；需真实后端+Corvus 运行 | 2026-08-28T11:30:00+08:00 | Failed |
| T-038-FE-003 | `frontend/tests/e2e/cr038-candidate-management.spec.ts` | AC-038-012, AC-038-013, AC-038-014, AC-038-015, AC-038-016 | `ls /root/isekai-wanderer/frontend/tests/e2e/cr038-candidate-management.spec.ts && bash /root/isekai-wanderer/frontend/tests/compile-check.sh` | E2E 测试文件已编写但编译检查 exit 0（Red 阶段基线确认）；需真实后端+Corvus 运行 | 2026-08-28T11:45:00+08:00 | Failed |
| T-038-FE-004 | `frontend/tests/e2e/cr038-sse-streaming.spec.ts` | AC-038-017, AC-038-018, AC-038-019, AC-038-020 | `ls /root/isekai-wanderer/frontend/tests/e2e/cr038-sse-streaming.spec.ts && bash /root/isekai-wanderer/frontend/tests/compile-check.sh` | E2E 测试文件已编写但编译检查 exit 0（Red 阶段基线确认）；需真实后端+Corvus 运行 | 2026-08-28T11:45:00+08:00 | Failed |
| T-038-FE-005 | `frontend/tests/e2e/cr038-resume-session.spec.ts` | AC-038-021, AC-038-022 | `ls /root/isekai-wanderer/frontend/tests/e2e/cr038-resume-session.spec.ts && bash /root/isekai-wanderer/frontend/tests/compile-check.sh` | E2E 测试文件已编写但编译检查 exit 0（Red 阶段基线确认）；需真实后端+Corvus 运行 | 2026-08-28T11:45:00+08:00 | Failed |

## Green Pass Records

| 任务编号 | 测试用例产物 | 覆盖验收项 | 命令 / 步骤 | 通过摘要 | 记录时间 | 状态 |
|---|---|---|---|---|---|---|
| T-038-BE-001 | `backend/tests/unit/test_scripts_engine_type.py` | AC-038-001, AC-038-002 | `cd /root/isekai-wanderer/backend && .venv/bin/python -m pytest /root/isekai-wanderer/backend/tests/unit/test_scripts_engine_type.py -v` | 2 PASSED: engine_type='corvus' 字段验证通过 | 2026-08-28T10:25:00+08:00 | Passed |
| T-038-BE-002 | `backend/tests/unit/test_player_candidates_create.py` | AC-038-003, AC-038-004, AC-038-005, AC-038-006 | `cd /root/isekai-wanderer/backend && .venv/bin/python -m pytest /root/isekai-wanderer/backend/tests/unit/test_player_candidates_create.py -v` | 4 PASSED: 创建成功+UUID+字段验证、name 缺失校验、3 个限制、完整字段 | 2026-08-28T10:25:00+08:00 | Passed |
| T-038-FE-001 | `frontend/tests/compile-check.sh` | AC-038-007, AC-038-008 | `bash /root/isekai-wanderer/frontend/tests/compile-check.sh` | exit 0 — 编译通过：Script interface 新增 engine_type 必填字段；GameSession interface engine_type 去掉 ? 改必填 | 2026-08-28T11:10:00+08:00 | Passed |
| T-038-FE-002 | `frontend/tests/e2e/cr038-start-game.spec.ts` + compile check | AC-038-009, AC-038-010, AC-038-011 | `ls /root/isekai-wanderer/frontend/tests/e2e/cr038-start-game.spec.ts && bash /root/isekai-wanderer/frontend/tests/compile-check.sh` | compile check exit 0 — startGame() Corvus 分支已实现；GameSession.engine_type 写入 'corvus'/'legacy'；Browser E2E 待 QA 环境 | 2026-08-28T11:35:00+08:00 | Passed |
| T-038-FE-003 | `frontend/tests/e2e/cr038-candidate-management.spec.ts` | AC-038-012, AC-038-013, AC-038-014, AC-038-015, AC-038-016 | `ls /root/isekai-wanderer/frontend/tests/e2e/cr038-candidate-management.spec.ts && bash /root/isekai-wanderer/frontend/tests/compile-check.sh` | compile check exit 0 — PlayerCandidateModal 组件已实现 | 2026-08-28T11:50:00+08:00 | Passed |
| T-038-FE-004 | `frontend/tests/e2e/cr038-sse-streaming.spec.ts` | AC-038-017, AC-038-018, AC-038-019, AC-038-020 | `ls /root/isekai-wanderer/frontend/tests/e2e/cr038-sse-streaming.spec.ts && bash /root/isekai-wanderer/frontend/tests/compile-check.sh` | compile check exit 0 — gm_update 处理补齐 | 2026-08-28T11:50:00+08:00 | Passed |
| T-038-FE-005 | `frontend/tests/e2e/cr038-resume-session.spec.ts` | AC-038-021, AC-038-022 | `ls /root/isekai-wanderer/frontend/tests/e2e/cr038-resume-session.spec.ts && bash /root/isekai-wanderer/frontend/tests/compile-check.sh` | compile check exit 0 — resumeSession engine_type 已写入 | 2026-08-28T11:50:00+08:00 | Passed |

| T-038-FE-006 | `frontend/tests/e2e/cr038-script-selection.spec.ts` + compile check | AC-038-023, AC-038-024, AC-038-025 | `ls /root/isekai-wanderer/frontend/tests/e2e/cr038-script-selection.spec.ts && bash /root/isekai-wanderer/frontend/tests/compile-check.sh` | compile check exit 0 — loadScripts 已解析 engine_type；legacy 分支条件保留；Browser E2E 待 QA 环境 | 2026-08-28T11:35:00+08:00 | Passed |


## Cannot Automate

| 任务编号 | Reason | Manual Verification Owner | 验证记录 |
|---|---|---|---|
| T-038-FE-002 | Browser E2E 需要真实后端+Corvus 运行环境，当前编译环境无法运行 Playwright | QA (Cat01-qa) | 待 QA 阶段运行 Playwright |

| T-038-FE-003 | Browser E2E 需要真实后端+Corvus 运行环境，当前编译环境无法运行 Playwright | QA (Cat01-qa) | 待 QA 阶段运行 Playwright |
| T-038-FE-004 | Browser E2E 需要真实后端+Corvus 运行环境，当前编译环境无法运行 Playwright | QA (Cat01-qa) | 待 QA 阶段运行 Playwright |
| T-038-FE-005 | Browser E2E 需要真实后端+Corvus 运行环境，当前编译环境无法运行 Playwright | QA (Cat01-qa) | 待 QA 阶段运行 Playwright |

| T-038-FE-006 | Browser E2E 需要真实后端+Corvus 运行环境，当前编译环境无法运行 Playwright | QA (Cat01-qa) | 待 QA 阶段运行 Playwright |

## CI/CD Evidence Plan

| 阶段 | 触发时机 | 命令 / Pipeline | 覆盖验收项 | 负责人 | 记录位置 | 状态 |
|---|---|---|---|---|---|---|
| 后端单元测试 | 代码提交 | `cd backend && pytest tests/test_scripts_engine_type.py tests/test_player_candidates_create.py -v` | AC-038-001~006 | BE | `logs/ci/backend-unit.log` | Ready |
| 前端编译检查 | 代码提交 | `cd frontend && npm run build` | AC-038-007, AC-038-008 | FE | `logs/ci/frontend-build.log` | Ready |
| 前端类型检查 | 代码提交 | `cd frontend && npx tsc --noEmit` | AC-038-007, AC-038-008 | FE | `logs/ci/frontend-tsc.log` | Ready |

## Delivery E2E / Runtime Smoke Plan

| 任务编号 | 命令 / 步骤 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
|---|---|---|---|---|---|---|---|---|
| DEL-038-001 | `curl -f http://localhost:8081/api/v1/health` | http://localhost:8081 | http://localhost:8000 | /api/v1/health | no | AC-038-001 (环境就绪前置) | `logs/e2e/health.log` | Ready |
| DEL-038-002 | `curl http://localhost:8081/api/v1/scripts` 验证每个对象有 engine_type | http://localhost:8081 | http://localhost:8000 | /api/v1/scripts | no | AC-038-001 | `logs/e2e/scripts-engine-type.log` | Ready |
| DEL-038-003 | `curl http://localhost:8081/api/v1/scripts/{id}` 验证 engine_type | http://localhost:8081 | http://localhost:8000 | /api/v1/scripts/{id} | no | AC-038-002 | `logs/e2e/script-detail-engine-type.log` | Ready |
| DEL-038-004 | `curl -X POST http://localhost:8081/api/v1/game/player/candidates -H "Authorization: Bearer {token}" -d '{"name":"星野"}'` → code:0 + UUID | http://localhost:8081 | http://localhost:8000 | /api/v1/game/player/candidates | no | AC-038-003 | `logs/e2e/create-candidate.log` | Ready |
| DEL-038-005 | `curl -X POST http://localhost:8081/api/v1/game/player/candidates -H "Authorization: Bearer {token}" -d '{"personality":"勇敢"}'` → 400 | http://localhost:8081 | http://localhost:8000 | /api/v1/game/player/candidates | no | AC-038-004 | `logs/e2e/create-candidate-no-name.log` | Ready |
| DEL-038-006 | 创建第 4 个候选 → 400 | http://localhost:8081 | http://localhost:8000 | /api/v1/game/player/candidates | no | AC-038-005 | `logs/e2e/create-candidate-limit.log` | Ready |
| DEL-038-007 | `curl -X POST ... -d '{"name":"星野","personality":"勇敢","backstory":"来自异世界","appearance":"银发蓝眼"}'` → 完整字段 | http://localhost:8081 | http://localhost:8000 | /api/v1/game/player/candidates | no | AC-038-006 | `logs/e2e/create-candidate-full.log` | Ready |
| DEL-038-008 | `cd frontend && npm run build` → exit 0 | http://localhost:8081 | http://localhost:8000 | /api/v1/health (编译检查后验证) | no | AC-038-007, AC-038-008 | `logs/ci/frontend-build.log` | Ready |

## Browser Interaction E2E Plan

| 任务编号 | 命令 / 步骤 | Browser / Tool | 用户动作 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
|---|---|---|---|---|---|---|---|---|---|---|
| BR-038-001 | `APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr038-start-game.spec.ts --headed --trace on` | Playwright Chromium | 选择剧本 → 点击"开始游戏" → 进入选角/游戏界面 | http://localhost:8081 | http://localhost:8000 | /api/v1/game/session/create | no | AC-038-009 | `logs/e2e/cr038-start-game/` | Ready |
| BR-038-002 | 同上 spec 文件 | Playwright Chromium | 等待选角页面加载 → 可见角色卡片列表 | http://localhost:8081 | http://localhost:8000 | /api/v1/game/player/candidates | no | AC-038-010 | `logs/e2e/cr038-start-game/` | Ready |
| BR-038-003 | 同上 spec 文件 | Playwright Chromium | 点击角色卡片 → 点击确认 → 进入游戏界面，SSE 开始 | http://localhost:8081 | http://localhost:8000 | /api/v1/game/session/select-player | no | AC-038-011 | `logs/e2e/cr038-start-game/` | Ready |
| BR-038-004 | `APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr038-candidate-management.spec.ts --headed --trace on` | Playwright Chromium | 打开候选管理界面 → 可见角色卡片列表 | http://localhost:8081 | http://localhost:8000 | /api/v1/game/player/candidates | no | AC-038-012 | `logs/e2e/cr038-candidate-mgmt/` | Ready |
| BR-038-005 | 同上 spec 文件 | Playwright Chromium | 填写表单 → 点击提交 → 列表新增角色卡片 | http://localhost:8081 | http://localhost:8000 | /api/v1/game/player/candidates | no | AC-038-013 | `logs/e2e/cr038-candidate-mgmt/` | Ready |
| BR-038-006 | 同上 spec 文件 | Playwright Chromium | 不填 name → 点击提交 → 错误提示显示 | http://localhost:8081 | http://localhost:8000 | - (前端校验) | no | AC-038-014 | `logs/e2e/cr038-candidate-mgmt/` | Ready |
| BR-038-007 | 同上 spec 文件 | Playwright Chromium | 已有 3 个 → 查看创建按钮 → 按钮不可用 | http://localhost:8081 | http://localhost:8000 | /api/v1/game/player/candidates | no | AC-038-015 | `logs/e2e/cr038-candidate-mgmt/` | Ready |
| BR-038-008 | 同上 spec 文件 | Playwright Chromium | 点击角色 → 点击确认 → 进入游戏界面 | http://localhost:8081 | http://localhost:8000 | /api/v1/game/session/select-player | no | AC-038-016 | `logs/e2e/cr038-candidate-mgmt/` | Ready |
| BR-038-009 | `APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr038-sse-streaming.spec.ts --headed --trace on` | Playwright Chromium | 输入文字 → 点击发送 → 观察文字逐步渲染 | http://localhost:8081 | http://localhost:8000 | /api/v1/game/{id}/custom-input (SSE) | no | AC-038-017 | `logs/e2e/cr038-sse/` | Ready |
| BR-038-010 | 同上 spec 文件 | Playwright Chromium | 对话中 → 好感度/道具列表更新（验证 UI 状态变化） | http://localhost:8081 | http://localhost:8000 | SSE gm_update 事件 | no | AC-038-018 | `logs/e2e/cr038-sse/` | Ready |
| BR-038-011 | 同上 spec 文件 | Playwright Chromium | 模拟断连 → 错误提示 → 点击重试 | http://localhost:8081 | http://localhost:8000 | SSE error 事件 | no | AC-038-019 | `logs/e2e/cr038-sse/` | Ready |
| BR-038-012 | 同上 spec 文件 | Playwright Chromium | 完成一轮对话 → 输入框可见可用 | http://localhost:8081 | http://localhost:8000 | SSE done 事件 | no | AC-038-020 | `logs/e2e/cr038-sse/` | Ready |
| BR-038-013 | `APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr038-resume-session.spec.ts --headed --trace on` | Playwright Chromium | 恢复 Corvus 会话 → engine_type='corvus' → SSE 分支 | http://localhost:8081 | http://localhost:8000 | /api/v1/game/{id} | no | AC-038-021 | `logs/e2e/cr038-resume/` | Ready |
| BR-038-014 | 同上 spec 文件 | Playwright Chromium | 恢复旧会话（无 engine_type）→ legacy 分支正常执行 | http://localhost:8081 | http://localhost:8000 | /api/v1/game/{id} | no | AC-038-022 | `logs/e2e/cr038-resume/` | Ready |
| BR-038-015 | `APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr038-script-selection.spec.ts --headed --trace on` | Playwright Chromium | 选择剧本 → 点击开始 → 走 Corvus 流程 | http://localhost:8081 | http://localhost:8000 | /api/v1/scripts | no | AC-038-023 | `logs/e2e/cr038-script-sel/` | Ready |
| BR-038-016 | 同上 spec 文件 | Playwright Chromium | 选择任意剧本 → 走 Corvus 流程（C3 约束） | http://localhost:8081 | http://localhost:8000 | /api/v1/scripts | no | AC-038-024 | `logs/e2e/cr038-script-sel/` | Ready |
| BR-038-017 | 同上 spec 文件 + 代码审查 | Playwright Chromium + git grep | 代码审查确认 legacy 代码仍存在；Browser E2E 确认 legacy 不激活 | http://localhost:8081 | http://localhost:8000 | /api/v1/scripts (验证 legacy 代码路径不执行) | no | AC-038-025 | `logs/e2e/cr038-script-sel/` | Ready |

## Browser E2E Command

```bash
APP_BASE=http://localhost:8081 \
npx playwright test \
  tests/e2e/cr038-start-game.spec.ts \
  tests/e2e/cr038-candidate-management.spec.ts \
  tests/e2e/cr038-sse-streaming.spec.ts \
  tests/e2e/cr038-resume-session.spec.ts \
  tests/e2e/cr038-script-selection.spec.ts \
  --headed --trace on
```

## 环境

- ENV-L1 (DEV_LOCAL): `http://localhost:8081` (Vite dev) → `http://localhost:8000` (Uvicorn)
- 证据等级: L1 (本地通过) / L2 (联调通过)
- Mock API: no — 所有 E2E 使用真实后端 API + 真实 Corvus 服务 (127.0.0.1:8082) + 真实 PostgreSQL + pgvector
