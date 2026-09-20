# Deploy Record

本文记录 CR-042 的实际部署执行结果。

| 项 | 内容 |
| --- | --- |
| CR 编号 | CR-042 |
| 变更内容 | Legacy 三条路径 SSE 流式改造（game.py 3 端点 SSE + model_router stream_with_fallback + free_chat_service send_message_stream + 前端 useSSEStream composable + game.ts SSE + FreeChatView.vue 流式） |
| 目标环境 | DEV (ENV-L1) |
| 证据等级 | L2（联调通过 — 真实前端 + 真实后端 + Vite proxy 链路验证） |
| 部署负责人 | ops (Cat01-op) |
| 部署日期 | 2026-09-16T19:00+08:00 |
| 部署结论 | ✅ Success |
| 人工确认 | 无 (CR-042 change.md 人工确认表全否) |
| RELEASE_GATE | ✅ Passed (PL 已确认 gate readiness 检查通过，用户已确认推进 DEPLOY) |

## 部署环境

| 项 | 值 |
| --- | --- |
| 主机 | iZwz99ce7glgmvtubvtbrrZ |
| 操作系统 | Linux 5.10.134-19.3.al8.x86_64 (x64) |
| Docker | Docker Compose (profile=app) |
| 前端入口 | `http://localhost:8081` (Vite dev server, Docker) |
| 后端地址 | `http://localhost:8000` (Uvicorn, Docker) |
| 代理 | Vite dev proxy → backend |
| PostgreSQL | `localhost:9000` (Docker, pgvector/pgvector:pg16) |
| Redis | `localhost:6379` (Docker, redis:7-alpine) |
| Mock API | no |

## 部署步骤执行记录

| 步骤 | 命令 / 操作 | 执行时间 | 结果 | 说明 |
| --- | --- | --- | --- | --- |
| 1 | 确认代码状态：`git status` + `git log --oneline -3` | 19:00 | ✅ 代码已挂载 | Docker volume mount `./backend/app:/app/app` + `./frontend/src:/app/src`，代码变更已生效。最新 commit: `1be219b feat: 全量提交` |
| 2 | 重启后端容器：`docker compose --profile app restart backend` | 19:01 | ✅ Started | 后端容器重启成功，加载 game.py / model_router.py / free_chat_service.py 变更 |
| 3 | 重启前端容器：`docker compose --profile app restart frontend` | 19:01 | ✅ Started | 前端容器重启成功，加载 useSSEStream.ts / game.ts / FreeChatView.vue 变更 |
| 4 | 健康检查：`sleep 10 && curl -sf http://localhost:8000/api/v1/health` | 19:02 | ✅ `{"status":"ok","version":"1.0.0"}` | 后端启动完成，健康检查通过 |
| 5 | 前端可达验证：`curl -sf -o /dev/null -w '%{http_code}' http://localhost:8081/` | 19:02 | ✅ 200 | 前端入口可达 |
| 6 | Vite proxy 验证：`curl -sf -o /dev/null -w '%{http_code}' http://localhost:8081/api/v1/health` | 19:02 | ✅ 200 | Vite dev proxy 正确代理到后端 |
| 7 | SSE 路由注册验证：`docker compose exec backend python3 -c "from app.main import app; ..."` | 19:03 | ✅ 5 routes confirmed | 确认 `/free-chat/stream`（新增）、`/choice`、`/custom-input`、`/free-chat`（旧兼容）、`/free-chat/history` 路由均注册 |
| 8 | 端点存在性验证（无认证返回 401 非 404） | 19:03 | ✅ All 401 | `free-chat` 401, `free-chat/stream` 401, `choice` 401, `custom-input` 401 — 全部路由存在，需 Bearer Token 认证 |
| 9 | 前端入口代理验证 | 19:03 | ✅ 200 | 经 Vite proxy 访问后端 health 端点成功 |

## SSE 端点验证结果

