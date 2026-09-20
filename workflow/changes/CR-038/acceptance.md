# Acceptance

验收覆盖矩阵。每个 P0/P1 验收项必须能从 OpenSpec Requirement / Scenario 追到 OpenSpec task、实现证据、测试证据和覆盖结论。

| 验收编号 | 需求编号 | 优先级 | 来源规格 | 验收标准 | 设计落点 | OpenSpec Task | 实现证据 | 测试用例 / 验证命令 | 状态 | 覆盖状态 | 未覆盖原因 | PL 处理 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AC-038-001 | REQ-CAP-001 | P0 | `openspec/changes/corvus-frontend-entry/specs/capability/spec.md` | `GET /api/v1/scripts` 返回的 `scripts` 数组中每个对象包含 `engine_type: 'corvus'` 字段；字段类型为 string | 后端 `scripts.py` list_scripts 返回值新增 engine_type 虚拟字段 | T-038-BE-001 | ✅ 已实现 | `cd /root/isekai-wanderer/backend && .venv/bin/python -m pytest /root/isekai-wanderer/backend/tests/unit/test_scripts_engine_type.py::TestScriptsEngineType::test_list_scripts_has_engine_type -v`; Delivery E2E: `curl http://localhost:8081/api/v1/scripts` 验证每个对象有 engine_type | Verified | covered | — | — | 单元测试已 PASSED; 需 Delivery E2E curl 验证 |
| AC-038-002 | REQ-CAP-001 | P0 | `openspec/changes/corvus-frontend-entry/specs/capability/spec.md` | `GET /api/v1/scripts/{script_id}` 返回的 script 对象包含 `engine_type: 'corvus'` 字段 | 后端 `scripts.py` get_script 返回值新增 engine_type 虚拟字段 | T-038-BE-001 | ✅ 已实现 | `cd /root/isekai-wanderer/backend && .venv/bin/python -m pytest /root/isekai-wanderer/backend/tests/unit/test_scripts_engine_type.py::TestScriptsEngineType::test_get_script_detail_has_engine_type -v`; Delivery E2E: `curl http://localhost:8081/api/v1/scripts/{id}` 验证 engine_type | Verified | covered | — | — | 单元测试已 PASSED; 需 Delivery E2E curl 验证 |
| AC-038-003 | REQ-CAP-002 | P0 | `openspec/changes/corvus-frontend-entry/specs/capability/spec.md` | 用户调用 `POST /api/v1/game/player/candidates` `{"name":"星野"}` → 返回 `code:0` + 候选 id（UUID v4）；DB player_candidates 有新记录 | 后端 `game.py` 新增 POST /game/player/candidates 端点 | T-038-BE-002 | ❌ 已移除 | — | removed | 2026-09-07 范围变更：移除自定义角色创建 | — | 移除 |
| AC-038-004 | REQ-CAP-002 | P0 | `openspec/changes/corvus-frontend-entry/specs/capability/spec.md` | `POST /api/v1/game/player/candidates` `{"personality":"勇敢"}`（无 name）→ 返回 400，错误信息含 "name" | 后端 `game.py` 新增 name 必填校验 | T-038-BE-002 | ❌ 已移除 | — | removed | 2026-09-07 范围变更：移除自定义角色创建 | — | 移除 |
| AC-038-005 | REQ-CAP-002 | P0 | `openspec/changes/corvus-frontend-entry/specs/capability/spec.md` | 用户已有 3 个候选时，`POST /api/v1/game/player/candidates` → 返回 400，错误信息含 "max 3" 或 "最多 3 个" | 后端 `game.py` 新增数量校验 (≤3) | T-038-BE-002 | ❌ 已移除 | — | removed | 2026-09-07 范围变更：移除自定义角色创建 | — | 移除 |
| AC-038-006 | REQ-CAP-002 | P1 | `openspec/changes/corvus-frontend-entry/specs/capability/spec.md` | `POST /api/v1/game/player/candidates` `{"name":"星野","personality":"勇敢","backstory":"来自异世界","appearance":"银发蓝眼"}` → 返回所有字段；DB 记录与请求一致 | 后端 `game.py` 新增 POST /game/player/candidates | T-038-BE-002 | ❌ 已移除 | — | removed | 2026-09-07 范围变更：移除自定义角色创建 | — | 移除 |
| AC-038-007 | REQ-FE-001 | P0 | `openspec/changes/corvus-frontend-entry/specs/frontend/spec.md` | 前端 `Script` interface（`stores/game.ts` + `api/game.ts`）包含 `engine_type` 必填字段（类型为 `'legacy'` 或 `'corvus'`）；`npm run build` 编译通过 | 前端 `stores/game.ts` Script interface + `api/game.ts` Script interface 新增 engine_type 必填 | T-038-FE-001 | ✅ 已实现 | `bash /root/isekai-wanderer/frontend/tests/compile-check.sh` → exit 0 | Verified | covered | — | — | Script interface 新增 engine_type: 'legacy' | 'corvus' 必填字段；compile-check.sh exit 0 |
| AC-038-008 | REQ-FE-002 | P0 | `openspec/changes/corvus-frontend-entry/specs/frontend/spec.md` | 前端 `GameSession` interface 的 `engine_type` 无 `?` 可选标记；`npm run build` 编译通过 | 前端 `stores/game.ts` GameSession interface engine_type 去掉 ? | T-038-FE-001 | ✅ 已实现 | `bash /root/isekai-wanderer/frontend/tests/compile-check.sh` → exit 0 | Verified | covered | — | — | GameSession interface engine_type 从可选改为必填（去掉 ?）；compile-check.sh exit 0 |
| AC-038-009 | REQ-FE-003 | P0 | `openspec/changes/corvus-frontend-entry/specs/frontend/spec.md` | 用户在剧本选择页选择剧本（engine_type='corvus'）→ 点击"开始游戏" → 前端调用 `POST /api/v1/game/session/create` → 返回 game_session_id → 前端设置 `engine_type:'corvus'` → localStorage 保存 → 页面进入选角流程。**用户动作**：点击"开始游戏"；**可观察结果**：页面进入选角/游戏界面 | 前端 `stores/game.ts` startGame 改造：新增 Corvus 会话创建分支 | T-038-FE-002 | ✅ 已实现 | Browser E2E: `frontend/tests/e2e/cr038-start-game.spec.ts` 点击开始游戏 → 进入选角界面 | Verified | covered |Browser E2E 需要真实后端+Corvus 运行环境，编译环境无法运行 Playwright；QA 阶段验证| — | startGame() Corvus 分支已实现：POST /game/session/create + engine_type 写入；Browser E2E PASSED (QA 第三次测试) |
| AC-038-010 | REQ-FE-003 | P0 | `openspec/changes/corvus-frontend-entry/specs/frontend/spec.md` | Corvus 会话已创建（status=waiting_select_player）→ 前端调用 `GET /api/v1/game/scripts/{script_id}/characters` → 返回可扮演角色列表 → 页面展示角色选择界面。**用户动作**：等待选角页面加载；**可观察结果**：可见预设角色卡片列表 | 前端选角 Modal (PlayerCandidateModal.vue) 展示预设角色列表 | T-038-FE-002 (改造) | ✅ 已实现 | Browser E2E: `frontend/tests/e2e/cr038-start-game.spec.ts` 等待选角页面加载 → 可见预设角色卡片列表; PL 独立 E2E 15/15 passed | Verified | covered | — | 改造完成：数据源从 player_candidates 改为剧本预设角色（GET /game/scripts/{script_id}/characters）；Browser E2E PASSED | 2026-09-10 改造完成验证 |
| AC-038-011 | REQ-FE-003 | P0 | `openspec/changes/corvus-frontend-entry/specs/frontend/spec.md` | 用户在选角界面选择预设角色 → 前端调用 `POST /api/v1/game/session/select-player` 传 `character_id` → 会话 status=playing → `engine_type='corvus'` → 页面进入游戏对话界面 → 开始 SSE 流式对话。**用户动作**：点击角色卡片 → 点击确认；**可观察结果**：进入游戏界面，SSE 开始流式渲染 | 前端选角 Modal 确认 → POST /game/session/select-player (character_id) → 进入游戏 | T-038-FE-002 (改造) | ✅ 已实现 | Browser E2E: `frontend/tests/e2e/cr038-start-game.spec.ts` 选择预设角色 → 确认 → 进入游戏界面; PL 独立 E2E 15/15 passed; Delivery E2E: select-player 传 character_id → code:0 + status=playing | Verified | covered | — | 改造完成：传 character_id 而非 player_candidate_id；Browser E2E + Delivery E2E PASSED | 2026-09-10 改造完成验证 |
| AC-038-012 | REQ-FE-004 | P0 | `openspec/changes/corvus-frontend-entry/specs/frontend/spec.md` | 用户打开选角界面 → 前端调用 `GET /api/v1/game/scripts/{script_id}/characters` → 返回可扮演角色列表 → 页面展示角色卡片（name/description/avatar_url/play_description）。**用户动作**：打开选角界面；**可观察结果**：可见预设角色卡片列表 | 前端 PlayerCandidateModal.vue 预设角色列表展示 | T-038-FE-003 (改造) | ✅ 已实现 | Browser E2E: `frontend/tests/e2e/cr038-candidate-management.spec.ts` 打开选角界面 → 可见预设角色卡片; PL 独立 E2E 15/15 passed | Verified | covered | — | 改造完成：数据源改为剧本预设角色（Character 表 playable=True）；Browser E2E PASSED | 2026-09-10 改造完成验证 |
| AC-038-013 | REQ-FE-004 | P0 | `openspec/changes/corvus-frontend-entry/specs/frontend/spec.md` | ❌ 已移除 — 自定义角色创建功能移除 | — | — | ❌ 已移除 | — | removed | 2026-09-07 范围变更：移除自定义角色创建 | — | 移除 |
| AC-038-014 | REQ-FE-004 | P0 | `openspec/changes/corvus-frontend-entry/specs/frontend/spec.md` | ❌ 已移除 — name 为空校验随创建功能一并移除 | — | — | ❌ 已移除 | — | removed | 2026-09-07 范围变更：移除自定义角色创建 | — | 移除 |
| AC-038-015 | REQ-FE-004 | P0 | `openspec/changes/corvus-frontend-entry/specs/frontend/spec.md` | ❌ 已移除 — 候选数量上限随创建功能一并移除 | — | — | ❌ 已移除 | — | removed | 2026-09-07 范围变更：移除自定义角色创建 | — | 移除 |
| AC-038-016 | REQ-FE-004 | P0 | `openspec/changes/corvus-frontend-entry/specs/frontend/spec.md` | 用户在选角界面点击预设角色卡片 → 高亮选中 → 点击"确认" → `POST /api/v1/game/session/select-player` 传 `character_id` → 进入游戏。**用户动作**：点击角色 → 点击确认；**可观察结果**：进入游戏界面 | 前端 PlayerCandidateModal.vue 选角确认 + POST API 调用 (character_id) | T-038-FE-003 (改造) | ✅ 已实现 | Browser E2E: `frontend/tests/e2e/cr038-candidate-management.spec.ts` 点击角色 → 高亮 → 确认 → 进入游戏; PL 独立 E2E 15/15 passed | Verified | covered | — | 改造完成：传 character_id；Browser E2E PASSED | 2026-09-10 改造完成验证 |
| AC-038-017 | REQ-FE-005 | P0 | `openspec/changes/corvus-frontend-entry/specs/frontend/spec.md` | 用户在 Corvus 游戏界面输入文字 → 点击发送 → 前端走 Corvus SSE 分支 → SSE `text` 事件逐步渲染到 StoryPanel → `done` 事件结束渲染。**用户动作**：输入文字 → 点击发送；**可观察结果**：文字逐步渲染 | 前端 game.ts submitCustomInput Corvus SSE 分支 (已在 CR-037 实现，本 CR 激活) | T-038-FE-004 | ✅ 已实现 | Browser E2E: `frontend/tests/e2e/cr038-sse-streaming.spec.ts` 输入文字 → 发送 → 观察逐字渲染 | Verified | covered |Browser E2E 需要真实后端+Corvus 运行环境，编译环境无法运行 Playwright；QA 阶段验证|Browser E2E PASSED (QA 第三次测试)| Browser Interaction E2E PASSED |
| AC-038-018 | REQ-FE-005 | P0 | `openspec/changes/corvus-frontend-entry/specs/frontend/spec.md` | Corvus SSE 流中收到 `gm_update` 事件（含 affection_delta + inventory_changes）→ 前端更新 NPC 好感度显示 + 道具列表 + 不阻塞文本流。**数据来源**：SSE gm_update 事件；**可验证结果**：UI 好感度数值更新 + 道具列表更新 | 前端 game.ts SSE gm_update 处理补齐 (StoryPanel UI 更新) | T-038-FE-004 | ✅ 已实现 | Browser E2E: `frontend/tests/e2e/cr038-sse-streaming.spec.ts` 对话中 → 好感度/道具列表更新 | Verified | covered |Browser E2E 需要真实后端+Corvus 运行环境，编译环境无法运行 Playwright；QA 阶段验证|Browser E2E PASSED (QA 第三次测试)| API/DB/Runtime 契约验证 PASSED |
| AC-038-019 | REQ-FE-005 | P0 | `openspec/changes/corvus-frontend-entry/specs/frontend/spec.md` | Corvus SSE 流中收到 error 事件或连接中断 → 前端显示错误提示 → 用户可点击重试。**用户动作**：模拟断连 → 观察错误提示 → 点击重试；**可观察结果**：错误提示显示，重试可用 | 前端 game.ts SSE error 处理 (已在 CR-037 实现，本 CR 验证) | T-038-FE-004 | ✅ 已实现 | Browser E2E: `frontend/tests/e2e/cr038-sse-streaming.spec.ts` 模拟断连 → 错误提示 → 重试 | Verified | covered |Browser E2E 需要真实后端+Corvus 运行环境，编译环境无法运行 Playwright；QA 阶段验证|Browser E2E PASSED (QA 第三次测试)| Browser Interaction E2E PASSED |
| AC-038-020 | REQ-FE-005 | P1 | `openspec/changes/corvus-frontend-entry/specs/frontend/spec.md` | Corvus SSE done 事件不含 player_options → ChoicePanel 隐藏 → FreeChatInput 始终显示 → 用户可自由输入。**用户动作**：完成一轮对话 → 观察输入框；**可观察结果**：输入框可见可用 | 前端 game.ts choices 降级 (pendingChoices=[] → hasChoices=false → ChoicePanel 隐藏) | T-038-FE-004 | ✅ 已实现 | Browser E2E: `frontend/tests/e2e/cr038-sse-streaming.spec.ts` 完成对话 → 输入框可见 | Verified | covered |Browser E2E 需要真实后端+Corvus 运行环境，编译环境无法运行 Playwright；QA 阶段验证|Browser E2E PASSED (QA 第三次测试)| Browser Interaction E2E PASSED |
| AC-038-021 | REQ-FE-006 | P0 | `openspec/changes/corvus-frontend-entry/specs/frontend/spec.md` | localStorage 中存在 Corvus 会话（engine_type='corvus'）→ `resumeSession(sessionId)` → `currentSession.engine_type='corvus'` → 后续走 Corvus SSE 分支。**数据来源**：localStorage + 后端 GET /game/{id}；**可验证结果**：engine_type 正确设置 | 前端 game.ts resumeSession 改造：写入 engine_type | T-038-FE-005 | ✅ 已实现 | Browser E2E: `frontend/tests/e2e/cr038-resume-session.spec.ts` 恢复会话 → engine_type='corvus' → SSE 分支 | Verified | covered |Browser E2E 需要真实后端+Corvus 运行环境，编译环境无法运行 Playwright；QA 阶段验证|Browser E2E PASSED (QA 第三次测试)| API/DB/Runtime 契约验证 PASSED |
| AC-038-022 | REQ-FE-006 | P1 | `openspec/changes/corvus-frontend-entry/specs/frontend/spec.md` | localStorage 中存在旧会话（无 engine_type）→ `resumeSession` → 默认视为 'legacy' → 走 legacy 分支。**用户动作**：恢复旧会话；**可观察结果**：legacy 分支正常执行 | 前端 game.ts resumeSession 旧数据兼容处理 (无 engine_type → 'legacy') | T-038-FE-005 | ✅ 已实现 | Browser E2E: `frontend/tests/e2e/cr038-resume-session.spec.ts` 恢复旧会话 → legacy 分支 | Verified | covered |Browser E2E 需要真实后端+Corvus 运行环境，编译环境无法运行 Playwright；QA 阶段验证|Browser E2E PASSED (QA 第三次测试)| Browser Interaction E2E PASSED |
| AC-038-023 | REQ-FE-007 | P1 | `openspec/changes/corvus-frontend-entry/specs/frontend/spec.md` | 前端加载剧本列表 `GET /scripts` → 每个 Script 对象的 engine_type 正确解析 → 点击"开始游戏"时根据 engine_type 走对应流程。**用户动作**：选择剧本 → 点击开始；**可观察结果**：走 Corvus 流程 | 前端 game.ts loadScripts 解析 engine_type + startGame 分支 | T-038-FE-006 | ✅ 已实现 | Browser E2E: `frontend/tests/e2e/cr038-script-selection.spec.ts` 选择剧本 → 开始 → Corvus 流程 | Verified | covered |Browser E2E 需要真实后端+Corvus 运行环境，编译环境无法运行 Playwright；QA 阶段验证| — | loadScripts TypeScript 类型自动解析 engine_type；startGame 根据 engine_type 分流；Browser E2E PASSED (QA 第三次测试) |
| AC-038-024 | REQ-FE-007 | P1 | `openspec/changes/corvus-frontend-entry/specs/frontend/spec.md` | C3 约束下全部剧本 engine_type='corvus' → 用户选择任意剧本 → 走 Corvus 流程 → Legacy 代码路径不执行。**用户动作**：选择任意剧本；**可观察结果**：走 Corvus 流程 | 前端 game.ts C3 约束处理 (全部走 Corvus 分支) | T-038-FE-006 | ✅ 已实现 | Browser E2E: `frontend/tests/e2e/cr038-script-selection.spec.ts` 任意剧本 → Corvus 流程 | Verified | covered |Browser E2E 需要真实后端+Corvus 运行环境，编译环境无法运行 Playwright；QA 阶段验证| — | C3 约束：后端返回 engine_type='corvus'，前端 startGame 自动走 Corvus 分支；Browser E2E PASSED (QA 第三次测试) |
| AC-038-025 | REQ-CAP-003 | P1 | `openspec/changes/corvus-frontend-entry/specs/capability/spec.md` | 前端代码库包含 legacy 游戏路径代码 → 用户选择任意剧本 → 走 Corvus 流程 → Legacy 代码不被执行 → Legacy 代码不被删除。**可验证结果**：代码库中 legacy 代码仍存在但不激活 | 前端 game.ts legacy 分支条件保留 (ADR-0012) | T-038-FE-006 | ✅ 已实现 | 代码审查 + Browser E2E: `frontend/tests/e2e/cr038-script-selection.spec.ts` | Verified | covered |Browser E2E 需要真实后端+Corvus 运行环境，编译环境无法运行 Playwright；QA 阶段验证| — | ADR-0012：legacy 分支以条件分支保留（if (isCorvus) { ... } else { ... }），不删除；Browser E2E PASSED (QA 第三次测试) |
| AC-038-026 | REQ-CAP-002 | P0 | `openspec/changes/corvus-frontend-entry/specs/capability/spec.md` | `GET /api/v1/game/scripts/{script_id}/characters` → 返回 `code:0` + `data` 数组，每个对象含 id/name/description/avatar_url/play_description；数据来源为 Character 表 `playable=True` 记录 | 后端 `game.py` 新增 GET /game/scripts/{script_id}/characters 端点 | T-038-BE-003 (新增) | ✅ 已实现 | `cd /root/isekai-wanderer/backend && .venv/bin/python -m pytest tests/unit/test_script_characters.py -v` → 5/5 PASSED; Delivery E2E: `curl http://localhost:8081/api/v1/game/scripts/{script_id}/characters` → code:0 + 3 角色列表（林辰/苏瑶/夏目）; PL 独立 E2E 15/15 passed | Verified | covered | — | 改造完成：新增端点 + 单元测试 + Delivery E2E 全通过 | 2026-09-10 改造完成验证 |

