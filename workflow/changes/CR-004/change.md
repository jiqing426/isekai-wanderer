# CR-004 移动端适配（Mobile Responsive）

- **变更ID**: CR-004
- **变更名称**: mobile-responsive
- **创建时间**: 2026-07-19T08:30:00Z
- **发起人**: CEO（通过 main session 转达）
- **负责人**: pl
- **当前阶段**: INTAKE

- 目标：为「异世界漫游」前端项目进行移动端适配，使所有页面在移动设备（≤767px）上可用且体验良好
- 成功标准：P0页面移动端可用、PC端零改动、触摸友好≥44px、底部TabBar正常、无UI溢出

## 变更目标

为「异世界漫游」前端项目进行移动端适配，使所有页面在移动设备（≤767px）上可用且体验良好。

## 核心原则

1. **零改动PC端**：所有修改仅针对移动端（≤767px），严禁影响PC端（≥1024px）
2. **逻辑复用**：共用数据和业务逻辑，只改呈现层
3. **媒体查询**：所有移动端样式写在 `@media screen and (max-width: 767px)` 内
4. **严禁修改公共样式**：不动 `global.css`
5. **触摸友好**：交互元素 ≥ 44px
6. **单列布局**：无横向滚动条

## 影响范围

### 前端页面（28个）

| 优先级 | 页面数 | 页面列表 |
|--------|--------|----------|
| P0 | 7 | LandingView、HomeView、GameView、DiscoverView、CharacterListView、CharacterDetailView、CommunityView |
| P1 | 18 | Login、Register、Onboarding、Profile、Settings、SaveManager、ShardCenter、Achievement、Subscription、Gallery、Gift、ScriptDetail、Ending、Recap、RouteMap、FreeChat、ForgotPassword、ResetPassword |
| P2 | 3 | Share、OAuthCallback、404 |

### 公共组件（22个）

AppHeader、DialogueBox、ChoicePanel、AudioPlayer、PaymentModal、BalanceDisplay、AffectionMeter/Bar、MemoryCard、TaskPanel、ScriptCard、EndingCard 等

### 新增文件

- `src/styles/mobile.css` — 所有移动端样式集中管理

### 不改动

- `src/styles/global.css` — 严禁修改
- 所有业务逻辑、API 调用、数据层

## 技术方案

1. **新建 mobile.css**：所有 `@media (max-width: 767px)` 规则集中管理
2. **底部 TabBar**：移动端替代顶部导航（5个核心入口：首页/发现/游戏/社区/我的）
3. **布局转换**：多列网格→单列全宽
4. **弹窗改造**：居中弹窗→底部抽屉
5. **表单适配**：居中卡片→全宽，padding 16px
6. **触摸目标**：所有按钮/链接/输入框 ≥ 44px
7. **iOS 安全区域**：`env(safe-area-inset-bottom)`

## 成功标准

1. P0 页面在移动端（≤767px）可正常使用，无横向滚动
2. PC端（≥1024px）完全不受影响
3. 所有交互元素触摸友好（≥44px）
4. 底部 TabBar 导航正常工作
5. 无 UI 溢出/错位/重叠

## 执行策略

**分阶段推进，Demo 先行：**

1. **Demo 阶段**：先做 LandingView + HomeView，老大确认效果
2. **P0 全面**：Demo 通过后，完成全部 P0 页面
3. **P1 推进**：P0 完成后推进 P1
4. **P2 收尾**：P1 完成后推进 P2 + 公共组件 + 回归测试

## 范围追加记录

### 2026-07-19 范围追加：移动端子模块轮播图

**追加原因**：老大在验收 Demo 时发现，移动端有很多子模块（如"热门剧本"等）需要做成轮播图形式展示，以节省垂直空间，提升浏览体验。

**追加内容**：
1. HomeView 羁绊概览（affection-grid）改为轮播图
2. HomeView 剧本列表（script-grid）改为轮播图
3. DiscoverView 热门剧本（trending-scroll）优化为轮播图
4. DiscoverView 推荐剧本（recommendations）改为轮播图
5. CharacterListView 角色网格（character-grid）改为轮播图

**技术要求**：
- 仅移动端（≤767px）生效
- PC 端保持原有网格布局
- 轮播图支持触摸滑动
- 轮播图自动播放，鼠标移入时暂停
- 轮播图指示器显示当前位置

**新增任务**：TASK-MOB-031~035

---

## 风险

| # | 风险 | 影响 | 缓解措施 |
|---|------|------|----------|
| 1 | Naive UI 组件自带响应式逻辑可能冲突 | 样式覆盖不生效 | 使用 `:deep()` 覆盖，逐个组件验证 |
| 2 | GameView 复杂度高（691行） | 适配难度大，可能引入 bug | 单独分配，充分测试 |
| 3 | 移动端触摸事件与 PC 端鼠标事件差异 | 交互异常 | 仅改 CSS，不改 JS 逻辑 |
| 4 | iOS 安全区域适配 | 底部内容被遮挡 | 使用 `env(safe-area-inset-bottom)` |

## 前期分析文档

- `/root/.openclaw/workspace/main/mobile-adaptation-plan.md`

## 工作量预估

| 阶段 | 内容 | 预估 |
|------|------|------|
| Demo | LandingView + HomeView + 基础设施 | 1天 |
| P0 | 7个核心页面 | 2-3天 |
| P1 | 18个功能页面 | 3-4天 |
| P2 | 3个辅助页面 + 公共组件 + 回归 | 1-2天 |
| **合计** | | **7-10天** |
