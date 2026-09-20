# Change

## 变更单

| 项 | 内容 |
| --- | --- |
| CR 编号 | CR-043 |
| 来源 | 用户 PRD |
| 类型 | feature |
| 优先级 | P1 |
| 当前状态 | intake-ready |
| 负责人 | pl |
| 关联 PRD | `docs/prd/prd.md` |
| 关联 OpenSpec Change | `../../../openspec/changes/CR-043-prd-cr-043-订阅权益区分与-cg-画廊权限控制/` |

## 问题和目标

- 现状：来自用户 PRD，待 PM 在 REQUIREMENT 阶段结构化。
- 目标：PRD: CR-043 — 订阅权益区分与 CG 画廊权限控制
- 成功标准：PRD 中 P0/P1 验收项被拆成可测试 acceptance，并通过后续设计、开发、QA 与发布关口。
- 本次不做：PRD 未明确授权的生产部署、真实支付、真实 AI/付费资源调用、不可逆数据操作。

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

## OpenSpec Change 生成

- PM 根据本文件创建或更新对应 OpenSpec change：`proposal.md`、`specs/**/spec.md`；同时维护 `docs/prd/prd.md` 摘要和 `acceptance.md`。
- 未确认内容必须以 Q 编号登记；非阻塞问题可以记录为暂缓，不得伪装为已确认事实。
- OpenSpec change 或 workflow 追踪文件不完整时，不能直接让关口 `passed`。

## 影响范围

| 领域 | 是否影响 | 说明 |
| --- | --- | --- |
| PROJECT / 项目事实 | 待确认，见 Q-001 | PM/PL 从 PRD 识别 |
| PRD / 需求输入 | 是 | 本 CR 来自用户 PRD |
| 架构 / 模块边界 | 待确认，见 Q-002、Q-005 | Architect 在 DESIGN 阶段判断 |
| API / 契约 | 待确认，见 Q-001 | Architect/BE 在 DESIGN 阶段判断 |
| 数据库 / 迁移 | 否 | 不修改数据库结构（不变项） |
| 权限 / 安全 / 隐私 | 是 | 需安全评审（CEO 附条件 C3），Security 在后续阶段审查 |
| 前端 / 管理端体验 | 是 | FE/Admin 按任务单执行 |
| 测试 / 验收 | 是 | QA/PM 生成 acceptance 和 test-plan |
| 部署 / 生产 / 回滚 | 否 | 无新增服务或基础设施变更 |

## 人工确认

以下任一项为 `是` 时，不能由 LLM 自动通过，只能由人工确认后继续。

| 项 | 是 / 否 | 说明 |
| --- | --- | --- |
| 生产环境变更 | 否 | PRD 自动入口默认不授权；本 CR 不涉及生产部署 |
| 数据删除或不可逆迁移 | 否 | 不修改数据库结构（不变项） |
| 认证、授权或权限边界变更 | 是 | 需安全评审（CEO 附条件 C3），Security 阶段必审 |
| 支付、账务或合规承诺 | 否 | 不做真实支付/订阅（不变项） |
| 公共 API 破坏性变更 | 待确认，见 Q-001 | 需人工确认兼容策略；is_accessible 为新增字段，不破坏现有 |
| 大范围跨模块重构 | 否 | 仅在 gallery.py + game.py + scripts.py 和前端组件追加权限检查逻辑 |

## 自动入口记录

- 创建时间：2026-09-16T08:16:13Z
- 执行方式：`tools/bootstrap-openclaw-prd.py`
- 初始授权：仅授权创建 CR、记录 PRD、生成初始 workflow / OpenSpec 骨架；不授权自动通过阶段、关口或部署。
- 放行要求：每个推进型流转仍必须由 PL 展示交付物清单、关键结论、缺口和风险，并取得用户明确同意后，才能运行 readiness 并推进。
