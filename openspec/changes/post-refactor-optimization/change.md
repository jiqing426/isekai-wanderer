# OpenSpec Change — CR-008 重构后页面优化

> 模式：CEO 直连模式（ceo-directive）
> 说明：本次变更跳过完整 OpenSpec 流程，由 CEO 直接确认任务清单

---

## 背景

用户要求对重构后的页面进行优化，包括：
- 修复后端接口问题（500 错误、404 路由、认证问题、ImportError）
- 新增用户中心 API（18 个接口）
- 前端页面优化（个人中心、设置页面、Header 调整）
- 设置页面优化 PRD（8 个接口）
- 碎片中心 PRD（3 个接口）

## 变更范围

### 后端（29 个接口）
- 第一批 18 个接口：用户中心 + 个人中心
- 第二批 8 个接口：设置页面优化
- 第三批 3 个接口：碎片中心

### 前端
- 个人中心页面（9 个模块卡片）
- 设置页面优化（左右分栏、5 个模块）
- 登录/注册密码框小眼睛
- DiscoverView 优化
- Header 结构调整
- 引导页面优化

### 数据库
- 新增表：posts、collections、login_devices、shop_goods、user_goods
- 扩展表：users（signature）、user_settings（播放偏好、通知设置）

## 任务分解

详见：
- `workflow/changes/CR-008-post-refactor-optimization/be-tasks.md`
- `workflow/changes/CR-008-post-refactor-optimization/fe-tasks.md`

## 验收标准

详见：
- `workflow/changes/CR-008-post-refactor-optimization/acceptance.md`
- `workflow/changes/CR-008-post-refactor-optimization/test-report.md`

## 安全审查

详见：
- `workflow/changes/CR-008-post-refactor-optimization/security-review.md`

## 豁免说明

本次变更采用 CEO 直连模式，跳过以下 OpenSpec 标准流程：
- DESIGN 阶段（无 design.md）
- 完整需求分析（无 proposal.md、specs/）

替代方案：
- 由 CEO 直接确认任务清单
- 由 PL 编写 API Contract 替代设计文档
- 由 QA 测试报告 + 用户确认替代验收文档
