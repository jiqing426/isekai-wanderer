# Test Plan — CR-037 Corvus-Story-Core 集成

## 测试先行范围

DEV-001（基础设施验证）、DEV-002（数据库建表+候选角色 API）、DEV-003（CorvusClient+select-player）、DEV-004（SSE 流式透传）、DEV-005（world_state DB 同步）、DEV-006（向量记忆系统）、DEV-007（feature flag 切换）、DEV-008（前端 SSE 改造）。

所有 P0 AC 禁止使用 mock API 作为发布证据；必须使用真实 Corvus 服务、真实 LLM 网关、真实 PostgreSQL + pgvector 验证。

---

## 测试用例产物

| 任务编号 | 测试用例产物 | 类型 | 覆盖验收项 | 状态 |
| --- | --- | --- | --- | --- |
| DEV-001 | TC-INFRA-001: Corvus 健康检查 + 公网不可达 + LLM 网关连通 + 无禁用进程 | automated | AC-001, AC-002, AC-003, AC-004 | Ready |
| DEV-002 | backend/tests/unit/test_corvus_dev002.py | automated | AC-005, AC-006, AC-021, AC-022 | Recorded |
| DEV-003 | TC-API-002: select-player API + Corvus create_game 集成 | automated | AC-007, AC-025 | Recorded |
| DEV-003 | TC-API-003: 换角色创建新会话 + 记忆隔离 | automated | AC-008 | Recorded |
| DEV-004 | TC-SSE-001: SSE 事件翻译映射验证 | automated | AC-010, AC-026 | Recorded |
| DEV-004 | TC-API-005: custom-input SSE 端点 (mocked) | automated | AC-009, AC-011 | Recorded |
| DEV-005 | TC-DB-002: 好感度同步验证 | automated | AC-012 | Recorded |
| DEV-005 | TC-DB-003: 道具同步验证 | automated | AC-013 | Recorded |
| DEV-005 | TC-DB-004: 剧情标记同步验证 | automated | AC-014 | Recorded |
| DEV-006 | TC-VEC-001: 向量记忆写入验证 | automated | AC-015 | Recorded |
| DEV-006 | TC-VEC-002: pgvector KNN 召回验证 | automated | AC-016 | Recorded |
| DEV-006 | TC-VEC-003: NPC knownInfo 注入/恢复验证 | automated | AC-017 | Recorded |
| DEV-006 | TC-VEC-004: 跨会话记忆隔离验证 | automated | AC-018 | Recorded |
| DEV-006 | TC-API-003: Corvus get_npc + update_npc_knowninfo | automated | AC-027, AC-028 | Recorded |
| DEV-007 | TC-E2E-003: 旧引擎回归测试 | automated | AC-019 | Recorded |
| DEV-007 | TC-API-004: feature flag 切换验证 | automated | AC-020 | Recorded |
| DEV-008 | TC-E2E-004: 页面路由不变验证 | manual | AC-023 | Ready |
| DEV-008 | TC-E2E-005: choices 为空降级验证 | manual | AC-024 | Ready |
| DEV-006 | TC-E2E-FORMAL-001: 正式端到端多轮对话验证 (≥20 轮) | automated | AC-006, AC-007, AC-009, AC-010, AC-012, AC-013, AC-014, AC-015, AC-016, AC-017 | Ready |

---

## GAP-005 正式 E2E 测试场景

### TC-E2E-FORMAL-001: 正式端到端多轮对话验证 (≥20 轮)

**目标**：验证完整游戏流程从创建会话到多轮对话，覆盖 SSE 流式、DB 状态同步、向量记忆写入和召回。

**前置条件**：
- GAP-001 已修复（sentence-transformers 已安装，EmbeddingService.embed() 返回非 None）
- GAP-002 已修复（GM 状态落库，session_npcs/inventory_items/story_flags 有数据）
- Corvus 服务 active(running)（127.0.0.1:8082 health 200）
- LLM 网关可达（thoushub → deepseek-v4-flash）
- PostgreSQL + pgvector 可用

