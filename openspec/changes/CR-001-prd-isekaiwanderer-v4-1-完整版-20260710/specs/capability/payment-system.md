# S024 内购系统（Mock）

## Capability: 内购系统

### Requirement: Mock 内购商品展示

系统在内购商店页面展示 2 类商品（单剧本购买 + 碎片充值），全部使用 mock 定价和 mock 支付流程。架构预留 Apple/Google/Stripe 真实支付接口。

#### Scenario: 用户浏览内购商店

**Given** 用户已登录
**When** 用户进入内购商店页面
**Then** 系统展示 2 类商品：单剧本购买（未购买的剧本）和碎片充值（多档面额）
**And** 所有商品标注"[Mock]"标识，明确非真实支付

#### Scenario: 用户点击购买商品

**Given** 用户在内购商店页面
**When** 用户点击某商品的购买按钮
**Then** 系统弹出 mock 支付确认弹窗（显示商品信息 + mock 支付方式选择：Apple/Google/Stripe）
**And** 用户点击确认后，商品立即到账，展示成功提示

### Requirement: 单剧本购买

用户可以购买尚未解锁的剧本，购买后该剧本变为可用状态。

#### Scenario: 购买新剧本

**Given** 用户有未购买的剧本（如悬疑推理）
**When** 用户点击购买并确认 mock 支付
**Then** 该剧本解锁，用户可进入游玩
**And** 交易流水记录商品 ID、剧本 ID、mock 支付方式、时间

### Requirement: 碎片充值

用户可以充值碎片（虚拟货币），碎片可用于解锁 CG、隐藏对话等内容。

#### Scenario: 充值碎片

**Given** 用户在碎片充值页面
**When** 用户选择充值面额（如 100/500/1000 碎片）并确认 mock 支付
**Then** 碎片余额增加，展示充值成功提示和当前余额

### Requirement: Mock 支付接口抽象

系统支付模块通过抽象接口（IPaymentProvider）实现，架构预留 Apple/Google/Stripe 真实支付接口，mock 和真实使用同一接口。

#### Scenario: Mock 支付完成回调

**Given** 用户确认 mock 购买
**When** mock 支付模块返回成功
**Then** 系统更新用户资产（剧本/碎片）并记录交易流水
**And** 交易流水包含商品 ID、数量、时间、mock 标记

#### Scenario: Mock 支付失败回调

**Given** 用户确认 mock 购买
**When** mock 支付模块模拟失败
**Then** 系统展示支付失败提示，不扣减用户资产

#### Scenario: 支付接口可替换

**Given** 系统支付模块使用抽象接口（IPaymentProvider）
**When** 用户后续替换为真实 Apple/Google/Stripe 凭证
**Then** 仅需修改配置和实现类，不改架构和调用方代码

### Requirement: 购买历史查看

用户可以查看自己的内购交易历史。

#### Scenario: 用户查看购买记录

**Given** 用户已登录且有购买记录
**When** 用户进入购买记录页面
**Then** 系统按时间倒序展示所有交易（含商品名称/价格/时间/mock 标记）
