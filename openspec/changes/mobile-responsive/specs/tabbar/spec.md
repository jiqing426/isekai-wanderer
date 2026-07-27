# 底部 TabBar 规格

> 变更：CR-004 mobile-responsive
> 优先级：P0（移动端核心导航）
> 断点：`@media (max-width: 767px)`

---

### Requirement: REQ-MOB-TAB-001 TabBar 显示条件

#### Scenario: S1 移动端显示 TabBar

- **Given** 用户以 ≤767px 视口访问应用
- **When** 用户处于主要页面（首页/发现/游戏/社区/我的）
- **Then** 底部 TabBar 固定显示
- **And** 当前页面对应的 Tab 高亮

#### Scenario: S2 PC 端不显示 TabBar

- **Given** 用户以 ≥1024px 视口访问应用
- **When** 页面加载完成
- **Then** 底部 TabBar 不显示
- **And** 保持原顶部水平导航

#### Scenario: S3 游戏沉浸模式隐藏 TabBar

- **Given** 移动端用户进入游戏界面（GameView）
- **When** 游戏场景加载中或进行中
- **Then** TabBar 隐藏，提供沉浸式体验
- **And** 退出游戏后 TabBar 恢复显示

---

### Requirement: REQ-MOB-TAB-002 TabBar 入口定义

#### Scenario: S1 5 个核心入口

- **Given** 移动端 TabBar 显示
- **When** 用户查看 TabBar
- **Then** 包含以下 5 个入口（从左到右）：
  1. 🏠 首页 → HomeView
  2. 🔍 发现 → DiscoverView
  3. 🎮 游戏 → GameView
  4. 👥 社区 → CommunityView
  5. 👤 我的 → ProfileView
- **And** 每个 Tab 包含图标和文字标签

---

### Requirement: REQ-MOB-TAB-003 TabBar 交互

#### Scenario: S1 Tab 点击导航

- **Given** 移动端 TabBar 显示
- **When** 用户点击某个 Tab
- **Then** 导航到对应页面
- **And** 被点击的 Tab 高亮
- **And** 之前的 Tab 取消高亮

#### Scenario: S2 当前页 Tab 高亮

- **Given** 用户通过 TabBar 导航到某页面
- **When** 页面加载完成
- **Then** 对应 Tab 呈激活状态（颜色/样式区分）

---

### Requirement: REQ-MOB-TAB-004 TabBar 视觉规格

#### Scenario: S1 TabBar 尺寸

- **Given** 移动端 TabBar 渲染
- **When** 测量 TabBar 尺寸
- **Then** 高度 ≥ 48px（含触摸区域）
- **And** 每个 Tab 触摸区域 ≥ 44×44px
- **And** TabBar 固定在视口底部

#### Scenario: S2 iOS 安全区域

- **Given** iOS 设备访问应用
- **When** TabBar 渲染
- **Then** TabBar 底部使用 `padding-bottom: env(safe-area-inset-bottom)`
- **And** 内容不被 Home Indicator 遮挡

#### Scenario: S3 TabBar 背景

- **Given** 移动端 TabBar 渲染
- **When** 页面滚动
- **Then** TabBar 背景不透明，不随页面滚动
- **And** TabBar 始终在内容之上（z-index 合适）

---

### Requirement: REQ-MOB-TAB-005 TabBar 实现约束

#### Scenario: S1 纯 CSS + Vue 组件

- **Given** TabBar 组件实现
- **When** 代码审查
- **Then** TabBar 为独立 Vue 组件
- **And** 仅在 `@media (max-width: 767px)` 下 display
- **And** 不引入新依赖
- **And** 不改路由逻辑