## 状态规则

- `覆盖状态` 只允许使用 `covered`、`not_covered`、`manual_pending`、`deferred_with_approval`、`out_of_scope_with_reason`。
- P0/P1 验收项不得缺少 `覆盖状态`、`未覆盖原因` 或 `PL 处理`。
- 发布关口前，P0/P1 不能是 `not_covered`。
- 前端可见的数据展示、列表、详情、刷新和状态查询必须作为独立可测试 AC 或明确设计落点记录，不能只写创建/更新/删除。

## 验收约束摘要

以下 AC 需要下游角色在 DESIGN/DEVELOPMENT 阶段特别关注：

### 需要 Browser Interaction E2E 的 AC

| AC | 验收要点 | 用户动作 | 可观察结果 |
| --- | --- | --- | --- |
| AC-038-009 | Corvus 剧本开始游戏 | 点击"开始游戏" | 进入选角/游戏界面 |
| AC-038-010 | 选角列表展示 | 等待选角页面加载 | 可见预设角色卡片列表 |
| AC-038-011 | 选定预设角色进入游戏 | 点击角色 → 点击确认 | 进入游戏界面，SSE 开始 |
| AC-038-012 | 查看预设角色列表 | 打开选角界面 | 可见预设角色卡片列表 |
| AC-038-013 | ❌ 已移除 | — | — |
| AC-038-014 | ❌ 已移除 | — | — |
| AC-038-015 | ❌ 已移除 | — | — |
| AC-038-016 | 选择预设角色进入游戏 | 点击角色 → 确认 | 进入游戏界面 |
| AC-038-017 | SSE 流式渲染 | 输入文字 → 发送 | 文字逐步渲染 |
| AC-038-019 | SSE 错误处理 | 模拟断连 → 重试 | 错误提示，重试可用 |
| AC-038-020 | 无预设选项降级 | 完成对话 → 观察 | 输入框可见可用 |
| AC-038-022 | 旧数据兼容 | 恢复旧会话 | legacy 分支正常 |
| AC-038-023 | 剧本列表 engine_type | 选择剧本 → 开始 | 走 Corvus 流程 |
| AC-038-024 | Legacy 保留不激活 | 选择任意剧本 | 走 Corvus 流程 |

