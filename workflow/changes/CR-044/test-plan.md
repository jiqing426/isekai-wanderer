# CR-044 Test Plan

## Test-First Scope

- 数据库迁移 (DEV-001)：先写迁移测试验证表删除、唯一约束、CASCADE 外键
- 动态配置 (DEV-002, DEV-003)：先写 system_config 模型和热更新测试
- Vben Admin (DEV-004)：先写 smoke spec 验证 8082 端口启动
- 前端页面迁移 (DEV-005~016)：手动验证为主，i18n 覆盖检查用 grep 脚本

## Test Case Artifacts

| Task ID | 测试用例产物 | 覆盖验收项 | 状态 |
|---------|-------------|------------|------|
| DEV-001 | backend/tests/unit/test_cr044_migration.py | AC-001, AC-002, AC-003, AC-004, AC-005 | Ready |
| DEV-002 | backend/tests/unit/test_system_config.py | AC-006, AC-008 | Ready |
| DEV-003 | backend/tests/unit/test_config_dynamic.py | AC-007 | Ready |
| DEV-004 | admin/e2e/smoke.spec.ts | AC-009 | Ready |
| DEV-005 | admin/e2e/page-migration.spec.ts | AC-010 | Ready |

## Red Failure Records

| Task ID | 失败描述 | 根因 | 修复提交 | 时间 |
|---------|----------|------|----------|------|
| DEV-001 | 尚未开始 RED 阶段，待 DEVELOPMENT 写代码前补充 | — | — | — |

## CI/CD Evidence Plan

| 阶段 | 触发时机 | 命令 / Pipeline | 覆盖验收项 | 负责人 | 记录位置 | 状态 |
|--------|----------|----------------|------------|--------|----------|------|
| unit | pre-commit | `cd backend && python -m pytest tests/unit/test_cr044_migration.py tests/unit/test_system_config.py tests/unit/test_config_dynamic.py -v` | AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-007, AC-008 | backend | CI log | Ready |
| e2e | pre-merge | `cd admin && npx playwright test e2e/smoke.spec.ts e2e/page-migration.spec.ts e2e/admin-pages.spec.ts` | AC-009, AC-010, AC-011, AC-012 | frontend | CI log | Ready |
| lint | pre-commit | `cd frontend && npx eslint src/` | AC-018 | frontend | CI log | Ready |

## Delivery E2E / Runtime Smoke Plan

| 任务编号 | 命令 / 步骤 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
|---------|-------------|----------|----------|-------------------|----------|------------|-------------|------|
| DEV-001 | `docker compose up -d && sleep 5 && alembic upgrade head && psql -c "\dt email_verifications" -c "\dt user_preferences" -c "\dt subscription_plans"` | 无 | http://localhost:8000 | /api/v1/health | no | AC-001, AC-002, AC-003 | test-report.md | Ready |
| DEV-002 | `curl -f http://localhost:8081/api/v1/admin/system-config -H "Authorization: Bearer $TOKEN"` | http://localhost:8081 | http://localhost:8000 | /api/v1/admin/system-config | no | AC-006, AC-008 | test-report.md | Ready |
| DEV-004 | `curl -f http://localhost:8082/` | http://localhost:8082 | http://localhost:8000 | /api/v1/health | no | AC-009 | test-report.md | Ready |

## Browser Interaction E2E Plan

| 任务编号 | 命令 / 步骤 | Browser / Tool | 用户动作 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
|---------|-------------|---------------|----------|----------|----------|-------------------|----------|------------|-------------|------|
| DEV-007 | `npx playwright test tests/e2e/personal-center.spec.ts` | Chromium | 点击头像下拉→验证设置/退出选项→验证会员卡内联展示 | http://localhost:8081 | http://localhost:8000 | /api/v1/users/me | no | AC-013, AC-014 | test-report.md | Ready |
| DEV-008 | `npx playwright test tests/e2e/settings.spec.ts` | Chromium | 打开设置页→验证 4 个 tab→验证无 member tab | http://localhost:8081 | http://localhost:8000 | /api/v1/users/me | no | AC-015 | test-report.md | Ready |
| DEV-009 | `npx playwright test tests/e2e/mobile-adapter.spec.ts` | Chromium (mobile viewport) | 375px 宽度打开页面→验证单列布局→验证触摸目标 44px | http://localhost:8081 | http://localhost:8000 | /api/v1/health | no | AC-016, AC-017 | test-report.md | Ready |
| DEV-013 | `npx playwright test tests/e2e/i18n-coverage.spec.ts` | Chromium | 切换语言→验证无硬编码中文→验证 zh-CN/en-US 切换 | http://localhost:8081 | http://localhost:8000 | /api/v1/health | no | AC-018, AC-019 | test-report.md | Ready |
