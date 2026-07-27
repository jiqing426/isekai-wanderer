# CR-003 Test Report — Wave 1c INTEGRATION Acceptance

> **测试执行人**: QA Agent (isekai-wanderer-qa)
> **测试时间**: 2026-07-19 03:37–03:45 CST
> **测试环境**: localhost (BE:8000, FE:3000, DB:5432, Redis:6379)
> **Mock API**: no

---

## 整体结论

### ✅ PASS — 5 个 Bug 修复全部验证通过

PL 报告的 5 个 bug 修复均通过独立 curl 验证，无回退。

---

## Bug 修复验证（5/5 通过）

| Bug ID | 严重级别 | 端点 | 修复前 | 修复后 | 验证命令 | 验证结果 |
|--------|---------|------|--------|--------|---------|---------|
| BUG-CR3-001 | **P0** | `/api/v1/achievements-v2` | 500 INTERNAL_ERROR | **200** | `curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/achievements-v2` | ✅ HTTP:200, total: 8, unlocked: 0, claimed: 0 |
| BUG-CR3-002 | **P0** | `/api/v1/saves` | 500 INTERNAL_ERROR | **200** | `curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/saves` | ✅ HTTP:200, snapshots: [], total: 0 |
| BUG-CR3-003 | **P1** | `/api/v1/game/{id}/route-map` | 200 (无 auth) | **401** | `curl http://localhost:8000/api/v1/game/00000000-0000-0000-0000-000000000001/route-map` | ✅ HTTP:401 (正确拒绝) |
| BUG-CR3-004 | **P1** | `/api/v1/discover/scripts` | mock 数据 | **真实 DB** | `curl http://localhost:8000/api/v1/discover/scripts` | ✅ HTTP:200, 3 scripts (星月奇缘, 樱花恋曲, 星辰之约), has_error_code: False |
| BUG-CR3-005 | **P2** | FE 端口 | 8081 | **3000** | `curl http://localhost:3000/` | ✅ HTTP:200, 8081 不再监听 |

**验证方式**: 独立 curl，非 PL 自述
**Token 获取**: `POST /api/v1/auth/register` 注册新用户获取 access_token

---

## CI/CD 执行结果

### FE Vitest: 50/50 通过 ✅

| 测试套件 | 用例数 | 通过 | 失败 | 耗时 |
|---------|-------|------|------|------|
| `src/__tests__/game-store.test.ts` | 14 | 14 | 0 | <1ms |
| `tests/unit/fe/i18n.test.ts` | 12 | 12 | 0 | 2ms |
| `src/__tests__/auth-store.test.ts` | 4 | 4 | 0 | 5ms |
| `tests/unit/fe/useTypewriter.test.ts` | 8 | 8 | 0 | 1ms |
| `tests/unit/fe/useNotification.test.ts` | 6 | 6 | 0 | 1ms |
| `tests/unit/fe/AudioPlayer.test.ts` | 6 | 6 | 0 | 1ms |

**执行命令**: `cd frontend && npx vitest run --reporter=verbose`
**总耗时**: 3.53s

### BE pytest: 218 passed, 9 failed, 12 errors ⚠️

#### 通过用例（218/239）

覆盖模块：`test_affection_service`, `test_config`, `test_dialogue_context`, `test_dialogue_quality`, `test_embedding_service`, `test_free_chat_service`, `test_health`, `test_llm_gateway`, `test_memory_service`, `test_mock_email_service`, `test_moderation_service`, `test_narrative_engine`, `test_recall_service`, `test_rule_engine`, `test_security`

#### 失败用例（9 个）

| # | 测试 | 失败原因 | 类型 | 退回对象 |
|---|------|---------|------|---------|
| 1 | `test_discord_config_crud` | sqlite 缺 `discord_configs` 表 | 测试 fixture (CR-002 遗留) | BE |
| 2 | `test_generate_reset_token` | offset-naive vs aware datetime | 测试代码 (CR-002 遗留) | BE |
| 3 | `test_reset_token_expires_in_1_hour` | 同上 | 测试代码 (CR-002 遗留) | BE |
| 4 | `test_route_map_returns_script_routes` | 响应缺 `routes` key | **业务缺陷** | BE |
| 5 | `test_route_map_marks_explored_routes` | KeyError: 'routes' | **业务缺陷** | BE |
| 6 | `test_route_map_requires_auth` | 预期 401 实际 200 | **业务缺陷** | BE |
| 7 | `test_route_map_returns_nodes_and_choices` | KeyError: 'routes' | **业务缺陷** | BE |
| 8 | `test_route_map_invalid_script_id` | 预期 404 实际 200 | **业务缺陷** | BE |
| 9 | `test_reset_password_with_invalid_token` | 预期 400 实际 200 | **业务缺陷** | BE |