| 端点 | 路由 | HTTP 状态（无 auth） | 路由注册 | Mock API | 结论 |
| --- | --- | --- | --- | --- | --- |
| Health | `/api/v1/health` | 200 | ✅ | no | ✅ 后端健康 |
| free-chat/stream（新增 SSE） | `/api/v1/game/{id}/free-chat/stream` | 401 | ✅ | no | ✅ 端点存在，需认证 |
| choice（Legacy SSE 改造） | `/api/v1/game/{id}/choice` | 401 | ✅ | no | ✅ 端点存在，需认证 |
| custom-input（Legacy SSE 改造） | `/api/v1/game/{id}/custom-input` | 401 | ✅ | no | ✅ 端点存在，需认证 |
| free-chat（旧端点兼容） | `/api/v1/game/{id}/free-chat` | 401 | ✅ | no | ✅ 旧端点保留，需认证 |

## 前端验证结果

| 检查项 | URL | 结果 | 说明 |
| --- | --- | --- | --- |
| 前端入口 | `http://localhost:8081/` | ✅ 200 | Vite dev server 正常 |
| Vite proxy | `http://localhost:8081/api/v1/health` | ✅ 200 | 代理到后端 `http://localhost:8000` 成功 |

## Nginx SSE 配置状态（S-2）

| 项 | 状态 | 说明 |
| --- | --- | --- |
| `deploy/nginx/app.conf.example` SSE 配置 | ⚠️ 缺少 | 当前 `/api/` location 缺少 `proxy_buffering off; proxy_cache off; proxy_read_timeout 300s;` |
| DEV 环境影响 | 无 | DEV 使用 Vite dev proxy，默认支持 SSE，不受 Nginx 配置影响 |
| 生产部署要求 | 必须补充 | 生产环境 Nginx 必须添加 SSE 专用配置，否则 SSE 流式响应将被缓冲 |
| runtime-contract 定义 | ✅ 已定义 | `docs/runtime/runtime-contract.md` CR-042 Additions 明确记录 SSE proxy 配置要求 |

## 回滚方案确认

| 项 | 状态 | 说明 |
| --- | --- | --- |
| git revert 方案 | ✅ 可执行 | `git revert <commit>` + `docker compose --profile app up -d --build backend` |
| DB 回滚 | 不需要 | CR-042 无 DB schema 变更，无数据修复需求 |
| 回滚验证 | 待执行 | 回滚后确认旧端点恢复同步 JSON 响应（无 Deprecation header） |

## 监控方案确认

| 检查项 | 方式 | 频率 | 状态 |
| --- | --- | --- | --- |
| 后端健康 | Docker healthcheck `curl -f http://localhost:8000/api/v1/health` | 每 15s | ✅ Active (healthy) |
| 前端可达 | Docker healthcheck `wget -q --spider http://127.0.0.1:8081/` | 每 15s | ✅ Active (healthy) |
| PostgreSQL | Docker healthcheck `pg_isready` | 每 10s | ✅ Active (healthy) |
| Redis | Docker healthcheck `redis-cli ping` | 每 10s | ✅ Active (healthy) |
| SSE 端点可用性 | curl 冒烟检查（需有效 token） | 每次发布后 | ✅ 部署时验证（路由注册 + 401 确认） |
| 后端日志 | `docker compose logs backend --tail 100` | 按需 | ✅ Application startup complete, 无错误 |

## 容器状态

| 容器 | 镜像 | 状态 | 端口 | Healthcheck |
| --- | --- | --- | --- | --- |
| isekai-wanderer-backend-1 | isekai-wanderer-backend | Up (healthy) | 0.0.0.0:8000->8000 | ✅ healthy |
| isekai-wanderer-frontend-1 | isekai-wanderer-frontend | Up (healthy) | 0.0.0.0:8081->8081 | ✅ healthy |
| isekai-wanderer-db-1 | pgvector/pgvector:pg16 | Up (healthy) | 0.0.0.0:9000->5432 | ✅ healthy |
| isekai-wanderer-redis-1 | redis:7-alpine | Up (healthy) | 0.0.0.0:6379->6379 | ✅ healthy |

