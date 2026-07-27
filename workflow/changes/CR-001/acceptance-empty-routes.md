# 6 个空 Route 修复验收方案

**CR-ID**: CR-001  
**制定时间**: 2026-07-27 10:00  
**制定人**: PM  
**状态**: 待 QA 执行

---

## 1. 验收目标

验证 6 个空 route 已成功补充 nodes 和 choices 数据，且游戏流程可正常走通。

---

## 2. 验收标准

### AC-FIX-01: 数据完整性 - Nodes 数量

**验收条件**: 6 个 route 各有 6 个 nodes

**验证方式**:
```sql
SELECT r.title, COUNT(n.id) as node_count
FROM routes r
JOIN nodes n ON n.route_id = r.id
WHERE r.id IN (
  '8ff72661-2954-4665-a611-5a63ce758996',  -- 双星线：命运交织
  'a41282b0-c27d-4868-aa1c-88ba08d50040',  -- 星澜线：星辰之约
  '90cf1451-80db-45a2-968e-aa84507bb854',  -- 辉夜线：月影传说
  '89424ab0-74d6-4fad-be8c-d2fd911f7323',  -- 月夜线：静谧之恋
  '55761d28-289f-445b-82ef-fa9709d5d507',  -- 阳菜线：夏日恋歌
  '8bb89d32-d99e-41ee-8a93-33b1f36ff3ee'   -- 雪乃线：樱花树下的约定
)
GROUP BY r.id, r.title
HAVING COUNT(n.id) = 6;
```

**预期结果**: 返回 6 行，每行 node_count = 6

---

### AC-FIX-02: 数据完整性 - Choices 数量

**验收条件**: 6 个 route 各有 6 个 choices

**验证方式**:
```sql
SELECT r.title, COUNT(nc.id) as choice_count
FROM routes r
JOIN nodes n ON n.route_id = r.id
JOIN node_choices nc ON nc.node_id = n.id
WHERE r.id IN (
  '8ff72661-2954-4665-a611-5a63ce758996',
  'a41282b0-c27d-4868-aa1c-88ba08d50040',
  '90cf1451-80db-45a2-968e-aa84507bb854',
  '89424ab0-74d6-4fad-be8c-d2fd911f7323',
  '55761d28-289f-445b-82ef-fa9709d5d507',
  '8bb89d32-d99e-41ee-8a93-33b1f36ff3ee'
)
GROUP BY r.id, r.title
HAVING COUNT(nc.id) = 6;
```

**预期结果**: 返回 6 行，每行 choice_count = 6

---

### AC-FIX-03: 数据结构 - Opening Node

**验收条件**: 每个 route 有且仅有 1 个 opening node (parent_id=NULL)

**验证方式**:
```sql
SELECT r.title, COUNT(n.id) as opening_count
FROM routes r
JOIN nodes n ON n.route_id = r.id
WHERE r.id IN (
  '8ff72661-2954-4665-a611-5a63ce758996',
  'a41282b0-c27d-4868-aa1c-88ba08d50040',
  '90cf1451-80db-45a2-968e-aa84507bb854',
  '89424ab0-74d6-4fad-be8c-d2fd911f7323',
  '55761d28-289f-445b-82ef-fa9709d5d507',
  '8bb89d32-d99e-41ee-8a93-33b1f36ff3ee'
)
AND n.parent_id IS NULL
GROUP BY r.id, r.title
HAVING COUNT(n.id) = 1;
```

**预期结果**: 返回 6 行，每行 opening_count = 1

---

### AC-FIX-04: 数据结构 - Ending Nodes

**验收条件**: 每个 route 有 3 个 ending (good/normal/bad)

**验证方式**:
```sql
SELECT r.title, 
       COUNT(CASE WHEN n.content->>'scene' = 'good_ending' THEN 1 END) as good_endings,
       COUNT(CASE WHEN n.content->>'scene' = 'normal_ending' THEN 1 END) as normal_endings,
       COUNT(CASE WHEN n.content->>'scene' = 'bad_ending' THEN 1 END) as bad_endings
FROM routes r
JOIN nodes n ON n.route_id = r.id
WHERE r.id IN (
  '8ff72661-2954-4665-a611-5a63ce758996',
  'a41282b0-c27d-4868-aa1c-88ba08d50040',
  '90cf1451-80db-45a2-968e-aa84507bb854',
  '89424ab0-74d6-4fad-be8c-d2fd911f7323',
  '55761d28-289f-445b-82ef-fa9709d5d507',
  '8bb89d32-d99e-41ee-8a93-33b1f36ff3ee'
)
AND n.node_type = 'ending'
GROUP BY r.id, r.title;
```

**预期结果**: 返回 6 行，每行 good_endings=1, normal_endings=1, bad_endings=1

---

### AC-FIX-05: API 验证 - Game Start

**验收条件**: POST /game/start 对每个 route 返回 200 + session_id

