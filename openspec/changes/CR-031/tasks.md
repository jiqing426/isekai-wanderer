# CR-031 任务清单

## Implementation Tasks

| 任务编号 | 负责人 Agent | 关联验收项 | 允许写入范围 | 测试用例产物 | 状态 |
|----------|--------------|------------|--------------|--------------|------|
| T-031-01a | be | AC-031-001 | backend/app/api/v1/game.py | tests/api/test_cr031_session.py | done |
| T-031-01b | fe | AC-031-001 | frontend/src/stores/game.ts | tests/e2e/cr031-resume.spec.ts | done |
| T-031-02a | be | AC-031-002 | N/A（验证已有逻辑） | tests/api/test_cr031_affection.py | done |
| T-031-02b | fe | AC-031-002 | frontend/src/stores/game.ts | tests/e2e/cr031-autosave.spec.ts | done |
| T-031-03 | fe | AC-031-003 | frontend/src/views/GameView.vue | tests/e2e/cr031-avatar.spec.ts | done |
| T-031-04 | fe | AC-031-004 | frontend/src/views/ScriptDetailView.vue, frontend/src/components/EndingList.vue | tests/e2e/cr031-endings.spec.ts | done |

## 任务总览

| 任务编号 | 任务名称 | 负责人 | 关联 AC | 预估工时 | 状态 |
|----------|----------|--------|---------|----------|------|
| T-031-01a | BE: 修复 GET /game/:sessionId 返回完整状态 | be | AC-031-001 | 0.5h | done |
| T-031-01b | FE: 修复 resumeSession() 先获取完整状态 | fe | AC-031-001 | 1h | done |
| T-031-02a | BE: 验证好感度持久化 | be | AC-031-002 | 0.5h | done |
| T-031-02b | FE: submitChoice 后调用 auto-save | fe | AC-031-002 | 0.5h | done |
| T-031-03 | FE: 修复 playerCharacterAvatar fallback | fe | AC-031-003 | 0.5h | done |
| T-031-04 | FE: 修复结局展示只显示一个的问题 | fe | AC-031-004 | 1h | done |