### 需要 API/DB/Runtime 契约验证的 AC

| AC | 验收要点 | 数据来源 | 可验证结果 |
| --- | --- | --- | --- |
| AC-038-001 | GET /scripts 列表 engine_type | 后端 GET /scripts | 每个 script 有 engine_type |
| AC-038-002 | GET /scripts/{id} 详情 engine_type | 后端 GET /scripts/{id} | script 有 engine_type |
| AC-038-003 | 创建角色候选 | POST /game/player/candidates + DB player_candidates | code:0 + UUID v4 |
| AC-038-004 | name 缺失拒绝 | POST /game/player/candidates | 400 错误 |
| AC-038-005 | 超过 3 个拒绝 | POST /game/player/candidates | 400 错误 |
| AC-038-011 | 选定角色 | DB corvus_game_sessions + select-player | status=playing |
| AC-038-018 | SSE gm_update | SSE 事件 | 好感度/道具更新 |
| AC-038-021 | 恢复 Corvus 会话 | localStorage + GET /game/{id} | engine_type='corvus' |

### 不得使用 mock 作为发布证据的 AC

所有 P0 AC（AC-038-001~005, AC-038-007~011, AC-038-012~019, AC-038-021）不得使用 mock 数据、mock API 或静态假数据作为发布证据。必须使用真实 Corvus 服务、真实后端 API、真实 PostgreSQL 验证。

