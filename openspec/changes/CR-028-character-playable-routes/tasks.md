# CR-028 Tasks: 剧本角色选择与多故事线系统

## Implementation Tasks

| 任务编号 | 负责人 Agent | 关联验收项 | 不覆盖验收项 | 允许写入范围 | 测试用例产物 | 验证方式 | 回滚 / 撤销方案 | 状态 |
|----------|--------------|------------|--------------|--------------|--------------|----------|-----------------|------|
| T-028-01 | be | AC-PLAY-007 | 无 | backend/alembic/versions/cr028_character_playable_routes.py | tests/db/test_cr028_migration.py | alembic upgrade head 成功 | alembic downgrade -1 | Done |
| T-028-02 | be | AC-PLAY-007 | 无 | backend/alembic/versions/cr028_character_playable_routes.py | tests/db/test_cr028_migration.py | 数据迁移脚本执行成功 | 回滚到迁移前版本 | Done |
| T-028-03 | be | AC-PLAY-001, AC-PLAY-006 | 无 | backend/app/api/v1/scripts.py | tests/api/test_cr028_scripts.py | API 返回 playable_characters | git revert | Done |
| T-028-04 | be | AC-PLAY-002, AC-PLAY-003 | 无 | backend/app/api/v1/game.py | tests/api/test_cr028_game.py | POST /game/start 支持 character_id | git revert | Done |
| T-028-05 | be | AC-PLAY-004, AC-PLAY-005 | 无 | backend/app/api/v1/saves.py | tests/api/test_cr028_saves.py | GET /saves 返回角色信息 | git revert | Done |
| T-028-06 | be | AC-PLAY-009 | 无 | backend/app/api/v1/characters.py | tests/api/test_cr028_unlock.py | POST /characters/{id}/unlock 成功 | git revert | Done |
| T-028-07 | be | AC-PLAY-002 | 无 | backend/app/services/narrative_engine.py | tests/api/test_cr028_narrative.py | 不同角色生成不同故事线 | git revert | Done |
| T-028-08 | fe | AC-PLAY-001, AC-PLAY-006 | 无 | frontend/src/views/ScriptDetailView.vue | tests/e2e/cr028_character_select.spec.ts | 页面展示可扮演角色 | git revert | Done |
| T-028-09 | fe | AC-PLAY-004 | 无 | frontend/src/views/GameView.vue | tests/e2e/cr028_game_character.spec.ts | 游戏页展示角色信息 | git revert | Done |
| T-028-10 | fe | AC-PLAY-005 | 无 | frontend/src/views/SaveManagerView.vue | tests/e2e/cr028_save_filter.spec.ts | 存档筛选功能正常 | git revert | Done |
| T-028-11 | fe | AC-PLAY-004 | 无 | frontend/src/views/ProfileView.vue | tests/e2e/cr028_profile.spec.ts | 个人中心展示角色信息 | git revert | Done |
| T-028-12 | qa | AC-PLAY-001, AC-PLAY-003, AC-PLAY-004, AC-PLAY-005, AC-PLAY-006 | 无 | tests/e2e/ | tests/e2e/cr028_*.spec.ts | 所有 E2E 测试通过 | 删除测试文件 | Done |
| T-028-13 | qa | AC-PLAY-002, AC-PLAY-007, AC-PLAY-008, AC-PLAY-009 | 无 | tests/api/ tests/db/ | tests/api/test_cr028_*.py tests/db/test_cr028_*.py | 所有 API/DB 测试通过 | 删除测试文件 | Done |

**总工时**: 24h

---

## 详细任务说明

### T-028-01: DB Migration: Schema 变更

**负责人**: be  
**关联 AC**: AC-PLAY-007  
**预估工时**: 2h  
**输入交付物**: `docs/database/database.md` (Character/GameSession 表扩展设计)  
**允许写入范围**: `backend/alembic/versions/`  
**验证方式**: 迁移脚本执行成功，数据库字段正确创建  
**回滚关注点**: 使用 `IF NOT EXISTS` 保证幂等，回滚时 DROP COLUMN

**任务内容**:
1. 创建 Alembic revision
2. Character 表新增 5 字段：playable, playable_route_id, play_description, unlock_type, unlock_price
3. GameSession 表新增 2 字段：character_id, character_name
4. 新建 user_character_unlocks 表（含 UNIQUE 约束和索引）
5. 所有 DDL 使用 `IF NOT EXISTS` / `IF EXISTS` 保证幂等

