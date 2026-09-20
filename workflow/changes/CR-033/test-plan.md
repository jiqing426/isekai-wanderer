# CR-033 Test Plan

## Test-First Scope

- AC-033-001: 星月奇缘第 4 章数据完整性
- AC-033-002: 星辰之约结局数量验证
- AC-033-003: 樱花恋曲结局数量验证
- AC-033-004: API 返回验证
- AC-033-005: 向后兼容回归测试

## Test Cases

| 任务编号 | 测试用例产物 | 覆盖验收项 | 状态 |
|----------|--------------|------------|------|
| T-033-01 | tests/db/test_cr033_chapter4.py | AC-033-001 | Ready |
| T-033-02 | tests/db/test_cr033_endings.py | AC-033-002, AC-033-003 | Ready |
| T-033-04 | tests/api/test_cr033_api.py | AC-033-004 | Ready |
| T-033-05 | tests/api/test_cr033_compat.py | AC-033-005 | Ready |

## Red Failure Records

| 任务编号 | 失败 ID | 失败现象 | 修复状态 |
|----------|---------|----------|----------|
| T-033-01 | RED-001 | 待记录 | Pending |
| T-033-02 | RED-002 | 待记录 | Pending |
| T-033-03 | RED-003 | 待记录 | Pending |
