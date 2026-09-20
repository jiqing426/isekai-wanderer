# CR-029 验收追踪

| 验收编号 | 需求编号 | 优先级 | 验收标准 | 来源规格 | 覆盖状态 | 未覆盖原因 | PL 处理 | 设计落点 | OpenSpec Task | 测试用例 / 验证命令 | 状态 |
|----------|----------|--------|----------|----------|----------|------------|--------|----------|---------------|---------------------|------|
| AC-BRANCH-001 | REQ-BRANCH-001 | P0 | DB Migration: nodes 表新增 character_id 字段 | [spec](openspec/changes/CR-029-node-branch-character-narrative/specs/narrative-branch/spec.md) | covered | 无 | 无 | design.md §2 | T-029-01 | tests/db/test_cr029_migration.py | Designed |
| AC-BRANCH-002 | REQ-BRANCH-002 | P0 | NarrativeEngine 节点过滤逻辑 | [spec](openspec/changes/CR-029-node-branch-character-narrative/specs/narrative-branch/spec.md) | covered | 无 | 无 | design.md §3 | T-029-02 | tests/api/test_cr029_filter.py | Designed |
| AC-BRANCH-003 | REQ-BRANCH-003 | P0 | 数据填充：MVP 剧本角色分支节点（1 个剧本） | [spec](openspec/changes/CR-029-node-branch-character-narrative/specs/narrative-branch/spec.md) | covered | 无 | 无 | design.md §4 | T-029-03 | tests/e2e/cr029-branch.spec.ts | Designed |
| AC-BRANCH-004 | REQ-BRANCH-003 | P1 | 数据填充：第 2 个剧本角色分支节点 | [spec](openspec/changes/CR-029-node-branch-character-narrative/specs/narrative-branch/spec.md) | out_of_scope_with_reason | CEO 条件：MVP 先聚焦 1 个剧本，其余延后 | 待 PL 排入后续 CR | design.md §4 | T-029-04 | tests/e2e/cr029-branch2.spec.ts | Designed |
| AC-BRANCH-005 | REQ-BRANCH-003 | P1 | 数据填充：第 3 个剧本角色分支节点 | [spec](openspec/changes/CR-029-node-branch-character-narrative/specs/narrative-branch/spec.md) | out_of_scope_with_reason | CEO 条件：MVP 先聚焦 1 个剧本，其余延后 | 待 PL 排入后续 CR | design.md §4 | T-029-05 | tests/e2e/cr029-branch3.spec.ts | Designed |
| AC-BRANCH-006 | REQ-BRANCH-004 | P1 | 选择项数量：从 2 个改为 3 个 | [spec](openspec/changes/CR-029-node-branch-character-narrative/specs/narrative-branch/spec.md) | covered | 无 | 无 | design.md §5 | T-029-06 | tests/e2e/cr029-choices.spec.ts | Designed |
| AC-BRANCH-007 | REQ-BRANCH-005 | P1 | 向后兼容：现有节点和 session 不受影响 | [spec](openspec/changes/CR-029-node-branch-character-narrative/specs/narrative-branch/spec.md) | covered | 无 | 无 | design.md §6 | T-029-07 | tests/api/test_cr029_compat.py | Designed |

## 验收项总览

| 验收编号 | 需求编号 | 优先级 | 验收标准 | 覆盖状态 | 验证类型 | 未覆盖原因 | PL 处理 | 设计落点 | OpenSpec Task | 测试用例 / 验证命令 | 状态 | 备注 |
|----------|----------|--------|----------|----------|----------|------------|--------|----------|---------------|---------------------|------|------|
| AC-BRANCH-001 | REQ-BRANCH-001 | P0 | DB Migration: nodes 表新增 character_id 字段 | covered | API/DB/Runtime 契约 | 无 | 无 | design.md §2 数据库设计 | T-029-01 | tests/db/test_cr029_migration.py | Designed | 数据来源：迁移脚本执行后 nodes 表包含 character_id 字段 |
| AC-BRANCH-002 | REQ-BRANCH-002 | P0 | NarrativeEngine 节点过滤逻辑 | covered | API/DB/Runtime 契约 | 无 | 无 | design.md §3 后端改动 | T-029-02 | tests/api/test_cr029_filter.py | Designed | 数据来源：不同角色调用 API 返回不同节点 |
| AC-BRANCH-003 | REQ-BRANCH-003 | P0 | 数据填充：MVP 剧本角色分支节点（1 个剧本） | covered | Browser Interaction E2E | 无 | 无 | design.md §4 数据填充 | T-029-03 | tests/e2e/cr029-branch.spec.ts | Designed | 用户动作：选择不同角色 → 看到不同分支 → 汇合到相同节点。CEO 条件：先聚焦 1 个剧本 MVP |
| AC-BRANCH-004 | REQ-BRANCH-003 | P1 | 数据填充：第 2 个剧本角色分支节点 | not_covered | Browser Interaction E2E | CEO 条件：MVP 先聚焦 1 个剧本，其余延后 | 待 PL 排入后续 CR | - | T-029-04 | - | Deferred | 非阻塞，MVP 后迭代 |
| AC-BRANCH-005 | REQ-BRANCH-003 | P1 | 数据填充：第 3 个剧本角色分支节点 | not_covered | Browser Interaction E2E | CEO 条件：MVP 先聚焦 1 个剧本，其余延后 | 待 PL 排入后续 CR | - | T-029-05 | - | Deferred | 非阻塞，MVP 后迭代 |
| AC-BRANCH-006 | REQ-BRANCH-004 | P1 | 选择项数量：从 2 个改为 3 个 | covered | Browser Interaction E2E | 无 | 无 | design.md §5 选择项 | T-029-06 | tests/e2e/cr029-choices.spec.ts | Designed | 用户动作：到达选择节点 → 看到 3 个选项 |
| AC-BRANCH-007 | REQ-BRANCH-005 | P1 | 向后兼容：现有节点和 session 不受影响 | covered | API/DB/Runtime 契约 | 无 | 无 | design.md §6 兼容性 | T-029-07 | tests/api/test_cr029_compat.py | Designed | 数据来源：现有 session 正常运行 |