**验收标准**:
- [ ] `alembic upgrade head` 执行成功
- [ ] characters 表新增 5 字段，类型和约束正确
- [ ] game_sessions 表新增 2 字段，类型和约束正确
- [ ] user_character_unlocks 表创建成功，UNIQUE(user_id, character_id) 约束生效
- [ ] 索引创建成功

---

### T-028-02: DB Migration: 数据迁移脚本

**负责人**: be  
**关联 AC**: AC-PLAY-007  
**预估工时**: 1h  
**输入交付物**: T-028-01 完成  
**允许写入范围**: `backend/alembic/versions/`  
**验证方式**: 迁移后 is_main 角色 playable=true，已有 GameSession 正常加载  
**回滚关注点**: 数据迁移使用条件更新，重复执行不重复修改

**任务内容**:
1. 设置 is_main 角色为 playable=true
2. 设置 playable_route_id 为剧本第一条 Route
3. 设置 play_description 为角色基础介绍
4. 设置 unlock_type='free'
5. 回填已有 GameSession 的 character_name（如有 character_id 但无 character_name）
6. 日志记录 warning：无 is_main 角色的剧本

**验收标准**:
- [ ] 迁移脚本执行成功
- [ ] is_main 角色 playable=true, unlock_type='free'
- [ ] playable_route_id 正确关联
- [ ] 已有 GameSession character_id 保持 NULL
- [ ] 已有 GameSession 可正常加载
- [ ] 存档列表中已有存档显示"默认角色"

---

### T-028-03: BE: Script Service 扩展

**负责人**: be  
**关联 AC**: AC-PLAY-001, AC-PLAY-006  
**预估工时**: 2.5h  
**输入交付物**: `docs/api/api.md` (GET /scripts/{id} 扩展设计)  
**允许写入范围**: `backend/app/services/script_service.py`, `backend/app/schemas/script.py`  
**验证方式**: API 返回 playable_characters 列表，is_unlocked 计算正确  
**回滚关注点**: 新增字段 nullable，不影响现有逻辑

**任务内容**:
1. 扩展 ScriptDetailResponse schema，新增 playable_characters 数组
2. 查询 playable=true 且 playable_route_id IS NOT NULL 的角色
3. 计算 is_unlocked：
   - unlock_type='free' → true
   - unlock_type='paid' → 查 user_character_unlocks 表
   - unlock_type='subscription' → 检查用户 subscription_tier
   - 未登录 → free 类型 true，其余 false
4. 返回角色信息：id, name, avatar_url, play_description, unlock_type, unlock_price, is_unlocked

**验收标准**:
- [ ] GET /scripts/{id} 返回 playable_characters 数组
- [ ] 只返回 playable=true 且 playable_route_id 不为 NULL 的角色
- [ ] is_unlocked 计算逻辑正确
- [ ] 未登录用户返回正确结果
- [ ] 无可扮演角色时返回空数组

---

### T-028-04: BE: Game Service 扩展

**负责人**: be  
**关联 AC**: AC-PLAY-002, AC-PLAY-003  
**预估工时**: 2.5h  
**输入交付物**: `docs/api/api.md` (POST /game/start 扩展设计)  
**允许写入范围**: `backend/app/services/game_service.py`, `backend/app/schemas/game.py`  
**验证方式**: 传入 character_id 后创建 GameSession，route_id 正确关联  
**回滚关注点**: character_id 可选，未传时走原逻辑

**任务内容**:
1. 扩展 StartGameRequest schema，新增可选 character_id 参数
2. character_id 不为 NULL 时：
   - 验证角色 playable=true
   - 使用角色 playable_route_id 作为 route_id
   - 写入 character_id 和 character_name（快照）
3. character_id 为 NULL 时：
   - 使用默认 Route（现有逻辑）
   - character_id=NULL, character_name=NULL
4. 新增错误码 CHARACTER_NOT_PLAYABLE (400)

**验收标准**:
- [ ] POST /game/start 接受可选 character_id 参数
- [ ] 传入 character_id 后，GameSession.route_id 为角色 playable_route_id
- [ ] GameSession.character_id 和 character_name 正确写入
- [ ] 未传 character_id 时走原逻辑，character_id=NULL
- [ ] 角色不可 playable 时返回 400

---

### T-028-05: BE: Saves Service 扩展

