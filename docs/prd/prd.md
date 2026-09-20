# PRD

## 当前输入

| 项 | 内容 |
| --- | --- |
| 来源 | 用户 PRD |
| 关联 CR | CR-043 |
| 标题 | PRD: CR-043 — 订阅权益区分与 CG 画廊权限控制 |
| 记录时间 | 2026-09-16T08:16:13Z |

## 原始 PRD

```markdown
# PRD: CR-043 — 订阅权益区分与 CG 画廊权限控制

## 背景

当前系统中订阅权益的定义已在 `TIER_PERMISSIONS` 中完整定义（free/basic/standard/premium），包括 CG 画廊访问权限（`ugc_access`）、角色解锁权限（`script_access`）、存档数量、对话次数等。

但实际执行层面存在以下问题：

1. **CG 画廊未按订阅权益区分**：`gallery.py` 中 CG 解锁只检查 `UnlockedCG` 表（用户是否通过剧情解锁），不检查订阅等级。`canAccessCGGallery` 权限在后端 API 返回但前端 Gallery 页面不检查。
2. **剧本访问未强制检查**：`script_access` 权限已定义（trial_only / all_normal / all_including_exclusive），但 `game.py` 中选角和开始游戏时不检查 `script_access`，只检查 `character.playable`。
3. **订阅页面点击订阅报错**：已修复（dateutil 模块问题 + payment URL 问题）。

## 变更目标

1. CG 画廊页面和 API 按订阅等级限制访问/显示
2. 剧本和角色选择时强制检查 `script_access` 权限
3. 前端在需要订阅的功能入口处显示锁/升级提示

## 功能需求

### REQ-001：CG 画廊订阅权益区分
- standard 及以上用户可访问完整 CG 画廊
- free/basic 用户只能看到已解锁的 CG，未解锁 CG 显示锁图标和"升级订阅解锁"提示
- 后端 gallery API 返回 `is_accessible` 字段标识当前用户是否有权访问

### REQ-002：剧本访问权限强制检查
- `script_access = trial_only`（free）：只能玩试用剧本
- `script_access = all_normal`（basic/standard）：可玩所有普通剧本
- `script_access = all_including_exclusive`（premium）：可玩所有剧本含独家内容
- game.py 中开始游戏、选角时检查用户 tier 对应的 script_access

### REQ-003：前端订阅权益展示
- 需要订阅才能访问的功能入口显示锁/升级提示
- CG 画廊中未解锁且需要订阅的 CG 显示"升级订阅"按钮
- 角色列表中需要更高订阅等级的角色显示"升级订阅"按钮

### REQ-004：订阅流程状态同步修复
- 订阅成功后立即刷新订阅状态（`subscriptionStore.fetchSubscriptionStatus()`），不只是刷新套餐列表
- 订阅成功后刷新用户信息（`getUserProfile()` → `authStore.setUser()`），更新 `user.subscription_tier`
- 修复 Settings 会员页面 `member-info` 状态判断逻辑：从 `SubscriptionService.get_user_subscription()` 读取 status/expires_at/member_since，不再依赖 `User.trial_started_at`/`User.trial_ends_at`
- `member-info` 的 tier 通过 `SubscriptionService.get_user_tier()` 获取，和 `/cr016/subscription/status` 保持一致
- 登录成功后自动加载订阅状态（`fetchSubscriptionStatus()`）
- `UserProfile.subscription_tier` 类型补齐 `'basic'`

## 不变项
- 已有的 `TIER_PERMISSIONS` 定义不变
- 已有的 `unlock_type` 角色解锁机制不变
- 已有的订阅状态管理不变

## 技术约束
- 复用 `SubscriptionService.check_permission()` 和 `get_tier_permissions()`
- 前端复用 `useSubscriptionStore`
- 不修改数据库结构
```

## 结构化摘要

| 项 | 内容 |
| --- | --- |
| 目标 | 让订阅权益在执行层面真正落地——TIER_PERMISSIONS 已定义但未被后端代码强制执行，CG 画廊和剧本访问存在权益绕过 |
| 目标用户 | 乙女玩家（核心）、冒险者（核心）；free/basic/standard/premium 四档订阅用户 |
| 范围（做） | REQ-001 CG 画廊按订阅等级限制访问/显示、REQ-002 剧本和角色选择强制检查 script_access、REQ-003 前端订阅权益展示（锁/升级提示）、REQ-004 订阅流程状态同步修复（订阅成功后状态刷新、member-info 数据源修复、登录后自动加载、类型补齐） |
| 非目标（不做） | 不修改 TIER_PERMISSIONS 定义、不修改数据库结构、不修改 unlock_type 机制、不做真实支付/订阅、不新增订阅等级 |
| MVP 验收 | 21 条 AC（AC-001~AC-021），P0：AC-001/002/005/006/009/011/012/015/016/017/018/019，P1：AC-003/004/007/008/010/013/014/020/021 |
| 待澄清问题 | Q-001 is_accessible 字段 API 契约（暂缓 DESIGN）、Q-002 script_access 映射规则（暂缓 DESIGN）、Q-003 试用剧本范围（暂缓 DESIGN）、Q-004 standard+ 查看 CG 显示方式（暂缓 DESIGN）、Q-005 权限检查层级（暂缓 DESIGN） |
| CEO 附条件 | C1 is_accessible 字段设计 Architect 确认、C2 script_access 三档映射规则 Architect 确认、C3 权限边界变更 Security 审查 |
| OpenSpec Change | `openspec/changes/CR-043-prd-cr-043-订阅权益区分与-cg-画廊权限控制/` |
| 需求关口 | `python tools/check-gate-readiness.py --gate requirement --change CR-043-prd-cr-043-订阅权益区分与-cg-画廊权限控制 --change-id CR-043` |
