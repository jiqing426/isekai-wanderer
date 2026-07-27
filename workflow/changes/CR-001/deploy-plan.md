# Deploy Plan — CR-001 Isekai Wanderer MVP

## 发布步骤

| 步骤 | 操作 | 负责人 | 预估时间 |
|------|------|--------|----------|
| 1 | 合并 release 分支到 main | ops | 5 min |
| 2 | 运行 CI pipeline（pytest + vitest + build） | ci | 10 min |
| 3 | 构建 Docker 镜像（BE + FE） | ops | 5 min |
| 4 | 推送镜像到 registry | ops | 2 min |
| 5 | 执行数据库迁移（Alembic） | ops | 3 min |
| 6 | 部署 BE + FE 容器（docker-compose up） | ops | 5 min |
| 7 | 运行 health check（/health） | ops | 1 min |
| 8 | 运行 smoke test（3 核心路径） | qa | 5 min |
| 9 | 通知全员发布成功 | pl | 1 min |

## 回滚方案

- BE 启动失败：docker-compose rollback + 重新 deploy 上一版本镜像，回滚命令 `docker-compose stop backend && docker-compose up -d backend:previous`，负责人 ops，预估 5 min
- 数据库迁移失败：保留旧表结构，回滚 BE 镜像到上一版本，命令 `alembic downgrade -1`，负责人 ops，预估 5 min
- FE 白屏或 JS 错误：回滚 FE 容器到上一版本，命令 `docker-compose stop frontend && docker-compose up -d frontend:previous`，负责人 ops，预估 3 min
- API 大面积 500：回滚 BE 并检查日志，负责人 ops + security，预估 5 min
- 安全漏洞：立即下线并热修复，负责人 security + ops，预估 30 min

## 监控方案

- API 响应时间：Prometheus + Grafana，告警阈值 p99 > 3s，负责人 ops
- API 错误率：Prometheus，告警阈值 5xx > 5%，负责人 ops
- CPU 和内存：Docker stats，告警阈值 CPU > 80%，负责人 ops
- Redis 连接数：redis-cli info，告警阈值 connections > 100，负责人 ops
- 数据库连接池：pg_stat，告警阈值 connections > 50，负责人 ops
- JWT secret 环境变量：启动日志检查，使用默认值时告警，负责人 security
- 登录锁定触发次数：日志监控，告警阈值 > 100/min，负责人 security

## 环境变量

| 变量 | 说明 | 必须 |
|------|------|------|
| JWT_SECRET | JWT 签名密钥（生产环境必须设置，不可使用默认值） | 是 |
| DATABASE_URL | PostgreSQL 连接串 | 是 |
| REDIS_URL | Redis 连接串 | 是 |
| CORS_ORIGINS | 允许的 CORS 来源（逗号分隔） | 是 |
| LLM_API_KEY | LLM API 密钥（Mock 模式可省略） | 否 |

## 发布前检查

| 项 | 状态 | 说明 |
| --- | --- | --- |
| CI/CD 结果 | passed | pytest 180/180 + vitest 15/15 + build 0 errors |
| Delivery E2E / Runtime Smoke 结果 | passed | 24/24 API endpoints 200, Mock API=no, 15 条 Delivery E2E 全部通过 |
| Browser Interaction E2E 结果 | passed | 6/6 Playwright paths passed, 18+ screenshots, Mock API=no |
| Security review | passed | 0 Critical, 0 High, 5 issues fixed and verified |
| Deploy plan reviewed | approved | PL + CEO 审核通过 |
| 环境变量配置 | pending | 生产环境 JWT_SECRET 待配置 |
| 数据库迁移就绪 | approved | Alembic 迁移脚本已就绪 |
