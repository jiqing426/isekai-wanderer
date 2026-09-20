# Security Review: CR-038 — Corvus 前端入口接入

| 项 | 内容 |
|---|---|
| 审查结论 | ✅ PASS — 7 项审查全 PASS，无阻塞，无高风险项 |
| CR ID | CR-038 |
| Security Agent | Cat01-security |
| Execution Date | 2026-09-03T15:00:00+08:00 |
| Environment | ENV-L1 (DEV_LOCAL) — Docker 容器全 healthy |
| Mock API | no — 审查基于真实 Docker 后端 + 真实 Corvus 服务 |

---

## 1. 审查范围

| # | 审查项 | 来源 |
|---|---|---|
| 1 | 前端 Corvus 会话创建流程（game.ts startGame 改造、SSE 分支激活） | PL 触发信 |
| 2 | 角色候选管理 API（POST /game/player/candidates CRUD） | PL 触发信 |
| 3 | GET /scripts 新增 engine_type 字段 | PL 触发信 |
| 4 | SSE 流式叙事端到端透传 | PL 触发信 |
| 5 | 会话恢复 legacy/corvus 分流逻辑 | PL 触发信 |
| 6 | Runtime Contract 安全一致性（frontend 8081 / backend 8000 / Docker / proxy） | PL 触发信 |
| 7 | CR-037 遗留安全问题（公网 8082 iptables、config.json 权限 600、SSE 错误通用化） | PL 触发信 |

---

## 2. 文件审查清单

| 文件 | 路径 | 状态 |
|---|---|---|
| 安全契约 | `docs/security/security.md` | ✅ 已读 — CR-038 Additions 已记录 |
| API 契约 | `docs/api/api.md` | ✅ 已读 — 67 端点 + JWT + 错误码 + SSE |
| Runtime 契约 | `docs/runtime/runtime-contract.md` | ✅ 已读 — CR-038 Additions 已记录 |
| 追踪链 | `workflow/traceability-chain.md` | ✅ 已读 |
| 倒查链 | `workflow/failure-backtrace.md` | ✅ 已读 |
| 变更说明 | `workflow/changes/CR-038/change.md` | ✅ 已读 |
| 验收矩阵 | `workflow/changes/CR-038/acceptance.md` | ✅ 已读 — 25 AC 全 Verified + covered |
| 测试报告 | `workflow/changes/CR-038/test-report.md` | ✅ 已读 — QA 第三轮 25/25 PASSED, Mock API=no |
| 审查记录 | `workflow/changes/CR-038/review.md` | ✅ 已读 — INTEGRATION passed, QA 25/25 |
| 发布计划 | `workflow/changes/CR-038/deploy-plan.md` | ❌ 不存在 |
| 环境示例 | `.env.example` | ✅ 已读 |
| 前端源码 | `frontend/src/stores/game.ts` | ✅ 已审查 |
| 前端组件 | `frontend/src/components/PlayerCandidateModal.vue` | ✅ 已审查 |
| 后端源码 | `backend/app/api/v1/game.py` | ✅ 已审查 |
| 后端源码 | `backend/app/api/v1/scripts.py` | ✅ 已审查 |
| 后端服务 | `backend/app/services/corvus_adapter.py` | ✅ 已审查 |
| Docker 配置 | `docker-compose.yml` | ✅ 已审查 |
| Vite 配置 | `frontend/vite.config.ts` | ✅ 已审查 |
| systemd 服务 | `/etc/systemd/system/corvus-story.service` | ✅ 已审查 |
| iptables 规则 | INPUT 链 8082 端口 | ✅ 已审查 |
| Corvus 配置 | `/root/code/Corvus-Story-Core/corvus-data/config.json` | ✅ 已审查（权限 600） |
| .gitignore | `/root/isekai-wanderer/.gitignore` | ✅ 已审查 |

---

## 3. 逐项安全审查

### 3.1 前端 Corvus 会话创建流程（game.ts startGame 改造、SSE 分支激活）

