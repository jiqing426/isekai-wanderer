# CR-045: 工程清理 + 技术债务偿还

## 变更入口

- 提出者: 用户
- 提出时间: 2026-09-22
- 项目: isekai-wanderer
- 优先级: P0
- 目标: 清理技术债务、移除废弃代码、修复已知 bug、提升代码质量和生产就绪度
- 成功标准: admin.bak 删除、3个废弃API端点删除、QuotaExhaustedModal 移除、后端0个print()、前端<5个console.log、订阅toast不重复、语言下拉正常、/profile重定向

## 来源

用户要求对整个项目进行全面分析后的优化建议，按优先级分批处理。

## 变更目标

清理技术债务、移除废弃代码、修复已知 bug、提升代码质量和生产就绪度。

## 范围

### P0 — 立即处理（工程维护）

1. **清理 admin.bak + admin/node_modules** — 243MB 旧备份 + 1.1GB node_modules 不应提交到 git
2. **删除重复的订阅 API 端点** — subscription.py 和 user_subscription.py 的 create_order 统一委托 CR-016
3. **移除废弃的 fragment-purchase 端点** — CR-044 已改为碎片直接扣费，不再需要购买额外对话
4. **移除 QuotaExhaustedModal** — PaywallManager 中不再引用
5. **print() → logger** — 18 处 print 替换为 logging
6. **修复订阅成功 toast 重复** — 点击后出现 4-5 条重复消息
7. **修复语言切换器下拉 UI** — NDropdown 渲染异常
8. **添加 /profile 重定向到 /settings**

### P1 — 短期（代码质量）

9. **清理 mock 代码** — 132 处 mock 引用，MockMiddleware 已在生产禁用
10. **清理 console.log** — 前端 23 处调试日志
11. **Docker build cache 清理** — 962MB 可回收
12. **清理 deprecated 端点** — user_subscription.py 标记为 deprecated 的端点

### P2 — 已知 bug 修复

13. **语言切换器下拉 UI 修复** — AppHeader.vue NDropdown 条件渲染问题
14. **Vben Admin 8082 防火墙** — 需用户在阿里云安全组放行（非代码问题）

## 不包含

- OAuth 第三方登录接入（后续 CR）
- 真实支付网关（后续 CR）
- CI/CD 搭建（后续 CR）
- Push 通知（后续 CR）
- 更多剧本内容（内容创作，非工程任务）

## 验收标准

见 acceptance.md
