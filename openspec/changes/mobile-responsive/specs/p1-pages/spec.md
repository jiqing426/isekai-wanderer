# P1 页面移动端适配规格

> 变更：CR-004 mobile-responsive
> 优先级：P1（功能页面，重要但使用频率稍低）
> 断点：`@media (max-width: 767px)`

---

### Requirement: REQ-MOB-P1-001 LoginView 移动端适配

#### Scenario: S1 移动端登录表单

- **Given** 用户以 ≤767px 视口访问登录页
- **When** 页面加载完成
- **Then** 登录表单全宽显示，padding 16px
- **And** 输入框高度 ≥ 44px
- **And** 登录按钮高度 ≥ 44px，全宽
- **And** 无横向滚动

---

### Requirement: REQ-MOB-P1-002 RegisterView 移动端适配

#### Scenario: S1 移动端注册表单

- **Given** 用户以 ≤767px 视口访问注册页
- **When** 页面加载完成
- **Then** 注册表单全宽显示，padding 16px
- **And** 所有输入框和按钮高度 ≥ 44px

---

### Requirement: REQ-MOB-P1-003 OnboardingView 移动端适配

#### Scenario: S1 移动端新手引导

- **Given** 用户以 ≤767px 视口进入新手引导
- **When** 引导步骤展示
- **Then** 步骤内容单列全宽
- **And** 下一步/跳过按钮触摸目标 ≥ 44px

---

### Requirement: REQ-MOB-P1-004 ProfileView 移动端适配

#### Scenario: S1 移动端个人中心

- **Given** 用户以 ≤767px 视口访问个人中心
- **When** 页面加载完成
- **Then** 用户信息单列显示
- **And** 底部 TabBar「我的」入口可达
- **And** 菜单项触摸区域 ≥ 44px

---

### Requirement: REQ-MOB-P1-005 SettingsView 移动端适配

#### Scenario: S1 移动端设置页

- **Given** 用户以 ≤767px 视口访问设置页
- **When** 页面加载完成
- **Then** 设置项列表全宽单列
- **And** 每个设置项触摸区域 ≥ 44px
- **And** 开关/选择器可正常操作

---

### Requirement: REQ-MOB-P1-006 SaveManagerView 移动端适配

#### Scenario: S1 移动端存档管理

- **Given** 用户以 ≤767px 视口访问存档管理
- **When** 页面加载完成
- **Then** 存档列表单列全宽
- **And** 操作按钮（加载/删除）触摸目标 ≥ 44px

---

### Requirement: REQ-MOB-P1-007 ShardCenterView 移动端适配

#### Scenario: S1 移动端碎片中心

- **Given** 用户以 ≤767px 视口访问碎片中心
- **When** 页面加载完成
- **Then** 余额/商城内容单列全宽
- **And** 购买按钮触摸目标 ≥ 44px

---

### Requirement: REQ-MOB-P1-008 AchievementView 移动端适配

#### Scenario: S1 移动端成就墙

- **Given** 用户以 ≤767px 视口访问成就墙
- **When** 页面加载完成
- **Then** 成就网格转为单列或双列
- **And** 每个成就卡片可点击（≥ 44px）

---

### Requirement: REQ-MOB-P1-009 SubscriptionView 移动端适配

#### Scenario: S1 移动端订阅页

- **Given** 用户以 ≤767px 视口访问订阅页
- **When** 页面加载完成
- **Then** 套餐卡片单列全宽
- **And** 订阅按钮高度 ≥ 44px

---

### Requirement: REQ-MOB-P1-010 GalleryView 移动端适配

#### Scenario: S1 移动端画廊

- **Given** 用户以 ≤767px 视口访问画廊
- **When** 页面加载完成
- **Then** 图片网格转为单列或双列
- **And** 图片自适应宽度
- **And** 点击图片可正常预览

---

### Requirement: REQ-MOB-P1-011 GiftView 移动端适配

#### Scenario: S1 移动端送礼页

- **Given** 用户以 ≤767px 视口访问送礼页
- **When** 页面加载完成
- **Then** 礼物列表单列全宽
- **And** 送礼按钮触摸目标 ≥ 44px

---

### Requirement: REQ-MOB-P1-012 ScriptDetailView 移动端适配

#### Scenario: S1 移动端剧本详情

- **Given** 用户以 ≤767px 视口访问剧本详情
- **When** 页面加载完成
- **Then** 已有部分媒体查询基础上完善适配
- **And** 剧本内容全宽可读
- **And** 开始游戏按钮 ≥ 44px

---

### Requirement: REQ-MOB-P1-013 EndingView 移动端适配

#### Scenario: S1 移动端结局页

- **Given** 用户以 ≤767px 视口查看结局
- **When** 页面加载完成
- **Then** 结局内容单列全宽显示
- **And** 操作按钮（回顾/分享/重新开始）≥ 44px

---

### Requirement: REQ-MOB-P1-014 RecapView 移动端适配

#### Scenario: S1 移动端回顾页

- **Given** 用户以 ≤767px 视口访问回顾页
- **When** 页面加载完成
- **Then** 剧情回顾内容单列全宽
- **And** 文字可读，图片自适应

---

### Requirement: REQ-MOB-P1-015 RouteMap 移动端适配

#### Scenario: S1 移动端路线图

- **Given** 用户以 ≤767px 视口访问路线图
- **When** 页面加载完成
- **Then** 节点图自适应宽度，无横向滚动
- **And** 节点可点击（≥ 44px）

---

### Requirement: REQ-MOB-P1-016 FreeChatView 移动端适配

#### Scenario: S1 移动端自由聊天

- **Given** 用户以 ≤767px 视口进入自由聊天
- **When** 页面加载完成
- **Then** 聊天消息全宽显示
- **And** 输入框固定底部，高度 ≥ 44px
- **And** 发送按钮 ≥ 44px

---

### Requirement: REQ-MOB-P1-017 ForgotPasswordView 移动端适配

#### Scenario: S1 移动端忘记密码

- **Given** 用户以 ≤767px 视口访问忘记密码页
- **When** 页面加载完成
- **Then** 表单全宽，padding 16px
- **And** 输入框和提交按钮 ≥ 44px

---

### Requirement: REQ-MOB-P1-018 ResetPasswordView 移动端适配

#### Scenario: S1 移动端重置密码

- **Given** 用户以 ≤767px 视口访问重置密码页
- **When** 页面加载完成
- **Then** 表单全宽，padding 16px
- **And** 输入框和提交按钮 ≥ 44px

---

## 通用约束

- 所有 P1 页面移动端样式写在 `mobile.css` 的 `@media (max-width: 767px)` 内
- 不修改 `global.css`
- 不改业务逻辑
- 表单类页面统一：全宽、padding 16px、输入框/按钮 ≥ 44px
- iOS 安全区域：底部内容使用 `padding-bottom: env(safe-area-inset-bottom)` 兜底