| 检查项 | 结论 | 证据 |
|---|---|---|
| startGame 是否正确写入 engine_type | ✅ PASS | `game.ts:174`: `engine_type: 'corvus'` 硬编码写入 currentSession；legacy 分支 `game.ts:201`: `engine_type: 'legacy'` |
| startGame Corvus 分支调用 POST /game/session/create | ✅ PASS | `game.ts:157`: 调用 `POST /game/session/create`，返回 game_session_id |
| SSE 分支条件判断 | ✅ PASS | `game.ts:305`: `const isCorvus = currentSession.value.engine_type === 'corvus'`; `game.ts:452`: submitCustomInput 同样判断 |
| engine_type 字段必填（无 ? 可选标记） | ✅ PASS | `game.ts:13`: `engine_type: 'legacy' \| 'corvus'`（Script interface 必填）；`game.ts:76`: `engine_type: 'legacy' \| 'corvus'`（GameSession interface 必填） |
| 前端不可直接请求 Corvus 8082 | ✅ PASS | `grep -rn '8082' frontend/src/` 无结果；前端只通过后端 SSE 代理访问 Corvus |
| engine_type 不接受外部参数 | ✅ PASS | startGame() 不接受 engine_type 参数，硬编码为 'corvus'（C3 约束）；resumeSession 从后端 API 响应读取 |

**结论: PASS** — 前端会话创建流程安全，engine_type 硬编码不可篡改，前端不可直接访问 Corvus 服务。

### 3.2 角色候选管理 API（POST /game/player/candidates CRUD）

| 检查项 | 结论 | 证据 |
|---|---|---|
| POST /game/player/candidates 需要 Bearer 认证 | ✅ PASS | `game.py:2251`: `user_id: str = Depends(get_current_user_id)` — FastAPI Bearer Token 中间件 |
| name 字段必填 + 长度限制 | ✅ PASS | `game.py` Pydantic schema: `name: str = Field(..., max_length=100, description="角色名字（必填，≤100字符）")` — `Field(...)` 表示必填 |
| 角色候选创建有 ≤3 数量限制 | ✅ PASS | `game.py`: 查询 `SELECT count(*) FROM player_candidates WHERE user_id = ?`; 若 `current_count >= 3` 返回 400 `CANDIDATE_LIMIT_EXCEEDED` |
| GET /game/player/candidates 只返回当前用户候选 | ✅ PASS | `game.py:2211`: `Depends(get_current_user_id)` + `WHERE user_id = ?`; 无批量枚举端点 |
| initial_inventory 不接受用户输入 | ✅ PASS | `PlayerCandidateCreate` schema 只含 name/personality/backstory/appearance；initial_inventory 由后端管理 |
| 前端表单 name 为空不发送请求 | ✅ PASS | Browser E2E AC-038-014 PASSED: 不填 name → 提交 → 错误提示显示（不发送 API 请求） |
| 前端 Vue 模板转义渲染（防 XSS） | ✅ PASS | `PlayerCandidateModal.vue` 使用 `{{ candidate.name }}`、`{{ candidate.personality }}`、`{{ candidate.backstory }}` — Vue `{{ }}` 双花括号默认 HTML 转义；无 `v-html` 使用 |
| 跨用户数据泄露 | ✅ PASS | GET 端点 WHERE user_id 过滤；POST 端点 user_id 从 JWT 提取；无跨用户查询 |

**结论: PASS** — 角色候选管理 API 安全：认证、授权、数量限制、输入校验、XSS 防护均完整。

### 3.3 GET /scripts 新增 engine_type 字段

| 检查项 | 结论 | 证据 |
|---|---|---|
| engine_type 作为运行时虚拟字段返回 | ✅ PASS | `scripts.py:132`: `"engine_type": "corvus"` 硬编码返回；不持久化到 DB |
| 所有剧本统一返回 engine_type='corvus' | ✅ PASS | Delivery E2E DEL-038-002: 3 个剧本全部返回 `engine_type: "corvus"`（星辰之约/星月奇缘/樱花恋曲） |
| GET /scripts/{id} 也返回 engine_type | ✅ PASS | `scripts.py:446`: `"engine_type": "corvus"`；单元测试 test_get_script_detail_has_engine_type PASSED |
| engine_type 不从用户输入接受 | ✅ PASS | GET 端点无请求体；engine_type 在后端硬编码 |

**结论: PASS** — GET /scripts engine_type 字段安全，后端硬编码，不接受外部篡改。

### 3.4 SSE 流式叙事端到端透传

