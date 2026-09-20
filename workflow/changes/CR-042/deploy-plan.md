# Deploy Plan

本文记录发布关口前必须评审的发布计划。实际部署执行结果写入 `deploy-record.md`。

| 项 | 内容 |
| --- | --- |
| CR 编号 | CR-042 |
| 变更内容 | Legacy 三条路径 SSE 流式改造（game.py 3 端点 + model_router stream_with_fallback + free_chat_service send_message_stream + 前端 useSSEStream composable + game.ts SSE + FreeChatView.vue 流式） |
| 目标环境 | DEV (ENV-L1) |
| 目标证据等级 | L3 |
| 发布负责人 | ops (Cat01-op) |
| 计划状态 | Ready |
| 人工确认要求 | 无 (CR-042 change.md 人工确认表全否) |
| 无 DB 变更 | 是（无新增表、无 schema 变更，Deferred DB 写入复用现有表） |
| 无新增依赖 | 是（无新增 Python/npm 包） |
| 旧端点兼容 | 是（POST /game/{id}/free-chat 保留，追加 Deprecation: true header） |

## 安全审查结论

- 安全审查已通过，详见 `workflow/changes/CR-042/security-review.md`
- 3 项低风险建议不阻塞发布：S-1 (token 日志 hash), S-2 (Nginx SSE 配置), H-1 (StoryPanel DOMPurify)
- **Ops 注意事项 (S-2)**：生产环境 Nginx `/api/` location 必须包含 SSE 专用配置：
  ```nginx
  proxy_buffering off;
  proxy_cache off;
  proxy_read_timeout 300s;
  ```
  确保 SSE 流式响应不被 Nginx 缓冲。

## 发布步骤

| 步骤 | 命令 / 操作 | 预期结果 | 负责人 |
| --- | --- | --- | --- |
| 1 | `cd /root/isekai-wanderer && git pull origin main` | 拉取最新代码，包含 CR-042 全部变更 | ops |
| 2 | `cd /root/isekai-wanderer && docker compose --profile app up -d --build backend` | 重新构建并重启后端容器，加载 game.py / model_router.py / free_chat_service.py 变更 | ops |
| 3 | `sleep 10 && curl -sf http://localhost:8000/api/v1/health` | 等待后端健康检查通过，返回 `{"status":"ok","version":"1.0.0"}` | ops |
| 4 | `cd /root/isekai-wanderer/frontend && npx vite build` 或重启 Vite dev server：`docker compose --profile app restart frontend` | 前端重建/重启，加载 useSSEStream.ts / game.ts / FreeChatView.vue 变更 | ops |
| 5 | `curl -sf http://localhost:8081/` | 验证前端入口可达 | ops |
| 6 | SSE 端点冒烟验证（见下方"发布后冒烟验证"） | 3 个 SSE 端点 + 1 个旧端点全部返回正确响应 | ops |
| 7 | 通知 PL 发布完成，等待 PL 执行 `python tools/check-gate-readiness.py --gate release --change CR-042-prd-cr-040-非-corvus-路径-sse-流式改造 --change-id CR-042` | gate readiness 检查通过 | PL |
| 8 | PL 确认后，写入 `deploy-record.md` | 部署记录完成 | ops |

### 发布后冒烟验证

```bash
# 1. Health check
curl -sf http://localhost:8000/api/v1/health
# 预期: {"status":"ok","version":"1.0.0"}

# 2. free-chat/stream SSE 端点（需有效 token + session_id）
curl -N -X POST http://localhost:8081/api/v1/game/{session_id}/free-chat/stream \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{"message":"你好"}'
# 预期: text/event-stream，data: {"type":"text","content":"..."} 逐字推送

# 3. Legacy choice SSE（transition 节点）
curl -N -X POST http://localhost:8081/api/v1/game/{session_id}/choice \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{"choice_id":"{uuid}"}'
# 预期: transition 节点返回 text/event-stream；preset/choice 节点返回 JSON

# 4. Legacy custom-input SSE
curl -N -X POST http://localhost:8081/api/v1/game/{session_id}/custom-input \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{"text":"你好"}'
# 预期: text/event-stream，逐字推送

# 5. 旧 free-chat 端点兼容
curl -D - -X POST http://localhost:8081/api/v1/game/{session_id}/free-chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{"message":"你好"}'
# 预期: HTTP 200 + JSON 响应 + Deprecation: true header
```

## 回滚方案

