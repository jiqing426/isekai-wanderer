# CR-030 验收追踪

| 验收编号 | 需求编号 | 优先级 | 验收标准 | 来源规格 | 覆盖状态 | 未覆盖原因 | PL 处理 | 设计落点 | OpenSpec Task | 测试用例 / 验证命令 | 状态 |
|----------|----------|--------|----------|----------|----------|------------|--------|----------|---------------|---------------------|------|
| AC-CHAP-001 | REQ-CHAP-001 | P0 | DB Migration: routes表新增chapter_number和chapter_type字段，执行alembic upgrade head成功 | openspec/changes/chapter-structure-refactor/specs/chapter-structure/spec.md | covered | 无 | 无 | design.md §1.1 | T-030-01 | tests/db/test_cr030_migration.py | Verified |
| AC-CHAP-002 | REQ-CHAP-002 | P0 | 数据迁移: 11条route正确映射到章节（星月奇缘3条、星辰之约4条、樱花恋曲4条） | openspec/changes/chapter-structure-refactor/specs/chapter-structure/spec.md | covered | 无 | 无 | design.md §1.2 | T-030-02 | tests/db/test_cr030_data_migration.py | Verified |
| AC-CHAP-003 | REQ-CHAP-003 | P0 | API返回: GET /game/{session_id}/status 响应包含chapter_number、chapter_type、chapter_title字段 | openspec/changes/chapter-structure-refactor/specs/chapter-structure/spec.md | covered | 无 | 无 | design.md §2.1 | T-030-03 | tests/api/test_cr030_chapter_api.py | Verified |
| AC-CHAP-004 | REQ-CHAP-004 | P1 | 前端展示: 进度条显示"第X章：章节名"，章节切换时实时更新 | openspec/changes/chapter-structure-refactor/specs/chapter-structure/spec.md | covered | 无 | 无 | design.md §3 | T-030-04 | tests/e2e/cr030-chapter-display.spec.ts | Verified |
| AC-CHAP-005 | REQ-CHAP-005 | P1 | 向后兼容: 旧session查询返回chapter_number=null，游戏流程不受影响 | openspec/changes/chapter-structure-refactor/specs/chapter-structure/spec.md | covered | 无 | 无 | design.md §4 | T-030-05 | tests/api/test_cr030_compat.py | Verified |
| AC-CHAP-006 | REQ-CHAP-006 | P1 | 剧本章节列表API: GET /scripts/{script_id}/chapters 返回章节数组，按chapter_number升序 | openspec/changes/chapter-structure-refactor/specs/chapter-structure/spec.md | covered | 无 | 无 | design.md §2.2 | T-030-03 | tests/api/test_cr030_chapter_api.py | Verified |

## 验收项明细

### AC-CHAP-001 — DB Migration: routes 表新增 chapter 字段

**验收标准**:

1. **用户/操作**: BE 执行 `alembic upgrade head`
2. **可观察结果**: 命令退出码 0，`alembic current` 显示目标版本号
3. **数据状态**: `SELECT column_name, data_type FROM information_schema.columns WHERE table_name='routes' AND column_name IN ('chapter_number','chapter_type')` 返回两行：
   - `chapter_number` / `INTEGER`
   - `chapter_type` / `VARCHAR(50)`
4. **回滚验证**: 执行 `alembic downgrade -1` 后，上述查询返回 0 行

**测试用例**: `tests/db/test_cr030_migration.py`  
**验证约束**: 需要真实后端/数据库状态验证，不得用 mock 作为发布证据

---

### AC-CHAP-002 — 数据迁移: 现有 route 正确映射到章节

**验收标准**:

1. **用户/操作**: BE 执行数据迁移脚本
2. **可观察结果**: 脚本退出码 0，无报错
3. **数据状态**: 执行以下 SQL 验证：
   ```sql
   -- 星月奇缘（3条route）
   SELECT title, chapter_number, chapter_type FROM routes 
   WHERE script_id='星月奇缘' ORDER BY chapter_number;
   -- 预期: 第一章：月夜邂逅/1/encounter, 第二章：星辰之约/2/daily, 第三章：命运交织/3/conflict
   
   -- 星辰之约（4条route）
   SELECT title, chapter_number, chapter_type FROM routes 
   WHERE script_id='星辰之约' ORDER BY chapter_number;
   -- 预期: 星夜邂逅/1/encounter, 林辰线：星光指引/2/daily, 流星线：刹那永恒/3/conflict, 银河线：命运交汇/4/convergence
   
   -- 樱花恋曲（4条route）
   SELECT title, chapter_number, chapter_type FROM routes 
   WHERE script_id='樱花恋曲' ORDER BY chapter_number;
   -- 预期: 樱花树下/1/encounter, 月夜线：静谧之恋/2/daily, 阳菜线：夏日恋歌/3/conflict, 雪乃线：樱花树下的约定/4/convergence
   ```