**负责人**: be  
**关联 AC**: AC-PLAY-004, AC-PLAY-005  
**预估工时**: 1.5h  
**输入交付物**: `docs/api/api.md` (GET /saves 扩展设计)  
**允许写入范围**: `backend/app/services/save_service.py`, `backend/app/schemas/save.py`  
**验证方式**: API 返回 character_name，支持 character_id 筛选  
**回滚关注点**: 新增字段 nullable，不影响现有逻辑

**任务内容**:
1. 扩展 SaveResponse schema，新增 character_id 和 character_name 字段
2. character_name 为 NULL 时返回 "默认角色"
3. 新增可选查询参数 character_id，支持按角色筛选
4. 更新 SQL 查询，JOIN characters 表获取 character_name

**验收标准**:
- [ ] GET /saves 返回 character_id 和 character_name
- [ ] character_name 为 NULL 时返回 "默认角色"
- [ ] 支持 ?character_id= 筛选参数
- [ ] 筛选后只返回对应角色的存档

---

### T-028-06: BE: Unlock API 实现

**负责人**: be  
**关联 AC**: AC-PLAY-009  
**预估工时**: 1.5h  
**输入交付物**: `docs/api/api.md` (POST /characters/{id}/unlock 设计)  
**允许写入范围**: `backend/app/api/v1/characters.py`, `backend/app/services/character_service.py`  
**验证方式**: 解锁接口正确写入 user_character_unlocks，幂等性验证通过  
**回滚关注点**: 新增接口，不影响现有逻辑

**任务内容**:
1. 创建 POST /characters/{character_id}/unlock 端点
2. 验证 character_id 存在
3. 验证 unlock_type='paid'（free 角色返回 400）
4. 检查 user_character_unlocks 是否已有记录（幂等）
5. 插入 user_character_unlocks 记录（本期直接写入，不扣费）
6. 新增错误码：CHARACTER_NOT_FOUND (404), CHARACTER_NOT_PAID (400)

**验收标准**:
- [ ] POST /characters/{id}/unlock 接口可用
- [ ] 解锁成功后 user_character_unlocks 表新增记录
- [ ] 重复解锁幂等，不插入重复记录
- [ ] 解锁 free 角色返回 400
- [ ] 未登录调用返回 401

---

### T-028-07: BE: NarrativeEngine 改造

**负责人**: be  
**关联 AC**: AC-PLAY-002  
**预估工时**: 3h  
**输入交付物**: `docs/architecture/architecture.md` (PromptBuilder L3 层设计)  
**允许写入范围**: `backend/app/llm/prompts/prompt_builder.py`, `backend/app/services/narrative_engine.py`  
**验证方式**: 不同角色身份注入 Prompt 后，NPC 对话内容不同；未配置角色时走原逻辑  
**回滚关注点**: character_id=NULL 时 L3 为空，完全向后兼容

**任务内容**:
1. PromptBuilder 新增 L3 Player Identity 层（100 tok 预算）
2. 实现 _build_player_identity() 方法：
   - character_id 不为 NULL → 查询 Character 表获取 play_description → 构建 L3
   - character_id 为 NULL → L3 为空字符串
3. NarrativeEngine 调用 PromptBuilder.build() 时传入 game_session
4. 错误处理：Character 查询失败时 L3 使用空字符串
5. 总预算调整为 2400 tokens

**验收标准**:
- [ ] PromptBuilder 新增 L3 层
- [ ] character_id 不为 NULL 时 L3 包含角色身份信息
- [ ] character_id 为 NULL 时 L3 为空
- [ ] 不同角色身份注入后，NPC 对话内容不同
- [ ] 已有 GameSession（character_id=NULL）对话质量不受影响

---

### T-028-08: FE: 剧本详情页角色选择

**负责人**: fe  
**关联 AC**: AC-PLAY-001, AC-PLAY-006  
**预估工时**: 3.5h  
**输入交付物**: `design.md` (剧本详情页设计)  
**允许写入范围**: `frontend/src/views/ScriptDetailView.vue`, `frontend/src/components/LockedCharacterOverlay.vue`, `frontend/src/stores/script.ts`  
**验证方式**: 可扮演角色正确展示，锁定角色显示遮罩，选中状态正确  
**回滚关注点**: 无可扮演角色时不显示角色选择区域

**任务内容**:
1. Script Store 新增 selectedCharacterId 和 playableCharacters 状态
2. 剧本详情页新增"🎮 可扮演角色"区域
3. 角色卡片展示：
   - 已解锁角色：显示「🎮可玩」标识
   - 锁定角色：显示锁定遮罩 + 🔒 + 价格标签
