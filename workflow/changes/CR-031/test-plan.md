# CR-031 Test Plan

## Test-First Scope

- AC-031-001: 继续游戏恢复正确角色和进度
- AC-031-002: 游戏进度（节点、好感度）持久化
- AC-031-003: 头像显示逻辑统一（无头像显示首字母）

## Test Cases

| 任务编号 | 测试用例产物 | 覆盖验收项 | 状态 |
|----------|--------------|------------|------|
| T-031-01 | tests/api/test_cr031_resume.py | AC-031-001 | Ready |
| T-031-02 | tests/api/test_cr031_autosave.py | AC-031-002 | Ready |
| T-031-03 | tests/e2e/cr031-avatar.spec.ts | AC-031-003 | Ready |

## Red Failure Records

| 任务编号 | 失败 ID | 失败现象 | 修复状态 |
|----------|---------|----------|----------|
| T-031-01 | RED-001 | 待记录 | Pending |
| T-031-02 | RED-002 | 待记录 | Pending |
| T-031-03 | RED-003 | 待记录 | Pending |
