# CR-029 任务清单

## Implementation Tasks

| 任务编号 | 负责人 Agent | 关联验收项 | 不覆盖验收项 | 允许写入范围 | 测试用例产物 | 验证方式 | 回滚 / 撤销方案 | 状态 |
|----------|--------------|------------|--------------|--------------|--------------|----------|-----------------|------|
| T-029-01 | be | AC-BRANCH-001 | 无 | backend/alembic/versions/ | tests/db/test_cr029_migration.py | alembic upgrade head 成功 | alembic downgrade -1 | Ready |
| T-029-02 | be | AC-BRANCH-002 | 无 | backend/app/services/narrative/, backend/app/models/script.py | tests/api/test_cr029_filter.py | 不同角色返回不同节点 | git revert | Ready |
| T-029-03 | be | AC-BRANCH-003 | AC-BRANCH-004, AC-BRANCH-005 | backend/scripts/data/ | tests/e2e/cr029-branch.spec.ts | 选择不同角色看到不同分支，汇合后相同 | DELETE 数据 | Ready |
| T-029-04 | be | AC-BRANCH-004 | 无 | backend/scripts/data/ | tests/e2e/cr029-branch2.spec.ts | 第 2 个剧本分支节点数据正确 | DELETE 数据 | Ready |
| T-029-05 | be | AC-BRANCH-005 | 无 | backend/scripts/data/ | tests/e2e/cr029-branch3.spec.ts | 第 3 个剧本分支节点数据正确 | DELETE 数据 | Ready |
| T-029-06 | be | AC-BRANCH-006 | 无 | backend/scripts/data/ | tests/e2e/cr029-choices.spec.ts | 选择节点显示 3 选项 | DELETE 数据 | Ready |
| T-029-07 | qa | AC-BRANCH-007 | 无 | tests/ | tests/api/test_cr029_compat.py | 现有 session 正常运行 | 删除测试文件 | Ready |

## 任务总览

| 任务编号 | 任务名称 | 负责人 | 关联 AC | 预估工时 | 状态 |
|----------|----------|--------|---------|----------|------|
| T-029-01 | DB Migration: nodes 表新增 character_id 字段 | be | AC-BRANCH-001 | 1h | done |
| T-029-02 | BE: NarrativeEngine 节点过滤逻辑 | be | AC-BRANCH-002 | 3h | done |
| T-029-03 | 数据填充：MVP 剧本角色分支节点（1 个剧本） | be | AC-BRANCH-003 | 2h | done |
| T-029-04 | 数据填充：第 2 个剧本角色分支节点 | be | AC-BRANCH-004 | 2h | deferred |
| T-029-05 | 数据填充：第 3 个剧本角色分支节点 | be | AC-BRANCH-005 | 2h | deferred |
| T-029-06 | 数据填充：选择项数量改为 3 个 | be | AC-BRANCH-006 | 1h | done |
| T-029-07 | QA: 回归测试 | qa | AC-BRANCH-007 | 2h | pending |

**MVP 工时**: 9h（T-029-01/02/03/06/07）
**延后工时**: 4h（T-029-04/05，CEO 条件：先 1 个剧本 MVP）

---

## 详细任务说明

### T-029-01: DB Migration: nodes 表新增 character_id 字段

**负责人**: be
**关联 AC**: AC-BRANCH-001
**预估工时**: 1h
**输入交付物**: `docs/database/database.md`
**允许写入范围**: `backend/alembic/versions/`
**验证方式**: 迁移脚本执行成功，nodes 表包含 character_id 字段
**回滚关注点**: 使用 `IF NOT EXISTS` 保证幂等，回滚时 DROP COLUMN

**任务内容**:
1. 创建 Alembic revision
2. nodes 表新增 character_id 字段（UUID，可空）
3. 创建索引 ix_nodes_character_id
4. 所有 DDL 使用 `IF NOT EXISTS` / `IF EXISTS` 保证幂等

**验收标准**:
- [ ] `alembic upgrade head` 执行成功
- [ ] nodes 表新增 character_id 字段，类型 UUID，可空
- [ ] 索引 ix_nodes_character_id 创建成功
- [ ] 现有节点 character_id 为 NULL

---

### T-029-02: BE: NarrativeEngine 节点过滤逻辑

**负责人**: be
**关联 AC**: AC-BRANCH-002
**预估工时**: 3h
**输入交付物**: `docs/api/api.md`
**允许写入范围**: `backend/app/services/narrative/`
**验证方式**: 不同角色调用 API 返回不同节点
**回滚关注点**: character_id 为 NULL 时走原逻辑

