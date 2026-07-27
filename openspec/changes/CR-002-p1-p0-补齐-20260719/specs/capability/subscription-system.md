# Subscription System — CR-002 测试补齐

> 本规格覆盖 CR-001 已有订阅系统的 P0 测试补齐。功能已在 CR-001 实现，本 CR 仅补齐自动化测试。

## Background

CR-001 已实现订阅方案体系：Free/Basic/Standard/Premium 四档、月付/年付、试用机制。但 1 项 P0 测试（订阅到期降级）未运行，需要在 Phase 2 补齐自动化验证。

## Requirements

### Requirement: 订阅到期自动降级

订阅到期后状态变为过期，用户权益必须降级为免费档；用户可取消订阅，当前周期结束前权益不变。

#### Scenario: 订阅到期降级

- Given: 用户订阅 Standard 档，到期日为 2026-08-01
- When: 当前时间超过 2026-08-01
- Then: 订阅状态变为 expired
- And: 用户权益降级为 Free 档
- And: 付费功能（如高级剧本）不可访问

#### Scenario: 取消订阅后权益保持到周期结束

- Given: 用户订阅 Premium 档，到期日为 2026-08-15
- When: 用户在 2026-08-01 取消订阅
- Then: 订阅状态变为 cancelled
- And: 当前周期内（到 2026-08-15）权益不变
- And: 周期结束后自动降级为 Free

#### Scenario: 续费恢复权益

- Given: 用户订阅已过期，当前为 Free 档
- When: 用户续费 Standard 档
- Then: 订阅状态变为 active
- And: 权益恢复为 Standard 档
- And: 付费功能重新可用

## Implementation Notes

- 所有功能已在 CR-001 实现（subscription_service、订阅状态机）
- 本 CR Phase 2 仅补齐测试：pytest + Delivery（时间模拟到期/取消/续费）
- 不需要新增代码，只需新增测试用例

## R/C/U/D Matrix

| Action | User | System | Notes |
|---|---|---|---|
| Create | user | system | 用户订阅创建 |
| Read | user | system | 用户查看订阅状态 |
| Update | system | system | 到期自动降级 |
| Delete | — | — | — |

## Downstream Constraints

| Consumer | Contract |
|---|---|
| DEV-CR2-019 | pytest + Delivery：时间模拟到期/取消/续费测试 |
| QA Phase 2 | 测试用例必须 Mock API=no |
