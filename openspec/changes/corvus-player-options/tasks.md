# Implementation Tasks: Corvus 玩家选项功能 (CR-039)

## Implementation Tasks

| Task ID | Owner Agent | Module | Description | Requirement / AC | Excluded AC | Allowed Write Scope | Test Case Artifact | Verification | Rollback / Revert Plan | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| T-039-GM-001 | BE | Corvus `gameMaster.ts` | GM prompt JSON schema 增加 `playerOptions: [{text, hint}]` 字段；GM 指令追加选项生成规则。**C1 附条件：GM 调优 ≤0.5h，超时以 fallback（空数组=纯自由输入）先上线** | AC-039-001, AC-039-002 | 无 | `/root/code/Corvus-Story-Core/server/services/gameMaster.ts` (GM_SYSTEM_PROMPT) | Delivery E2E: SSE `gm_update` 事件包含 `playerOptions` | Delivery E2E + 单元测试 | `git revert <commit>`; GM prompt 恢复原样，不影响现有功能 | Approved |
| T-039-SSE-001 | BE | Corvus `chat.ts` | `gm_update` SSE 事件带上 `playerOptions` 数据 | AC-039-003 | 无 | `/root/code/Corvus-Story-Core/server/routes/chat.ts` (writeSseEvent gm_update case) | Delivery E2E: SSE 事件含 `playerOptions` 字段 | Delivery E2E | `git revert <commit>`; gm_update 恢复原样 | Approved |
| T-039-BE-001 | BE | 后端 `game.py` | SSE 透传时将 Corvus `playerOptions` 映射为前端期望的 `choices` 格式（`{id, text, hint}`） | AC-039-004 | 无 | `backend/app/api/v1/game.py` (Corvus SSE 透传部分) | Delivery E2E: 前端收到 `choices` 格式数据 | Delivery E2E | `git revert <commit>`; 透传恢复原样 | Approved |
| T-039-FE-001 | FE | 前端 `game.ts` | `gm_update` 事件处理中：将 `player_options`/`choices` 赋值到 `pendingChoices`；选项点击后以选项文字调用 `submitCustomInput` | AC-039-005, AC-039-006, AC-039-007, AC-039-008 | AC-039-009 | `frontend/src/stores/game.ts` (gm_update 事件处理 + ChoicePanel 点击逻辑) | Browser E2E: `tests/e2e/cr039-*.spec.ts` | Browser E2E + `npm run build` | `git revert <commit>`; gm_update 处理恢复原样 | Approved |
| T-039-FE-002 | FE | 前端 `PlayerCandidateModal.vue` + `ScriptDetailView.vue` + `game.ts` + `GameView.vue` | 选角后页面显示初始叙事（非"剧情正在展开..."）；PlayerCandidateModal emit initial_scene；ScriptDetailView 存 sessionStorage；game.ts resumeSession 取 opening_text；GameView 自动发送初始消息 | AC-039-010 | 无 | `frontend/src/components/PlayerCandidateModal.vue` + `frontend/src/views/ScriptDetailView.vue` + `frontend/src/stores/game.ts` + `frontend/src/views/GameView.vue` | Browser E2E: `tests/e2e/cr039-player-options.spec.ts` | Browser E2E + `npm run build` | `git revert <commit>`; 选角后 initial_scene 恢复为空 | Ready |
| T-039-FE-003 | FE | 前端 E2E 测试 | E2E 测试通过 UI 流程验证：点击开始游戏 → 选角 → 验证初始叙事显示（createCorvusSessionViaUI，不用 API 绕过） | AC-039-011 | 无 | `frontend/tests/e2e/cr039-player-options.spec.ts` | Browser E2E: `tests/e2e/cr039-player-options.spec.ts` | Browser E2E | `git revert <commit>`; E2E 测试恢复 API 绕过方式 | Ready |

## Task Dependencies

```
T-039-GM-001 (GM prompt) ──┐
                           ├── T-039-SSE-001 (SSE 事件) ── T-039-BE-001 (后端透传) ── T-039-FE-001 (前端处理)
```

- T-039-GM-001 必须先完成（GM 输出格式定义）
- T-039-SSE-001 和 T-039-BE-001 可并行（SSE 事件扩展 + 后端透传映射）
- T-039-FE-001 依赖 T-039-BE-001（前端需要后端透传的 `choices` 格式）

## Module Breakdown Summary

| 模块 | 任务数 | 负责人 | 验证方式 | 回滚关注点 |
|---|---|---|---|---|
| Corvus gameMaster.ts | 1 (T-039-GM-001) | BE | Delivery E2E | GM prompt 恢复原样 |
| Corvus chat.ts | 1 (T-039-SSE-001) | BE | Delivery E2E | gm_update 恢复原样 |
| 后端 game.py | 1 (T-039-BE-001) | BE | Delivery E2E | 透传恢复原样 |
| 前端 game.ts | 1 (T-039-FE-001) | FE | Browser E2E + npm run build | gm_update 处理恢复原样 |