4. 角色选中交互：
   - 点击已解锁角色 → 选中（高亮边框）→ 按钮文案更新
   - 点击锁定角色 → 弹出解锁提示弹窗
5. 开始游戏按钮：
   - 未选中角色 → `🎮 开始游戏`
   - 选中角色 → `🎮 开始游戏（以{角色名}身份）`
6. 创建 LockedCharacterOverlay.vue 组件
7. 创建解锁提示弹窗组件

**验收标准**:
- [ ] 可扮演角色正确展示
- [ ] 锁定角色显示遮罩和价格标签
- [ ] 点击已解锁角色选中，按钮文案更新
- [ ] 点击锁定角色弹出解锁提示
- [ ] 无可扮演角色时不显示角色选择区域

---

### T-028-09: FE: 游戏页角色信息展示

**负责人**: fe  
**关联 AC**: AC-PLAY-004  
**预估工时**: 1h  
**输入交付物**: `design.md` (游戏页角色信息设计)  
**允许写入范围**: `frontend/src/views/GameView.vue`, `frontend/src/stores/game.ts`  
**验证方式**: character_id 不为 NULL 时显示角色信息，为 NULL 时不显示  
**回滚关注点**: character_id 为 NULL 时保持现有 UI

**任务内容**:
1. Game Store 新增 characterId 和 characterName 状态
2. 游戏页顶部新增角色信息区域
3. 展示条件：characterId 不为 NULL
4. 展示内容：`[立绘] 以{characterName}身份探索`
5. 不展示"切换角色"按钮

**验收标准**:
- [ ] character_id 不为 NULL 时显示角色信息
- [ ] character_id 为 NULL 时不显示角色信息区域
- [ ] 不展示切换角色按钮

---

### T-028-10: FE: 存档管理页角色筛选

**负责人**: fe  
**关联 AC**: AC-PLAY-005  
**预估工时**: 1.5h  
**输入交付物**: `design.md` (存档管理页筛选设计)  
**允许写入范围**: `frontend/src/views/SavesView.vue`, `frontend/src/stores/save.ts`  
**验证方式**: 标签栏正确展示，筛选后列表正确更新  
**回滚关注点**: 无角色存档时不显示标签栏

**任务内容**:
1. Save Store 新增 selectedCharacterId 状态
2. 存档管理页顶部新增角色筛选标签栏
3. 标签内容：「全部」+ 各角色名（去重）
4. 点击标签 → 调用 GET /saves?character_id={id}
5. 点击「全部」→ 调用 GET /saves
6. 无角色存档时不显示标签栏

**验收标准**:
- [ ] 标签栏正确展示
- [ ] 「全部」标签默认选中
- [ ] 点击角色标签后列表仅显示该角色存档
- [ ] 点击「全部」后列表恢复
- [ ] 无角色存档时不显示标签栏

---

### T-028-11: FE: 个人中心角色信息

**负责人**: fe  
**关联 AC**: AC-PLAY-004  
**预估工时**: 1h  
**输入交付物**: `design.md` (个人中心角色信息设计)  
**允许写入范围**: `frontend/src/views/ProfileView.vue`  
**验证方式**: 最近扮演角色正确展示，点击跳转正确  
**回滚关注点**: 无角色游戏记录时不显示区域

**任务内容**:
1. 个人中心新增"最近扮演角色"区域
2. 展示条件：用户有 character_id 不为 NULL 的 GameSession
3. 展示内容：角色名 + 立绘
4. 点击跳转到对应剧本详情页
5. 数据来源：GET /saves 取最近一条有 character_id 的记录

**验收标准**:
- [ ] 最近扮演角色正确展示
- [ ] 点击跳转到对应剧本详情页
- [ ] 无角色游戏记录时不显示区域

---

### T-028-12: QA: Browser E2E 测试

**负责人**: qa  
**关联 AC**: AC-PLAY-001, AC-PLAY-003, AC-PLAY-004, AC-PLAY-005, AC-PLAY-006  
**预估工时**: 2.5h  
**输入交付物**: `workflow/changes/CR-028/test-plan.md`  
**允许写入范围**: `tests/e2e/cr028-*.spec.ts`, `tests/e2e/cr028-*.test.ts`  
**验证方式**: 所有 Browser E2E 测试用例通过  
**回滚关注点**: 测试用例可独立运行，不影响现有测试