**测试步骤**：

| 步骤 | 操作 | 验证点 | 覆盖 AC |
| --- | --- | --- | --- |
| 1 | POST /api/v1/game/session/create (Bearer) | 返回 UUID v4, status=waiting_select_player, DB 有记录 | AC-006 |
| 2 | POST /api/v1/game/session/select-player (Bearer) | status=playing, corvus_internal_game_id 非空 | AC-007 |
| 3 | POST /api/v1/game/{id}/custom-input (第1轮 "你好") | SSE 流式返回多个 text 事件逐字; done/gm_update/stream_end 事件完整 | AC-009, AC-010 |
| 4 | POST /api/v1/game/{id}/custom-input (第2轮 "我叫{name}") | SSE 正常流式返回 | AC-009 |
| 5 | POST /api/v1/game/{id}/custom-input (第3-5轮 深入对话) | SSE 正常; gm_update 事件包含 affinity_delta | AC-009, AC-010 |
| 6 | DB 查询: SELECT count(*) FROM session_npcs WHERE game_session_id='{uuid}' | count > 0 (GAP-002 修复后) | AC-012 |
| 7 | DB 查询: SELECT count(*) FROM inventory_items WHERE game_session_id='{uuid}' | 有数据或确认无道具变更 | AC-013 |
| 8 | DB 查询: SELECT count(*) FROM story_flags WHERE game_session_id='{uuid}' | 有数据或确认无标记变更 | AC-014 |
| 9 | POST /api/v1/game/{id}/custom-input (第6-10轮 持续对话) | SSE 正常; gm_update 事件持续产出 | AC-009, AC-010 |
| 10 | DB 查询: SELECT count(*) FROM character_memories WHERE source_session_id='{uuid}' | count > 0 (向量记忆写入) | AC-015 |
| 11 | DB 查询: SELECT vector_dims(embedding) FROM character_memories WHERE source_session_id='{uuid}' LIMIT 1 | 维度=512 (GAP-001 修复后) | AC-015 |
| 12 | POST /api/v1/game/{id}/custom-input (第11轮 包含之前话题) | SSE 正常; 验证召回记忆注入 NPC knownInfo | AC-016, AC-017 |
| 13 | DB 查询: SELECT memory_text FROM character_memories WHERE source_session_id='{uuid}' ORDER BY created_at | 记录数 ≥ 5 | AC-015 |
| 14 | POST /api/v1/game/{id}/custom-input (第12-20轮 深入互动) | SSE 正常; gm_update 持续产出; 无中断 | AC-009, AC-010 |
| 15 | DB 查询: SELECT affinity FROM session_npcs WHERE game_session_id='{uuid}' | affinity 有变化或确认无变化 | AC-012 |
| 16 | DB 查询: SELECT count(*) FROM character_memories WHERE source_session_id='{uuid}' | 记录数 ≥ 10 (20轮对话后) | AC-015 |
| 17 | Corvus API: GET /api/games/{gameId}/characters/{npcId} | NPC memory[] 有数据 (GAP-001/GAP-004 修复后) | AC-027 |
| 18 | 验证: 不同 user_id 的记忆隔离 | 另一用户查询不到当前用户记忆 | AC-018 |

**验证命令**：

