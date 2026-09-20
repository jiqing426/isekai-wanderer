# Implementation Tasks: Corvus Frontend Entry (CR-038)

## Implementation Tasks

| Task ID | Owner Agent | Module | Description | Requirement / AC | Excluded AC | Allowed Write Scope | Test Case Artifact | Verification | Rollback / Revert Plan | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| T-038-BE-001 | BE (`Cat01-be`) | backend `scripts.py` | GET /scripts 和 GET /scripts/{id} 返回 engine_type: 'corvus' 字段 | AC-038-001, AC-038-002 | 无 | `backend/app/api/v1/scripts.py` | `backend/tests/unit/test_scripts_engine_type.py` | `curl http://localhost:8081/api/v1/scripts` 验证每个对象有 engine_type='corvus'; `curl http://localhost:8081/api/v1/scripts/{id}` 验证 engine_type='corvus' | `git revert <commit>`; engine_type 字段移除后前端 fallback 为 undefined，不影响现有流程 | Implemented |
| T-038-BE-002 | ~~BE (`Cat01-be`)~~ | ~~backend `game.py`~~ | ~~POST /game/player/candidates 创建端点~~ | ~~AC-038-003~006~~ | — | — | — | — | **DEPRECATED** — 2026-09-07 范围变更：移除自定义角色创建 | Deprecated |
| T-038-FE-001 | FE (`Cat01-fe`) | frontend `stores/game.ts` + `api/game.ts` | Script interface 新增 engine_type 必填字段；GameSession interface engine_type 改必填（去掉 ?） | AC-038-007, AC-038-008 | 无 | `frontend/src/stores/game.ts` (Script, GameSession interfaces), `frontend/src/api/game.ts` (Script interface) | `npm run build` 编译检查 | `cd frontend && npm run build` → exit 0 | `git revert <commit>`; 恢复可选标记，不影响现有代码 | Implemented |
| T-038-FE-002 | FE (`Cat01-fe`) | frontend `stores/game.ts` | startGame() 改造（**2026-09-07 修订**）：Corvus 剧本走 POST /game/session/create → 选角（GET /game/scripts/{script_id}/characters）→ POST /game/session/select-player（传 character_id）→ 进入游戏；写入 engine_type: 'corvus' | AC-038-009, AC-038-010, AC-038-011 | AC-038-012~016 (选角 UI), AC-038-017~020 (SSE 流式渲染) | `frontend/src/stores/game.ts` (startGame function, selectPlayer function) | `tests/e2e/cr038-start-game.spec.ts` | Browser E2E: 选择剧本 → 点击开始游戏 → 进入选角界面 → 选择预设角色 → 确认 → 进入游戏界面 | `git revert <commit>`; startGame 恢复为仅调用 POST /game/start，不影响 legacy 流程 | **Redev** |
| T-038-FE-003 | FE (`Cat01-fe`) | frontend `PlayerCandidateModal.vue` | 选角 UI 改造（**2026-09-07 修订**）：移除创建表单和自定义角色区域，改为只展示预设角色卡片列表（数据来源 GET /game/scripts/{script_id}/characters）；保留角色选择和确认流程 | AC-038-010, AC-038-012, AC-038-016 | 无 | `frontend/src/components/PlayerCandidateModal.vue` (改造), `frontend/src/stores/game.ts` (selectPlayer 改为传 character_id) | `tests/e2e/cr038-candidate-management.spec.ts` | Browser E2E: 打开选角界面 → 可见预设角色卡片; 点击角色 → 高亮 → 确认 → 进入游戏 | `git revert <commit>`; 恢复创建表单版本 | **Redev** |
| T-038-FE-004 | FE (`Cat01-fe`) | frontend `stores/game.ts` | SSE 流式渲染激活：submitChoice/submitCustomInput 的 Corvus SSE 分支已存在，补齐 gm_update UI 更新逻辑；error 重试；choices 为空降级 | AC-038-017, AC-038-018, AC-038-019, AC-038-020 | 无 | `frontend/src/stores/game.ts` (submitChoice, submitCustomInput 的 gm_update 处理), `frontend/src/components/StoryPanel.vue` (好感度/道具 UI 更新) | `tests/e2e/cr038-sse-streaming.spec.ts` | Browser E2E: 输入文字 → 发送 → 观察逐字渲染; 对话中好感度/道具更新; 模拟断连 → 错误提示 → 重试; 完成对话 → 输入框可见 | `git revert <commit>`; gm_update 处理恢复为空注释，SSE 文本渲染不受影响（已在 CR-037 实现） | Implemented |
| T-038-FE-005 | FE (`Cat01-fe`) | frontend `stores/game.ts` | resumeSession() 补齐 engine_type：新会话写入 'corvus'，旧数据兼容处理（无 engine_type 视为 'legacy'） | AC-038-021, AC-038-022 | 无 | `frontend/src/stores/game.ts` (resumeSession function) | `tests/e2e/cr038-resume-session.spec.ts` | Browser E2E: 恢复 Corvus 会话 → engine_type='corvus' → SSE 分支; 恢复旧会话 → legacy 分支 | `git revert <commit>`; resumeSession 恢复为不写 engine_type，旧代码不受影响 | Implemented |
| T-038-FE-006 | FE (`Cat01-fe`) | frontend `stores/game.ts` + 视图 | 剧本选择页区分引擎类型：loadScripts 解析 engine_type；startGame 根据 engine_type 走对应流程；Legacy 分支保留不激活 | AC-038-023, AC-038-024, AC-038-025 | 无 | `frontend/src/stores/game.ts` (loadScripts), `frontend/src/views/ScriptDetailView.vue` 或 `GameView.vue` (按 engine_type 分支) | `tests/e2e/cr038-script-selection.spec.ts` | Browser E2E: 选择任意剧本 → 开始 → 走 Corvus 流程; 代码审查确认 legacy 代码仍存在但不激活 | `git revert <commit>`; loadScripts 恢复原样，不影响现有流程 | Implemented |
| T-038-BE-003 | BE (`Cat01-be`) | backend `game.py` | **新增 (2026-09-07)** GET /api/v1/game/scripts/{script_id}/characters 端点：返回 Character 表 playable=True 的角色列表（id/name/description/avatar_url/play_description） | AC-038-026, AC-038-010, AC-038-012 | 无 | `backend/app/api/v1/game.py` (新增 GET /game/scripts/{script_id}/characters), `backend/app/schemas/game.py` (如需 CharacterResponse schema) | `backend/tests/unit/test_script_characters.py` | Delivery E2E: `curl http://localhost:8081/api/v1/game/scripts/{script_id}/characters` → code:0 + 可扮演角色列表 | `git revert <commit>`; 端点移除后不影响现有功能 | **New** |

