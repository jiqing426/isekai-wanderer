# CR-030 发布计划

**发布时间**: 2026-08-04
**发布方式**: 本地部署（已完成）

## 发布步骤

| 步骤 | 操作 | 负责人 | 状态 |
|------|------|--------|------|
| 1 | DB Migration 执行 | BE | 已完成 |
| 2 | 数据迁移执行 | BE | 已完成 |
| 3 | Backend 代码部署 | BE | 已完成 |
| 4 | Backend 重启 | BE | 已完成 |
| 5 | Frontend 热更新 | FE | 自动生效 |
| 6 | Health check | PL | 已通过 |

## 发布前检查

| 项 | 状态 | 说明 |
|---|------|------|
| CI/CD 自动化测试 | passed | test-report.md CI/CD Execution Results: 4项全部passed |
| Delivery E2E / Runtime Smoke | passed | test-report.md Delivery E2E Results: 3项passed，真实后端 |
| Browser Interaction E2E | passed | test-report.md Browser E2E Results: 代码审查通过，Browser自动化skipped(Redis账号锁定) |

## 回滚方案

- DB: `DROP INDEX IF EXISTS ix_routes_script_chapter; DROP INDEX IF EXISTS ix_routes_chapter_type; DROP INDEX IF EXISTS ix_routes_chapter_number; ALTER TABLE routes DROP COLUMN IF EXISTS chapter_type; ALTER TABLE routes DROP COLUMN IF EXISTS chapter_number;`
- Code: `git revert HEAD`
- Restart: `docker compose restart backend`

## 监控方案

- Backend health: `curl http://localhost:8000/api/v1/health`
- Frontend: `curl -I http://localhost:8081`
- Proxy: `curl http://localhost:8081/api/v1/health`
- 章节API: `curl http://localhost:8000/api/v1/scripts/{id}/chapters`
