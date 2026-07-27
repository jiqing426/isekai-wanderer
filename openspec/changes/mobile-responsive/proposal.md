# OpenSpec Change Proposal — CR-004 移动端适配

| 项 | 内容 |
| --- | --- |
| 变更 ID | CR-004 |
| 变更名称 | mobile-responsive |
| 提出人 | CEO（通过 main session 转达） |
| 负责人 | pm（需求）→ sa（设计）→ fe（实现） |
| 创建时间 | 2026-07-19 |
| 状态 | REQUIREMENT in-progress |

## Why

- 「异世界漫游」当前前端仅支持 PC 端（≥1024px），完全没有移动端适配
- 目标用户（乙女玩家 ~30% + 冒险者 ~25%）大量使用手机浏览和游玩
- 缺乏移动端支持将直接影响 D1 留存和用户体验
- CEO 决策同意立项，全部范围纳入，P0 优先，Demo 先行

## What Changes

- 为 28 个前端页面 + 22 个公共组件增加移动端（≤767px）适配
- P0（7 页面）：LandingView、HomeView、GameView、DiscoverView、CharacterListView、CharacterDetailView、CommunityView
- P1（18 页面）：Login、Register、Onboarding、Profile、Settings、SaveManager、ShardCenter、Achievement、Subscription、Gallery、Gift、ScriptDetail、Ending、Recap、RouteMap、FreeChat、ForgotPassword、ResetPassword
- P2（3 页面）：Share、OAuthCallback、404
- 新增底部 TabBar（5 入口：首页/发现/游戏/社区/我的），仅移动端显示
- 新增 `src/styles/mobile.css`，所有移动端样式集中管理
- 核心原则：零改动 PC 端、纯 CSS 层改动、触摸友好 ≥44px、单列布局无横向滚动

## Non-Goals

- 不改 PC 端（≥1024px）任何样式
- 不改 `global.css`
- 不改任何业务逻辑、API 调用、数据层、路由
- 不做平板端（768px–1023px）适配
- 不做原生 App 或 PWA
- 不做移动端性能优化（图片压缩、懒加载等）

## Success Criteria

- P0 页面在 ≤767px 可正常使用，无横向滚动（Browser Interaction E2E 验证）
- PC 端 ≥1024px 完全不受影响（回归测试验证）
- 所有交互元素触摸友好 ≥44px（样式审查 + E2E 测量）
- 底部 TabBar 5 入口导航正常（Browser Interaction E2E 验证）
- 无 UI 溢出/错位/重叠（视觉回归 + E2E 截图对比）

## Impact

- 前端页面：28 个页面新增移动端样式
- 公共组件：22 个组件新增移动端样式
- 新增文件：`src/styles/mobile.css`、TabBar 组件
- 不改：`global.css`、业务逻辑、API、数据层、路由
- 后端：无影响
- 数据库：无影响

## 执行策略

**Demo 先行，分阶段推进**：

| 阶段 | 内容 | 预估 | 前置条件 |
|------|------|------|----------|
| Demo | LandingView + HomeView + 基础设施（mobile.css + TabBar） | 1 天 | REQ_GATE passed |
| P0 全面 | 7 个核心页面 | 2-3 天 | Demo 用户确认 |
| P1 | 18 个功能页面 | 3-4 天 | P0 完成 |
| P2 | 3 个辅助页面 + 公共组件 + 回归 | 1-2 天 | P1 完成 |
| **合计** | | **7-10 天** | |

## 风险

| # | 风险 | 影响 | 缓解 |
|---|------|------|------|
| R1 | Naive UI 组件自带响应式逻辑可能冲突 | 样式覆盖不生效 | 使用 `:deep()` 覆盖，逐个组件验证 |
| R2 | GameView 复杂度高（691 行） | 适配难度大 | 单独分配，充分测试 |
| R3 | iOS 安全区域适配 | 底部内容被遮挡 | `env(safe-area-inset-bottom)` |
| R4 | 移动端触摸事件与 PC 端鼠标事件差异 | 交互异常 | 仅改 CSS，不改 JS 逻辑 |

## 待澄清问题

无。用户已确认 5 项（页面清单、优先级、TabBar 入口、工作量、Demo 先行策略），CEO 已 INIT 通过。

## 依赖

- 前期分析文档：`/root/.openclaw/workspace/main/mobile-adaptation-plan.md`
- CR-002 已关闭，无冲突