**验证方式**: 对每个 route 执行以下 API 调用

```bash
# 获取 test token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123456"}' | jq -r '.access_token')

# 测试每个 route
for route_id in \
  "8ff72661-2954-4665-a611-5a63ce758996" \
  "a41282b0-c27d-4868-aa1c-88ba08d50040" \
  "90cf1451-80db-45a2-968e-aa84507bb854" \
  "89424ab0-74d6-4fad-be8c-d2fd911f7323" \
  "55761d28-289f-445b-82ef-fa9709d5d507" \
  "8bb89d32-d99e-41ee-8a93-33b1f36ff3ee"; do
  
  # 获取 route 对应的 script_id
  script_id=$(docker exec isekai-wanderer-db-1 psql -U isekai -d isekai -t -c \
    "SELECT script_id FROM routes WHERE id='$route_id'" | tr -d ' ')
  
  echo "Testing route: $route_id (script: $script_id)"
  
  response=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/api/v1/game/start \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"script_id\":\"$script_id\",\"route_id\":\"$route_id\"}")
  
  http_code=$(echo "$response" | tail -1)
  body=$(echo "$response" | head -n -1)
  
  echo "HTTP $http_code"
  echo "$body" | jq .
  echo ""
done
```

**预期结果**: 
- HTTP 200
- 响应包含 `session_id` 字段
- 响应包含 `node_id` 字段

---

### AC-FIX-06: E2E 验证 - 完整游戏流程

**验收条件**: 选择→对话→结局流程可走通

**验证方式**: 手动或自动化测试以下流程

1. 选择任意一个修复的 route 开始游戏
2. 获取对话内容 (GET /game/{session_id}/dialogue)
3. 提交选择 (POST /game/{session_id}/choice)
4. 重复步骤 2-3 直到到达结局
5. 验证结局类型 (good/normal/bad)

**测试用例**:

| Route | 路径 | 预期结局 |
|-------|------|----------|
| 双星线：命运交织 | opening → friendly → good_ending | good |
| 星澜线：星辰之约 | opening → friendly → normal_ending | normal |
| 辉夜线：月影传说 | opening → cold → bad_ending | bad |
| 月夜线：静谧之恋 | opening → friendly → good_ending | good |
| 阳菜线：夏日恋歌 | opening → cold → normal_ending | normal |
| 雪乃线：樱花树下的约定 | opening → friendly → normal_ending | normal |

---

## 3. 验收执行清单

- [x] AC-FIX-01: 验证 nodes 数量 ✅
- [x] AC-FIX-02: 验证 choices 数量 ✅
- [x] AC-FIX-03: 验证 opening node ✅
- [x] AC-FIX-04: 验证 ending nodes ✅
- [x] AC-FIX-05: 验证 API 返回 ✅
- [x] AC-FIX-06: 验证游戏流程 ✅

---

## 4. 验收报告模板

```markdown
# 验收报告

**验收时间**: 
**验收人**: QA

## 验收结果

| AC-ID | 验收项 | 结果 | 备注 |
|-------|--------|------|------|
| AC-FIX-01 | Nodes 数量 | ✅/❌ | |
| AC-FIX-02 | Choices 数量 | ✅/❌ | |
| AC-FIX-03 | Opening node | ✅/❌ | |
| AC-FIX-04 | Ending nodes | ✅/❌ | |
| AC-FIX-05 | API 验证 | ✅/❌ | |
| AC-FIX-06 | 游戏流程 | ✅/❌ | |

## 总结

- 通过: X/6
- 失败: X/6

## 问题记录

（如有失败项，记录具体问题）
```

---

## 5. 回滚方案

如验收失败，可按以下 SQL 回滚：

```sql
-- 删除新增的 choices
DELETE FROM node_choices 
WHERE node_id IN (
  SELECT n.id FROM nodes n
  JOIN routes r ON r.id = n.route_id
  WHERE r.id IN (
    '8ff72661-2954-4665-a611-5a63ce758996',
    'a41282b0-c27d-4868-aa1c-88ba08d50040',
    '90cf1451-80db-45a2-968e-aa84507bb854',
    '89424ab0-74d6-4fad-be8c-d2fd911f7323',
    '55761d28-289f-445b-82ef-fa9709d5d507',
    '8bb89d32-d99e-41ee-8a93-33b1f36ff3ee'
  )
);

-- 删除新增的 nodes
DELETE FROM nodes 
WHERE route_id IN (
  '8ff72661-2954-4665-a611-5a63ce758996',
  'a41282b0-c27d-4868-aa1c-88ba08d50040',
  '90cf1451-80db-45a2-968e-aa84507bb854',
  '89424ab0-74d6-4fad-be8c-d2fd911f7323',
  '55761d28-289f-445b-82ef-fa9709d5d507',
  '8bb89d32-d99e-41ee-8a93-33b1f36ff3ee'
);
```