### 角色候选字段定义（INIT 附条件 1 回答）

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| name | string (≤100) | ✅ 必填 | 角色名字 |
| personality | string | ❌ 可选 | 角色性格描述 |
| backstory | string | ❌ 可选 | 角色完整背景故事 |
| appearance | string | ❌ 可选 | 角色外貌描述 |

依据：后端 PlayerCandidate model 中 name 为 nullable=False，其余为 nullable=True。initial_inventory 由后端管理，用户不填写。

---

## 安全审查结论

- **审查人**: Cat01-security
- **审查日期**: 2026-09-06T16:30:00+08:00
- **审查文件**: `workflow/changes/CR-038/security-review.md`
- **总体结论**: ✅ **PASS**

### 安全相关验收项验证

| AC | 安全检查项 | 结论 | 证据 |
|---|---|---|---|
| AC-038-001~002 | GET /scripts engine_type 后端硬编码, 不接受外部参数 | ✅ PASS | scripts.py 虚拟字段; Delivery E2E Mock API=no |
| AC-038-003~006 | POST /game/player/candidates Bearer 认证 + Pydantic 校验 + ≤3 限制 + 用户隔离 | ✅ PASS | game.py Depends(get_current_user_id); Field(..., max_length=100); CANDIDATE_LIMIT_EXCEEDED |
| AC-038-007~008 | Script/GameSession interface engine_type 必填 (防篡改) | ✅ PASS | npm run build exit 0; TypeScript 编译通过 |
| AC-038-021 | 会话恢复 engine_type 从后端读取, 不接受前端参数 | ✅ PASS | game.ts resumeSession 从 API 响应读取; Browser E2E PASSED |
| AC-038-022 | 旧数据兼容默认 legacy, 不影响 Corvus 安全 | ✅ PASS | game.ts `|| 'legacy'` 默认值; Browser E2E PASSED |

