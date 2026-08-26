# CR-030 任务清单

## Implementation Tasks

| 任务编号 | 负责人 Agent | 关联验收项 | 不覆盖验收项 | 允许写入范围 | 测试用例产物 | 验证方式 | 回滚 / 撤销方案 | 状态 |
|----------|--------------|------------|--------------|--------------|--------------|----------|-----------------|------|
| T-030-01 | be | AC-CHAP-001 | 无 | backend/app/models/script.py, backend/alembic/versions/ | tests/db/test_cr030_migration.py | alembic upgrade head 成功，字段存在 | alembic downgrade -1 | Ready |
| T-030-02 | be | AC-CHAP-002 | 无 | backend/alembic/versions/ (data migration in upgrade()) | tests/db/test_cr030_data_migration.py | 11条route正确映射到章节 | alembic downgrade -1（字段移除，数据自动回滚） | Ready |
| T-030-03 | be | AC-CHAP-003, AC-CHAP-006 | 无 | backend/app/api/v1/game.py, backend/app/api/v1/scripts.py, backend/app/schemas/game.py, backend/app/schemas/script.py | tests/api/test_cr030_chapter_api.py | API返回章节信息；chapters端点返回正确列表 | git revert | Ready |
| T-030-04 | fe | AC-CHAP-004 | 无 | frontend/src/views/GameView.vue, frontend/src/components/ChapterProgress.vue | tests/e2e/cr030-chapter-display.spec.ts | 进度条显示"第X章：章节名" | git revert | Ready |
| T-030-05 | be | AC-CHAP-005 | 无 | backend/app/api/v1/game.py | tests/api/test_cr030_compat.py | 旧session返回null，游戏流程不受影响 | git revert | Ready |

## 任务总览

| 任务编号 | 任务名称 | 负责人 | 关联 AC | 预估工时 | 依赖 | 状态 |
|----------|----------|--------|---------|----------|------|------|
| T-030-01 | DB Migration: routes表新增chapter_number/chapter_type字段+索引 | be | AC-CHAP-001 | 1h | 无 | Ready |
| T-030-02 | 数据迁移: 11条现有route映射到章节（含回滚脚本） | be | AC-CHAP-002 | 2h | T-030-01 | Ready |
| T-030-03 | BE: API返回章节信息 + 新增 /scripts/{id}/chapters 端点 | be | AC-CHAP-003, AC-CHAP-006 | 3h | T-030-02 | Ready |
| T-030-04 | FE: 进度条显示"第X章：章节名" | fe | AC-CHAP-004 | 2h | T-030-03 | Ready |
| T-030-05 | BE: 向后兼容处理（旧session返回null） | be | AC-CHAP-005 | 1h | T-030-03 | Ready |

**总工时**: 9h

## 任务依赖关系

```
T-030-01 (DB Migration: schema)
    ↓
T-030-02 (数据迁移: 11条route映射)
    ↓
T-030-03 (API: 返回章节信息 + 新端点)
    ↓
T-030-04 (FE: 进度条展示) + T-030-05 (向后兼容)
```

## 任务详细说明

### T-030-01: DB Migration — routes 表新增 chapter 字段

**允许写入范围**:
- `backend/app/models/script.py` — Route 模型新增 `chapter_number`, `chapter_type` 字段
- `backend/alembic/versions/<revision>_add_chapter_fields_to_routes.py` — Alembic migration

**实现要点**:
1. Route 模型新增:
   ```python
   chapter_number: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
   chapter_type: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
   ```
2. Alembic migration:
   - `op.add_column('routes', sa.Column('chapter_number', sa.Integer(), nullable=True))`
   - `op.add_column('routes', sa.Column('chapter_type', sa.String(50), nullable=True))`
   - `op.create_index('ix_routes_chapter_number', 'routes', ['chapter_number'])`
   - `op.create_index('ix_routes_chapter_type', 'routes', ['chapter_type'])`
   - `op.create_index('ix_routes_script_chapter', 'routes', ['script_id', 'chapter_number'])`
3. downgrade() 反向操作

**验证方式**:
```bash
alembic upgrade head
alembic current  # 显示目标版本
docker compose exec -T db psql -U isekai -d isekai -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_name='routes' AND column_name IN ('chapter_number','chapter_type');"
```

**回滚方案**: `alembic downgrade -1`

---

### T-030-02: 数据迁移 — 11条 route 映射到章节

**允许写入范围**:
- `backend/alembic/versions/<revision>_add_chapter_fields_to_routes.py` — 在 upgrade() 中执行数据迁移 SQL

