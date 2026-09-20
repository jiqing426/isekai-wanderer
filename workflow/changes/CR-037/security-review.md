# Security Review — CR-037 Corvus-Story-Core 集成

| 项 | 内容 |
| --- | --- |
| CR 编号 | CR-037 |
| 审查角色 | Security |
| 审查时间 | 2026-08-06 19:05 CST |
| 审查结论 | **PASS (有条件)** — AC-002 已修复验证；2 项低风险后续修复项 |
| 阻塞项 | 0 阻塞 |
| 退回对象 | 无 |

---

## 1. 审查范围

依据 `docs/security/security.md`、`docs/runtime/runtime-contract.md`、`docs/api/api.md`、`docs/database/database.md`、`test-report.md`、`deploy-plan.md` 和 `acceptance.md`，对以下安全检查项逐项审查：

1. 8082 端口隔离（AC-002）
2. LLM API Key 存储
3. 用户数据隔离
4. 候选角色过滤
5. SSE 流式安全
6. 向量记忆隔离
7. 鉴权与授权
8. 依赖与部署配置

---

## 2. 逐项审查结论

### 2.1 8082 端口隔离（AC-002）— ✅ PASS

| 检查 | 结果 | 证据 |
| --- | --- | --- |
| 公网 8082 不可达 | **PASS** | `curl --connect-timeout 5 http://47.107.174.176:8082/api/health` → Connection timed out (5s) |
| 本机 127.0.0.1:8082 可达 | **PASS** | `curl http://127.0.0.1:8082/api/health` → `{"ok":true,...}` |
| Docker bridge 可达 | **PASS** | `curl http://10.255.0.1:8082/api/health` → `{"ok":true,...}` (10.255.0.1 = docker0) |
| iptables 规则正确 | **PASS** | 规则链：ACCEPT 127.0.0.1 → ACCEPT 172.17.0.0/16 → ACCEPT 172.18.0.0/16 → DROP all (末尾兜底) |
| systemd 绑定 127.0.0.1 | **PASS** | `systemctl status corvus-story` → active(running); ExecStart 绑定 `--host 127.0.0.1 --port 8082` |
| test-report.md AC-002 | **PASS** | 原 FAIL (公网可达)，修复后 PASS |

**结论**：BUG-001 (P0 安全) 已修复并验证。iptables DROP 规则在 ACCEPT Docker bridge 之后，确保 Docker 容器可通过 bridge 访问 Corvus，公网请求被 DROP。

### 2.2 LLM API Key 存储 — ⚠️ LOW RISK (后续修复)

| 检查 | 结果 | 证据 |
| --- | --- | --- |
| API Key 不经后端 | **PASS** | `corvus_client.py` 无 API Key 硬编码；后端只调 Corvus HTTP API，不存储/转发 LLM Key |
| API Key 在 Corvus config.json | **PASS** | 存储在 `corvus-data/config.json` → `lmStudio.apiKey` |
| config.json 不被 git 追踪 | **PASS** | `git ls-files --error-unmatch corvus-data/config.json` → NOT TRACKED；`.gitignore` 包含 `corvus-data/` |
| .env 不被 git 追踪 | **PASS** | `git ls-files --error-unmatch .env` → NOT TRACKED；`.gitignore` 包含 `.env` |
| config.json 文件权限 | **⚠️ LOW** | `644 root:root` — world-readable；建议 `600` 仅 owner 可读 |
| API Key 明文存储 | **⚠️ LOW** | `sk-6Nig_1ndlOU3eaIVK2dDHQ` 明文在 config.json；Corvus 设计如此，非本 CR 引入；建议生产环境改用环境变量注入 |

**结论**：API Key 不经后端（安全设计正确），git 不追踪敏感文件（正确）。文件权限 644 和明文存储为低风险项，建议后续修复。

### 2.3 用户数据隔离（会话不串）— ✅ PASS

| 检查 | 结果 | 证据 |
| --- | --- | --- |
| 会话所有权校验 | **PASS** | `CorvusAdapter.create_session` 和 `stream_turn` 均校验 `session.user_id != user_id` → 403 `SESSION_FORBIDDEN` |
| `game.py` 所有权校验 | **PASS** | `_verify_session_ownership()` 在 dialogue、choice、custom-input 端点调用；返回 403 on mismatch |
| 换角色创建新会话 | **PASS** | AC-008 验证：旧会话 corvus_internal_game_id 不变，新会话有不同 game_id |
| Bearer Token 鉴权 | **PASS** | 所有 `/api/v1/game/` 端点使用 `Depends(get_current_user_id)` |
| Corvus game_id 隔离 | **PASS** | 每个 CorvusGameSession 有独立 corvus_internal_game_id；Corvus 内部按 game_id 隔离会话 |

**结论**：会话隔离完整，所有权校验覆盖所有相关端点。

