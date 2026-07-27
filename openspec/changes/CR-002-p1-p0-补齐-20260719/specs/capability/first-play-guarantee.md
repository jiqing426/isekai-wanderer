# First Play Guarantee — CR-002 测试补齐

> 本规格覆盖 CR-001 已有首玩保障功能的 P0 测试补齐。功能已在 CR-001 实现，本 CR 仅补齐自动化测试。

## Background

CR-001 已实现首玩保障：新用户首次 AI 对话失败时（超时/质量不达标），系统自动使用预设引导脚本完成对话，首玩失败率小于 5%。但 1 项 P0 测试未运行，需要在 Phase 2 补齐自动化验证。

## Requirements

### Requirement: AI 失败兜底机制

新用户首次 AI 对话失败时（超时/质量不达标），系统必须自动使用预设引导脚本完成对话，首玩失败率小于 5%。

#### Scenario: Mock Provider 失败率统计

- Given: MockProvider 配置为 3% 失败率
- When: 运行 100 次首玩对话
- Then: 失败次数 < 5
- And: 每次失败后系统自动使用预设脚本恢复
- And: 用户端无空白或错误提示

#### Scenario: 超时触发兜底

- Given: MockProvider 配置为超时模式
- When: 首玩对话超时
- Then: onboarding_service 自动切换到预设脚本
- And: 对话继续，用户感知不到超时

#### Scenario: 质量不达标触发兜底

- Given: MockProvider 返回低质量内容
- When: 内容质量检查不通过
- Then: fallback 机制触发，返回预设引导文本
- And: 对话流畅继续

## Implementation Notes

- 所有功能已在 CR-001 实现（onboarding_service、fallback 机制、MockProvider）
- 本 CR Phase 2 仅补齐测试：pytest 单元测试（MockProvider 失败率统计）
- 不需要新增代码，只需新增测试用例

## R/C/U/D Matrix

| Action | User | System | Notes |
|---|---|---|---|
| Create | — | system | 首玩对话自动创建 |
| Read | user | system | 用户看到对话内容 |
| Update | system | system | 失败时自动切换脚本 |
| Delete | — | — | — |

## Downstream Constraints

| Consumer | Contract |
|---|---|
| DEV-CR2-018 | pytest：MockProvider 失败率统计 <5% |
| QA Phase 2 | 测试用例必须验证兜底机制完整性 |