**实现要点**:
1. 在 Alembic migration 的 `upgrade()` 中，schema 变更之后执行数据迁移:
   ```python
   def upgrade():
       # Schema changes first
       op.add_column(...)
       op.create_index(...)
       
       # Data migration: map routes to chapters
       op.execute("""
           UPDATE routes SET chapter_number = 1, chapter_type = 'encounter'
           WHERE script_id = (SELECT id FROM scripts WHERE title = '星月奇缘')
             AND title = '第一章：月夜邂逅';
       """)
       # ... (all 11 routes)
   ```
2. 未匹配到的 route 保持 NULL（不报错）
3. 回滚: downgrade 移除字段，数据自动回滚

**验证方式**:
```bash
docker compose exec -T db psql -U isekai -d isekai -c "
SELECT s.title as script, r.title as route, r.chapter_number, r.chapter_type 
FROM routes r JOIN scripts s ON r.script_id = s.id 
WHERE r.chapter_number IS NOT NULL
ORDER BY s.title, r.chapter_number;"
```
预期: 11 行，无 NULL

**回滚方案**: `alembic downgrade -1`（字段移除，数据自动回滚）

---

### T-030-03: BE API — 返回章节信息 + 新增 chapters 端点

**允许写入范围**:
- `backend/app/api/v1/game.py` — game status 和 dialogue 响应新增章节字段
- `backend/app/api/v1/scripts.py` — 新增 `/scripts/{script_id}/chapters` 端点
- `backend/app/schemas/game.py` — GameStatusResponse 新增字段
- `backend/app/schemas/script.py` — 新增 ChapterResponse, ChapterListResponse

**实现要点**:

1. **扩展 game status** (`GET /game/{session_id}/status`):
   - 从 session.route_id 查询 route 的 chapter_number, chapter_type
   - 映射 chapter_type → chapter_title（encounter→相遇, daily→日常, conflict→冲突, convergence→收束）
   - route 无章节信息时返回 null

2. **扩展 dialogue** (`GET /game/{session_id}/dialogue`):
   - 在现有 chapter/chapter_id 字段基础上，新增 chapter_number, chapter_type, chapter_title
   - 数据来源同 game status

3. **新增 chapters 端点** (`GET /scripts/{script_id}/chapters`):
   - 查询 routes WHERE script_id = ? AND chapter_number IS NOT NULL
   - 按 chapter_number 分组，升序排列
   - 返回章节列表，每章包含 routes 数组
   - 无章节数据时返回空数组

4. **chapter_title 映射**:
   ```python
   CHAPTER_TITLE_MAP = {
       "encounter": "相遇",
       "daily": "日常",
       "conflict": "冲突",
       "convergence": "收束",
   }
   ```

**验证方式**:
```bash
# Game status
curl -sf http://localhost:8000/api/v1/game/{session_id}/status -H "Authorization: Bearer {token}" | jq '.chapter_number, .chapter_type, .chapter_title'

# Chapters list
curl -sf http://localhost:8000/api/v1/scripts/{script_id}/chapters -H "Authorization: Bearer {token}" | jq '.chapters | length'
```

**回滚方案**: `git revert`

---

### T-030-04: FE — 进度条显示章节名

**允许写入范围**:
- `frontend/src/views/GameView.vue` — 消费 chapter_number/chapter_title
- `frontend/src/components/ChapterProgress.vue` — 展示"第X章：章节名"

**实现要点**:
1. 从 game status API 获取 chapter_number, chapter_type, chapter_title
2. 当 chapter_number 不为 null 时，显示"第X章：章节名"
3. 当 chapter_number 为 null 时，降级显示 route.title（现有行为）
4. 章节切换时实时更新文本

**验证方式**: Browser E2E (Playwright)
```typescript
// tests/e2e/cr030-chapter-display.spec.ts
test('进度条显示章节名', async ({ page }) => {
  // 进入游戏 → 验证进度条显示"第X章：章节名"
  await expect(page.locator('.chapter-label')).toContainText('第');
});
```

**回滚方案**: `git revert`

---

### T-030-05: BE — 向后兼容处理

**允许写入范围**:
- `backend/app/api/v1/game.py` — 确保旧 session 返回 null

**实现要点**:
1. 旧 session 的 route 没有 chapter_number/chapter_type → 查询结果为 NULL
2. API 层检测 NULL → 返回 `chapter_number: null, chapter_type: null, chapter_title: null`
3. 旧 session 继续游戏流程不受影响（不依赖 chapter 字段做业务逻辑）
4. 保留现有 `chapter` (route.title) 和 `chapter_id` (route.id) 字段，确保过渡期双格式

**验证方式**:
```bash
# 使用旧 session_id 调用
curl -sf http://localhost:8000/api/v1/game/{old_session_id}/status -H "Authorization: Bearer {token}" | jq '.chapter_number, .chapter_type, .chapter_title'
# 预期: null, null, null
```

**回滚方案**: `git revert`

---

## 创建时间

2026-08-04
