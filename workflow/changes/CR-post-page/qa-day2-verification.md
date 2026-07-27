# QA Day 2 接口验证报告 — CR-post-page

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

### BE-O1: `user_dialogue_counts` 表不存在

**错误**: `asyncpg.exceptions.UndefinedTableError: relation "user_dialogue_counts" does not exist`  
**位置**: `game.py:653` — 查询 `UserDialogueCount` 模型  
**原因**: SQLAlchemy 模型 `UserDialogueCount` 已创建（`models/user_dialogue_count.py`），但 Alembic 迁移未执行，数据库中没有 `user_dialogue_counts` 表。

### BE-O3: `dialogue_history` 表不存在

**错误**: `asyncpg.exceptions.UndefinedTableError: relation "dialogue_history" does not exist`  
**位置**: `game.py:830` — INSERT `DialogueHistory` 模型  
**原因**: SQLAlchemy 模型 `DialogueHistory` 已创建，但 Alembic 迁移未执行，数据库中没有 `dialogue_history` 表。

### 共同根因

BE 创建了模型代码但未运行 `alembic revision --autogenerate` + `alembic upgrade head`。两张新表（`dialogue_history`、`user_dialogue_counts`）在数据库中不存在。

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

1. **BE 需运行 Alembic 迁移**创建 `dialogue_history` 和 `user_dialogue_counts` 两张表
2. 迁移完成后需重新验证 BE-O1 和 BE-O3（共 3 个端点）

## 退回

BE-O1、BE-O3 退回 BE 执行数据库迁移。
