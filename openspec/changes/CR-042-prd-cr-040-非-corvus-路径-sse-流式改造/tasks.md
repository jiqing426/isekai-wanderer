# Tasks

## Implementation Tasks

| Task ID | Phase | Owner Agent | Requirement / AC | Consumers | Excluded AC | Allowed Write Scope | Test Case Artifact | Verification | Rollback / Revert Plan | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEV-001 | DEVELOPMENT | Cat01-be | AC-001, AC-002, AC-003, AC-004, AC-006, AC-007, AC-008, AC-009, AC-011, AC-012, AC-013, AC-014, AC-015, AC-017, AC-018, AC-019 | backend/app/api/v1/game.py (submit_choice Legacy SSE branch, submit_custom_input Legacy SSE branch, free-chat/stream new endpoint), backend/app/llm/model_router.py (stream_with_fallback), backend/app/services/free_chat_service.py (send_message_stream), backend/app/api/v1/game.py (_stream_legacy_turn, _stream_legacy_custom_input, _run_legacy_deferred, _run_legacy_custom_input_deferred helper functions) | 无 | backend/app/api/v1/game.py, backend/app/llm/model_router.py, backend/app/services/free_chat_service.py | `workflow/changes/CR-042/test-plan.md` | 单元测试 (model_router stream_with_fallback) + 集成测试 (SSE 端点 API 契约) + API 契约验证 (Content-Type, SSE 事件格式, X-Accel-Buffering header) | 回滚到同步 JSON 响应（旧端点保留兼容，git revert 端点层改动即可恢复） | Ready |
| DEV-002 | DEVELOPMENT | Cat01-fe | AC-005, AC-010, AC-016, AC-020, AC-021, AC-022 | frontend/src/stores/game.ts (Legacy submitChoice SSE branch, Legacy submitCustomInput SSE branch, Corvus branch SSE migration), frontend/src/views/FreeChatView.vue (switch to streaming endpoint), frontend/src/composables/useSSEStream.ts (new), frontend/src/api/game.ts (free-chat/stream API call) | 无 | frontend/src/composables/useSSEStream.ts, frontend/src/stores/game.ts, frontend/src/views/FreeChatView.vue, frontend/src/api/game.ts | `workflow/changes/CR-042/test-plan.md` | 单元测试 (useSSEStream composable SSE event parsing) + Browser Interaction E2E (Legacy SSE 逐字显示, Corvus 回归) + 代码审查 (三处使用 composable) | 回滚到各路径独立 inline SSE 解析逻辑（Corvus 保持原逻辑，Legacy 回退到 JSON 同步响应） | Ready |

## Task Rules

- 每个任务必须关联至少一个 AC 编号。
- 每个涉及 API、页面、管理端或用户动作的任务必须填写 `Consumers`，明确哪个页面、组件、菜单、按钮、调用方或脚本会消费这项能力。
- 不覆盖的 AC 必须显式写入 `不覆盖验收项`；无不覆盖项时写 `无`。
- 声明任务完成前，必须在 `workflow/changes/<CR-ID>/review.md` 写开发覆盖声明。
- DEV-001（后端）先于 DEV-002（前端）— 前端依赖后端端点签名。
- BE 先行：model_router stream_with_fallback → narrative_engine stream → game.py 端点 → free_chat_service stream。
- FE 依赖 BE 端点签名确认后再开发。

## Dependency

```
DEV-001 (BE)
  ├─ model_router.stream_with_fallback()  ← AC-017, AC-018, AC-019
  ├─ game.py _stream_legacy_turn()  ← AC-001, AC-002, AC-003, AC-004
  ├─ game.py _stream_legacy_custom_input()  ← AC-006, AC-007, AC-008, AC-009
  ├─ game.py free-chat/stream 新端点  ← AC-011, AC-013, AC-014, AC-015
  ├─ free_chat_service.send_message_stream()  ← AC-013
  └─ 旧端点 deprecation header  ← AC-015
     ↓ (BE 端点签名确认后)
DEV-002 (FE)
  ├─ composables/useSSEStream.ts 提取  ← AC-020
  ├─ stores/game.ts Legacy submitChoice SSE  ← AC-005
  ├─ stores/game.ts Legacy submitCustomInput SSE  ← AC-010
  ├─ FreeChatView.vue 改用流式端点  ← AC-016
  ├─ 三处 Legacy 路径使用 composable  ← AC-021
  └─ Corvus 分支迁移 + 回归验证  ← AC-022
```

## BE Implementation Order (DEV-001)

1. `model_router.stream_with_fallback()` — 基础设施，无依赖
2. `free_chat_service.send_message_stream()` — 依赖 stream_with_fallback
3. `game.py _stream_legacy_turn()` + `_run_legacy_deferred()` — submit_choice Legacy SSE
4. `game.py _stream_legacy_custom_input()` + `_run_legacy_custom_input_deferred()` — submit_custom_input Legacy SSE
5. `game.py POST /game/{id}/free-chat/stream` 新端点
6. `game.py POST /game/{id}/free-chat` 旧端点追加 deprecation header

## FE Implementation Order (DEV-002)

1. `composables/useSSEStream.ts` 提取 — 基础设施，无依赖
2. `stores/game.ts` Legacy submitChoice 分支使用 composable
3. `stores/game.ts` Legacy submitCustomInput 分支使用 composable
4. `FreeChatView.vue` 改用流式端点 + composable
5. `stores/game.ts` Corvus 分支迁移到 composable
6. Corvus 回归 E2E 验证（CEO 附条件 C2）