## Task Dependencies

```
T-038-BE-001 (GET /scripts engine_type) ──┐
                                          ├── T-038-FE-001 (Interface 补齐) ──┐
T-038-BE-002 (~~POST /candidates~~ DEPRECATED) ──┤                       │
                                               ├── T-038-FE-002 (startGame 改造) ──┐
T-038-BE-003 (GET /scripts/{id}/characters) ───┤                                   ├── T-038-FE-003 (选角 UI 改造)
                                               │                                   │
                                               │                                   ├── T-038-FE-004 (SSE 激活)
                                               │                                   │
                                               ├── T-038-FE-005 (resumeSession) ──┘
                                               │
                                               └── T-038-FE-006 (剧本选择页区分)
```

- T-038-BE-001 和 T-038-BE-003 可并行
- T-038-BE-002 已 DEPRECATED（范围变更移除）
- T-038-FE-002 依赖 T-038-BE-003（startGame 选角需调用 GET /scripts/{id}/characters）和 T-038-FE-001
- T-038-FE-003 依赖 T-038-FE-002（选角 UI 嵌入 startGame 流程）和 T-038-BE-003（数据来源）
- T-038-FE-004 可与 T-038-FE-003 并行（SSE 代码已存在，补齐 gm_update）
- T-038-FE-005 可与 T-038-FE-002 并行
- T-038-FE-006 依赖 T-038-FE-001

## Module Breakdown Summary

| 模块 | 任务数 | 负责人 | 验证方式 | 回滚关注点 |
|---|---|---|---|---|
| 后端 scripts.py | 1 (T-038-BE-001) | BE | curl API 验证 | 移除 engine_type 字段不影响现有流程 |
| 后端 game.py | 1 (T-038-BE-002) | BE | curl API 验证 + DB 检查 | 移除端点不影响 GET /game/player/candidates |
| 前端 game.ts interfaces | 1 (T-038-FE-001) | FE | npm run build 编译检查 | 恢复可选标记不影响现有代码 |
| 前端 startGame | 1 (T-038-FE-002) | FE | Browser E2E | 恢复 legacy startGame 路径 |
| 前端选角 UI | 1 (T-038-FE-003) | FE | Browser E2E | 删除新组件不影响现有组件 |
| 前端 SSE | 1 (T-038-FE-004) | FE | Browser E2E | gm_update 恢复为空注释 |
| 前端 resumeSession | 1 (T-038-FE-005) | FE | Browser E2E | 恢复不写 engine_type |
| 前端剧本选择 | 1 (T-038-FE-006) | FE | Browser E2E + 代码审查 | 恢复原 loadScripts |
