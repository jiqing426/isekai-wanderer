# Daily Streak — CR-002 测试补齐

> 本规格覆盖 CR-001 已有签到系统的 P0 测试补齐。功能已在 CR-001 实现，本 CR 仅补齐自动化测试。

## Background

CR-001 已实现每日签到 Streak 系统：每日自动签到、连续天数追踪、Day 3/7/14/30 阶梯奖励、签到月历 UI。但 2 项 P0 测试未运行，需要在 Phase 2 补齐自动化验证。

## Requirements

### Requirement: 签到阶梯奖励发放

streak 达到 Day 3/7/14/30 时，系统必须发放对应阶梯奖励（碎片 + 特殊内容），并展示奖励弹窗。

#### Scenario: Day 3 奖励发放

- Given: 用户 streak = 2
- When: 用户今日签到后 streak = 3
- Then: 系统发放 Day 3 奖励（碎片 + 隐藏对话）
- And: 奖励弹窗展示奖励内容

#### Scenario: Day 7 奖励发放

- Given: 用户 streak = 6
- When: 用户今日签到后 streak = 7
- Then: 系统发放 Day 7 奖励（碎片 + 稀有 CG）
- And: 奖励弹窗展示奖励内容

#### Scenario: Day 14 和 Day 30 奖励

- Given: 用户 streak = 13 或 29
- When: 用户签到后达到 Day 14 或 30
- Then: 系统发放对应阶梯奖励
- And: 奖励内容符合 PRD 定义

### Requirement: 签到月历 UI 展示

用户进入签到页面可查看当月签到日历，已签到日期标记，当前 streak 天数和下一阶梯进度。

#### Scenario: 签到日历展示

- Given: 用户已签到 5 天
- When: 用户进入签到页面
- Then: 月历展示当月，已签到日期有标记
- And: 显示当前 streak = 5
- And: 显示下一阶梯（Day 7）进度 2/7

#### Scenario: 跨月签到

- Given: 上月最后签到日为 31 日
- When: 本月 1 日用户签到
- Then: 月历切换为本月
- And: streak 连续计算（不重置）

## Implementation Notes

- 所有功能已在 CR-001 实现（daily_service、StreakCalendar.vue）
- 本 CR Phase 2 仅补齐测试：pytest + Delivery（种子数据驱动奖励测试）、Playwright（月历 UI 验证）
- 不需要新增代码，只需新增测试用例

## R/C/U/D Matrix

| Action | User | System | Notes |
|---|---|---|---|
| Create | — | system | 签到记录自动创建 |
| Read | user | system | 用户查看月历和 streak |
| Update | system | system | streak 自动递增 |
| Delete | — | — | — |

## Downstream Constraints

| Consumer | Contract |
|---|---|
| DEV-CR2-016 | pytest + Delivery：种子数据驱动 Day 3/7/14/30 奖励测试 |
| DEV-CR2-017 | Playwright：签到日历 UI 展示验证 |
| QA Phase 2 | 测试用例必须 Mock API=no |
