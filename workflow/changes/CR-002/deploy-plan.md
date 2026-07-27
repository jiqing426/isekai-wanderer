# Deploy Plan — CR-002

> **Plan Date**: 2026-07-22T18:00:00Z
> **Change**: CR-002 Phase 1 (9 P1 features + 11 Bug fixes)
> **Environment**: DEV_LOCAL → STAGING → PRODUCTION

---

## 发布前检查

| 项 | 状态 | 说明 |
|---|------|------|
| CI/CD 结果 | passed | FE Vitest 50/50 + BE pytest 38/38 + FE Build 成功 |
| Delivery E2E / Runtime Smoke 结果 | passed | 4/4 端点 200 OK (health, frontend, scripts, subscription/plans) |
| Browser Interaction E2E 结果 | passed | 12/12 Playwright 场景通过，Mock API=no |

---

## 部署步骤

| 步骤 | 命令 | 预期结果 | 负责人 |
|------|------|---------|--------|
| 数据库迁移 | docker compose exec -T backend alembic upgrade head | head = c2b84460a40d | ops |
| 种子数据 | docker compose exec -T backend python -m scripts.seed_data | test@isekai-wanderer.com / Test123456! 创建成功 | ops |
| Backend 部署 | docker compose --profile app up -d backend | health 200 OK | ops |
| Frontend 部署 | docker compose --profile app up -d frontend | page 200 OK HTML | ops |
| 端点验证 | curl -f /api/v1/health && curl -f / && curl -f /api/v1/scripts && curl -f /api/v1/subscription/plans | 全部 200 OK | ops |

---

## 回滚方案

- **数据库回滚**: `docker compose exec -T backend alembic downgrade -1`
- **Backend 回滚**: 停止容器，git checkout CR-001，重启容器
- **Frontend 回滚**: 停止容器，git checkout CR-001，重新构建，重启容器
- **验证**: 回滚后执行 health check 和 4 端点验证

---

## 监控方案

- **Health Check**: `watch -n 5 'curl -f http://localhost:8000/api/v1/health'`
- **日志监控**: `docker compose logs -f backend frontend`
- **关键指标**:
  - Backend health: 200 OK（非 200 立即告警）
  - Frontend page: 200 OK（非 200 立即告警）
  - API 响应时间: < 500ms（> 1s 告警）
  - 错误率: < 1%（> 5% 告警）

---

## 部署后验证

| 验证项 | 命令 | 预期 |
|-------|------|------|
| Backend health | curl -f http://localhost:8000/api/v1/health | 200 OK |
| Frontend page | curl -f http://localhost:3000 | 200 OK |
| 剧本大厅 | curl -f http://localhost:8000/api/v1/scripts | 200 OK JSON |
| 订阅计划 | curl -f http://localhost:8000/api/v1/subscription/plans | 200 OK JSON |
| 测试账号登录 | curl -X POST ... | 200 OK + token |

---

## 已知风险（P2，不阻塞发布）

| # | 风险 | 级别 | 缓解 |
|---|------|------|------|
| 1 | vite.config.ts port=3000 vs runtime-contract port=3000 | P2 | 已修复，DEV_LOCAL 使用 3000 |
| 2 | Mock 服务生产替换 | P2 | 生产需替换为真实 SMTP/Discord/LLM |
| 3 | datetime.utcnow deprecation | P2 | Python 3.12 废弃，建议后续 CR 修复 |