| 步骤 | 命令 / 操作 | 预期结果 | 负责人 |
| --- | --- | --- | --- |
| 1 | `cd /root/isekai-wanderer && git revert <CR-042 merge commit>` | 代码回滚到 CR-042 前状态 | ops |
| 2 | `git push origin main` | 推送回滚 commit | ops |
| 3 | `docker compose --profile app up -d --build backend` | 重建并重启后端容器 | ops |
| 4 | `docker compose --profile app restart frontend` | 重启前端容器 | ops |
| 5 | `sleep 10 && curl -sf http://localhost:8000/api/v1/health` | 验证后端健康 | ops |
| 6 | `curl -sf http://localhost:8081/` | 验证前端入口可达 | ops |
| 7 | 验证旧端点恢复正常（非 SSE 同步 JSON 响应） | 确认回滚成功 | ops |

### 回滚注意事项

- CR-042 无 DB schema 变更，回滚不需要数据库迁移或数据修复
- 回滚后旧 `POST /game/{id}/free-chat` 端点恢复为同步 JSON 响应（无 Deprecation header）
- 回滚后 Legacy `submit_choice` 和 `submit_custom_input` 恢复为同步 JSON 响应
- Deferred DB 写入复用现有表结构，回滚后表结构不变，无需数据修复
- 如 git revert 不可行（合并冲突等），可使用 `git reset --hard <pre-CR-042 commit>` 强制回退

## 监控方案
- 健康检查: Docker healthcheck backend/frontend/db/redis
- SSE 端点可用性: free-chat/stream + 旧 free-chat 每 5min curl
- 日志监控: Uvicorn SSE 错误 + Deferred DB + Nginx 499/502/504
- 告警方案: P0 后端不可达/P1 SSE 500/P1 旧端点不可达/P2 SSE 中断率

### 健康检查

| 检查项 | 命令 | 频率 | 预期 | 告警阈值 |
| --- | --- | --- | --- | --- |
| 后端健康 | `curl -sf http://localhost:8000/api/v1/health` | 每 15s（Docker healthcheck） | `{"status":"ok"}` | 连续 3 次失败 |
| 前端可达 | `curl -sf http://localhost:8081/` | 每 15s（Docker healthcheck） | HTTP 200 | 连续 3 次失败 |
| PostgreSQL | Docker healthcheck `pg_isready` | 每 10s | ready | 连续 5 次失败 |
| Redis | Docker healthcheck `redis-cli ping` | 每 10s | PONG | 连续 5 次失败 |

### SSE 端点可用性检查

| 检查项 | 命令 | 频率 | 预期 | 告警阈值 |
| --- | --- | --- | --- | --- |
| free-chat/stream 端点 | `curl -sf -o /dev/null -w '%{http_code}' -X POST http://localhost:8000/api/v1/game/{test_session_id}/free-chat/stream -H "Authorization: Bearer {test_token}" -d '{"message":"ping"}'` | 每 5min | HTTP 200 + `text/event-stream` | 连续 2 次非 200 |
| Legacy choice SSE | 通过 Browser E2E `cr042-legacy-sse.spec.ts` 定期回归 | 每次发布后 | E2E passed | 任何 failed |
| Legacy custom-input SSE | 通过 Browser E2E `cr042-legacy-sse.spec.ts` 定期回归 | 每次发布后 | E2E passed | 任何 failed |
| 旧 free-chat 兼容 | `curl -sf -o /dev/null -w '%{http_code}' -X POST http://localhost:8000/api/v1/game/{test_session_id}/free-chat -H "Authorization: Bearer {test_token}" -d '{"message":"ping"}'` | 每 5min | HTTP 200 + JSON 响应 | 连续 2 次非 200 |

### 日志监控

| 日志源 | 路径 / 命令 | 关注关键词 | 处理 |
| --- | --- | --- | --- |
| 后端 Uvicorn | `docker compose logs backend --tail 100` | `[Legacy SSE`, `[Free chat SSE`, `Error`, `Traceback` | 发现 SSE 错误立即检查 stream_with_fallback 降级是否生效 |
| 后端 Deferred DB | `docker compose logs backend 2>&1 \| grep -i "deferred"` | `deferred`, `async_session_factory`, `Error` | Deferred 写入失败需检查 DB 连接池 |
| Nginx（生产） | `/var/log/nginx/access.log` + `/var/log/nginx/error.log` | `499`（客户端断开）, `502`, `504` | SSE 长连接 499 为正常（用户关闭页面）；502/504 需检查后端状态 |
| 前端 Vite | `docker compose logs frontend --tail 50` | `error`, `failed` | 编译错误需检查 useSSEStream.ts 引入 |