**任务内容**:
1. 修改 `NarrativeEngine.get_next_node()` 方法
2. 根据 `session.character_id` 过滤可见节点
3. 只返回 `character_id` 为 NULL 或匹配当前角色的节点
4. 向后兼容：session.character_id 为 NULL 时只返回 NULL 节点

**验收标准**:
- [ ] 角色A返回 character_id 为 A 或 NULL 的节点
- [ ] 角色B返回 character_id 为 B 或 NULL 的节点
- [ ] 两者返回的分支节点不同
- [ ] session.character_id 为 NULL 时只返回 NULL 节点

---

### T-029-03: 数据填充：MVP 剧本角色分支节点（1 个剧本）

**负责人**: be
**关联 AC**: AC-BRANCH-003
**预估工时**: 2h
**输入交付物**: T-029-01, T-029-02 完成
**允许写入范围**: `backend/scripts/data/`
**验证方式**: 选择不同角色看到不同分支，汇合后相同
**回滚关注点**: 使用 INSERT，回滚时 DELETE

**任务内容**:
1. 确认 MVP 剧本（建议：星月奇缘，待 Q-029-001 确认）
2. 创建分支起点节点（公共）
3. 创建角色A/B/C 专属分支节点（character_id 分别为 A/B/C）
4. 创建汇合节点（公共）
5. 配置选择项指向

**验收标准**:
- [ ] 选择角色A看到专属分支
- [ ] 选择角色B看到专属分支
- [ ] 选择角色C看到专属分支
- [ ] 分支结束后汇合到相同节点

> **待确认 Q-029-001**: MVP 聚焦哪个剧本？建议默认：星月奇缘。展示状态=PRD 自动入口已记录，暂缓到数据填充阶段确认。

---

### T-029-04: 数据填充：第 2 个剧本角色分支节点

**负责人**: be
**关联 AC**: AC-BRANCH-004
**预估工时**: 2h
**状态**: deferred（CEO 条件：MVP 先 1 个剧本）
**PL 处理**: 待 PL 排入后续 CR

---

### T-029-05: 数据填充：第 3 个剧本角色分支节点

**负责人**: be
**关联 AC**: AC-BRANCH-005
**预估工时**: 2h
**状态**: deferred（CEO 条件：MVP 先 1 个剧本）
**PL 处理**: 待 PL 排入后续 CR

---

### T-029-06: 数据填充：选择项数量改为 3 个

**负责人**: be
**关联 AC**: AC-BRANCH-006
**预估工时**: 1h
**输入交付物**: T-029-01 完成
**允许写入范围**: `backend/scripts/data/`
**验证方式**: 到达选择节点显示 3 个选项

**任务内容**:
1. 修改现有选择节点，插入第 3 个选项
2. 或后端动态生成第 3 个选项（"自由输入"或预设选项）

**验收标准**:
- [ ] 选择节点显示 3 个选项
- [ ] 第 3 个选项为预设选项或"自由输入"

> **待确认 Q-029-002**: 第 3 个选项是"自由输入"还是预设选项？建议默认：预设选项。展示状态=PRD 自动入口已记录，暂缓到数据填充阶段确认。

---

### T-029-07: QA: 回归测试

**负责人**: qa
**关联 AC**: AC-BRANCH-007
**预估工时**: 2h
**输入交付物**: T-029-01~03, T-029-06 完成
**允许写入范围**: `tests/`
**验证方式**: 现有 session 正常运行

**任务内容**:
1. 数据库迁移测试
2. 后端 API 过滤逻辑测试
3. MVP 剧本分支数据测试
4. 选择项数量测试
5. 向后兼容测试

**验收标准**:
- [ ] 数据库迁移成功
- [ ] 不同角色看到不同分支内容
- [ ] 分支结束后汇合到相同节点
- [ ] 选择项数量为 3 个
- [ ] 现有 session 正常运行

---

## 任务依赖关系

```
T-029-01 (DB Migration)
    ↓
T-029-02 (NarrativeEngine)
    ↓
T-029-03 (MVP 剧本数据填充)
    ↓
T-029-06 (选择项)
    ↓
T-029-07 (QA 测试)

T-029-04/05 (其他剧本数据填充) - deferred，待 PL 排入后续 CR
```

---

## CEO 条件说明

**CR-028 QA 关闭后再启动 CR-029 DEVELOPMENT**：
- 避免 BE 资源冲突
- PL 在 CR-028 QA 通过后，再触发 CR-029 DEVELOPMENT

**先聚焦 1 个剧本 MVP**：
- T-029-03 仅填充 1 个剧本的分支节点
- T-029-04/05 标记为 deferred，待后续 CR 处理

---

## 创建时间

2026-08-03 13:26

## 更新时间

2026-08-03 14:00 — PM 根据 CEO 条件裁剪，T-029-04/05 标记 deferred