---

## 详细验收标准

### AC-BRANCH-001 — DB Migration: nodes 表新增 character_id 字段

**需求编号**: REQ-BRANCH-001
**优先级**: P0
**验证类型**: API/DB/Runtime 契约

**验收标准**:
1. **前置条件**: 迁移脚本已准备
2. **用户动作**: 执行 `alembic upgrade head`
3. **数据结果**:
   - `nodes` 表包含 `character_id` 字段（UUID，可空）
   - 索引 `ix_nodes_character_id` 已创建
   - 现有节点 `character_id` 为 NULL
4. **回滚验证**: `alembic downgrade -1` 成功移除字段

**不得用 mock 作为发布证据**: 需真实 PostgreSQL 环境验证

---

### AC-BRANCH-002 — NarrativeEngine 节点过滤逻辑

**需求编号**: REQ-BRANCH-002
**优先级**: P0
**验证类型**: API/DB/Runtime 契约

**验收标准**:
1. **前置条件**: 数据库迁移完成，分支节点数据已填充
2. **用户动作**:
   - 以角色A开始游戏，调用 `GET /game/{session_id}/dialogue`
   - 以角色B开始游戏，调用 `GET /game/{session_id}/dialogue`
3. **数据结果**:
   - 角色A返回 `character_id` 为 NULL 或 A 的节点
   - 角色B返回 `character_id` 为 NULL 或 B 的节点
   - 两者返回的分支节点不同
4. **边界情况**:
   - `session.character_id` 为 NULL 时，只返回 `character_id` 为 NULL 的节点
   - 无匹配节点时，返回错误提示

**不得用 mock 作为发布证据**: 需真实后端验证

---

### AC-BRANCH-003 — 数据填充：MVP 剧本角色分支节点

**需求编号**: REQ-BRANCH-003
**优先级**: P0
**验证类型**: Browser Interaction E2E
**CEO 条件**: 先聚焦 1 个剧本 MVP

**验收标准**:
1. **用户动作**:
   - 选择角色A开始游戏 → 看到角色A专属分支
   - 选择角色B开始游戏 → 看到角色B专属分支
   - 选择角色C开始游戏 → 看到角色C专属分支
2. **可观察结果**:
   - 三个角色的分支内容不同
   - 分支结束后，三个角色汇合到相同节点
   - 汇合后的剧情一致

> **待确认 Q-029-001**: MVP 聚焦哪个剧本？建议默认：星月奇缘。展示状态=PRD 自动入口已记录，暂缓到数据填充阶段确认。

---

### AC-BRANCH-004 — 数据填充：第 2 个剧本角色分支节点

**需求编号**: REQ-BRANCH-003
**优先级**: P1
**验证类型**: Browser Interaction E2E
**覆盖状态**: not_covered
**未覆盖原因**: CEO 条件：MVP 先聚焦 1 个剧本，其余延后
**PL 处理**: 待 PL 排入后续 CR

---

### AC-BRANCH-005 — 数据填充：第 3 个剧本角色分支节点

**需求编号**: REQ-BRANCH-003
**优先级**: P1
**验证类型**: Browser Interaction E2E
**覆盖状态**: not_covered
**未覆盖原因**: CEO 条件：MVP 先聚焦 1 个剧本，其余延后
**PL 处理**: 待 PL 排入后续 CR

---

### AC-BRANCH-006 — 选择项数量：从 2 个改为 3 个

**需求编号**: REQ-BRANCH-004
**优先级**: P1
**验证类型**: Browser Interaction E2E

**验收标准**:
1. **用户动作**: 到达选择节点
2. **可观察结果**:
   - 显示 3 个选项（而不是 2 个）
   - 第 3 个选项为预设选项或"自由输入"
3. **数据验证**:
   - `node_choices` 表包含 3 条记录

> **待确认 Q-029-002**: 第 3 个选项是"自由输入"还是预设选项？建议默认：预设选项。展示状态=PRD 自动入口已记录，暂缓到数据填充阶段确认。

---

### AC-BRANCH-007 — 向后兼容：现有节点和 session 不受影响

**需求编号**: REQ-BRANCH-005
**优先级**: P1
**验证类型**: API/DB/Runtime 契约

**验收标准**:
1. **前置条件**: 数据库迁移完成
2. **用户动作**:
   - 以现有 session（无 character_id）继续游戏
   - 调用 `GET /game/{session_id}/dialogue`
3. **数据结果**:
   - 返回 `character_id` 为 NULL 的节点
   - 现有剧情正常运行
4. **边界情况**:
   - 旧 session 的 `character_id` 为 NULL，只看到公共节点

---

## 验收追踪日志

| 时间 | 验收编号 | 状态 | 验证结果 | 备注 |
|------|----------|------|----------|------|
| 2026-08-03T14:00:00+08:00 | ALL | Designed | PM 完成验收标准细化 | CEO 条件：MVP 先 1 个剧本，AC-BRANCH-004/005 标记 Deferred |
