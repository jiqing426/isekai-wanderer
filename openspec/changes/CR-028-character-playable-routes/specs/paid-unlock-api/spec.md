# Spec: 付费角色解锁接口

### Requirement: 付费角色解锁 API（暂不实现支付）

#### Scenario: 解锁接口接受请求
- **Given** 用户已登录
- **When** 调用 POST /characters/{character_id}/unlock
- **Then** 接口验证 character_id 存在且 unlock_type='paid'
- **And** 检查用户是否已解锁（幂等）
- **And** 本期直接写入 user_character_unlocks 记录（模拟解锁，不扣费）
- **And** 返回 200 + 解锁成功信息

#### Scenario: 解锁免费角色返回错误
- **Given** 角色 unlock_type='free'
- **When** 调用 POST /characters/{character_id}/unlock
- **Then** 返回 400 错误"免费角色无需解锁"

#### Scenario: 解锁已解锁角色幂等
- **Given** 用户已解锁该角色
- **When** 再次调用 POST /characters/{character_id}/unlock
- **Then** 返回 200（幂等）
- **And** 不插入重复记录

#### Scenario: 未登录用户调用解锁接口
- **Given** 用户未登录
- **When** 调用 POST /characters/{character_id}/unlock
- **Then** 返回 401 未授权

### Requirement: 解锁接口预留支付扩展

#### Scenario: 接口设计支持后续接入支付
- **Given** 解锁接口当前直接写入记录
- **When** 后续 CR 接入支付流程
- **Then** 接口签名不变（POST /characters/{character_id}/unlock）
- **And** 仅内部逻辑变更为：先创建支付订单 → 支付回调 → 写入解锁记录
- **And** unlock_price 字段已存在，无需新增字段