### 2.4 候选角色过滤 — ✅ PASS

| 检查 | 结果 | 证据 |
| --- | --- | --- |
| 仅选中角色送入 Corvus | **PASS** | `CorvusAdapter.create_session` 查询单个 `PlayerCandidate`（WHERE id=player_candidate_id AND user_id），仅将该候选的 name/backstory/appearance/inventory 传入 `CorvusClient.create_game` |
| 另外两个角色不泄露 | **PASS** | 代码只查询和传递选中的 candidate，不查询/不传递其他 candidate |
| 代码注释明确 | **PASS** | 注释 `# 3. Call Corvus create_game — ONLY the selected candidate` 和 `#    The other two candidates are NOT sent to Corvus.` |

**结论**：候选角色过滤正确实现，未选中角色数据不送入 Corvus。

### 2.5 SSE 流式安全 — ✅ PASS

| 检查 | 结果 | 证据 |
| --- | --- | --- |
| SSE 不返回 embedding 向量 | **PASS** | `game.py` SSE 响应中不含 embedding 字段；`SSETranslator` 输出仅 text/done/gm_update/stream_end/error |
| SSE 错误信息不泄露内部细节 | **PASS** | `httpx.ConnectError` → `"Corvus 服务连接失败，请重试"`（通用消息）；其他异常 → `str(e)` |
| SSE 通用错误消息 | **⚠️ LOW** | `str(e)` 可能包含内部异常细节；建议生产环境改为通用消息 + 日志记录完整错误 |
| SSE 连接超时 | **PASS** | `CORVUS_TIMEOUT = 300` 秒，适合长对话 SSE；超时后前端 onError 触发重试 (AC-011) |
| Corvus 不直接暴露前端 | **PASS** | 前端只通过后端 SSE 代理访问；Corvus 8082 不在 Nginx/Vite proxy 中暴露 |

**结论**：SSE 安全基本通过。`str(e)` 暴露内部异常细节为低风险，建议后续修复。

### 2.6 向量记忆隔离 — ✅ PASS

| 检查 | 结果 | 证据 |
| --- | --- | --- |
| 跨用户记忆隔离 | **PASS** | `EmbeddingService.recall` WHERE `CharacterMemory.user_id == user_id`；不同用户记忆不可互相检索 |
| 跨角色记忆隔离 | **PASS** | `EmbeddingService.recall` WHERE `CharacterMemory.character_id == character_id`；不同角色记忆不可互相检索 |
| embedding 不通过 API 返回 | **PASS** | `game.py` API 响应和 `SSETranslator` 输出均不含 embedding 字段；`embedding_service.py` 的 `recall()` 只返回 `memory_text` 字符串列表 |
| NPC knownInfo 注入/恢复加锁 | **PASS** | `_get_lock(session_id)` 返回 per-session `asyncio.Lock`；注入和恢复都在 `async with lock` 内执行 |
| NPC knownInfo 恢复 | **PASS** | `restore_npc_knowninfo` 在 SSE 流结束后调用，恢复原始值 |
| pgvector KNN 查询 | **PASS** | 使用 `cosine_distance` 操作符，`WHERE embedding.isnot(None)` 过滤 NULL embedding；`LIMIT 5` + 阈值 0.7 |

**结论**：向量记忆隔离完整，按 user_id + character_id 双重过滤，embedding 不泄露。

### 2.7 鉴权与授权 — ✅ PASS

| 检查 | 结果 | 证据 |
| --- | --- | --- |
| JWT Bearer 鉴权 | **PASS** | 所有 `/api/v1/game/` 端点使用 `Depends(get_current_user_id)` |
| 会话所有权 403 | **PASS** | `_verify_session_ownership` 和 `CorvusAdapter` 内部均校验 user_id，返回 403 on mismatch |
| Rate limiting | **PASS** | Redis sliding window: general API 60/min, LLM calls 10/min (security.md) |
| 无新增认证/授权边界 | **PASS** | `acceptance.md` 人工确认表：认证/授权变更 = 否 |

**结论**：鉴权与授权完整，无新增权限边界变更。

### 2.8 依赖与部署配置 — ✅ PASS

| 检查 | 结果 | 证据 |
| --- | --- | --- |
| 无禁用进程 | **PASS** | `ps aux | grep -E 'ollama|vllm|hermes'` 无匹配 (AC-004) |
| 依赖版本固定 | **PASS** | `pyproject.toml` 固定版本 (security.md) |
| Docker 容器隔离 | **PASS** | Corvus 运行在宿主机 systemd（非 Docker），但绑定 127.0.0.1 + iptables DROP 公网 |
| deploy-plan 状态 | **PASS** | deploy-plan.md 为 Pending 模板，尚未部署到生产；DEPLOY 阶段尚未开始 |
| 不可逆迁移 | **⚠️ INFO** | embedding 维度 1536→512 属不可逆迁移，已在 acceptance.md 标记人工确认 = 是；需 DEPLOY 前人工追认 |

