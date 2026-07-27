# P0 页面移动端适配规格

> 变更：CR-004 mobile-responsive
> 优先级：P0（核心页面，用户高频使用）
> 断点：`@media (max-width: 767px)`

---

### Requirement: REQ-MOB-P0-001 LandingView 移动端适配

#### Scenario: S1 移动端用户访问落地页

- **Given** 用户以 ≤767px 视口访问落地页
- **When** 页面加载完成
- **Then** 页面呈单列布局，无横向滚动
- **And** 所有 CTA 按钮触摸目标 ≥ 44px
- **And** 图片/视频自适应宽度（max-width: 100%）
- **And** 文字可读，字号 ≥ 14px

#### Scenario: S2 PC 端落地页不受影响

- **Given** 用户以 ≥1024px 视口访问落地页
- **When** 页面加载完成
- **Then** 页面视觉与适配前完全一致

---

### Requirement: REQ-MOB-P0-002 HomeView 移动端适配

#### Scenario: S1 移动端用户访问主页

- **Given** 已登录用户以 ≤767px 视口访问主页
- **When** 页面加载完成
- **Then** 多卡片布局转为单列全宽
- **And** 卡片间距 12-16px
- **And** 底部 TabBar 可见且「首页」高亮

#### Scenario: S2 主页内容无溢出

- **Given** 移动端视口下主页已加载
- **When** 用户上下滚动浏览
- **Then** 无横向滚动条
- **And** 无内容溢出/错位/重叠

---

### Requirement: REQ-MOB-P0-003 GameView 移动端适配

#### Scenario: S1 移动端用户进入游戏

- **Given** 用户以 ≤767px 视口进入游戏界面
- **When** 游戏场景加载完成
- **Then** 对话区域全宽显示，字号 ≥ 14px
- **And** 选择面板按钮触摸目标 ≥ 44px
- **And** 场景图片自适应宽度
- **And** 底部 TabBar 隐藏（游戏内沉浸模式）

#### Scenario: S2 GameView 对话与选择交互

- **Given** 移动端游戏进行中
- **When** 出现选择分支
- **Then** 选项按钮全宽单列排列
- **And** 每个按钮高度 ≥ 44px
- **And** 点击后正常触发剧情推进

---

### Requirement: REQ-MOB-P0-004 DiscoverView 移动端适配

#### Scenario: S1 移动端发现页浏览

- **Given** 用户以 ≤767px 视口访问发现页
- **When** 页面加载完成
- **Then** 内容列表单列全宽
- **And** 底部 TabBar 可见且「发现」高亮
- **And** 卡片/列表项触摸区域 ≥ 44px

---

### Requirement: REQ-MOB-P0-005 CharacterListView 移动端适配

#### Scenario: S1 移动端角色列表浏览

- **Given** 用户以 ≤767px 视口访问角色列表
- **When** 页面加载完成
- **Then** 多列网格转为单列全宽
- **And** 每个角色卡片高度 ≥ 44px，可点击
- **And** 无横向滚动

---

### Requirement: REQ-MOB-P0-006 CharacterDetailView 移动端适配

#### Scenario: S1 移动端角色详情查看

- **Given** 用户以 ≤767px 视口访问角色详情
- **When** 页面加载完成
- **Then** 图文混排呈单列布局
- **And** 图片自适应宽度
- **And** 文字内容全宽可读
- **And** 交互按钮（送礼、对话等）触摸目标 ≥ 44px

---

### Requirement: REQ-MOB-P0-007 CommunityView 移动端适配

#### Scenario: S1 移动端社区浏览

- **Given** 用户以 ≤767px 视口访问社区
- **When** 页面加载完成
- **Then** 帖子列表单列全宽
- **And** 底部 TabBar 可见且「社区」高亮
- **And** 列表项触摸区域 ≥ 44px
- **And** 评论/点赞交互正常

---

## 通用约束

- 所有 P0 页面移动端样式写在 `mobile.css` 的 `@media (max-width: 767px)` 内
- 不修改 `global.css`
- 不改业务逻辑
- iOS 安全区域：底部内容使用 `padding-bottom: env(safe-area-inset-bottom)` 兜底
- 全局 `overflow-x: hidden` 防止横向滚动