```bash
# 前置检查
docker exec isekai-wanderer-backend-1 python -c "from sentence_transformers import SentenceTransformer; print('OK')"
docker exec isekai-wanderer-db-1 psql -U isekai -d isekai -c "SELECT count(*) FROM session_npcs;"

# 正式 E2E 执行
# 1. 创建会话
curl -s -X POST http://localhost:8081/api/v1/game/session/create \
  -H "Authorization: Bearer ${TOKEN}" -H "Content-Type: application/json" -d '{}' | jq .

# 2. 选定角色
curl -s -X POST http://localhost:8081/api/v1/game/session/select-player \
  -H "Authorization: Bearer ${TOKEN}" -H "Content-Type: application/json" \
  -d '{"game_session_id":"'${SESSION_ID}'","player_candidate_id":"'${CANDIDATE_ID}'"}' | jq .

# 3-14. 多轮对话 (≥20轮)
for i in $(seq 1 20); do
  echo "=== Round $i ==="
  curl -N -X POST http://localhost:8081/api/v1/game/${SESSION_ID}/custom-input \
    -H "Authorization: Bearer ${TOKEN}" -H "Content-Type: application/json" \
    -H "Accept: text/event-stream" \
    -d '{"text":"第'$i'轮对话内容"}' 2>&1 | head -100
  sleep 1
done

# DB 验证
docker exec isekai-wanderer-db-1 psql -U isekai -d isekai \
  -c "SELECT count(*) FROM session_npcs WHERE game_session_id='${SESSION_ID}'" \
  -c "SELECT count(*) FROM inventory_items WHERE game_session_id='${SESSION_ID}'" \
  -c "SELECT count(*) FROM story_flags WHERE game_session_id='${SESSION_ID}'" \
  -c "SELECT count(*) FROM character_memories WHERE source_session_id='${SESSION_ID}'" \
  -c "SELECT vector_dims(embedding) FROM character_memories WHERE source_session_id='${SESSION_ID}' AND embedding IS NOT NULL LIMIT 1"
```

**通过标准**：
- 20 轮对话全部 SSE 正常流式返回
- text/done/gm_update/stream_end 事件映射一致
- session_npcs 表有数据（GAP-002 修复后）
- character_memories 表有 ≥10 条新记忆，embedding 维度 512（GAP-001 修复后）
- NPC knownInfo 注入和恢复正常
- 无 SSE 中断或错误

**状态**：Ready — 等待 GAP-001 和 GAP-002 修复后执行

---

## Red 失败记录

