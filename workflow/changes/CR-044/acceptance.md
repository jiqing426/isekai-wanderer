| 验收编号 | 需求编号 | 来源规格 | 验收标准 | 优先级 | 覆盖状态 | 设计落点 | OpenSpec Task | 测试用例 / 验证命令 | 未覆盖原因 | PL 处理 | 状态 |
|----------|----------|----------|----------|--------|----------|----------|---------------|---------------------|------------|---------|------|
| AC-001 | REQ-001 | openspec/changes/CR-044-db-cleanup-vben-admin-refactor/specs/system/spec.md | email_verifications 表已删除 | P0 | not_covered | cr044_db_cleanup.py DROP TABLE | DEV-001 | backend/tests/unit/test_cr044_migration.py | 待开发 | 无 | Designed |
| AC-002 | REQ-001 | openspec/changes/CR-044-db-cleanup-vben-admin-refactor/specs/system/spec.md | user_preferences 表已删除 | P0 | not_covered | cr044_db_cleanup.py DROP TABLE | DEV-001 | backend/tests/unit/test_cr044_migration.py | 待开发 | 无 | Designed |
| AC-003 | REQ-001 | openspec/changes/CR-044-db-cleanup-vben-admin-refactor/specs/system/spec.md | subscription_plans 表已删除 | P0 | not_covered | cr044_db_cleanup.py DROP + 迁移 | DEV-001 | backend/tests/unit/test_cr044_migration.py | 待开发 | 无 | Designed |
| AC-004 | REQ-001 | openspec/changes/CR-044-db-cleanup-vben-admin-refactor/specs/system/spec.md | post_likes 有唯一约束 | P1 | not_covered | cr044_db_cleanup.py ADD CONSTRAINT | DEV-001 | backend/tests/unit/test_cr044_migration.py | 待开发 | 无 | Designed |
| AC-005 | REQ-001 | openspec/changes/CR-044-db-cleanup-vben-admin-refactor/specs/system/spec.md | affection 外键 CASCADE | P1 | not_covered | cr044_db_cleanup.py 重建 FK | DEV-001 | backend/tests/unit/test_cr044_migration.py | 待开发 | 无 | Designed |
| AC-006 | REQ-002 | openspec/changes/CR-044-db-cleanup-vben-admin-refactor/specs/system/spec.md | GET /api/v1/admin/system-config | P0 | not_covered | admin_system.py GET endpoint | DEV-002 | backend/tests/unit/test_system_config.py | 待开发 | 无 | Designed |
| AC-007 | REQ-002 | openspec/changes/CR-044-db-cleanup-vben-admin-refactor/specs/system/spec.md | PUT 修改配置后热生效 | P0 | not_covered | config.py reload + email.py rebuild | DEV-003 | backend/tests/unit/test_config_dynamic.py | 待开发 | 无 | Designed |
| AC-008 | REQ-002 | openspec/changes/CR-044-db-cleanup-vben-admin-refactor/specs/system/spec.md | 敏感字段返回 *** | P0 | not_covered | admin_system.py is_secret 逻辑 | DEV-002 | backend/tests/unit/test_system_config.py | 待开发 | 无 | Designed |
| AC-009 | REQ-003 | openspec/changes/CR-044-db-cleanup-vben-admin-refactor/specs/system/spec.md | Vben 8082 运行 | P0 | not_covered | admin/ Vben 替换 + port 8082 | DEV-004 | admin/e2e/smoke.spec.ts | 待开发 | 无 | Designed |
| AC-010 | REQ-003 | openspec/changes/CR-044-db-cleanup-vben-admin-refactor/specs/system/spec.md | 7 个页面已迁移 | P0 | not_covered | admin/src/views/ 迁移 | DEV-005 | admin/e2e/page-migration.spec.ts | 待开发 | 无 | Designed |
| AC-011 | REQ-003 | openspec/changes/CR-044-db-cleanup-vben-admin-refactor/specs/system/spec.md | 系统配置页面可访问 | P1 | not_covered | admin/src/views/system-config/ | DEV-006 | admin/e2e/admin-pages.spec.ts | 待开发 | 无 | Designed |
| AC-012 | REQ-003 | openspec/changes/CR-044-db-cleanup-vben-admin-refactor/specs/system/spec.md | 用户管理页面可访问 | P1 | not_covered | admin/src/views/user-management/ | DEV-006 | admin/e2e/admin-pages.spec.ts | 待开发 | 无 | Designed |
| AC-013 | REQ-004 | openspec/changes/CR-044-db-cleanup-vben-admin-refactor/specs/system/spec.md | 头像下拉有设置/退出 | P0 | not_covered | PersonalCenterView.vue 头像下拉 | DEV-007 | frontend/tests/unit/PersonalCenterView.spec.ts | 待开发 | 无 | Designed |
| AC-014 | REQ-004 | openspec/changes/CR-044-db-cleanup-vben-admin-refactor/specs/system/spec.md | 会员卡内联展示 | P0 | not_covered | PersonalCenterView.vue 内联会员卡 | DEV-007 | frontend/tests/unit/PersonalCenterView.spec.ts | 待开发 | 无 | Designed |
| AC-015 | REQ-005 | openspec/changes/CR-044-db-cleanup-vben-admin-refactor/specs/system/spec.md | 设置页 4 tab 无 member | P0 | not_covered | SettingsView.vue 删 member tab | DEV-008 | frontend/tests/unit/SettingsView.spec.ts | 待开发 | 无 | Designed |
| AC-016 | REQ-006 | openspec/changes/CR-044-db-cleanup-vben-admin-refactor/specs/system/spec.md | 14 页面移动端单列布局 | P0 | not_covered | views @media 适配 | DEV-009 | frontend/tests/unit/mobile-adapter.spec.ts | 待开发 | 无 | Designed |
| AC-017 | REQ-006 | openspec/changes/CR-044-db-cleanup-vben-admin-refactor/specs/system/spec.md | 桌面端布局不受影响 | P1 | not_covered | 桌面端零影响设计 | DEV-009 | frontend/tests/unit/mobile-adapter.spec.ts | 待开发 | 无 | Designed |
| AC-018 | REQ-007 | openspec/changes/CR-044-db-cleanup-vben-admin-refactor/specs/system/spec.md | 前端无硬编码中文 | P0 | not_covered | i18n 全覆盖 | DEV-013 | frontend/tests/unit/i18n-coverage.spec.ts | 待开发 | 无 | Designed |
| AC-019 | REQ-007 | openspec/changes/CR-044-db-cleanup-vben-admin-refactor/specs/system/spec.md | 语言切换 zh-CN/en-US | P0 | not_covered | i18n key 补全 | DEV-013 | frontend/tests/unit/i18n-coverage.spec.ts | 待开发 | 无 | Designed |

## 验收追踪说明

- 覆盖状态 not_covered 表示尚未开发，DEV 任务完成后逐项更新为 covered
- 状态 Designed 表示已完成设计落点关联，等待开发
- 手动验证项在 QA 阶段由 QA Agent 复核
