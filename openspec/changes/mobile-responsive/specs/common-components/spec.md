# 公共组件移动端适配规格

> 变更：CR-004 mobile-responsive
> 优先级：P0/P1（公共组件影响所有页面）
> 断点：`@media (max-width: 767px)`

---

### Requirement: REQ-MOB-COM-001 AppHeader 移动端适配

#### Scenario: S1 移动端顶部导航改造

- **Given** 用户以 ≤767px 视口访问任意页面
- **When** 页面加载完成
- **Then** 顶部水平导航栏隐藏或简化
- **And** 导航功能由底部 TabBar 承接（见 tabbar/spec.md）
- **And** AppHeader 仅保留 Logo 和必要操作（如返回）

---

### Requirement: REQ-MOB-COM-002 DialogueBox 移动端适配

#### Scenario: S1 移动端对话框显示

- **Given** 移动端游戏中触发对话
- **When** DialogueBox 显示
- **Then** 对话框全宽显示
- **And** 字号 ≥ 14px
- **And** 边距 12-16px
- **And** 不遮挡关键游戏元素

---

### Requirement: REQ-MOB-COM-003 ChoicePanel 移动端适配

#### Scenario: S1 移动端选择面板

- **Given** 移动端游戏中出现选择分支
- **When** ChoicePanel 显示
- **Then** 选项按钮全宽单列排列
- **And** 每个按钮高度 ≥ 44px
- **And** 按钮间距 ≥ 8px

---

### Requirement: REQ-MOB-COM-004 AudioPlayer 移动端适配

#### Scenario: S1 移动端音频播放器

- **Given** 移动端使用音频播放功能
- **When** AudioPlayer 显示
- **Then** 播放控件触摸目标 ≥ 44px
- **And** 进度条可触摸拖动

---

### Requirement: REQ-MOB-COM-005 PaymentModal 移动端适配

#### Scenario: S1 移动端支付弹窗

- **Given** 移动端触发支付弹窗
- **When** PaymentModal 显示
- **Then** 弹窗转为底部抽屉或全屏
- **And** 支付按钮 ≥ 44px
- **And** 可正常关闭

---

### Requirement: REQ-MOB-COM-006 BalanceDisplay 移动端适配

#### Scenario: S1 移动端余额显示

- **Given** 移动端显示余额信息
- **When** BalanceDisplay 渲染
- **Then** 余额文字可读，不被截断
- **And** 布局不错位

---

### Requirement: REQ-MOB-COM-007 AffectionMeter/AffectionBar 移动端适配

#### Scenario: S1 移动端好感度显示

- **Given** 移动端显示好感度
- **When** 好感度组件渲染
- **Then** 进度条自适应宽度
- **And** 数值可读

---

### Requirement: REQ-MOB-COM-008 MemoryCard 移动端适配

#### Scenario: S1 移动端记忆卡片

- **Given** 移动端显示记忆卡片
- **When** MemoryCard 渲染
- **Then** 卡片全宽单列
- **And** 文字可读，图片自适应

---

### Requirement: REQ-MOB-COM-009 TaskPanel 移动端适配

#### Scenario: S1 移动端任务面板

- **Given** 移动端显示任务面板
- **When** TaskPanel 渲染
- **Then** 任务列表单列全宽
- **And** 任务项触摸区域 ≥ 44px

---

### Requirement: REQ-MOB-COM-010 ScriptCard 移动端适配

#### Scenario: S1 移动端剧本卡片

- **Given** 移动端显示剧本卡片
- **When** ScriptCard 渲染
- **Then** 卡片全宽单列
- **And** 封面图自适应宽度
- **And** 整个卡片可点击（≥ 44px）

---

### Requirement: REQ-MOB-COM-011 EndingCard 移动端适配

#### Scenario: S1 移动端结局卡片

- **Given** 移动端显示结局卡片
- **When** EndingCard 渲染
- **Then** 卡片全宽单列
- **And** 可点击查看详情（≥ 44px）

---

## 通用约束

- 所有公共组件移动端样式写在 `mobile.css` 的 `@media (max-width: 767px)` 内
- 不修改 `global.css`
- 不改业务逻辑
- Naive UI 组件需要 `:deep()` 覆盖时使用，逐个验证
- 弹窗类组件统一转为底部抽屉或全屏模式
