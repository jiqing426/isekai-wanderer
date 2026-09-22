# CR-045 System Spec

### Requirement: Git 仓库清理

#### Scenario: admin.bak 已删除
- WHEN 开发者 clone 仓库
- THEN admin.bak 目录不存在

#### Scenario: node_modules 不在 git 跟踪中
- WHEN 运行 git check-ignore admin/node_modules
- THEN 返回 admin/node_modules
- AND .gitignore 包含 admin/node_modules

### Requirement: 废弃 API 端点已清理

#### Scenario: subscription/order/create 返回 404
- WHEN 调用 POST /api/v1/subscription/order/create
- THEN 返回 404（端点已删除）

#### Scenario: order/create 返回 404
- WHEN 调用 POST /api/v1/order/create
- THEN 返回 404（端点已删除）

#### Scenario: fragment-purchase 返回 404
- WHEN 调用 POST /api/v1/cr016/subscription/fragment-purchase
- THEN 返回 404（端点已删除）

#### Scenario: CR-016 create 保留
- WHEN 调用 POST /api/v1/cr016/subscription/create
- THEN 正常返回（CR-016 统一入口保留）

### Requirement: 废弃前端组件已清理

#### Scenario: QuotaExhaustedModal 无引用
- WHEN 搜索 frontend/src 中的 QuotaExhaustedModal
- THEN 无任何引用

### Requirement: 代码质量

#### Scenario: 后端无 print()
- WHEN 搜索后端代码中的 print()
- THEN 返回 0 个结果

#### Scenario: 前端 console.log 减少
- WHEN 搜索前端代码中的 console.log
- THEN 返回 < 5 个结果

### Requirement: Bug 修复

#### Scenario: 订阅成功 toast 不重复
- WHEN 用户订阅成功
- THEN 只显示 1 条 toast 消息

#### Scenario: 语言切换下拉正常
- WHEN 点击导航栏语言切换按钮
- THEN 出现下拉选项（中文/English）

#### Scenario: /profile 重定向
- WHEN 直接访问 /profile
- THEN 重定向到 /settings