### 告警方案

| 告警项 | 触发条件 | 严重程度 | 处理步骤 |
| --- | --- | --- | --- |
| 后端不可达 | Docker healthcheck 连续 3 次失败 | P0 | 1. `docker compose logs backend --tail 100` 查日志 2. 检查 PostgreSQL/Redis 健康 3. 必要时执行回滚方案 |
| SSE 端点 500 | curl 检查返回 5xx | P1 | 1. 检查 model_router stream_with_fallback 日志 2. 检查 LLM API Key 有效性 3. 确认 fallback 降级是否触发 |
| SSE 流中断率 > 10% | 日志中 `Error` / `client disconnect` 占比 | P2 | 1. 检查 Nginx proxy_read_timeout 配置 2. 检查 LLM provider 超时设置 3. 检查网络稳定性 |
| 旧 free-chat 端点不可达 | curl 检查返回非 200 | P1 | 1. 检查后端路由注册 2. 确认端点未被误删 3. 必要时回滚 |

## 发布前检查

| 项 | 状态 | 说明 |
| --- | --- | --- |
| CI/CD 结果已通过或有批准豁免 | passed | BE pytest 33/35 passed（2 env errors 非 business failure，`OSError: could not get source code` 为 pytest-asyncio 在 Docker 容器内环境问题）；FE vitest 18/18 passed。详见 `test-report.md` CI/CD 执行结果。Mock API=no。 |
| Delivery E2E / Runtime Smoke 已通过 | passed | 5/5 passed, Mock API=no。从真实前端入口 `http://localhost:8081` 经 Vite proxy 访问真实后端 `http://localhost:8000`。覆盖 AC-002, AC-003, AC-006, AC-007, AC-008, AC-011, AC-013, AC-015。详见 `test-report.md` Delivery E2E / Runtime Smoke Results。 |
| Browser Interaction E2E 已通过 | passed | 7/9 passed (2 skipped_with_reason: CEO C2 不阻塞). Playwright Chromium 真实浏览器执行用户动作，Mock API=no。覆盖 AC-001, AC-002, AC-005, AC-006, AC-008, AC-010, AC-013, AC-016。AC-022 Corvus 回归 skipped_with_reason（CEO 附条件 C2 满足：页面快照证明功能正常，Corvus 保持原逻辑不阻塞）。详见 `test-report.md` Browser Interaction E2E Results。 |
| 目标环境测试矩阵已覆盖 | ✅ ENV-L1 已验证 | 证据等级 L1（本地通过）。CI/CD + Delivery E2E + Browser E2E 均在 ENV-L1 环境执行。目标环境为 DEV (ENV-L1)，交付目标证据等级 L3，当前 L1 证据满足 RELEASE_GATE 前置条件。 |
| 公网 / 外网访问验证已完成或声明不适用 | ⚠️ 注意事项 | CR-042 目标环境为 DEV (ENV-L1)，使用 localhost:8081 + localhost:8000，不涉及公网入口。**生产部署时** Nginx `/api/` location 必须添加 SSE 专用配置（S-2）：`proxy_buffering off; proxy_cache off; proxy_read_timeout 300s;`。`deploy/nginx/app.conf.example` 当前缺少此配置，需在生产部署前补充。 |
| 测试结论已通过或阻塞项有负责人 | passed | QA 结论：✅ 可推进到 RELEASE_GATE。P0 AC 13 项全部通过；P1 AC 9 项 8 通过 + 1 条件性通过（AC-022 CEO C2）。BUG-001 Fixed；BUG-002 Open（非业务缺陷）。详见 `test-report.md`。 |
| 安全审查已通过或阻塞项有负责人 | passed | Security 结论：通过。认证/授权/所有权校验完整；SSE 流不泄露敏感信息；Deferred DB 无竞态；旧端点兼容安全；Fallback 文本硬编码；Mock API=no。3 项低风险建议（S-1/S-2/H-1）不阻塞。详见 `security-review.md`。 |
| 回滚路径可执行 | ✅ Ready | 回滚方案见上方：git revert + docker compose rebuild + restart。无 DB schema 变更，回滚不需要数据修复。步骤可执行，预期结果明确。 |
| Nginx SSE 配置（S-2） | ⚠️ 生产部署前补充 | `deploy/nginx/app.conf.example` 当前 `/api/` location 缺少 `proxy_buffering off; proxy_cache off; proxy_read_timeout 300s;`。DEV 环境使用 Vite dev proxy（默认支持 SSE），不受影响。生产部署前必须在 Nginx 配置中添加。 |
| 环境变量一致性 | ✅ Verified | `.env.example` 与 `docker-compose.yml` 一致。`DATABASE_URL`、`REDIS_URL`、`CORS_ORIGINS`、`BACKEND_PORT=8000`、`FRONTEND_PORT=8081` 均匹配 `docs/runtime/runtime-contract.md`。无新增环境变量。 |
| 部署配置无真实密钥 | ✅ Verified | `.env.example` 所有敏感值均为占位符（`change-me-local-only`、`test-key-placeholder`、`isekai_password`）。`docker-compose.yml` 使用 `${VAR:-default}` 引用，无硬编码密钥。Security 审查确认。 |
| 健康检查和监控入口 | ✅ Ready | Docker healthcheck 已配置 backend（`curl -f http://localhost:8000/api/v1/health`）、frontend（`wget -q --spider http://127.0.0.1:8081/`）、db（`pg_isready`）、redis（`redis-cli ping`）。SSE 端点冒烟验证步骤已定义。 |
| 发布计划、回滚步骤、监控方案和失败处理是否可执行 | ✅ Ready | 发布步骤 8 步逐项可执行；回滚方案 7 步逐项可执行；监控方案含健康检查、SSE 端点检查、日志监控和告警方案；失败处理有明确告警和处理步骤。 |