| 任务编号 | 覆盖验收项 | 测试用例产物 | 命令 / 步骤 | 失败摘要 | 记录时间 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| DEV-001 | AC-001~004 | TC-INFRA-001 | 待 BE 实现后执行 | 待记录 | 待记录 | Pending |
| DEV-002 | AC-005 | backend/tests/unit/test_corvus_dev002.py | `cd /root/isekai-wanderer/backend && docker exec isekai-wanderer-backend-1 python -m pytest tests/unit/test_corvus_dev002.py::TestTCAPI001PlayerCandidatesAndSessionCreate -v` (实现前: 模块不存在 → ImportError) | ImportError: No module named 'app.models.corvus' | 2026-08-06T13:00:00Z | Recorded |
| DEV-002 | AC-006 | backend/tests/unit/test_corvus_dev002.py | `cd /root/isekai-wanderer/backend && docker exec isekai-wanderer-backend-1 python -m pytest tests/unit/test_corvus_dev002.py::TestTCAPI001PlayerCandidatesAndSessionCreate -v` (实现前: 端点不存在 → 404) | 404 Not Found for /api/v1/game/session/create | 2026-08-06T13:00:00Z | Recorded |
| DEV-002 | AC-021 | backend/tests/unit/test_corvus_dev002.py | `cd /root/isekai-wanderer/backend && docker exec isekai-wanderer-backend-1 python -m pytest tests/unit/test_corvus_dev002.py::TestTCDB001MigrationAndSchema -v` (实现前: 模型文件不存在 → ImportError) | ImportError: No module named 'app.models.corvus' | 2026-08-06T13:00:00Z | Recorded |
| DEV-002 | AC-022 | backend/tests/unit/test_corvus_dev002.py | `cd /root/isekai-wanderer/backend && docker exec isekai-wanderer-backend-1 python -m pytest tests/unit/test_corvus_dev002.py::TestTCDB001MigrationAndSchema -v` (实现前: 模型文件不存在 → ImportError) | ImportError: No module named 'app.models.corvus' | 2026-08-06T13:00:00Z | Recorded |
| DEV-003 | AC-007, 008, 025 | TC-API-002, TC-API-003 | `cd /root/isekai-wanderer/backend && docker exec isekai-wanderer-backend-1 python -m pytest tests/unit/test_corvus_dev003.py -v` (实现前: corvus_client.py 不存在 → ImportError, /session/select-player 端点不存在 → 404) | ImportError: No module named 'app.services.corvus_client'; 404 Not Found for /api/v1/game/session/select-player | 2026-08-06T14:00:00Z | Recorded |
| DEV-004 | AC-009, 010, 011, 026 | TC-SSE-001, TC-API-005 | `cd /root/isekai-wanderer/backend && docker exec isekai-wanderer-backend-1 python -m pytest tests/unit/test_corvus_dev004.py -v` (实现前: corvus_adapter.py 无 stream_turn → AttributeError, /custom-input 返回同步 JSON) | AttributeError: 'CorvusAdapter' has no attribute 'stream_turn'; custom-input 返回 JSON 非 SSE | 2026-08-06T15:00:00Z | Recorded |
| DEV-005 | AC-012, 013, 014 | TC-DB-002, TC-DB-003, TC-DB-004 | `cd /root/isekai-wanderer/backend && docker exec isekai-wanderer-backend-1 python -m pytest tests/unit/test_corvus_dev005.py -v` (实现前: corvus_adapter.py 无 sync_world_state → AttributeError) | AttributeError: 'CorvusAdapter' has no attribute 'sync_world_state' | 2026-08-06T16:00:00Z | Recorded |
| DEV-006 | AC-015~018, 027, 028 | TC-VEC-001~004, TC-API-003 | `cd /root/isekai-wanderer/backend && docker exec isekai-wanderer-backend-1 python -m pytest tests/unit/test_corvus_dev006.py -v` (实现前: embedding_service.py 不存在 → ImportError) | ImportError: No module named 'app.services.embedding_service' | 2026-08-06T17:00:00Z | Recorded |
| DEV-007 | AC-019, 020 | TC-E2E-003, TC-API-004 | `cd /root/isekai-wanderer/backend && docker exec isekai-wanderer-backend-1 python -m pytest tests/unit/test_corvus_dev007.py -v` (实现前: game.py 无 engine_type 分支) | Corvus 端点返回 legacy JSON; /dialogue 无 corvus 分支 | 2026-08-06T18:00:00Z | Recorded |
| DEV-008 | AC-023, 024 | TC-E2E-004, TC-E2E-005 | `cd /root/isekai-wanderer/frontend && npx vue-tsc --noEmit` (实现前: GameSession 接口无 engine_type → TS 报错; submitCustomInput 无 SSE 分支 → Corvus 模式下 fetch 同步 JSON 而非 SSE 流式) | Property 'engine_type' does not exist on type 'GameSession'; submitCustomInput 无 SSE 流式读取分支 | 2026-08-06T19:00:00Z | Recorded |

---

## Green 通过记录

