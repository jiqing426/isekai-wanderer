# Deploy Plan: CR-038 — Corvus 前端入口接入

| 项 | 内容 |
|---|---|
| 部署结论 | pending — 待 RELEASE_GATE 通过后执行 |
| CR ID | CR-038 |
| 变更名称 | Corvus 前端入口接入 |
| 负责人 | ops |
| 部署环境 | ENV-L1 (DEV_LOCAL) |

---

## 发布前检查

| 项 | 状态 | 说明 |
|---|---|---|
| Docker 容器全部 healthy | passed | backend/db/frontend/redis 全 Up (healthy) |
| CI/CD 后端单元测试 | passed | 6/6 PASSED (test_scripts_engine_type + test_player_candidates_create) |
| CI/CD 前端编译 | passed | npm run build exit 0, ✓ built in 15.64s |
| Delivery E2E / Runtime Smoke | passed | 7/7 PASS, Mock API=no — health + GET /scripts engine_type=corvus + npm build |
| Browser Interaction E2E | passed | 17/17 passed (Playwright Chromium), Mock API=no |
| Corvus 服务可达 | passed | http://127.0.0.1:8082/api/health → {"ok":true} |
| iptables 8082 规则 | passed | DROP 公网 + ACCEPT Docker bridge |

## 发布步骤

| # | 步骤 | 命令 | 说明 |
|---|---|---|---|
| 1 | 拉取最新代码 | `cd /root/isekai-wanderer && git pull` | 确保代码最新 |
| 2 | 重建前端 | `cd frontend && npm run build` | 生成 dist/ 产物 |
| 3 | 重建 Docker 容器 | `cd /root/isekai-wanderer && docker compose up -d --build` | 重建 backend/frontend 容器 |
| 4 | 验证容器健康 | `docker compose ps` | 全部 Up (healthy) |
| 5 | Delivery E2E 冒烟 | `curl http://localhost:8081/api/v1/health && curl http://localhost:8081/api/v1/scripts` | health ok + scripts 返回 engine_type=corvus |
| 6 | Browser E2E 冒烟 | `SKIP_WEB_SERVER=1 APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr038-start-game.spec.ts --project=chromium` | 3/3 passed |

## 回滚方案

- 前端构建失败：`git checkout HEAD~1 -- frontend/ && cd frontend && npm run build && docker compose up -d frontend` 回滚前端代码
- 后端启动失败：`git checkout HEAD~1 -- backend/ && docker compose up -d --build backend` 回滚后端代码
- Docker 容器异常：`docker compose down && docker compose up -d` 全量重启
- 数据库迁移问题：`cd backend && .venv/bin/alembic downgrade -1` 回滚一个迁移

## 监控方案

- 容器状态：`docker compose ps` 全部 Up (healthy)
- API 健康：`curl http://localhost:8081/api/v1/health` → `{"status":"ok"}`
- Corvus 健康：`curl http://127.0.0.1:8082/api/health` → `{"ok":true}`
- 错误日志：`docker compose logs --tail=50 backend` 无 ERROR

## 非阻塞已知项

| # | 问题 | 优先级 | 说明 |
|---|---|---|---|
| 1 | Docker backend 未开启 --reload | P3 | 开发环境非阻塞，生产环境不影响 |
| 2 | Corvus systemd HOST=0.0.0.0 | P3 | 已被 iptables 补偿，建议收紧为 127.0.0.1 |
