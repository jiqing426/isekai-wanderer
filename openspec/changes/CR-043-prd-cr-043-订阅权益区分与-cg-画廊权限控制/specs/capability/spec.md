# Capability Spec — CR-043: 订阅权益区分与 CG 画廊权限控制

## REQ-001：CG 画廊按订阅等级限制访问/显示

### Requirement: CG 画廊按订阅等级限制访问/显示

系统必须在 CG 画廊 API 和前端页面中按用户订阅等级区分 CG 访问权限。

**权益映射**（来自 `TIER_PERMISSIONS`，不变项）：

| 订阅等级 | ugc_access | CG 画廊权益 |
| --- | --- | --- |
| free | False | 仅查看已通过剧情解锁的 CG；未解锁 CG 显示锁图标和升级提示 |
| basic | False | 同 free（仅查看已解锁 CG） |
| standard | False | 可访问完整 CG 画廊（含未通过剧情解锁的 CG）* |
| premium | True | 可访问完整 CG 画廊（含 UGC 内容） |

> *注：standard 的 `ugc_access=False` 但 PRD 明确要求 standard+ 可访问完整 CG 画廊。CEO 附条件 C1 指出 `is_accessible` 字段设计由 Architect 确认。此处描述的是产品需求语义，不替代 API 契约设计。

#### Scenario: free 用户浏览 CG 画廊

- **Given** 用户订阅等级为 free
- **When** 用户访问 `GET /api/v1/gallery/collections` 和 `GET /api/v1/gallery/collections/{script_id}`
- **Then** API 返回 CG 列表，每个 CG 项包含 `is_accessible` 字段
- **And** 已通过剧情解锁的 CG `is_accessible=true`
- **And** 未通过剧情解锁的 CG `is_accessible=false`
- **And** 前端对 `is_accessible=false` 的 CG 显示锁图标和"升级订阅解锁"提示
- **And** 用户点击锁定的 CG 时不展开完整图片

#### Scenario: standard 用户浏览 CG 画廊

- **Given** 用户订阅等级为 standard
- **When** 用户访问 `GET /api/v1/gallery/collections` 和 `GET /api/v1/gallery/collections/{script_id}`
- **Then** API 返回 CG 列表，所有 CG 项 `is_accessible=true`
- **And** 前端显示全部 CG 可查看（无锁图标）
- **And** 用户点击任意 CG 可预览完整图片

#### Scenario: basic 用户浏览 CG 画廊

- **Given** 用户订阅等级为 basic
- **When** 用户访问 CG 画廊
- **Then** 行为与 free 用户一致（仅查看已解锁 CG，未解锁显示锁和升级提示）
- **And** API 返回的 `is_accessible` 字段对 basic 用户和 free 用户逻辑一致

#### Scenario: 后端 gallery API 返回 is_accessible 字段

- **Given** 任意已认证用户访问 CG 画廊 API
- **When** API 构建响应
- **Then** 每个 CG 项包含 `is_accessible` 布尔字段
- **And** `is_accessible` 值基于用户订阅等级和 CG 解锁状态计算
- **And** 计算逻辑复用 `SubscriptionService.get_tier_permissions()` 和 `get_user_tier()`
- **Note** `is_accessible` 字段的具体设计（字段名、返回位置、类型）待 Architect 在 DESIGN 阶段确认，见 Q-001（附条件 C1）

## REQ-002：剧本和角色选择强制检查 script_access

### Requirement: 剧本和角色选择强制检查 script_access

系统必须在剧本和角色选择时强制检查用户 tier 对应的 `script_access` 权限，不允许绕过。

**script_access 三档语义**（来自 `TIER_PERMISSIONS`，不变项）：

| 订阅等级 | script_access | 可玩剧本范围 |
| --- | --- | --- |
| free | trial_only | 只能玩试用剧本 |
| basic | all_normal | 可玩所有普通剧本 |
| standard | all_normal | 同 basic |
| premium | all_including_exclusive | 可玩所有剧本含独家内容 |

#### Scenario: free 用户尝试开始非试用剧本

- **Given** 用户订阅等级为 free（script_access = trial_only）
- **When** 用户调用 `POST /api/v1/game/start` 传入非试用剧本的 `script_id`
- **Then** API 返回 403 权限拒绝
- **And** 错误信息提示"当前订阅等级无法游玩此剧本，请升级订阅"
- **And** 前端剧本列表中非试用剧本显示锁定状态和升级提示

#### Scenario: basic 用户开始普通剧本

- **Given** 用户订阅等级为 basic（script_access = all_normal）
- **When** 用户调用 `POST /api/v1/game/start` 传入普通剧本的 `script_id`
- **Then** API 允许开始游戏，正常创建 GameSession
- **And** 前端剧本列表中普通剧本显示为可游玩

#### Scenario: basic 用户尝试开始独家剧本

- **Given** 用户订阅等级为 basic（script_access = all_normal）
- **When** 用户调用 `POST /api/v1/game/start` 传入独家剧本的 `script_id`
- **Then** API 返回 403 权限拒绝
- **And** 前端剧本列表中独家剧本显示锁定和升级提示

#### Scenario: premium 用户开始任意剧本

- **Given** 用户订阅等级为 premium（script_access = all_including_exclusive）
- **When** 用户调用 `POST /api/v1/game/start` 传入任意剧本的 `script_id`
- **Then** API 允许开始游戏，正常创建 GameSession

#### Scenario: 剧本列表 API 返回 script_access 状态

