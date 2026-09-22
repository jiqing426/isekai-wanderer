| 验收编号 | 需求编号 | 来源规格 | 验收标准 | 优先级 | 覆盖状态 | 设计落点 | OpenSpec Task | 测试用例 / 验证命令 | 未覆盖原因 | PL 处理 | 状态 |
|----------|----------|----------|----------|--------|----------|----------|---------------|---------------------|------------|---------|------|
| AC-001 | REQ-001 | openspec/changes/CR-045-engineering-cleanup/specs/system/spec.md | admin.bak 目录已删除 | P0 | covered | git rm -r admin.bak | DEV-001 | du -sh admin.bak 返回不存在 | 无 | 无 | Verified |
| AC-002 | REQ-001 | openspec/changes/CR-045-engineering-cleanup/specs/system/spec.md | admin/node_modules 在 .gitignore 中 | P0 | covered | .gitignore 更新 | DEV-001 | git check-ignore admin/node_modules | 无 | 无 | Verified |
| AC-003 | REQ-001 | openspec/changes/CR-045-engineering-cleanup/specs/system/spec.md | Docker build cache 已清理 | P1 | covered | docker builder prune | DEV-001 | docker system df 回收量减少 | 无 | 无 | Verified |
| AC-004 | REQ-002 | openspec/changes/CR-045-engineering-cleanup/specs/system/spec.md | subscription.py 无 create_order 端点 | P0 | covered | 删除 create_order | DEV-002 | grep create_order subscription.py 返回空 | 无 | 无 | Verified |
| AC-005 | REQ-002 | openspec/changes/CR-045-engineering-cleanup/specs/system/spec.md | user_subscription.py 无 create_order 端点 | P0 | covered | 删除 create_order | DEV-002 | grep create_order user_subscription.py 返回空 | 无 | 无 | Verified |
| AC-006 | REQ-002 | openspec/changes/CR-045-engineering-cleanup/specs/system/spec.md | fragment-purchase 端点已删除 | P0 | covered | 删除 fragment_purchase_dialogue | DEV-002 | grep fragment-purchase 返回空 | 无 | 无 | Verified |
| AC-007 | REQ-003 | openspec/changes/CR-045-engineering-cleanup/specs/system/spec.md | PaywallManager 无 QuotaExhaustedModal 引用 | P0 | covered | 移除 import 和模板引用 | DEV-003 | grep QuotaExhaustedModal 返回空 | 无 | 无 | Verified |
| AC-008 | REQ-003 | openspec/changes/CR-045-engineering-cleanup/specs/system/spec.md | QuotaExhaustedModal.vue 已删除 | P0 | covered | rm QuotaExhaustedModal.vue | DEV-003 | 文件不存在 | 无 | 无 | Verified |
| AC-009 | REQ-004 | openspec/changes/CR-045-engineering-cleanup/specs/system/spec.md | 后端无 print() 语句 | P0 | covered | print → logger | DEV-004 | grep "^\s*print(" 返回 0 | 无 | 无 | Verified |
| AC-010 | REQ-004 | openspec/changes/CR-045-engineering-cleanup/specs/system/spec.md | 前端 console.log 清理 | P1 | covered | 删除或改为条件日志 | DEV-004 | console.log 数量 < 5 | 无 | 无 | Verified |
| AC-011 | REQ-005 | openspec/changes/CR-045-engineering-cleanup/specs/system/spec.md | 订阅成功 toast 不重复 | P0 | covered | 事件去重 | DEV-005 | 订阅后只显示 1 条 toast | 无 | 无 | Verified |
| AC-012 | REQ-005 | openspec/changes/CR-045-engineering-cleanup/specs/system/spec.md | 语言切换器下拉 UI 正常 | P0 | covered | 修复 NDropdown 渲染 | DEV-005 | 点击语言按钮出现下拉选项 | 无 | 无 | Verified |
| AC-013 | REQ-005 | openspec/changes/CR-045-engineering-cleanup/specs/system/spec.md | /profile 重定向到 /settings | P2 | covered | 路由 redirect | DEV-005 | 访问 /profile 跳转到 /settings | 无 | 无 | Verified |

## 验收追踪说明

- 覆盖状态 covered 表示已完成开发并通过 QA E2E 验证
- 状态 Verified 表示 QA Agent 已独立验证通过
- QA E2E 测试日期: 2026-09-22