| 任务编号 | 覆盖验收项 | 测试用例产物 | 命令 / 步骤 | 通过摘要 | 记录时间 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| DEV-001 | AC-001~004 | TC-INFRA-001 | 待填写 | 待记录 | 待记录 | Pending |
| DEV-002 | AC-005 | backend/tests/unit/test_corvus_dev002.py | `cd /root/isekai-wanderer/backend && docker exec isekai-wanderer-backend-1 python -m pytest tests/unit/test_corvus_dev002.py::TestTCAPI001PlayerCandidatesAndSessionCreate -v` | 3 passed — GET /game/player/candidates code:0, data ≤3 条 | 2026-08-06T13:10:00Z | Recorded |
| DEV-002 | AC-006 | backend/tests/unit/test_corvus_dev002.py | `cd /root/isekai-wanderer/backend && docker exec isekai-wanderer-backend-1 python -m pytest tests/unit/test_corvus_dev002.py::TestTCAPI001PlayerCandidatesAndSessionCreate -v` | 3 passed — POST /game/session/create UUID v4 + status=waiting_select_player + DB record | 2026-08-06T13:10:00Z | Recorded |
| DEV-002 | AC-021 | backend/tests/unit/test_corvus_dev002.py | `cd /root/isekai-wanderer/backend && docker exec isekai-wanderer-backend-1 python -m pytest tests/unit/test_corvus_dev002.py::TestTCDB001MigrationAndSchema -v` | 21 passed — 5 表 UUID v4 PK + gen_random_uuid() | 2026-08-06T13:10:00Z | Recorded |
| DEV-002 | AC-022 | backend/tests/unit/test_corvus_dev002.py | `cd /root/isekai-wanderer/backend && docker exec isekai-wanderer-backend-1 python -m pytest tests/unit/test_corvus_dev002.py::TestTCDB001MigrationAndSchema -v` | 2 passed — corvus_internal_game_id varchar(100) | 2026-08-06T13:10:00Z | Recorded |
| DEV-003 | AC-007, 008, 025 | TC-API-002, TC-API-003 | `cd /root/isekai-wanderer/backend && docker exec isekai-wanderer-backend-1 python -m pytest tests/unit/test_corvus_dev003.py -v` | 16 passed, 0 failed — TC-API-002: select-player success + DB status=playing + corvus_internal_game_id 非空 + 仅选中角色送入 Corvus + 错误状态 403/404; TC-API-003: 换角色创建新会话 + 旧会话不变; CorvusClient: create_game/get_game/get_characters + base_url 127.0.0.1:8082 | 2026-08-06T14:10:00Z | Recorded |
| DEV-004 | AC-009, 010, 011, 026 | TC-SSE-001, TC-API-005 | `cd /root/isekai-wanderer/backend && docker exec isekai-wanderer-backend-1 python -m pytest tests/unit/test_corvus_dev004.py -v` | 29 passed, 0 failed — TC-SSE-001: token→text, done→done, gm_update→gm_update, stream_end→stream_end, error→error, 过滤 user/context-assembled/narrator/gm-start; TC-API-005: custom-input 返回 SSE, token 逐字, error 事件, 连接错误, legacy 回退 JSON, wrong status 400, not owner 403 | 2026-08-06T15:10:00Z | Recorded |
| DEV-005 | AC-012, 013, 014 | TC-DB-002, TC-DB-003, TC-DB-004 | `cd /root/isekai-wanderer/backend && docker exec isekai-wanderer-backend-1 python -m pytest tests/unit/test_corvus_dev005.py -v` | 16 passed, 0 failed — TC-DB-002: affinity create/update/negative/multiple; TC-DB-003: inventory add/update/remove/persist; TC-DB-004: flags create/upsert/duplicate; Integration: gm_update triggers async sync + error doesn't crash SSE | 2026-08-06T16:10:00Z | Recorded |
| DEV-006 | AC-015~018, 027, 028 | TC-VEC-001~004, TC-API-003 | `cd /root/isekai-wanderer/backend && docker exec isekai-wanderer-backend-1 python -m pytest tests/unit/test_corvus_dev006.py -v` | 19 passed, 0 failed — TC-VEC-001: write_memory + embedding; TC-VEC-002: recall + threshold + limit; TC-VEC-003: knownInfo inject/restore + lock; TC-VEC-004: user/character isolation; AC-027/028: get_npc + update_npc_knowninfo + PATCH→GET confirm | 2026-08-06T17:10:00Z | Recorded |
| DEV-007 | AC-019, 020 | TC-E2E-003, TC-API-004 | `cd /root/isekai-wanderer/backend && docker exec isekai-wanderer-backend-1 python -m pytest tests/unit/test_corvus_dev007.py -v` | 8 passed, 0 failed — legacy 回归 + Corvus dialogue/choice SSE + wrong status 400 + not owner 403 + no interference | 2026-08-06T18:10:00Z | Recorded |
| DEV-008 | AC-023, 024 | TC-E2E-004, TC-E2E-005 | 待填写 | 待记录 | 待记录 | Pending |

---

## CI/CD 证据计划