| 检查项 | 结论 | 证据 |
|---|---|---|
| SSE 代理通过后端 StreamingResponse | ✅ PASS | `game.py`: `StreamingResponse(event_generator(), media_type="text/event-stream")` — 后端作为 SSE 代理 |
| SSE 错误事件不泄露内部细节 | ✅ PASS | `corvus_adapter.py:332`: `yield f"data: {json.dumps({'type': 'error', 'message': 'Corvus 服务连接失败，请重试'}, ensure_ascii=False)}\n\n"`; `corvus_adapter.py:335`: `yield f"data: {json.dumps({'type': 'error', 'message': '服务器内部错误，请重试'}, ensure_ascii=False)}\n\n"` — 错误消息通用化，不暴露堆栈/异常详情 |
| SSE 连接有会话所有权验证 | ✅ PASS | `game.py`: `await _verify_session_ownership(UUID(session_id), user_id, db)` 在 SSE 端点调用前执行 |
| SSE 流不暴露 Corvus 内部 API | ✅ PASS | Corvus SSE 事件经 `SSETranslator` / `CorvusAdapter` 转换格式后输出；前端不直接接触 Corvus 原始 API |
| Nginx/Vite proxy 支持 SSE（proxy_buffering off） | ✅ PASS | Runtime Contract 记录 Nginx: `proxy_buffering off; proxy_cache off; proxy_read_timeout 300s`; Vite dev proxy 支持 SSE |
| SSE 响应头正确 | ✅ PASS | `Cache-Control: no-cache`, `Connection: keep-alive`, `X-Accel-Buffering: no` — 防止缓冲/缓存 |
| 向量记忆不通过 SSE 返回前端 | ✅ PASS | `corvus_adapter.py`: embedding 向量仅用于 KNN 计算，SSE 只输出 text/done/gm_update/error 事件 |

**结论: PASS** — SSE 流式透传安全：错误消息通用化、会话所有权验证、Corvus 内部 API 隔离、向量数据不泄露。

### 3.5 会话恢复 legacy/corvus 分流逻辑

| 检查项 | 结论 | 证据 |
|---|---|---|
| resumeSession 从后端 API 读取 engine_type | ✅ PASS | `game.ts:599-611`: `GET /game/{sessionId}` 返回 `engine_type` 字段；`game.ts:611`: `const engineType = (sessionData as any).engine_type \|\| 'legacy'` |
| 旧数据兼容（无 engine_type → legacy） | ✅ PASS | `game.ts:611`: `|| 'legacy'` 默认值 — 旧 localStorage 数据无 engine_type 时默认走 legacy 分支 |
| engine_type 不从前端请求参数接受 | ✅ PASS | resumeSession(sessionId) 只接受 sessionId 参数；engine_type 从 API 响应读取 |
| Corvus 会话恢复后走 SSE 分支 | ✅ PASS | `game.ts:638`: `if (engineType === 'corvus' && sessionData.status === 'playing')` — Corvus 恢复走 SSE |
| 会话恢复有所有权验证 | ✅ PASS | 后端 `GET /game/{session_id}` 调用 `_verify_session_ownership` |

**结论: PASS** — 会话恢复分流安全：engine_type 从后端读取不可篡改，旧数据兼容降级为 legacy，所有权验证完整。

### 3.6 Runtime Contract 安全一致性

