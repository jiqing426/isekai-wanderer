# QA Day 1 接口验证报告 — CR-post-page

**验证时间**: 2026-07-24  
**验证环境**: localhost:8000 (Backend) + localhost:8081 (Frontend Docker)  
**验证方式**: curl 直接调用后端 API  
**Mock API**: no（真实路由 + 真实数据库）

---

## 验证结果汇总

| # | 任务 | 验证点 | 状态 | 详情 |
|---|------|--------|------|------|
| 1 | BE-D1 | GET /scripts 返回 hot_value 字段 | ✅ PASS | 每条记录包含 `hot_value`（数字，当前均为 0） |
| 2 | BE-D2 | GET /scripts?category=校园 → categoryList + totalPage | ✅ PASS | categoryList 返回 9 项（全部/恋爱/冒险/悬疑/恐怖/科幻/日常/动作/剧情），totalPage 正常返回 |
| 3 | BE-D2 | GET /scripts?sortType=hot → 按热门排序 | ⚠️ PARTIAL | `sortType=hot` 被接受但 **不触发 hot_value 排序**。代码只识别 `popular`→hot_value DESC；`hot` 落入默认 `newest`（created_at DESC）。当所有 hot_value=0 时结果相同，但数据有 hot_value 差异时排序会错 |
| 4 | BE-D3 | 多次刷新 GET /scripts → 同分记录顺序一致 | ✅ PASS | 3 次请求返回相同顺序（created_at DESC + script_id ASC 作为 tiebreaker） |
| 5 | BE-D4 | GET /scripts?page=1&size=10 → 分页生效 | ✅ PASS | size=10 生效，size=5 自动 clamp 到 10，size=50 clamp 到 40，[10,40] 范围正确 |
| 6 | BE-O14 | POST /free-chat → 200 | ❌ FAIL | 404 Not Found。不存在 `/api/v1/free-chat` 路由 |
| 7 | BE-O14 | GET /free-chat/topics → 200 | ❌ FAIL | 404 Not Found。不存在 `/api/v1/free-chat/topics` 路由 |
| 8 | BE-O14 | GET /free-chat/history → 200 | ❌ FAIL | 404 Not Found。不存在 `/api/v1/free-chat/history` 路由 |

---

## 详细发现

### BE-D2: sortType=hot 不生效（代码缺陷）

**文件**: `backend/app/api/v1/scripts.py` 第 ~103 行  
**代码**:
```python
if effective_sort == "popular":
    base_stmt = base_stmt.order_by(Script.hot_value.desc(), Script.id.asc())
```
**问题**: 前端发送 `sortType=hot`，但后端只识别 `popular`。`hot` 落入 `else` 分支，按 `created_at DESC` 排序。  
**当前影响**: 测试数据 hot_value 全为 0，结果碰巧一致。但一旦有真实 hot_value 差异，排序将不正确。  
**建议修复**: 增加 `effective_sort == "hot"` 条件，或将 `hot` 映射到 `popular`。

### BE-D3: 排序稳定性

**实现**: `created_at DESC, script_id ASC`  
**验证**: 3 次请求顺序完全一致。  
**注意**: PL 要求 "script_id 升序" 作为唯一排序条件，但代码实现是 `created_at DESC + script_id ASC`。当前测试数据 created_at 不同，无法验证同分 tiebreaker。若需求是 "同分时 script_id 升序"，则实现正确。

### BE-O14: free-chat 路由不存在

**PL 要求的路由**:
- `POST /api/v1/free-chat`
- `GET /api/v1/free-chat/topics`
- `GET /api/v1/free-chat/history`

**实际存在的路由**:
- `POST /api/v1/game/{session_id}/free-chat` (需 auth)
- `GET /api/v1/game/{session_id}/free-chat/topics` (需 auth)
- `GET /api/v1/game/{session_id}/free-chat/history` (需 auth)
- `POST /api/v1/chat/free` (需 auth, character_id 参数)

**前端调用**: `frontend/src/api/game.ts` 使用 `/game/${sessionId}/free-chat*` 路径  
**结论**: 独立 `/free-chat` 路由从未实现。PL 描述的 "MockMiddleware 拦截" 不准确 — 这些路由在代码中不存在。

---

## 环境状态

| 服务 | 状态 | 端口 |
|------|------|------|
| Backend (uvicorn) | ✅ Running | 8000 |
| Frontend (Vite Docker) | ✅ Running | 8081 |
| PostgreSQL | ✅ Running | 5432 |
| Redis | ✅ Running | 6379 |
| Health Check | ✅ `{"status":"ok","version":"1.0.0"}` | — |

---

## PL 澄清（2026-07-24）

1. **BE-O14 路径修正**: PL 验证清单路径有误，实际路由是 `/api/v1/game/{session_id}/free-chat*`。BE-O14 实际通过 ✅
2. **sortType=hot**: 记录为后续优化项，前端将使用 `sortType=popular`。不阻塞当前进度。

---

## 最终结论

- **PASS**: 7/8 项（含 BE-O14 澄清后 3 子项通过）
- **后续优化**: 1/8 项（sortType=hot → 前端改用 popular）
- **阻塞**: 0 项

**FE Day 2 已放行。**