**结论**：依赖与部署配置安全。

---

## 3. 发布证据安全复核

依据 `traceability-chain.md` 和 `failure-backtrace.md` 要求：

| 证据类型 | Mock API | 结论 |
| --- | --- | --- |
| CI/CD (120 unit tests) | no | **PASS** — 测试在真实 Docker 容器内运行 |
| Delivery E2E / Runtime Smoke (25/28 AC) | no | **PASS** — 所有 Delivery E2E 记录 Mock API=no，使用真实 Corvus + 真实 LLM + 真实 PostgreSQL |
| Browser Interaction E2E (7 AC pending) | no | **MANUAL PENDING** — AC-023, AC-024 需 Browser E2E 人工验收；Security 不阻止 RELEASE_GATE，但 PL 需决定验收方式 |

**Mock 检查**：
- 未发现 Mock API、fixture server、MSW、静态假数据或 mock 模型作为发布证据
- Delivery E2E 全部记录 `Mock API=no`
- 单元测试中 mock CorvusClient/EmbeddingService 仅用于隔离测试，不作为发布证据

---

## 4. 低风险后续修复项

| 编号 | 风险等级 | 描述 | 责任人 | 修复建议 | 验证方式 |
| --- | --- | --- | --- | --- | --- |
| SEC-001 | LOW | Corvus `config.json` 文件权限 644 (world-readable)，LLM API Key 明文 | ops | `chmod 600 /root/code/Corvus-Story-Core/corvus-data/config.json`；建议生产环境改用环境变量注入 API Key | `stat -c '%a' config.json` → 600 |
| SEC-002 | LOW | SSE 错误处理中 `str(e)` 可能泄露内部异常细节给前端 | backend | 将 `stream_turn` 的通用 Exception 分支改为返回通用错误消息，完整错误仅写日志 | 前端 SSE error 事件不含文件路径/堆栈信息 |

**说明**：以上两项不阻塞 CR-037 RELEASE_GATE，但应在下一轮迭代或部署前修复。

---

## 5. 安全检查清单复核

| 检查项 | 结论 |
| --- | --- |
| 是否提交真实密钥、token、证书、密码或生产数据 | **否** — config.json 不被 git 追踪；.env 不被 git 追踪；.env.example 只有 placeholder |
| 鉴权、授权、审计和敏感操作确认是否完整 | **是** — JWT Bearer + 会话所有权校验 + 403 on mismatch |
| 敏感字段、隐私、日志脱敏和数据保留是否清楚 | **是** — embedding 不通过 API 返回；密码 bcrypt hash；JWT 不记日志 |
| API、DB/Runtime 和 Mock 策略是否一致 | **是** — runtime-contract.md、api.md、database.md 一致；Delivery E2E 全部 Mock API=no |
| test-report.md 是否区分 CI/CD、Delivery E2E / Runtime Smoke 和 Browser Interaction E2E | **是** — 第 1/2/3 节分别记录三类测试 |
| 依赖、容器和部署配置是否存在明显风险 | **否** — 依赖固定版本；iptables 正确；无禁用进程 |
| 安全相关验收项是否在 acceptance.md 有验证结论 | **是** — AC-002 修复后 PASS；AC-004 PASS |
| 高风险事项是否需要人工确认 | **是** — 不可逆迁移 (embedding 1536→512) 需 DEPLOY 前人工追认（已在 acceptance.md 标记） |

---

## 6. 倒查链验证

| 追踪链路段 | 结论 |
| --- | --- |
| PRD → REQ → AC → Design → Task → Code → Test → Green → Acceptance → QA → Release | 完整可追踪 |
| AC-002 (P0 安全) | test-report.md FAIL → 修复 → 重新验证 PASS；证据链完整 |
| Mock 检查 | Delivery E2E 全部 Mock API=no；无 mock 作为发布证据 |
| 安全相关 AC | AC-002 (端口隔离) PASS；AC-004 (无禁用进程) PASS；AC-018 (跨会话记忆隔离) PASS |
| 阻塞项 | 0 阻塞；2 项低风险后续修复 (SEC-001, SEC-002) |

---

## 7. 结论

**CR-037 安全审查结论：PASS (有条件)**

- AC-002 (P0 安全 — 公网 8082 可达) 已修复并验证通过
- 所有安全检查项通过，无阻塞项
- 2 项低风险后续修复项 (SEC-001, SEC-002) 不阻塞 RELEASE_GATE
- 不可逆迁移 (embedding 维度变更) 需 DEPLOY 前人工追认
- Browser Interaction E2E (AC-023, AC-024) 需 PL 决定验收方式

**建议**：PL 审查安全结论后推进到 RELEASE_GATE。
