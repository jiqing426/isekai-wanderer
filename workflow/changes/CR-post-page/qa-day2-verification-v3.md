# QA Day 2 接口验证报告 v3（最终）— CR-post-page

**验证时间**: 2026-07-24  
**验证环境**: localhost:8000 (Backend) + localhost:8081 (Frontend Docker)  
**验证方式**: curl + JWT（真实用户 token）  
**Mock API**: no

---

## 验证结果汇总

| # | 任务 | 端点 | 状态 | 详情 |
|---|------|------|------|------|
| 1 | BE-O1 | GET /game/{sessionId}/progress | ✅ PASS | 返回 completion_rate, choice_count, dialogue_count |
| 2 | BE-O2 | GET /game/{sessionId}/status | ✅ PASS | 返回 script_name, character_name, affection_value, affection_level |
| 3 | BE-O3 | POST /game/{sessionId}/dialogue | ✅ PASS | 200，对话已存储，返回完整记录 |
| 4 | BE-O3 | GET /game/{sessionId}/dialogues | ✅ PASS | 返回对话列表，支持分页 |
| 5 | BE-O6 | POST /daily/checkin | ✅ PASS | fragments_earned=11, streak_days=1 |

**通过 5/5 | 失败 0/5**

---

## 详细验证结果

### BE-O1: GET /game/{sessionId}/progress ✅

```json
{
  "session_id": "e7b7eb7f-86d6-4aa8-b15c-07bfdfebc732",
  "script_id": "66666666-6666-6666-6666-666666666666",
  "current_node_id": "99999999-9999-9999-9999-999999999992",
  "total_nodes": 11,
  "explored_nodes": 0,
  "completion_rate": 0.0,
  "progress_percentage": 0.0,
  "choice_count": 0,
  "dialogue_count": 0,
  "status": "active"
}
```

必需字段：completion_rate ✅, choice_count ✅, dialogue_count ✅

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

必需字段：script_name ✅, character_name ✅, affection_value ✅, affection_level ✅

### BE-O3: POST /game/{sessionId}/dialogue ✅

**接口性质**：内部接口，由 game.py 内部调用（如 choice 选择、free-chat 对话后自动存储），不是前端直接调用。

请求：`{"content":"测试对话内容","role":"user","character_id":"77777777-7777-7777-7777-777777777777"}`

```json
{
  "id": "e0ae4ab4-ca19-44e3-8eb2-2eee60f8fa88",
  "session_id": "e7b7eb7f-86d6-4aa8-b15c-07bfdfebc732",
  "role": "user",
  "content": "测试对话内容",
  "character_id": "77777777-7777-7777-7777-777777777777",
  "character_name": null,
  "emotion": null,
  "created_at": "2026-07-23T22:28:52.113188+00:00"
}
```

返回 200 ✅，对话已存储 ✅

**参数说明**：
- `role`：必填，`user` 或 `assistant`
- `content`：必填，对话内容
- `character_id`：可选，角色 ID
- `character_name`：可选，角色名称
- `emotion`：可选，情感标签

### BE-O3: GET /game/{sessionId}/dialogues ✅

```json
{
  "dialogues": [
    {
      "id": "e0ae4ab4-ca19-44e3-8eb2-2eee60f8fa88",
      "session_id": "e7b7eb7f-86d6-4aa8-b15c-07bfdfebc732",
      "role": "user",
      "content": "测试对话内容",
      "character_id": "77777777-7777-7777-7777-777777777777",
      "character_name": null,
      "emotion": null,
      "created_at": "2026-07-23T22:28:52.113188+00:00"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

返回对话列表 ✅，支持分页 ✅

### BE-O6: POST /daily/checkin ✅

```json
{
  "status": "ok",
  "fragments_earned": 11,
  "streak_days": 1,
  "message": "签到成功！获得 11 碎片"
}
```

fragments_earned = 10 + streak_bonus(1) = 11 ✅, streak_days ✅, message ✅

---

## 数据库验证

```
\dt dialogue_history      → ✅ 存在
\dt user_dialogue_counts  → ✅ 存在
```

---

## 结论

**全部通过 5/5。** FE Day 2 可放行开发 BE-O1~O3、BE-O6 相关前端。