4. **完整性**: 11 条 route 全部映射，无 NULL 值
5. **回滚验证**: 执行回滚脚本后，所有 chapter_number 和 chapter_type 恢复为 NULL

**测试用例**: `tests/db/test_cr030_data_migration.py`  
**验证约束**: 需要真实后端/数据库状态验证，不得用 mock 作为发布证据

---

### AC-CHAP-003 — API 返回: 游戏状态包含章节信息

**验收标准**:

1. **用户/操作**: 调用 `GET /api/v1/game/{session_id}/status`，session 处于某剧本的第 N 章
2. **可观察结果**: HTTP 200，响应 JSON 包含：
   - `chapter_number`: INTEGER，等于当前 route 对应的章节编号
   - `chapter_type`: STRING，等于当前 route 对应的章节类型（encounter/daily/conflict/convergence）
   - `chapter_title`: STRING，章节中文名称
3. **章节切换**: 用户从第 1 章进入第 2 章后，再次调用 API，`chapter_number` 和 `chapter_type` 更新为新章节值
4. **数据来源**: 章节信息从 routes 表的 chapter_number/chapter_type 字段读取，与当前 session 所在 route 关联

**测试用例**: `tests/api/test_cr030_chapter_api.py`  
**验证约束**: 需要真实后端/API 状态验证，不得用 mock 作为发布证据

---

### AC-CHAP-004 — 前端展示: 进度条显示章节名

**验收标准**:

1. **用户动作**: 用户打开游戏界面，进入某剧本的第 N 章
2. **可观察结果**: 进度条上方/旁边显示文本"第 N 章：章节名"（如"第 2 章：日常"）
3. **章节切换**: 用户从第 1 章推进到第 2 章时，文本实时更新为"第 2 章：日常"
4. **数据来源**: 章节信息从 `GET /api/v1/game/{session_id}/status` 的 `chapter_number` 和 `chapter_title` 字段获取

**测试用例**: `tests/e2e/cr030-chapter-display.spec.ts`  
**验证约束**: 需要浏览器交互验证（Browser Interaction E2E Plan）

---

### AC-CHAP-005 — 向后兼容: 旧 session 不受影响

**验收标准**:

1. **用户/操作**: 调用 `GET /api/v1/game/{session_id}/status`，session_id 为迁移前创建的旧 session
2. **可观察结果**: HTTP 200，响应 JSON 包含：
   - `chapter_number`: null
   - `chapter_type`: null
   - `chapter_title`: null
3. **游戏流程**: 旧 session 继续执行游戏操作（选择选项、推进剧情），无报错，功能正常
4. **无副作用**: 旧 session 的游戏状态、进度、route 选择等不受影响

**测试用例**: `tests/api/test_cr030_compat.py`  
**验证约束**: 需要真实后端/API 状态验证，不得用 mock 作为发布证据

---

### AC-CHAP-006 — 剧本章节列表 API

**验收标准**:

1. **用户/操作**: 调用 `GET /api/v1/scripts/{script_id}/chapters`
2. **可观察结果**: HTTP 200，响应 JSON 包含 `chapters` 数组，每个元素包含：
   - `chapter_number`: INTEGER
   - `chapter_type`: STRING
   - `title`: STRING（章节中文名称）
   - `routes`: ARRAY（该章节包含的 route 列表）
3. **章节顺序**: 按 chapter_number 升序排列
4. **数据完整性**: 星月奇缘返回 3 个章节，星辰之约返回 4 个章节，樱花恋曲返回 4 个章节

**测试用例**: `tests/api/test_cr030_chapter_api.py`  
**验证约束**: 需要真实后端/API 状态验证，不得用 mock 作为发布证据

---

## 创建时间

2026-08-04