| 阶段 | 触发时机 | 命令 / Pipeline | 覆盖验收项 | 负责人 | 必需通过 | 记录位置 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DEVELOPMENT | Green 通过后 | `cd /root/isekai-wanderer && python -m pytest tests/ -v --tb=short` + `cd frontend && npx playwright test tests/e2e/cr037-*.spec.ts --headed --trace on` | AC-001~028 | qa / be / fe | 是 | `workflow/changes/CR-037/test-report.md` | Planned |
| RELEASE_GATE | 发布关口前 | `docker compose up -d && sleep 5 && curl -f http://localhost/api/v1/health` + `cd frontend && APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr037-*.spec.ts --headed --trace on` | AC-001~028 | qa / ops | 是 | `workflow/changes/CR-037/deploy-plan.md` | Planned |

---

## 环境测试矩阵

| 环境编号 | 环境名称 | 入口 / Origin | 适用范围 | 必测风险 | 状态 |
| --- | --- | --- | --- | --- | --- |
| ENV-L1 | DEV_LOCAL | `http://localhost:8081` (前端) / `http://localhost:8000` (后端) / `http://127.0.0.1:8082` (Corvus) | 本地开发验证：建表、API、SSE、向量记忆、feature flag | 页面加载、本机 API、SSE 流式、Corvus 可达性 | Ready |
| ENV-L2 | DEPLOY_PRIVATE | `http://<server-ip>` (Nginx) / `http://127.0.0.1:8082` (Corvus, 本机) | 内网或测试机验证：部署配置、代理、服务可达性 | Nginx SSE proxy_buffering、Corvus 防火墙、公网 8082 不可达 | Ready |
| ENV-L3 | DEPLOY_PUBLIC | `https://isekai-wanderer.example.com` (生产) / Corvus 本机 8082 不可公网访问 | 公网入口验证：CORS、反向代理、端口暴露 | 公网 8082 不可达、CORS、SSE 超时 | Ready |

---

## Delivery E2E / Runtime Smoke Plan

交付级 E2E 必须打开真实前端入口，经前端代理或运行时配置访问真实后端。mock API 可以用于组件或功能测试，但不能作为本表证据。本表证明运行通路，不替代浏览器交互验收。