**任务内容**:
1. 编写 AC-PLAY-001 测试：剧本详情页选择可扮演角色
2. 编写 AC-PLAY-003 测试：切换角色重新游玩，生成新存档
3. 编写 AC-PLAY-004 测试：个人中心存档展示角色信息
4. 编写 AC-PLAY-005 测试：存档管理页按角色筛选
5. 编写 AC-PLAY-006 测试：未解锁角色显示锁定状态
6. 使用 Playwright 编写，遵循 E2E 测试规范
7. 记录 APP_BASE、API_BASE、Mock API=no、截图路径

**验收标准**:
- [ ] 所有 Browser E2E 测试用例通过
- [ ] 截图和 trace 保存到 logs/e2e/
- [ ] 测试报告包含 APP_BASE、API_BASE、Mock API=no

---

### T-028-13: QA: API/DB 测试

**负责人**: qa  
**关联 AC**: AC-PLAY-002, AC-PLAY-007, AC-PLAY-008, AC-PLAY-009  
**预估工时**: 1.5h  
**输入交付物**: `workflow/changes/CR-028/test-plan.md`  
**允许写入范围**: `tests/api/cr028-*.test.ts`, `tests/db/cr028-*.test.ts`  
**验证方式**: 所有 API/DB 测试用例通过  
**回滚关注点**: 测试用例可独立运行，不影响现有测试

**任务内容**:
1. 编写 AC-PLAY-002 测试：不同角色进入不同故事线
2. 编写 AC-PLAY-007 测试：数据迁移后原主角自动可扮演
3. 编写 AC-PLAY-008 测试：直接操作数据库新增可扮演角色
4. 编写 AC-PLAY-009 测试：付费角色解锁接口
5. 验证 GameSession.route_id 正确关联
6. 验证 user_character_unlocks 表数据正确
7. 验证向后兼容：已有 GameSession 正常加载

**验收标准**:
- [ ] 所有 API/DB 测试用例通过
- [ ] GameSession.route_id 正确关联
- [ ] user_character_unlocks 表数据正确
- [ ] 已有 GameSession 正常加载

---

## 任务依赖关系

```
T-028-01 (DB Schema)
    ↓
T-028-02 (数据迁移)
    ↓
T-028-03 (Script Service) ──→ T-028-08 (FE 剧本详情)
    ↓
T-028-04 (Game Service) ──→ T-028-07 (NarrativeEngine) ──→ T-028-09 (FE 游戏页)
    ↓
T-028-05 (Saves Service) ──→ T-028-10 (FE 存档筛选) ──→ T-028-11 (FE 个人中心)
    ↓
T-028-06 (Unlock API) ──→ T-028-08 (FE 剧本详情)
    ↓
T-028-12 (Browser E2E) ──→ 所有 FE 任务完成
T-028-13 (API/DB 测试) ──→ 所有 BE 任务完成
```

---

## 任务执行顺序建议

### Phase 1: 数据层（BE）
1. T-028-01: DB Schema 变更 (2h)
2. T-028-02: 数据迁移脚本 (1h)

### Phase 2: 后端服务层（BE）
3. T-028-03: Script Service 扩展 (2.5h)
4. T-028-04: Game Service 扩展 (2.5h)
5. T-028-05: Saves Service 扩展 (1.5h)
6. T-028-06: Unlock API 实现 (1.5h)
7. T-028-07: NarrativeEngine 改造 (3h)

### Phase 3: 前端实现（FE）
8. T-028-08: 剧本详情页角色选择 (3.5h)
9. T-028-09: 游戏页角色信息展示 (1h)
10. T-028-10: 存档管理页角色筛选 (1.5h)
11. T-028-11: 个人中心角色信息 (1h)

### Phase 4: 测试验证（QA）
12. T-028-12: Browser E2E 测试 (2.5h)
13. T-028-13: API/DB 测试 (1.5h)

---

## 任务状态追踪

| 任务编号 | 状态 | 开始时间 | 完成时间 | 备注 |
|----------|------|----------|----------|------|
| T-028-01 | pending | - | - | - |
| T-028-02 | pending | - | - | - |
| T-028-03 | pending | - | - | - |
| T-028-04 | pending | - | - | - |
| T-028-05 | pending | - | - | - |
| T-028-06 | pending | - | - | - |
| T-028-07 | pending | - | - | - |
| T-028-08 | pending | - | - | - |
| T-028-09 | pending | - | - | - |
| T-028-10 | pending | - | - | - |
| T-028-11 | pending | - | - | - |
| T-028-12 | pending | - | - | - |
| T-028-13 | pending | - | - | - |