## 风险评估

| 风险项 | 等级 | 说明 | 缓解措施 |
| --- | --- | --- | --- |
| Nginx SSE 缓冲（S-2） | Low | 生产环境 Nginx 默认缓冲响应，可能导致 SSE 逐字输出变为批量推送 | 生产部署前在 Nginx `/api/` location 添加 `proxy_buffering off; proxy_cache off; proxy_read_timeout 300s;` |
| LLM API 不稳定 | Medium | SSE 流式依赖 LLM provider 稳定性，provider 超时或断连影响用户体验 | model_router stream_with_fallback 已实现多模型降级；所有模型失败时返回 fallback 文本不中断流 |
| BUG-002 Corvus 回归 E2E 时序 | Low | 测试 spec timing issue，非业务缺陷 | CEO 附条件 C2 满足；建议 FE 后续修复 listener 注册时机 |
| StoryPanel v-html XSS（H-1） | Low | LLM 输出含恶意 HTML 理论上可触发 XSS | LLM 受 Prompt 约束 + RuleEngine 验证；CR-039 已登记，后续迭代增加 DOMPurify |

## 退回规则

- 发布条件不完整退回 PL。
- 安全问题退回 Security。
- 构建或运行失败退回对应实现 Agent 或 PL。

## 完成标准

- 发布计划有步骤、回滚方案和监控方案；部署记录有版本、环境和实际执行结果。
- 监控或验证结果可追踪。
- Release 证据、部署步骤、健康检查和回滚记录能沿验收追踪链回到对应 AC；发布失败时能按失败倒查链定位最早断链环节。

## Ops 确认

| 项 | 确认人 | 日期 | 结论 |
| --- | --- | --- | --- |
| CI/CD 证据已审查 | ops (Cat01-op) | 2026-09-16T18:00+08:00 | ✅ 33/35 BE + 18/18 FE passed，2 env errors 非 business failure |
| Delivery E2E 证据已审查 | ops (Cat01-op) | 2026-09-16T18:00+08:00 | ✅ 5/5 passed, Mock API=no |
| Browser E2E 证据已审查 | ops (Cat01-op) | 2026-09-16T18:00+08:00 | ✅ 7/9 passed, BUG-002 非业务缺陷, CEO C2 满足 |
| 安全审查证据已审查 | ops (Cat01-op) | 2026-09-16T18:00+08:00 | passed, 3 项低风险建议不阻塞 |
| 回滚方案可执行 | ops (Cat01-op) | 2026-09-16T18:00+08:00 | ✅ git revert + docker compose rebuild, 无 DB 变更 |
| 监控方案已就绪 | ops (Cat01-op) | 2026-09-16T18:00+08:00 | ✅ Docker healthcheck + SSE 冒烟 + 日志监控 + 告警方案 |
| Nginx SSE 配置提醒 | ops (Cat01-op) | 2026-09-16T18:00+08:00 | ⚠️ DEV 不受影响，生产部署前必须补充 |
| 发布计划结论 | ops (Cat01-op) | 2026-09-16T18:00+08:00 | **Ready — 待 PL 执行 gate readiness 检查后可写 deploy-record** |