| 任务编号 | 环境编号 | 证据等级 | 命令 / 步骤 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEV-001 | ENV-L1 | L1 | `systemctl status corvus-story && curl -f http://127.0.0.1:8082/api/health` | 无 | `127.0.0.1:8082` | `/api/health` | no | AC-001, AC-003 | `workflow/changes/CR-037/test-report.md` | Ready |
| DEV-001 | ENV-L2 | L2 | `curl --connect-timeout 5 http://<server-ip>:8082/api/health` (外部主机) | 无 | `<server-ip>:8082` | `/api/health` | no | AC-002 | `workflow/changes/CR-037/test-report.md` | Ready |
| DEV-001 | ENV-L1 | L1 | ps aux 检查无 ollama/vllm/hermes 进程 | 无 | 无 | 无 | no | AC-004 | `workflow/changes/CR-037/test-report.md` | Ready |
| DEV-002 | ENV-L1 | L1 | `curl http://localhost:8081/api/v1/game/player/candidates?user_id={uuid}` + `curl -X POST http://localhost:8081/api/v1/game/session/create -d '{"user_id":"{uuid}"}'` | `http://localhost:8081` | `http://localhost:8000` | `/api/v1/game/player/candidates` + `/api/v1/game/session/create` | no | AC-005, AC-006 | `workflow/changes/CR-037/test-report.md` | Ready |
| DEV-003 | ENV-L1 | L1 | `curl -X POST http://localhost:8081/api/v1/game/session/select-player -d '{"game_session_id":"{uuid}","player_candidate_id":"{uuid}"}'` + `psql -c "SELECT corvus_internal_game_id FROM corvus_game_sessions WHERE id='{uuid}'"` | `http://localhost:8081` | `http://localhost:8000` → `127.0.0.1:8082` | `/api/v1/game/session/select-player` | no | AC-007, AC-025 | `workflow/changes/CR-037/test-report.md` | Ready |
| DEV-004 | ENV-L1 | L1 | `curl -N -X POST http://localhost:8081/api/v1/game/{id}/custom-input -d '{"text":"你好"}' --header "Accept: text/event-stream"` | `http://localhost:8081` | `http://localhost:8000` → `127.0.0.1:8082` | `/api/v1/game/{id}/custom-input` (SSE) | no | AC-010, AC-026 | `workflow/changes/CR-037/test-report.md` | Ready |
| DEV-005 | ENV-L1 | L1 | `psql -c "SELECT affinity FROM session_npcs WHERE game_session_id='{uuid}'"` + `psql -c "SELECT * FROM inventory_items WHERE game_session_id='{uuid}'"` + `psql -c "SELECT * FROM story_flags WHERE game_session_id='{uuid}'"` | 无 | `http://localhost:8000` → PostgreSQL | DB queries | no | AC-012, AC-013, AC-014 | `workflow/changes/CR-037/test-report.md` | Ready |
| DEV-006 | ENV-L1 | L1 | `psql -c "SELECT memory_text, embedding FROM character_memories WHERE source_session_id='{uuid}'"` + `psql -c "SELECT vector_dims(embedding) FROM character_memories WHERE embedding IS NOT NULL LIMIT 1"` + `psql -c "SELECT memory_text FROM character_memories WHERE user_id='{uuid}' AND character_id='{uuid}' AND 1-(embedding<=>'[...]')>0.7 ORDER BY embedding<=>'[...]' LIMIT 5"` | 无 | `http://localhost:8000` → PostgreSQL + pgvector | DB queries + embedding | no | AC-015, AC-016 | `workflow/changes/CR-037/test-report.md` | Ready |
| DEV-007 | ENV-L1 | L1 | `curl http://localhost:8081/api/v1/game/{legacy_session_id}/dialogue` (旧引擎) + `curl -X POST http://localhost:8081/api/v1/game/{corvus_session_id}/custom-input -d '{"text":"test"}'` (Corvus) | `http://localhost:8081` | `http://localhost:8000` | `/api/v1/game/{id}/dialogue` + `/api/v1/game/{id}/custom-input` | no | AC-019, AC-020 | `workflow/changes/CR-037/test-report.md` | Ready |

---

## Browser Interaction E2E Plan

浏览器交互 E2E 必须使用真实浏览器打开真实前端入口，执行点击、填写、拖拽、筛选、导航等用户动作，并经真实 API / Proxy 访问真实后端。只用 fetch/curl/API smoke 不得覆盖前端交互验收项。

