# Deploy Plan

本文记录发布关口前必须评审的发布计划。实际部署执行结果写入 `deploy-record.md`。

| 项 | 内容 |
| --- | --- |
| CR 编号 | CR-037 |
| 目标环境 | ENV-L1 (DEV_LOCAL) + ENV-L2 (DEPLOY_PRIVATE) |
| 目标证据等级 | L2 |
| 发布负责人 | ops |
| 计划状态 | Ready |
| 人工确认要求 | 是 — 不可逆 DB 迁移(embedding 1536→512)需人工追认；生产环境变更(systemd/防火墙)需人工确认 |

## 发布步骤

| 步骤 | 命令 / 操作 | 预期结果 | 负责人 |
| --- | --- | --- | --- |
| 1 | 确认 Corvus systemd 服务运行 | `systemctl status corvus-story` → active(running) | ops |
| 2 | 确认 Corvus health | `curl http://127.0.0.1:8082/api/health` → `{"ok":true}` | ops |
| 3 | 确认 iptables DROP 规则 | `iptables -L INPUT -n | grep 8082` → DROP all | ops |
| 4 | 确认后端 Docker 容器运行 | `docker compose ps` → backend/healthy | ops |
| 5 | 运行 CI/CD pytest 全量 | `docker exec isekai-wanderer-backend-1 python -m pytest tests/unit/test_corvus_dev*.py -v` → 120 passed | ops |
| 6 | Delivery E2E 冒烟 | `curl http://localhost:8081/api/v1/game/player/candidates` → code:0, 3 条 | ops |
| 7 | SSE 流式冒烟 | `curl -N -X POST http://localhost:8081/api/v1/game/{id}/custom-input -d '{"text":"你好"}'` → SSE 事件流 | ops |
| 8 | 前端 build | `cd frontend && npm run build` → exit 0 | ops |
| 9 | 人工 Browser E2E | 打开浏览器 `/game?script={uuid}` → 页面正常加载 → 输入文本 → SSE 逐字渲染 | qa/用户 |

## 回滚方案

- `systemctl stop corvus-story` — 停止 Corvus 服务
- `alembic downgrade -1` — 回滚数据库迁移
- 删除 Corvus 新增 API 端点（session/create, player/candidates, select-player, game-turn）
- `frontend/src/stores/game.ts` 删除 SSE 分支，回退到同步 api.post
- `frontend/src/views/GameView.vue` 删除 Corvus 分支
- 旧引擎路径完全不变，feature flag 隔离确保回滚不影响现有功能

## 监控方案

- `systemctl status corvus-story` — Corvus 服务状态
- `curl http://127.0.0.1:8082/api/health` — Corvus 健康检查
- `journalctl -u corvus-story -f` — Corvus 日志（LLM 调用、错误）
- `docker compose logs -f backend` — 后端 API 日志
- `docker compose logs -f frontend` — 前端日志
- `psql -c "SELECT count(*) FROM corvus_game_sessions WHERE status='playing'"` — 活跃 Corvus 会话数

## 发布前检查

| 项 | 状态 | 说明 |
| --- | --- | --- |
| CI/CD 结果已通过或有批准豁免 | passed | 120/120 pytest passed, 0 failed |
| Delivery E2E / Runtime Smoke 已通过 | passed | 25/28 AC PASS, AC-002 已修复验证; Mock API=no |
| Browser Interaction E2E 已通过 | passed | 7/7 Browser E2E PASS (Playwright Chromium); 旧 E2E 回归 10/10 passed |
| 目标环境测试矩阵已覆盖 | passed | ENV-L1 (DEV_LOCAL) 25/28 AC PASS; ENV-L2 (DEPLOY_PRIVATE) AC-002 修复验证 |
| 公网 / 外网访问验证已完成或声明不适用 | passed | AC-002 公网 8082 不可达已修复验证; CORS 配置正确 |
| 测试结论已通过或阻塞项有负责人 | passed | QA FAIL→有条件通过; AC-002 已修复; AC-023/024 deferred_with_approval |
| 安全审查已通过或阻塞项有负责人 | passed | Security PASS(有条件); 2 项低风险后续修复(SEC-001/SEC-002)不阻塞 |
| 回滚路径可执行 | passed | systemctl stop + alembic downgrade + 删除端点 + game.ts 回退 |
