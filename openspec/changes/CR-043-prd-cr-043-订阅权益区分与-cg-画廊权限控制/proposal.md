# Proposal — CR-043: 订阅权益区分与 CG 画廊权限控制

## Why

- 当前系统 `TIER_PERMISSIONS` 已完整定义 free/basic/standard/premium 四档订阅权益（含 `ugc_access`、`script_access` 等权限字段），`SubscriptionService.check_permission()` 已实现，前端 `useSubscriptionStore` 已有状态管理。但实际执行层存在权益绕过：
- CG 画廊：`gallery.py` 中 CG 解锁只检查 `UnlockedCG` 表，不检查订阅等级。free/basic 用户可看到全部 CG，standard+ 的权益未体现。
- 剧本访问：`script_access` 权限已定义三档（trial_only / all_normal / all_including_exclusive），但 `game.py` 中选角和开始游戏时不检查 `script_access`，只检查 `character.playable`。free 用户可玩所有剧本。
- 前端入口：需要订阅才能访问的功能入口无锁/升级提示，用户无法感知权益差异。
- 订阅流程状态同步：用户点击订阅成功后，前端只调用 `loadPlans()` 刷新套餐列表，不调用 `subscriptionStore.fetchSubscriptionStatus()` 刷新订阅状态，也不刷新 `authStore.user.subscription_tier`；Settings 会员页面 `member-info` 从 `User.trial_started_at`/`User.trial_ends_at` 读取状态但 `on_subscription_created()` 不写这俩字段；三套订阅 API 数据源不统一。
- 这是权益保护类变更，直接影响免费用户→付费转化漏斗的完整性。

## What Changes

- REQ-001：CG 画廊按订阅等级限制访问/显示。standard 及以上用户可访问完整 CG 画廊，free/basic 用户只能看到已解锁的 CG，未解锁 CG 显示锁图标和"升级订阅解锁"提示。后端 gallery API 返回 `is_accessible` 字段。
- REQ-002：剧本和角色选择强制检查 script_access。`game.py` 中开始游戏、选角时检查用户 tier 对应的 `script_access`（trial_only / all_normal / all_including_exclusive）。
- REQ-003：前端订阅权益展示。需要订阅才能访问的功能入口显示锁/升级提示。复用 `useSubscriptionStore` 和 `SubscriptionService.check_permission()`。
- REQ-004：订阅流程状态同步修复。订阅成功后立即刷新订阅状态和用户信息；修复 Settings 会员页面 member-info 数据源不一致问题；登录成功后自动加载订阅状态；补齐 `UserProfile.subscription_tier` 类型包含 `'basic'`。

## Non-Goals

- 不修改 `TIER_PERMISSIONS` 定义（已定义且不变）
- 不修改数据库结构（不新增表、不修改字段）
- 不修改 `unlock_type` 角色解锁机制（free/paid/subscription 不变）
- 不做真实支付/订阅流程
- 不新增订阅等级或权益项
- 不修改 `SubscriptionService` 核心逻辑（只调用现有方法）

## Success Criteria

- free 用户访问 CG 画廊时，未解锁 CG 显示锁图标和升级提示，无法查看完整图
- standard 用户访问 CG 画廊时，可查看全部 CG（含未通过剧情解锁的）
- free 用户开始游戏时，只能选择试用剧本，非试用剧本显示锁定
- premium 用户可玩所有剧本含独家内容
- 前端功能入口需要订阅的显示锁/升级提示
- API 层面不可通过伪造请求绕过订阅等级限制（Security 阶段审查，CEO 附条件 C3）
- 用户点击订阅成功后，前端订阅状态、用户信息、会员页面立即正确更新，无需手动刷新页面

## Impact

- 后端 API：`gallery.py`（CG 列表/API 返回 `is_accessible`）、`game.py`（开始游戏时检查 `script_access`）、`scripts.py`（剧本列表返回访问状态）、`settings.py`（`get_member_info()` 数据源修复）
- 前端：`GalleryView.vue`（锁/升级提示）、角色选择组件（升级提示）、`useSubscriptionStore`（复用）、`SubscriptionPlans.vue`（订阅成功后状态同步）、`auth.ts`（登录后加载订阅状态）、`types/user.ts`（补齐 `'basic'`）
- 数据库：不修改结构（不变项）
- 订阅服务：复用现有 `SubscriptionService.check_permission()` 和 `get_tier_permissions()`，不修改
- 安全：权限边界变更，需 Security 审查（附条件 C3）
- 部署：无新增服务或基础设施变更

## Open Questions

| 编号 | 问题 | 阻塞 MVP | 用户回答 | 处理结论 | 展示状态 |
| --- | --- | --- | --- | --- | --- |
| Q-001 | `is_accessible` 字段的 API 契约设计（字段名、返回位置、类型） | 否 | 暂缓到 DESIGN 阶段由 Architect 确认（CEO 附条件 C1） | 暂缓到 DESIGN | PRD 自动入口已记录，暂缓到 DESIGN 阶段 |
| Q-002 | `script_access` 三档如何映射到剧本表结构 | 否 | 暂缓到 DESIGN 阶段由 Architect 确认（CEO 附条件 C2） | 暂缓到 DESIGN | PRD 自动入口已记录，暂缓到 DESIGN 阶段 |
| Q-003 | "试用剧本"的具体范围是什么 | 否 | 建议默认值：trial = 所有 engine_type=legacy 且 genre=romance 的剧本中 hot_value 最高的 1 个 | 暂缓到 DESIGN | PRD 自动入口已记录，暂缓到 DESIGN 阶段 |
| Q-004 | standard+ 用户查看"未通过剧情解锁"的 CG 时，是否显示完整大图还是缩略图+提示 | 否 | 建议默认值：显示完整大图，因为 standard+ 权益就是"可访问完整画廊" | 暂缓到 DESIGN | PRD 自动入口已记录，暂缓到 DESIGN 阶段 |
| Q-005 | 权限检查应放在 API 层还是中间件层 | 否 | 暂缓到 DESIGN 阶段由 Architect 确认 | 暂缓到 DESIGN | PRD 自动入口已记录，暂缓到 DESIGN 阶段 |