## 发布前检查清单确认

| 项 | 状态 | 说明 |
| --- | --- | --- |
| CI/CD 结果已通过 | ✅ Passed | BE 33/35 (2 env errors), FE 18/18 |
| Delivery E2E / Runtime Smoke 已通过 | ✅ Passed | 5/5, Mock API=no |
| Browser Interaction E2E 已通过 | ✅ Passed | 7/9, BUG-002 非业务缺陷, CEO C2 满足 |
| 安全审查已通过 | ✅ Passed | 3 项低风险建议不阻塞 |
| 回滚路径可执行 | ✅ Ready | git revert + docker compose, 无 DB 变更 |
| 环境变量一致性 | ✅ Verified | .env.example 与 docker-compose.yml 一致 |
| 部署配置无真实密钥 | ✅ Verified | 全部占位符 |
| 健康检查和监控入口 | ✅ Active | Docker healthcheck 全部 healthy |
| Nginx SSE 配置（S-2） | ⚠️ DEV 不受影响 | 生产部署前必须补充 |

## 追踪链确认

| 链路段 | 追踪结论 |
| --- | --- |
| PRD → REQ | ✅ CR-040 PRD 五条需求 → REQ-001~REQ-005 |
| REQ → AC | ✅ acceptance.md 22 项 AC 映射到 5 条 REQ |
| AC → Design | ✅ 每项 AC 有设计落点（§1~§7 + ADR-042-01~03） |
| Design → Task | ✅ DEV-001（后端）、DEV-002（前端）有 owner |
| Task → Code | ✅ game.py, model_router.py, free_chat_service.py, useSSEStream.ts, game.ts, FreeChatView.vue |
| Code → Test | ✅ BE 6 测试文件 35 tests + FE 1 测试文件 18 tests |
| Test → Red/Green | ✅ BUG-001 修复后复验通过；BUG-002 非业务缺陷 |
| Green → Acceptance | ✅ acceptance.md 22/22 AC 有覆盖状态和 QA 复核结论 |
| Acceptance → QA | ✅ test-report.md 有 CI/CD + Delivery E2E + Browser E2E 分类记录 |
| QA → Release | ✅ Delivery E2E Mock API=no；Browser E2E Mock API=no |
| Release → Deploy | ✅ deploy-plan.md 步骤已执行，deploy-record.md 已写入 |

## 部署结论

**CR-042 部署成功。**

- 后端容器重启成功，健康检查通过
- 前端容器重启成功，入口可达
- 5 个 SSE 相关路由全部注册确认（free-chat/stream 新增 + choice/custom-input 改造 + free-chat 旧兼容）
- 端点存在性验证通过（全部 401 需认证，无 404）
- Vite proxy 链路正常（前端 → 后端 health 代理成功）
- Docker healthcheck 全部 healthy
- 无部署错误或异常

## 待办事项

| 项 | 责任人 | 说明 |
| --- | --- | --- |
| Nginx SSE 配置补充（S-2） | ops (Cat01-op) | 生产部署前在 `deploy/nginx/app.conf.example` 的 `/api/` location 添加 `proxy_buffering off; proxy_cache off; proxy_read_timeout 300s;` |
| BUG-002 修复 | fe (Cat01-fe) | Corvus 回归 E2E spec listener 注册时机，后续迭代修复 |
| S-1 token 日志 hash | be (Cat01-be) | auth.py token 前 20 字符日志改为 SHA-256 hash，后续迭代 |
| H-1 StoryPanel DOMPurify | fe (Cat01-fe) | StoryPanel.vue v-html 增加 DOMPurify 消毒，后续迭代（CR-039 已登记） |
