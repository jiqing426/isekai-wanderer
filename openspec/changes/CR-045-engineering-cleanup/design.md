# CR-045 Design

## Overview

- CR-045 是纯工程清理变更，不涉及新架构、新技术选型或不可逆设计决策
- 5 个 DEV 任务全部是删除废弃代码、替换调试语句、修复已知 bug
- 所有改动通过 git revert 回滚

## Technical Approach

### DEV-001: Git 仓库清理
- `git rm -r admin.bak` + `rm -rf admin.bak`
- `.gitignore` 添加 `admin/node_modules/`、`admin/node-jiti/`、`admin/.npm/`
- `git rm -r --cached admin/node-jiti`（已跟踪的需移除）
- `docker builder prune -f`
- 回滚：`git checkout admin.bak`

### DEV-002: 废弃 API 端点清理
- 删除 `subscription.py` 的 `create_order` 函数和 `CreateOrderRequest` schema
- 删除 `user_subscription.py` 的 `create_order` 函数和 `CreateOrderRequest` schema
- 删除 `cr016_subscription.py` 的 `fragment_purchase_dialogue` 函数、`FragmentPurchaseRequest`、`FragmentPurchaseResponse`、`FRAGMENT_COST_PER_DIALOGUE`
- 保留 `/cr016/subscription/create`（统一入口）
- 回滚：`git revert`

### DEV-003: 废弃前端组件清理
- 删除 `QuotaExhaustedModal.vue`
- 从 `PaywallManager.vue` 移除 import、模板、相关 state
- 从 `QuotaDisplay.vue` 移除购买额外额度 UI
- 回滚：`git revert`

### DEV-004: 代码质量
- 后端：每文件加 `import logging` + `logger = logging.getLogger(__name__)`，`print()` → `logger.info/warning`
- 前端：删除 `console.log`，保留 `console.error/warn`
- 回滚：`git revert`

### DEV-005: Bug 修复
- toast 重复：SubscriptionPlans.vue 中 `handleSubscribe` 加 guard
- 语言下拉：AppHeader.vue NDropdown 修复条件渲染
- /profile 重定向：router/index.ts 加 `{ path: '/profile', redirect: '/settings' }`
- 回滚：`git revert`

## Technology Decisions

| 选型项 | 选择 | 状态 | 确认依据 |
|--------|------|------|----------|
| 新技术选型 | Not Required | Accepted | 用户确认 CR-045 方案，纯工程清理无新选型 |

## Document Sync

| 目标文档 | 状态 | 同步说明 |
|----------|------|----------|
| docs/architecture/architecture.md | Not Required | 无架构变更 |
| docs/security/security.md | Not Required | 无安全变更 |
| docs/decisions/decisions.md | Not Required | 无技术决策 |
| docs/runtime/runtime-contract.md | Not Required | 无运行时契约变更 |
| docs/api/api.md | Not Required | 删除的是废弃端点，不影响 API 文档 |
| docs/database/database.md | Not Required | 无 DB 变更 |
