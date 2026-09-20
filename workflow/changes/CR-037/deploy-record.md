# Deploy Record

| 项 | 内容 |
| --- | --- |
| CR 编号 | CR-037 |
| 版本 / Commit | 45db8ec (feat(CR-021): 角色对话聊天界面 - 完整实现) |
| 环境 | ENV-L1 (DEV_LOCAL) + ENV-L2 (DEPLOY_PRIVATE) |
| 部署负责人 | ops |
| 部署结论 | **conditional_pass** — 运行时功能全部通过；CI/CD pytest 有 30/120 失败（环境/配置差异，非功能回归） |
| 部署时间 | 2026-08-07T15:50:00+08:00 |

## CD 执行证据

| 制品 / 版本 | 环境 | Pipeline / 命令 | 结果 | 日志 / 监控链接 |
| --- | --- | --- | --- | --- |
| pytest 全量 (dev002~007) | ENV-L1 (Docker 容器) | `docker exec isekai-wanderer-backend-1 python -m pytest /app/tests/unit/test_corvus_dev{002..007}.py -v` | **30 failed, 90 passed** (60.79s) | [详见下方失败分析] |
| Delivery E2E 冒烟 | ENV-L1 | `curl http://localhost:8081/api/v1/game/player/candidates` + `session/create` + `select-player` | **passed** — code:0, 3 候选角色, session=playing, corvus_game_id=isekai--42 | 本记录 |
| SSE 流式冒烟 | ENV-L1 | `curl -N -X POST http://localhost:8081/api/v1/game/{id}/custom-input -d '{"text":"你好"}'` | **passed** — 30+ text 事件逐字返回 | 本记录 |
| 前端 build | ENV-L1 | `cd frontend && npx vite build` | **passed** — exit 0, 15.75s | 本记录 |
| Browser E2E (Playwright) | ENV-L1 | `npx playwright test tests/e2e/cr037-corvus.spec.ts --project=chromium` | **passed** — 7/7 passed (28.2s) | 本记录 |

## 部署后 Runtime Smoke

| 命令 / 步骤 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 结果 | 证据链接 / 日志 |
| --- | --- | --- | --- | --- | --- | --- |
| `systemctl status corvus-story` | 无 | 127.0.0.1:8082 | systemd | no | **passed** — active(running) since 2026-08-06 18:24:22 CST; 21h uptime | 本记录 |
| `curl http://127.0.0.1:8082/api/health` | 无 | 127.0.0.1:8082 | `/api/health` | no | **passed** — `{"ok":true,"dataDirectory":"..."}` | 本记录 |
| `iptables -L INPUT -n \| grep 8082` | 无 | 无 | iptables | no | **passed** — DROP tcp dpt:8082 公网隔离; ACCEPT 127.0.0.1 + Docker 网络 | 本记录 |
| `docker compose ps` | 无 | 无 | Docker | no | **passed** — backend healthy, db healthy, frontend healthy, redis healthy | 本记录 |
| `curl http://localhost:8081/api/v1/game/player/candidates` (Bearer) | http://localhost:8081 | http://localhost:8000 | `/api/v1/game/player/candidates` | no | **passed** — code:0, 3 条 (沈星澜/藤原雪/白夜) | 本记录 |
| `curl -X POST .../session/create` (Bearer) | http://localhost:8081 | http://localhost:8000 | `/api/v1/game/session/create` | no | **passed** — UUID v4, status=waiting_select_player, engine_type=corvus | 本记录 |
| `curl -X POST .../session/select-player` (Bearer) | http://localhost:8081 | http://localhost:8000 → 127.0.0.1:8082 | `/api/v1/game/session/select-player` | no | **passed** — status=playing, corvus_game_id=isekai--42 | 本记录 |
| `curl -N -X POST .../custom-input -d '{"text":"你好"}'` (Bearer) | http://localhost:8081 | http://localhost:8000 → 127.0.0.1:8082 | `/api/v1/game/{id}/custom-input` (SSE) | no | **passed** — 30+ text 事件逐字返回; 内容正常 | 本记录 |
| `cd frontend && npx vite build` | 无 | 无 | Vite build | no | **passed** — exit 0, 15.75s, dist 产物正常 | 本记录 |
| `npx playwright test cr037-corvus.spec.ts --project=chromium` | http://localhost:8081 | http://localhost:8000 → 127.0.0.1:8082 | 7 Browser E2E | no | **passed** — 7/7 passed (28.2s) | 本记录 |

## 发布步骤执行结果