| 检查项 | 契约值 | 实际值 | 一致 |
|---|---|---|---|
| frontend_origin | http://localhost:8081 | Docker 容器 8081 (Vite) | ✅ |
| backend_origin | http://localhost:8000 | Docker 容器 8000 (Uvicorn) | ✅ |
| api_base_path | /api/v1 | /api/v1 | ✅ |
| vite_proxy_target | http://localhost:8000 | Docker backend:8000 | ✅ |
| health_endpoint | /api/v1/health | `{"status":"ok","version":"1.0.0"}` | ✅ |
| CORS allowed origins | ${CORS_ORIGINS} (default http://localhost:8081) | `.env.example`: `CORS_ORIGINS=http://localhost:8081,http://localhost:3100` | ✅ |
| Docker 容器隔离 | backend/db/frontend/redis 各自容器 | `docker compose ps` 全 Up (healthy) | ✅ |
| SSE proxy 配置 | Nginx proxy_buffering off + Vite proxy | Nginx example 有 `proxy_buffering off`; Vite proxy 默认支持 | ✅ |
| 前端不暴露 Corvus 8082 | 8082 不在 Nginx/Vite proxy 中 | `grep 8082 frontend/` 无结果; Vite proxy 只代理 /api → backend:8000 | ✅ |
| Backend 不开启 --reload | docker-compose: `uvicorn ... --host 0.0.0.0 --port 8000` (无 --reload) | 实际运行一致 | ✅ (BUG-038-007 P2 已知, 非阻塞) |

**结论: PASS** — Runtime Contract 全部一致。端口、proxy、CORS、Docker 隔离均正确配置。

### 3.7 CR-037 遗留安全问题

| # | 遗留安全问题 | 状态 | 证据 |
|---|---|---|---|
| 1 | 公网 8082 iptables DROP | ✅ PASS | `iptables -L INPUT -n`: `ACCEPT tcp 127.0.0.1 dpt:8082`; `ACCEPT tcp 172.17.0.0/16 dpt:8082`; `ACCEPT tcp 172.18.0.0/16 dpt:8082`; `DROP tcp 0.0.0.0/0 dpt:8082` — 公网 DROP 生效，仅本机 + Docker 网段可访问 |
| 2 | config.json 权限 600 | ✅ PASS | `ls -la /root/code/Corvus-Story-Core/corvus-data/config.json`: `-rw------- 1 root root` — 权限 600，仅 root 可读写 |
| 3 | SSE 错误通用化 | ✅ PASS | `corvus_adapter.py:332`: `'Corvus 服务连接失败，请重试'`; `corvus_adapter.py:335`: `'服务器内部错误，请重试'` — 不泄露异常类型/堆栈/内部路径 |

**附加发现**:

| # | 检查项 | 结论 | 详情 |
|---|---|---|---|
| 4 | Corvus systemd 服务绑定地址 | ⚠️ 注意 | `systemd service`: `Environment=HOST=0.0.0.0` — 服务监听 0.0.0.0:8082，但 iptables DROP 规则补偿了公网暴露风险。**非阻塞**，但建议未来改为 `HOST=127.0.0.1` |
| 5 | Corvus config.json 含 API-Key | ✅ PASS | `config.json` 含 `apiKey: "sk-6Ni…dDHQ"` — 但文件权限 600 + .gitignore 排除 + iptables 隔离 + 后端不经手 API-Key（CR-037 设计）。`.env` 也含 `LLM_API_KEY` 但 .gitignore 排除 `.env` |
| 6 | .env 文件安全 | ✅ PASS | `.gitignore` 排除 `.env`/`.env.*`/`*.pem`/`*.key`/`*.crt`; `.env.example` 使用占位符 (`change…only`, `test-k…lder`, `***`) 无真实密钥 |
| 7 | .env.example 无真实密钥泄露 | ✅ PASS | `POSTGRES_PASSWORD=***`, `JWT_SECRET=change…only`, `LLM_API_KEY=test-k…lder` — 全部为占位符 |

---

## 4. 发布证据安全审查

### 4.1 测试分类验证

| 测试类型 | 契约要求 | 实际状态 | 结论 |
|---|---|---|---|
| CI/CD 单元测试 | 禁止 mock API | 6/6 PASSED (test_scripts_engine_type + test_player_candidates_create), Mock API=no | ✅ PASS |
| 前端编译检查 | npm run build exit 0 | exit 0, ✓ built in 15.64s | ✅ PASS |
| Delivery E2E / Runtime Smoke | Mock API=no, 真实前后端 | 7/7 PASS (health + scripts engine_type + candidates CRUD + npm build), Docker 全 healthy | ✅ PASS |
| Browser Interaction E2E | Mock API=no, 真实浏览器用户动作 | 17/17 passed (chromium), 真实 Corvus 服务 + 真实后端 + 真实 PostgreSQL + pgvector | ✅ PASS |

### 4.2 Mock 策略验证

| 检查项 | 结论 |
|---|---|
| Delivery E2E 记录 Mock API=no | ✅ PASS — `test-report.md` 第 11.2 节全部标注 Mock API=no |
| Browser Interaction E2E 记录 Mock API=no | ✅ PASS — `test-report.md` 第 11.3 节标注 Mock API=no |
| 无 mock API、fixture server、MSW、静态假数据作为发布证据 | ✅ PASS — 全部使用真实 Docker 后端 + 真实 Corvus 服务 |
| 无未记录数据源 | ✅ PASS — 所有数据来源为 PostgreSQL + pgvector + Redis + Corvus 文件存储，均有契约记录 |

### 4.3 可追溯链验证

| 链路段 | 状态 | 说明 |
|---|---|---|
| PRD → REQ | ✅ | 10 REQ (REQ-CAP-001~003 + REQ-FE-001~007) 全有 PRD 来源 |
| REQ → AC | ✅ | 25 AC 全有 REQ 编号 |
| AC → Design | ✅ | 25 AC 全有设计落点 |
| Design → Task | ✅ | 8 任务 (2 BE + 6 FE) 全有 owner + AC 绑定 |
| Task → Code | ✅ | 实际改动文件在 allowed_write_scope 内 |
| Code → Test | ✅ | 6 单元测试 + 17 Browser E2E + 4 Delivery E2E |
| Test → Red/Green | ✅ | PL 建立 Red 基线 (5/34) → QA 三轮 → 25/25 PASSED |
| Green → Acceptance | ✅ | 25 AC 全 Verified + covered |
| Acceptance → QA | ✅ | QA 独立复核 25/25 PASSED |
| QA → Release | ✅ | Mock API=no, Browser E2E + Delivery E2E 全通过 |

**断链处理**: 无断链。所有 P0/P1 AC 从 PRD 到测试证据全链路可追溯。

---

## 5. 权限拒绝、敏感操作和审计路径审查

| 检查项 | 结论 | 证据 |
|---|---|---|
| 未认证访问保护 | ✅ PASS | 所有 /game/* 端点 `Depends(get_current_user_id)` — Bearer Token 中间件 |
| 会话所有权验证 | ✅ PASS | `_verify_session_ownership` 在 SSE/choice/custom-input/free-chat 端点调用 |
| 角色候选跨用户访问 | ✅ PASS | GET WHERE user_id 过滤; POST user_id 从 JWT 提取 |
| 角色候选数量限制 | ✅ PASS | ≤3 限制在后端执行, 返回 400 CANDIDATE_LIMIT_EXCEEDED |
| admin 端点权限 | ✅ PASS | CR-027 lorebook/scene-config 端点 `users.is_admin=True`; 非 admin 返回 403 (本 CR 不涉及新 admin 端点) |
| 敏感操作审计 | ✅ PASS | Corvus 会话创建/选角/游戏回合有 logger 记录; SSE 错误有 exc_info=True 日志 |
| 日志脱敏 | ✅ PASS | 邮箱 masked; JWT token never logged; 密码 bcrypt hash never logged; LLM API-Key 不经后端 |
| 数据保留 | ✅ PASS | Corvus 文件存储为会话内 JSON/JSONL, 用完即弃; PostgreSQL 主数据; pgvector 向量记忆按 user_id + character_id 隔离 |

---

## 6. 依赖、容器和部署配置审查

| 检查项 | 结论 | 证据 |
|---|---|---|
| Docker 容器隔离 | ✅ PASS | 4 容器 (backend/db/frontend/redis) 各自独立; healthcheck 全 healthy |
| Docker 端口暴露 | ✅ PASS | backend:8000, frontend:8081, db:5432, redis:6379 — 仅本机映射; Corvus 8082 不在 Docker 中 |
| Corvus 8082 公网隔离 | ✅ PASS | iptables: 127.0.0.1 ACCEPT, Docker 网段 ACCEPT, 0.0.0.0/0 DROP |
| config.json 权限 | ✅ PASS | `-rw-------` (600) root:root |
| .env 文件安全 | ✅ PASS | .gitignore 排除; .env.example 使用占位符 |
| 依赖版本固定 | ✅ PASS | `pyproject.toml` 固定版本; `package-lock.json` 固定前端依赖 |
| deploy-plan.md | ⚠️ 注意 | `workflow/changes/CR-038/deploy-plan.md` 不存在 — **非 SECURITY 阻塞项**，属 PL/Ops 交付物; Security 审查基于当前运行时配置（docker-compose.yml + systemd + iptables） |

---

## 7. 高风险事项评估

| # | 风险项 | 等级 | 状态 | 责任人 | 修复路径 |
|---|---|---|---|---|---|
| 1 | Corvus systemd 绑定 0.0.0.0:8082 | 中 | ⚠️ 已补偿 | Ops | iptables DROP 已补偿公网风险; 建议未来改 `HOST=127.0.0.1` (非阻塞, 不影响本 CR 发布) |
| 2 | deploy-plan.md 不存在 | 低 | 📋 待 PL 补 | PL | 发布计划属 PL 交付物, 不阻塞安全审查 (本审查基于运行时配置直接检查) |
| 3 | Docker backend 无 --reload | 低 | ✅ 已知 | Ops | BUG-038-007 P2, Ops 已 acked, 非阻塞 |
| 4 | 无新增高风险项 | — | ✅ | — | 本 CR 未引入新的密钥、权限、数据暴露或攻击面 |

**人工确认需求**: 无。本 CR 未涉及生产、支付、数据删除等高风险操作，不需要人工确认。

---

## 8. 安全审查检查清单

| 检查项 | 结论 | 详情 |
|---|---|---|
| 是否提交真实密钥/token/证书/密码/生产数据 | ✅ 未提交 | .env.example 全占位符; .env 被 .gitignore 排除; config.json 权限 600 + gitignored |
| 鉴权、授权、审计和敏感操作确认是否完整 | ✅ 完整 | Bearer Token + 会话所有权验证 + 候选数量限制 + 日志审计 |
| 敏感字段、隐私、日志脱敏和数据保留是否清楚 | ✅ 清楚 | 邮箱 masked, JWT/密码/API-Key never logged, Corvus 数据用完即弃 |
| API/DB/Runtime/Mock 策略是否一致, 无未记录数据源或 mock 发布证据 | ✅ 一致 | Runtime Contract 全一致; Mock API=no 全部; 无 mock/fixture/MSW 作为发布证据 |
| test-report.md 是否区分 CI/CD、Delivery E2E / Runtime Smoke 和 Browser Interaction E2E | ✅ 区分 | 三类测试独立记录: CI/CD (6 单元 + npm build), Delivery E2E (7/7), Browser E2E (17/17) |
| 依赖、容器和部署配置是否存在明显风险 | ✅ 无明显风险 | Docker 隔离 + iptables + config.json 600 + .gitignore; Corvus 0.0.0.0 已被 iptables 补偿 |
| 安全相关验收项是否在 acceptance.md 有验证结论 | ✅ 有 | 25 AC 全 Verified + covered; 安全相关 AC (001-006 候选安全, 007-008 编译, 021 会话恢复) 全 PASSED |
| 高风险事项是否需要人工确认 | ✅ 不需要 | 无生产/支付/数据删除风险 |

---

## 9. CR-038 安全检查清单验证

| 检查项 | 结论 | 证据 |
|---|---|---|
| POST /game/player/candidates 端点有 Bearer 认证 | ✅ PASS | `Depends(get_current_user_id)` |
| 角色候选创建有 ≤3 数量限制 | ✅ PASS | `current_count >= 3` → 400 CANDIDATE_LIMIT_EXCEEDED |
| name 字段有 Pydantic 必填 + 长度校验 | ✅ PASS | `name: str = Field(..., max_length=100)` |
| 前端表单 name 为空时不发送 API 请求 | ✅ PASS | Browser E2E AC-038-014 PASSED |
| 前端 Vue 模板转义渲染候选字段（防 XSS） | ✅ PASS | `{{ candidate.name }}` / `{{ candidate.personality }}` / `{{ candidate.backstory }}` — Vue 默认转义, 无 v-html |
| localStorage 旧数据兼容不影响 Corvus 流程安全 | ✅ PASS | 旧数据默认 'legacy' → legacy 分支; 不影响 Corvus 流程 |

---

## 10. 追踪链安全审查

### 10.1 安全相关 AC 追踪

| AC | REQ | 设计落点 | Task | 测试证据 | 发布证据 | 追踪状态 |
|---|---|---|---|---|---|---|
| AC-038-001 (GET /scripts engine_type) | REQ-CAP-001 | scripts.py 虚拟字段 | T-038-BE-001 | 单元测试 PASSED + Delivery E2E | Mock API=no | ✅ 完整 |
| AC-038-003 (POST candidates name 必填) | REQ-CAP-002 | game.py Pydantic 校验 | T-038-BE-002 | 单元测试 PASSED + Delivery E2E | Mock API=no | ✅ 完整 |
| AC-038-004 (无 name → 400/422) | REQ-CAP-002 | Pydantic Field 必填 | T-038-BE-002 | 单元测试 PASSED (422) + Delivery E2E | Mock API=no | ✅ 完整 |
| AC-038-005 (≤3 限制) | REQ-CAP-002 | game.py 数量校验 | T-038-BE-002 | 单元测试 PASSED (400) + Delivery E2E | Mock API=no | ✅ 完整 |
| AC-038-007 (Script interface engine_type 必填) | REQ-FE-001 | stores/game.ts interface | T-038-FE-001 | npm run build exit 0 | CI/CD | ✅ 完整 |
| AC-038-008 (GameSession engine_type 必填) | REQ-FE-002 | stores/game.ts interface | T-038-FE-001 | npm run build exit 0 | CI/CD | ✅ 完整 |
| AC-038-021 (会话恢复 Corvus) | REQ-FE-006 | game.ts resumeSession | T-038-FE-005 | Browser E2E PASSED | Mock API=no | ✅ 完整 |
| AC-038-022 (旧数据兼容 legacy) | REQ-FE-006 | game.ts 默认 'legacy' | T-038-FE-005 | Browser E2E PASSED | Mock API=no | ✅ 完整 |

### 10.2 倒查链验证

| 检查项 | 结论 |
|---|---|
| 发布证据是否使用真实 API/后端/数据源 | ✅ 是 — Docker 真实后端 + 真实 Corvus + 真实 PostgreSQL + pgvector |
| Browser Interaction E2E 记录 Mock API=no | ✅ 是 — test-report.md 第 11.3 节 |
| Delivery E2E / Runtime Smoke 记录 Mock API=no | ✅ 是 — test-report.md 第 11.2 节 |
| 无 mock/fixture/MSW/静态假数据作为发布证据 | ✅ 是 |
| 无未记录数据源 | ✅ 是 |
| 无权限绕过 | ✅ 是 — Bearer Token + 会话所有权验证全链路 |
| 无敏感信息泄露 | ✅ 是 — SSE 错误通用化 + 日志脱敏 + API-Key 隔离 |

---

## 11. 安全审查结论

### 总体结论: ✅ PASS

CR-038 安全审查通过。

**审查覆盖**:
- 前端 game.ts startGame/resumeSession/SSE 分支：engine_type 硬编码不可篡改
- 后端 POST /game/player/candidates：Bearer 认证 + Pydantic 校验 + ≤3 限制 + 用户隔离
- GET /scripts engine_type：后端虚拟字段硬编码返回
- SSE 流式透传：错误通用化 + 会话所有权验证 + Corvus API 隔离
- 会话恢复分流：engine_type 从后端读取 + 旧数据降级 legacy
- Runtime Contract：端口/proxy/CORS/Docker 全一致
- CR-037 遗留安全：iptables 8082 DROP ✅ + config.json 600 ✅ + SSE 错误通用化 ✅

**发布证据安全验证**:
- CI/CD: 6 单元测试 PASSED + npm run build exit 0
- Delivery E2E: 7/7 PASS, Mock API=no
- Browser Interaction E2E: 17/17 passed, Mock API=no
- 无 mock/fixture/MSW/未记录数据源作为发布证据

**追踪链**: 安全相关 AC 从 PRD → REQ → AC → Design → Task → Code → Test → Release 全链路可追溯，无断链。

**高风险事项**: 无新增高风险项。Corvus systemd 0.0.0.0 绑定已被 iptables 补偿（非阻塞建议改 127.0.0.1）。deploy-plan.md 不存在属 PL 交付物缺口（非安全阻塞）。

**人工确认需求**: 不需要。本 CR 未涉及生产/支付/数据删除风险。

### 阻塞项: 无

---

## 12. 建议（非阻塞）

| # | 建议 | 优先级 | 责任人 |
|---|---|---|---|
| 1 | Corvus systemd 服务 HOST 改为 127.0.0.1（当前 0.0.0.0 + iptables 补偿，建议收紧） | P3 | Ops |
| 2 | 补充 deploy-plan.md 发布计划文件 | P2 | PL |
| 3 | Docker backend 加入 --reload 或代码变更自动重启机制（BUG-038-007） | P3 | Ops |
| 4 | 定期运行 `pip-audit` 和 `npm audit` 依赖漏洞扫描 | P3 | Ops/BE/FE |

---

## 13. 通信台账

| 时间 | from | to | 阶段 | 状态 | 说明 |
|---|---|---|---|---|---|
| 2026-09-06T16:00 | Cat01-pl | Cat01-security | SECURITY | received | PL 触发 SECURITY 阶段（重新执行，前轮配额超限） |
| 2026-09-06T16:01 | Cat01-security | Cat01-pl | SECURITY | acked_msg | Security ACK 确认收到，开始执行 |
| 2026-09-06T16:30 | Cat01-security | Cat01-pl | SECURITY | sent_msg | Security 审查完成: ✅ PASS, security-review.md 已产出 |