### CR-037 遗留安全问题

| # | 安全项 | 结论 | 证据 |
|---|---|---|---|
| 1 | 公网 8082 iptables DROP | ✅ PASS | ACCEPT 127.0.0.1 + Docker 网段; DROP 0.0.0.0/0 |
| 2 | config.json 权限 600 | ✅ PASS | `-rw------- 1 root root` |
| 3 | SSE 错误通用化 | ✅ PASS | 'Corvus 服务连接失败, 请重试' / '服务器内部错误, 请重试' |

### 发布证据安全验证

| 检查项 | 结论 |
|---|---|
| CI/CD (单元测试 + 编译) | ✅ 6/6 PASSED + npm build exit 0 |
| Delivery E2E / Runtime Smoke (Mock API=no) | ✅ 7/7 PASS |
| Browser Interaction E2E (Mock API=no) | ✅ 17/17 passed |
| 无 mock/fixture/MSW/未记录数据源作为发布证据 | ✅ |
| 追踪链无断链 | ✅ PRD → REQ → AC → Design → Task → Code → Test → Release |

### 阻塞项

无阻塞项。

### 高风险事项

无新增高风险项。Corvus systemd 0.0.0.0 绑定已被 iptables 补偿（非阻塞建议改 127.0.0.1）。deploy-plan.md 不存在属 PL 交付物缺口（非安全阻塞）。

### 人工确认需求

不需要。本 CR 未涉及生产/支付/数据删除风险。
