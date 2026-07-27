# QA Day 2 接口验证报告 v2 — CR-post-page

**验证时间**: 2026-07-24  
**验证环境**: localhost:8000 (Backend) + localhost:8081 (Frontend Docker)  
**验证方式**: curl + JWT（真实用户 token）  
**Mock API**: no

---

## 验证结果汇总

| # | 任务 | 端点 | 状态 | 详情 |
|---|------|------|------|------|
| 1 | BE-O1 | GET /game/{sessionId}/progress | ❌ FAIL | 500 — `user_dialogue_counts` 表不存在 |
| 2 | BE-O2 | GET /game/{sessionId}/status | ✅ PASS | 返回 script_name, character_name, affection_value, affection_level |
| 3 | BE-O3 | POST /game/{sessionId}/dialogue | ❌ FAIL | 500 — `dialogue_history` 表不存在 |
| 4 | BE-O3 | GET /game/{sessionId}/dialogues | ❌ FAIL | 500 — `dialogue_history` 表不存在 |
| 5 | BE-O6 | POST /daily/checkin | ✅ PASS | fragments_earned=11, streak_days=1, message 正常 |

**通过 2/5 | 失败 3/5**

---

## 根因分析

### 数据库表缺失

BE 声称已执行 Alembic 迁移，但实际验证发现：

```bash
$ docker exec isekai-wanderer-db-1 psql -U isekai -d isekai -c "\dt dialogue_history"
Did not find any relation named "dialogue_history".

$ docker exec isekai-wanderer-db-1 psql -U isekai -d isekai -c "\dt user_dialogue_counts"
Did not find any relation named "user_dialogue_counts".
```

### Alembic 执行失败

```bash
$ cd /root/isekai-wanderer/backend && source .venv/bin/activate && alembic current
ModuleNotFoundError: No module named 'app'
```

Alembic 无法加载 `app` 模块，迁移脚本未实际执行。

### 错误详情

**BE-O1** (`game.py:653`):
```
asyncpg.exceptions.UndefinedTableError: relation "user_dialogue_counts" does not exist
[SQL: SELECT user_dialogue_counts.dialogue_count FROM user_dialogue_counts 
WHERE user_dialogue_counts.user_id = $1::UUID AND user_dialogue_counts.script_id = $2::UUID]
```

**BE-O3** (`game.py:830`):
```
asyncpg.exceptions.UndefinedTableError: relation "dialogue_history" does not exist
[SQL: INSERT INTO dialogue_history (id, session_id, user_id, role, content, character_id, character_name, emotion, created_at) 
VALUES ($1::UUID, $2::UUID, $3::UUID, $4::VARCHAR, $5::VARCHAR, $6::UUID, $7::VARCHAR, $8::VARCHAR, $9::TIMESTAMP WITH TIME ZONE)]
```

---

## 通过的接口详情

### BE-O2: GET /game/{sessionId}/status ✅

```json
{
  "session_id": "e7b7eb7f-86d6-4aa8-b15c-07bfdfebc732",
  "script_id": "66666666-6666-6666-6666-666666666666",
  "script_name": "星月奇缘",
  "character_id": "77777777-7777-7777-7777-777777777777",
  "character_name": "沈星澜",
  "affection_value": 3,
  "affection_level": "acquaintance",
  "status": "active",
  "current_node_id": "99999999-9999-9999-9999-999999999992"
}
```

包含所有必需字段：script_name ✅, character_name ✅, affection_value ✅, affection_level ✅

### BE-O6: POST /daily/checkin ✅

```json
{
  "status": "ok",
  "fragments_earned": 11,
  "streak_days": 1,
  "message": "签到成功！获得 11 碎片"
}
```

fragments_earned = 10 + streak_bonus ✅, streak_days ✅, message ✅

---

## 阻塞项

1. **BE 需修复 Alembic 环境问题**：`ModuleNotFoundError: No module named 'app'`
2. **BE 需实际执行数据库迁移**：创建 `dialogue_history` 和 `user_dialogue_counts` 两张表
3. 迁移完成后需重新验证 BE-O1 和 BE-O3（共 3 个端点）

## 退回

BE-O1、BE-O3 退回 BE 执行数据库迁移。BE 需确保：
1. 修复 Alembic 环境配置（PYTHONPATH 或工作目录）
2. 生成迁移脚本：`alembic revision --autogenerate -m "add dialogue_history and user_dialogue_counts"`
3. 执行迁移：`alembic upgrade head`
4. 验证表已创建：`\dt dialogue_history` 和 `\dt user_dialogue_counts`
