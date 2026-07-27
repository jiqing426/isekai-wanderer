# P2 页面移动端适配规格

> 变更：CR-004 mobile-responsive
> 优先级：P2（辅助页面，低频/简单）
> 断点：`@media (max-width: 767px)`

---

### Requirement: REQ-MOB-P2-001 ShareView 移动端适配

#### Scenario: S1 移动端分享页

- **Given** 用户以 ≤767px 视口访问外部分享链接
- **When** 页面加载完成
- **Then** 分享内容单列全宽显示
- **And** 文字可读，图片自适应
- **And** CTA 按钮 ≥ 44px

---

### Requirement: REQ-MOB-P2-002 OAuthCallbackView 移动端适配

#### Scenario: S1 移动端 OAuth 回调

- **Given** 用户以 ≤767px 视口到达 OAuth 回调页
- **When** 页面加载完成
- **Then** 加载中状态居中显示
- **And** 无横向滚动
- **And** 文字可读

---

### Requirement: REQ-MOB-P2-003 NotFoundView 移动端适配

#### Scenario: S1 移动端 404 页

- **Given** 用户以 ≤767px 视口到达 404 页
- **When** 页面加载完成
- **Then** 提示信息单列居中
- **And** 返回首页按钮 ≥ 44px

---

## 通用约束

- 所有 P2 页面移动端样式写在 `mobile.css` 的 `@media (max-width: 767px)` 内
- 不修改 `global.css`
- 不改业务逻辑