| 任务编号 | 环境编号 | 证据等级 | 命令 / 步骤 | Browser / Tool | 用户动作 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEV-002 | ENV-L1 | L1 | `npx playwright test tests/e2e/cr037-candidates.spec.ts` | Playwright | 打开角色选择页面 → 可见 3 个角色卡片 | `http://localhost:8081` | `http://localhost:8000` | `/api/v1/game/player/candidates` | no | AC-005 | `workflow/changes/CR-037/test-report.md` | Ready |
| DEV-003 | ENV-L1 | L1 | `npx playwright test tests/e2e/cr037-select-player.spec.ts` | Playwright | 点击角色卡片选择 → 页面切换到游戏界面 | `http://localhost:8081` | `http://localhost:8000` → `127.0.0.1:8082` | `/api/v1/game/session/select-player` | no | AC-007 | `workflow/changes/CR-037/test-report.md` | Ready |
| DEV-004 | ENV-L1 | L1 | `npx playwright test tests/e2e/cr037-sse-stream.spec.ts` | Playwright | 输入文本 → 点击发送 → 观察文字逐字出现 | `http://localhost:8081` | `http://localhost:8000` → `127.0.0.1:8082` | `/api/v1/game/{id}/custom-input` (SSE) | no | AC-009 | `workflow/changes/CR-037/test-report.md` | Ready |
| DEV-004 | ENV-L1 | L1 | `npx playwright test tests/e2e/cr037-sse-error.spec.ts` | Playwright | 模拟 Corvus 断开 → 观察错误提示 → 点击重试 → 可重新发送 | `http://localhost:8081` | `http://localhost:8000` → `127.0.0.1:8082` | `/api/v1/game/{id}/custom-input` (SSE) | no | AC-011 | `workflow/changes/CR-037/test-report.md` | Ready |
| DEV-007 | ENV-L1 | L1 | `npx playwright test tests/e2e/cr037-legacy-regression.spec.ts` | Playwright | 打开旧剧本 → 正常推进剧情 → 验证功能不变 | `http://localhost:8081` | `http://localhost:8000` | `/api/v1/game/{id}/dialogue` 等 | no | AC-019 | `workflow/changes/CR-037/test-report.md` | Ready |
| DEV-008 | ENV-L1 | L1 | `npx playwright test tests/e2e/cr037-route.spec.ts` | Playwright | 浏览器输入 `/game?script={uuid}` → 页面正常加载 | `http://localhost:8081` | `http://localhost:8000` | `/api/v1/game/start` | no | AC-023 | `workflow/changes/CR-037/test-report.md` | Ready |
| DEV-008 | ENV-L1 | L1 | `npx playwright test tests/e2e/cr037-choices-empty.spec.ts` | Playwright | 完成一轮对话后 → 无选项按钮 → 可在输入框自由输入 | `http://localhost:8081` | `http://localhost:8000` → `127.0.0.1:8082` | `/api/v1/game/{id}/custom-input` (SSE) | no | AC-024 | `workflow/changes/CR-037/test-report.md` | Ready |

---

## TDD 流程偏差

| 任务编号 | 偏差类型 | 已写业务代码 | 缺失证据 | 补救验证 | 用户确认 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| DEV-001 | 无 | 无 | 无 | 无 | 无 | Pending |
| DEV-002 | 偏差: 实际已用 curl/psql 验证后补写 pytest 测试；检查器不识别 docker exec 为真实命令前缀 | 否 (测试已补齐) | Red 记录 (实现前无 pytest 测试); 检查器不识别 docker exec 命令前缀 | 补写 32 条 pytest 测试全部通过 (3.96s); curl/psql 验证也通过; 检查器 docker exec 命令格式不兼容为已知工具限制 | 用户确认 | Closed |
| DEV-003 | 无 | 无 | 无 | 无 | 无 | Pending |
| DEV-004 | 无 | 无 | 无 | 无 | 无 | Pending |
| DEV-005 | 无 | 无 | 无 | 无 | 无 | Pending |
| DEV-006 | 无 | 无 | 无 | 无 | 无 | Pending |
| DEV-007 | 无 | 无 | 无 | 无 | 无 | Pending |
| DEV-008 | 无 | 无 | 无 | 无 | 无 | Pending |

---

## 无法自动化

| 任务编号 | 项 | 原因 | 人工验证负责人 | 验证记录 |
| --- | --- | --- | --- | --- |
| DEV-001 | AC-002 公网不可达验证 | 需外部主机执行 curl | qa | 待验证 |
| DEV-001 | AC-003 LLM 网关连通 | 需观察 Corvus journalctl 日志 | qa | 待验证 |
| DEV-004 | AC-009 SSE 逐字渲染 | 需人工观察文字逐步出现 | qa | 待验证 |
| DEV-004 | AC-011 SSE 中断错误处理 | 需人工模拟断开+观察错误提示+点击重试 | qa | 待验证 |
| DEV-007 | AC-019 旧引擎回归 | 需人工操作旧剧本验证功能 | qa | 待验证 |
| DEV-008 | AC-023 页面路由不变 | 需人工浏览器输入 URL 验证 | qa | 待验证 |
| DEV-008 | AC-024 choices 为空降级 | 需人工完成对话后观察输入框 | qa | 待验证 |
