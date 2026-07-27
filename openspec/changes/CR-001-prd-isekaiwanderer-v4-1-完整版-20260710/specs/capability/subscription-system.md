# S025 订阅方案体系（Mock）

## Capability: 订阅方案体系

### Requirement: Mock 订阅页面展示

系统在订阅页面展示 4 档订阅方案（Free/Basic/Standard/Premium），每档支持月付和年付，支持 4 种货币（USD/JPY/EUR/KRW），全部使用 mock 定价和 mock 支付流程。

#### Scenario: 用户浏览订阅方案

**Given** 用户已登录
**When** 用户进入订阅页面
**Then** 系统展示 4 档方案卡片（Free/Basic/Standard/Premium），每档包含名称、价格（月付/年付）、权益列表和选择按钮
**And** 所有付费方案标注"[Mock]"标识，明确非真实支付
**And** 用户可切换货币显示（USD/JPY/EUR/KRW），价格按汇率换算

#### Scenario: 用户选择订阅方案

**Given** 用户在订阅页面
**When** 用户点击某方案的"订阅"按钮并选择月付/年付
**Then** 系统弹出 mock 支付确认弹窗（显示方案信息和 mock 支付按钮）
**And** 用户点击确认后，订阅立即生效，展示成功提示

### Requirement: 订阅状态管理

系统管理用户的订阅状态（活跃/过期/取消），mock 模式下自动处理续费和过期。

#### Scenario: 订阅生效

**Given** 用户确认 mock 订阅
**When** mock 支付模块返回成功
**Then** 系统更新用户订阅状态为"活跃"，记录方案、周期、到期时间
**And** 用户获得对应权益（如每日额外碎片、优先客服、解锁内容）

#### Scenario: 订阅到期

**Given** 用户有活跃订阅且到达到期时间
**When** 系统每日检查订阅状态
**Then** 系统将订阅状态更新为"过期"，用户权益降级为 Free 档

### Requirement: 订阅取消

用户可以取消当前订阅，取消后权益在当前周期结束时失效。

#### Scenario: 用户取消订阅

**Given** 用户有活跃订阅
**When** 用户在订阅管理页面点击"取消订阅"并确认
**Then** 系统标记订阅为"已取消"，当前周期结束前权益不变
**And** 展示取消成功提示和权益失效时间

### Requirement: 订阅接口抽象层

系统订阅模块通过抽象接口实现，架构预留真实订阅接口（Apple/Google/Stripe），mock 和真实使用同一接口。

#### Scenario: 订阅接口可替换

**Given** 系统订阅模块使用抽象接口（ISubscriptionProvider）
**When** 用户后续替换为真实支付凭证
**Then** 仅需修改配置和实现类，不改架构和调用方代码
