# CR-045: 工程清理 + 技术债务偿还

## Why

- CR-001~CR-044 累积了大量技术债务：废弃 API 端点、旧组件残留、print() 调试语句、243MB 旧备份目录、重复代码等
- 需要一次集中清理，提升代码质量和生产就绪度

## What Changes

1. **Git 仓库清理** — 删除 admin.bak（243MB），admin/node_modules 加入 .gitignore，清理 Docker build cache
2. **废弃 API 端点清理** — 删除 subscription.py 和 user_subscription.py 的 create_order（已委托 CR-016），删除 fragment-purchase 端点（碎片直接扣费替代）
3. **废弃前端组件清理** — 删除 QuotaExhaustedModal.vue，从 PaywallManager 移除引用，清理 QuotaDisplay 购买额外额度 UI
4. **代码质量提升** — 后端 18 处 print() → logging，前端 23 处 console.log 清理
5. **已知 Bug 修复** — 订阅成功 toast 重复、语言切换器下拉 UI 异常、/profile 404 重定向

### REQ-001: Git 仓库清理
- 删除 admin.bak 目录（243MB 旧备份）
- 将 admin/node_modules 加入 .gitignore
- 清理 Docker build cache

### REQ-002: 废弃 API 端点清理
- 删除 subscription.py 中的 create_order 端点（已委托 CR-016）
- 删除 user_subscription.py 中的 create_order 端点（已委托 CR-016）
- 删除 cr016_subscription.py 中的 fragment-purchase 端点（碎片直接扣费替代）
- 保留 user_subscription.py 的 GET /user/subscription（向后兼容）

### REQ-003: 废弃前端组件清理
- 从 PaywallManager 中移除 QuotaExhaustedModal 引用
- 删除 QuotaExhaustedModal.vue 文件
- 清理 QuotaDisplay 中"购买额外额度"相关 UI

### REQ-004: 代码质量提升
- 后端 18 处 print() 替换为 logging
- 前端 23 处 console.log 清理或改为条件日志
- 清理 mock_middleware 相关代码（生产已禁用）

### REQ-005: 已知 Bug 修复
- 修复订阅成功后 toast 重复显示（4-5 条）
- 修复语言切换器 NDropdown 下拉 UI 渲染异常
- 添加 /profile → /settings 重定向

## Non-Goals

- OAuth 第三方登录接入（后续 CR）
- 真实支付网关（后续 CR）
- CI/CD 搭建（后续 CR）
- Push 通知（后续 CR）
- 更多剧本内容（内容创作，非工程任务）
- 新增功能

## Success Criteria

- admin.bak 不存在，admin/node_modules 在 .gitignore 中
- 3 个废弃 API 端点返回 404
- QuotaExhaustedModal 无任何引用
- 后端 0 个 print()，前端 < 5 个 console.log
- 订阅成功只显示 1 条 toast
- 语言切换下拉正常显示选项
- /profile 重定向到 /settings
- QA E2E 回归测试无回归

## Impact

- 无新功能，不影响现有用户行为
- 删除的 API 端点前端已不再调用（已切换到 CR-016 统一入口）
- 所有改动有 git revert 回滚计划

## 约束

- 不改变现有功能行为
- 不新增功能
- 所有改动有回滚计划
- QA E2E 回归测试确认无回归