- **Given** 任意已认证用户访问剧本列表 `GET /api/v1/scripts`
- **When** API 构建响应
- **Then** 每个剧本项包含 `is_accessible` 字段标识当前用户是否有权游玩
- **And** `is_accessible` 值基于用户 tier 对应的 script_access 和剧本分类计算
- **Note** script_access 三档如何映射到剧本表结构待 Architect 在 DESIGN 阶段确认，见 Q-002（附条件 C2）

#### Scenario: 角色选择时检查 script_access

- **Given** 用户通过 `GET /api/v1/scripts/{script_id}` 获取剧本详情和可扮演角色列表
- **When** 剧本对当前用户的 script_access 不可用
- **Then** 该剧本的可扮演角色列表为空或标记为锁定
- **And** 前端角色选择组件显示"升级订阅解锁"提示

## REQ-003：前端订阅权益展示

### Requirement: 前端订阅权益展示

系统前端必须在需要订阅才能访问的功能入口显示锁/升级提示，使用户可感知权益差异。

#### Scenario: CG 画廊锁定 CG 显示升级提示

- **Given** free/basic 用户浏览 CG 画廊
- **When** 遇到未解锁且需要订阅的 CG
- **Then** CG 缩略图上显示锁图标
- **And** 显示"升级订阅解锁"按钮或文字提示
- **And** 点击锁定 CG 不展开完整图片，而是展示升级提示

#### Scenario: 剧本列表锁定剧本显示升级提示

- **Given** free 用户浏览剧本列表
- **When** 遇到非试用剧本
- **Then** 剧本卡片显示锁定状态（如锁图标或遮罩）
- **And** 显示"升级订阅解锁"按钮或文字提示
- **And** 点击锁定剧本不进入游戏，而是展示升级提示

#### Scenario: 角色列表锁定角色显示升级提示

- **Given** 用户浏览角色列表
- **When** 遇到需要更高订阅等级的角色
- **Then** 角色卡片显示锁定状态
- **And** 显示"升级订阅"按钮
- **And** 点击锁定角色不进入选择，而是展示升级提示

#### Scenario: 前端复用 useSubscriptionStore

- **Given** 前端需要判断用户权益
- **When** 渲染 CG 画廊、剧本列表、角色列表等组件
- **Then** 组件通过 `useSubscriptionStore` 获取当前用户 tier 和 permissions
- **And** 不在前端本地硬编码 tier 对应的权限映射
- **And** 权限判断以后端 API 返回的 `is_accessible` 等字段为权威值，前端状态仅用于 UI 展示

## REQ-004：订阅流程状态同步修复

### Requirement: 订阅流程状态同步修复

系统必须在订阅成功后立即同步前端订阅状态和用户信息，修复 Settings 会员页面数据源不一致问题，并在登录后自动加载订阅状态。

**问题根因**：
1. 订阅成功后 `SubscriptionPlans.vue` 只调用 `loadPlans()` 刷新套餐列表，不调用 `subscriptionStore.fetchSubscriptionStatus()`
2. 不刷新 `authStore.user.subscription_tier`
3. Settings 会员页面 `member-info` 从 `User.trial_started_at`/`User.trial_ends_at` 读取状态，但 `on_subscription_created()` 不写这俩字段
4. 三套订阅 API 数据源不统一（`/cr016/subscription/status`、`/users/me/member-info`、`/users/me` 返回的 tier 不一致）

#### Scenario: 订阅成功后前端订阅状态立即更新

- **Given** 用户在 `SubscriptionPlans.vue` 点击订阅并支付成功
- **When** 订阅 API 返回成功响应
- **Then** 前端调用 `subscriptionStore.fetchSubscriptionStatus()` 刷新订阅状态
- **And** `subscriptionStore.subscriptionStatus` 中的 tier 更新为用户新订阅的等级

#### Scenario: 订阅成功后用户信息刷新

- **Given** 用户订阅成功
- **When** 订阅状态刷新完成
- **Then** 前端调用 `authApi.getProfile()` 获取最新用户信息
- **And** `authStore.user.subscription_tier` 更新为订阅 tier
- **And** 前端 UI 中显示的用户等级立即更新，无需手动刷新页面

#### Scenario: Settings 会员页面显示正确的 tier/status/expires_at

- **Given** 用户访问 Settings 会员页面，调用 `GET /api/v1/users/me/member-info`
- **When** 后端 `get_member_info()` 构建响应
- **Then** `tier` 从 `SubscriptionService.get_user_tier()` 获取（而非 `User.subscription_tier` 字段直接读取）
- **And** `status` 和 `expires_at` 从 `SubscriptionService.get_user_subscription()` 读取 Subscription 表数据
- **And** 不再依赖 `User.trial_started_at`/`User.trial_ends_at` 字段

#### Scenario: member-info 的 tier 与 subscription/status 返回的 tier 一致

- **Given** 用户同时调用 `GET /api/v1/users/me/member-info` 和 `GET /api/v1/cr016/subscription/status`
- **When** 两个 API 返回响应
- **Then** 两个 API 返回的 `tier` 值一致
- **And** 两者都基于 `SubscriptionService.get_user_tier()` 获取 tier

#### Scenario: 登录成功后自动加载订阅状态

- **Given** 用户登录成功
- **When** 登录 API 返回 token
- **Then** 前端自动调用 `subscriptionStore.fetchSubscriptionStatus()`
- **And** 订阅状态在登录后立即可用，无需用户手动触发或页面刷新

#### Scenario: UserProfile.subscription_tier 类型包含 basic

- **Given** 前端 TypeScript 类型定义 `UserProfile.subscription_tier`
- **When** 后端返回 `subscription_tier: 'basic'`
- **Then** 前端类型定义包含 `'basic'` 选项
- **And** TypeScript 编译不报类型错误
- **And** `MemberInfo.tier` 和 `SubscriptionStatus.tier` 类型也包含 `'basic'`