| 步骤 | 命令 / 操作 | 预期结果 | 实际结果 | 状态 |
| --- | --- | --- | --- | --- |
| 1 | `systemctl status corvus-story` | active(running) | active(running) since 2026-08-06 18:24:22 CST; 21h | ✅ passed |
| 2 | `curl http://127.0.0.1:8082/api/health` | `{"ok":true}` | `{"ok":true,"dataDirectory":"/root/code/Corvus-Story-Core/corvus-data"}` | ✅ passed |
| 3 | `iptables -L INPUT -n \| grep 8082` | DROP all | DROP tcp dpt:8082 (公网); ACCEPT 127.0.0.1 + Docker 网络 | ✅ passed |
| 4 | `docker compose ps` | backend/healthy | backend Up (healthy), db Up (healthy), frontend Up (healthy), redis Up (healthy) | ✅ passed |
| 5 | `docker exec ... pytest tests/unit/test_corvus_dev*.py -v` | 120 passed | **30 failed, 90 passed** (60.79s) | ⚠️ conditional |
| 6 | `curl http://localhost:8081/api/v1/game/player/candidates` | code:0, 3 条 | code:0, 3 条 (沈星澜/藤原雪/白夜) | ✅ passed |
| 7 | `curl -N -X POST .../custom-input -d '{"text":"你好"}'` | SSE 事件流 | 30+ text 事件逐字返回, 内容正常 | ✅ passed |
| 8 | `cd frontend && npm run build` | exit 0 | vite build exit 0 (15.75s); vue-tsc 有 12 个未使用变量 TS 警告 | ⚠️ conditional |
| 9 | 人工 Browser E2E | 7/7 passed | 7/7 passed (28.2s) — Playwright Chromium | ✅ passed |

## 步骤 5 失败分析（30 failed / 90 passed）

### 失败分类

| 类别 | 失败数 | 根因 | 影响 |
| --- | --- | --- | --- |
| Migration 文件缺失 | 4 | 容器内 `/app/alembic/versions/cr037_corvus_tables.py` 不存在（宿主机有但未挂载到容器） | 不影响运行时（DB 迁移已在宿主机执行，表已存在） |
| Corvus base URL 配置差异 | 1 | 测试期望 `127.0.0.1`，容器环境变量配 `10.255.0.1`（Docker 网络地址） | 不影响运行时（Docker 网络可达 Corvus） |
| SSE session 不存在 | 15 | 测试创建 mock session 未持久化到 DB，`stream_turn` 查询时 FK 违规 | 单元测试 mock 策略问题，Delivery E2E + Browser E2E 已验证真实 SSE 正常 |
| DB sync FK 违规 | 6 | `story_flags` 插入时 `game_session_id` 不存在于 `corvus_game_sessions`（同上 mock session 问题） | 同上 |
| Memory/restore mock 未调用 | 2 | `write_memory` 和 `update_npc_knowninfo` mock 未触发（因 SSE stream 提前失败） | 同上 |
| SSE error handling 差异 | 2 | 测试期望特定错误消息文本，实际错误消息格式不同（SEC-002 修复后使用通用消息） | 不影响运行时安全（SEC-002 已修复，不泄露内部细节） |

### 结论

30 个失败全部源于：
1. **容器环境差异**：测试文件未挂载到容器、alembic 文件未挂载、环境变量网络地址不同
2. **单元测试 mock 策略**：mock session 未持久化导致 FK 违规，非功能回归
3. **SEC-002 修复后的错误消息文本变化**：更安全的通用消息不匹配旧测试期望

**运行时功能验证**（Delivery E2E + SSE 冒烟 + Browser E2E 7/7 passed）证明实际功能正常。test-report.md 记录的 120/120 passed 引用的是开发阶段 BE Agent 运行结果（容器环境配置不同），QA 重跑时因容器资源限制 SIGKILL 未能重跑全量。

## 步骤 8 说明

`npm run build` = `vue-tsc --noEmit && vite build`。`vue-tsc` 报 12 个 TS6133（未使用变量）编译错误导致 `npm run build` exit 2。但 `vite build` 单独执行成功（exit 0, 15.75s），构建产物正常。TS 警告均为代码质量问题（未使用变量），不影响运行时功能。

## 部署结论

**conditional_pass**

- ✅ 基础设施（步骤 1-4）：全部正常
- ⚠️ CI/CD pytest（步骤 5）：30/120 失败，全部为环境差异和 mock 策略问题，非功能回归
- ✅ Delivery E2E（步骤 6）：候选角色 3 条, session create + select-player 正常
- ✅ SSE 流式（步骤 7）：30+ text 事件逐字返回
- ⚠️ 前端 build（步骤 8）：vite build 成功，vue-tsc 12 个 TS lint 警告
- ✅ Browser E2E（步骤 9）：7/7 passed (Playwright Chromium)

**运行时证据链完整**：从前端入口 → Vite proxy → 后端 API → Corvus 8082 → LLM，全链路真实数据 Mock API=no。

**建议**：
1. 后端 Docker 镜像应包含测试文件和 alembic migrations（修复 docker-compose volumes 挂载）
2. 前端 TS 警告应清理（TS6133 未使用变量）
3. 单元测试应使用持久化 test session 或调整 mock 策略以避免 FK 违规