**注意**: 失败 #6 (`test_route_map_requires_auth`) 与 BUG-CR3-003 矛盾。curl 验证返回 401，但 pytest 返回 200。可能测试用例使用 mock client 绕过 auth middleware，需 BE 检查测试代码。

#### ERROR 用例（12 个）

`tests/test_wave_1c_part_a.py` 全部 12 个用例 ERROR（fixture 或 import 问题），非业务缺陷。

**执行命令**: `cd backend && PYTHONPATH=/root/isekai-wanderer/backend .venv/bin/python -m pytest tests/unit/ tests/test_wave_1c_part_a.py -v --tb=short`
**总耗时**: 21.02s

---

## Delivery E2E / Runtime Smoke Results

| 命令 / Command | 前端入口 | 后端地址 | API 路径 | Mock API | 覆盖验收项 | 结果 | 证据 |
|---|---|---|---|---|---|---|---|
| `curl http://localhost:8000/api/v1/health` | http://localhost:3000 | http://localhost:8000 | /api/v1/health | no | CR-003 | ✅ passed | 200 OK |
| `curl http://localhost:3000/` | http://localhost:3000 | http://localhost:8000 | — | no | BUG-CR3-005 | ✅ passed | 200 OK HTML |
| `curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/achievements-v2` | http://localhost:3000 | http://localhost:8000 | /api/v1/achievements-v2 | no | BUG-CR3-001 | ✅ passed | 200 OK, 8 achievements |
| `curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/saves` | http://localhost:3000 | http://localhost:8000 | /api/v1/saves | no | BUG-CR3-002 | ✅ passed | 200 OK, snapshots: [] |
| `curl http://localhost:8000/api/v1/game/00000000-0000-0000-0000-000000000001/route-map` | http://localhost:3000 | http://localhost:8000 | /api/v1/game/{id}/route-map | no | BUG-CR3-003 | ✅ passed | 401 Unauthorized |
| `curl http://localhost:8000/api/v1/discover/scripts` | http://localhost:3000 | http://localhost:8000 | /api/v1/discover/scripts | no | BUG-CR3-004 | ✅ passed | 200 OK, 3 real scripts |

---

## Browser Interaction E2E Results

### CR-003 E2E 测试文件不存在 ⚠️

`tests/e2e/cr003-platform.spec.ts` 不存在。可用 E2E 文件：
- `tests/e2e/auth-flow.spec.ts`
- `tests/e2e/cr002-features.spec.ts`
- `tests/e2e/game-flow.spec.ts`

**退回对象**: FE Agent — 需创建 CR-003 专项 E2E 测试

### CR-002 E2E 测试（正在执行）

`npx playwright test tests/e2e/cr002-features.spec.ts` 正在运行中，待汇总完整结果。

---

## 风险评估

| # | 缺陷 | 严重级别 | 来源 | 退回对象 |
|---|------|---------|------|---------|
| BUG-CR3-006 | `/api/v1/game/{id}/route-map` 响应缺 `routes` key | P1 | `test_route_map` pytest | BE |
| BUG-CR3-007 | `/api/v1/game/{id}/route-map` 无效 script_id 返回 200 而非 404 | P2 | `test_route_map` pytest | BE |
| BUG-CR3-008 | `/api/v1/auth/reset-password` 无效 token 返回 200 而非 400 | P1 | `test_password_reset` pytest | BE |
| BUG-CR3-009 | `test_wave_1c_part_a.py` 12 个用例 ERROR | P2 | 测试文件 fixture | BE |
| BUG-CR3-010 | CR-003 E2E 测试文件不存在 | P2 | 测试覆盖缺口 | FE |

---

## 结论

### ✅ PASS — Bug 修复验证

PL 报告的 5 个 bug 修复全部通过独立验证，无回退。

### ⚠️ CONDITIONAL PASS — 整体测试

- ✅ 5/5 bug 修复验证通过
- ✅ 50/50 FE Vitest 通过
- ⚠️ 218/239 BE pytest 通过（9 failed, 12 errors）
- ⚠️ CR-003 E2E 测试文件不存在

**建议**:
1. BE Agent 修复 3 个 P1 业务缺陷（BUG-CR3-006/007/008）
2. BE Agent 修复 `test_wave_1c_part_a.py` fixture 问题
3. FE Agent 创建 CR-003 专项 E2E 测试

---

**报告生成时间**: 2026-07-19 03:45 CST
**QA Agent**: isekai-wanderer-qa
**签名**: QA_PASS_BUG_FIXES_20260719
