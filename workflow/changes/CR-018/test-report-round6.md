# CR-018 T-008 测试报告

**测试时间**: 2026-07-26 11:30-11:45  
**测试环境**: Docker Compose (backend + frontend + postgres + redis)  
**后端版本**: 1.0.0  
**测试状态**: ❌ 失败（发现关键缺陷）

---

## 测试结果汇总

| 测试项 | 优先级 | 状态 | 说明 |
|-------|-------|------|------|
| T-008: UUID v4 数据迁移 | P1 | ❌ FAIL | JSON 字段内嵌 UUID 未更新，导致外键违反 |

**总计**: 0/1 通过

---

## 详细测试结果

### 1. 数据完整性验证

#### ✅ 列级 UUID 迁移正确

| 表名 | 记录数 | 全部新 UUID v4 |
|-----|-------|---------------|
| scripts | 3 | ✅ |
| characters | 3 | ✅ |
| routes | 12 | ✅ |

**验证 SQL**:
```sql
SELECT 'scripts' as tbl, COUNT(*) as cnt, 
       bool_and(id NOT IN ('11111111-...','a1111111-...','66666666-...')) as all_new_uuid
FROM scripts
-- 结果: scripts | 3 | t
```

#### ✅ 外键关联完整性（列级）

| 外键 | 孤儿记录数 |
|-----|-----------|
| characters.script_id | 0 |
| routes.script_id | 0 |
| game_sessions.script_id | 0 |
| game_sessions.route_id | 0 |
| nodes.route_id | 0 |
| affection.character_id | 0 |

**结论**: 列级外键全部正确。

---

### 2. ❌ 关键缺陷：JSON 字段内嵌 UUID 未更新

**问题描述**:
迁移脚本只更新了列级外键引用，但**未更新 JSON 字段内嵌的 UUID 引用**。

**影响范围**:
- `nodes.content` JSON 字段中 `character_id` 仍为旧硬编码 UUID
- 18 个 nodes 受影响
- 3 个不同的旧 character_id：
  - `22222222-2222-2222-2222-222222222222` (林辰)
  - `a2222222-2222-2222-2222-222222222222` (藤原雪)
  - `77777777-7777-7777-7777-777777777777` (沈星澜)

**验证 SQL**:
```sql
SELECT COUNT(*) as nodes_with_old_char_id,
       COUNT(DISTINCT content->>'character_id') as distinct_old_ids
FROM nodes
WHERE content->>'character_id' IN (
  '22222222-2222-2222-2222-222222222222',
  'a2222222-2222-2222-2222-222222222222',
  '77777777-7777-7777-7777-777777777777'
);
-- 结果: 18 nodes, 3 distinct old IDs
```

**实际错误日志**:
```
sqlalchemy.exc.IntegrityError: insert or update on table "affection" 
violates foreign key constraint "affection_character_id_fkey"
DETAIL: Key (character_id)=(77777777-7777-7777-7777-777777777777) 
is not present in table "characters".
```

**复现步骤**:
1. 注册新用户
2. 开始游戏（选择星月奇缘剧本）
3. 获取对话（成功）
4. 做出选择（失败，500 错误）

**错误堆栈**:
```
File "/app/app/services/narrative/narrative_engine.py", line 438, in process_choice
    affection_change = await self.affection_service.apply_choice_delta(user_id, choice_id)
File "/app/app/services/narrative/affection_service.py", line 93, in apply_choice_delta
    return await self.update_affection(user_id, character_id, delta)
File "/app/app/services/narrative/affection_service.py", line 102, in update_affection
    affection = await self.get_affection(user_id, character_id)
```

**根因分析**:
- `narrative_engine.py` 从 `nodes.content->>'character_id'` 读取 character_id
- 该值仍为旧硬编码 UUID（`77777777-...`）
- 但 `characters` 表已迁移到新 UUID v4
- 尝试插入 `affection` 表时违反外键约束

---

### 3. 功能回归测试

#### ❌ 游戏选择功能完全失效

**测试步骤**:
1. ✅ 注册新用户
2. ✅ 获取剧本列表（3 个剧本）
3. ✅ 开始游戏（指定有 nodes 的 route）
4. ✅ 获取对话（返回 2 个选择）
5. ❌ 做出选择（500 错误）

**错误响应**:
```
POST /api/v1/game/{session_id}/choice - 500
```

**影响**:
- 用户无法进行任何游戏选择
- 好感度系统失效
- 游戏流程完全中断

---

### 4. 备份验证

**备份文件**: `/tmp/backup_before_uuid_migration.sql`
- 文件大小: 447K
- 行数: 4892
- 状态: ✅ 存在

---

## 修复建议

### 方案 1: 补充 JSON 字段更新（推荐）

在迁移脚本中增加 JSON 字段更新步骤：

```sql
-- 3e. 更新 nodes.content JSON 中的 character_id 引用
UPDATE nodes 
SET content = jsonb_set(
    content, 
    '{character_id}', 
    to_jsonb(m.new_id::text)
)
FROM uuid_mapping m
WHERE content->>'character_id' = m.old_id::text;

-- 3f. 更新其他可能包含 UUID 的 JSON 字段（如 choices.next_node_id）
-- 需要根据实际数据结构调整
```

### 方案 2: 回滚迁移

如果 JSON 字段更新复杂，可以：
1. 从备份恢复数据库
2. 重新设计迁移脚本
3. 重新执行迁移

---

## 结论

**❌ T-008 验证失败**

**关键缺陷**:
- 迁移脚本未更新 JSON 字段内嵌的 UUID 引用
- 18 个 nodes 的 `content->>'character_id'` 仍为旧硬编码 UUID
- 导致游戏选择功能完全失效（500 错误）

**影响**:
- P0 级别：核心游戏功能不可用
- 阻塞发布

**退回对象**: be（后端）

**修复优先级**: P0（立即修复）

---

**测试执行**: QA Agent  
**报告生成时间**: 2026-07-26 11:45
