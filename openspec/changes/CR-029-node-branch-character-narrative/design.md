# CR-029 Design: 节点分支标记与角色专属叙事

## Overview

- nodes 表新增 character_id 字段（UUID，可空），NULL=公共节点，非NULL=分支节点仅该角色可见
- NarrativeEngine 在 get_node_with_choices 层增加可选 character_id 过滤，向后兼容旧 session
- MVP 聚焦 1 个剧本（星月奇缘）创建分支-汇合节点数据
- 选择项数量从 2 个扩展为 3 个
- 前端零改动，过滤在后端完成

## Technical Approach

- 数据层：Alembic 迁移脚本，nodes 表加 character_id FK → characters(id)，创建索引 ix_nodes_character_id，DDL 使用 IF NOT EXISTS 保证幂等
- API 层：ScriptService.get_node_with_choices 增加 session_character_id 参数，WHERE character_id IS NULL OR character_id = :session_character_id；submit_choice 增加二次校验（403 NARRATIVE_NODE_NOT_VISIBLE）
- NarrativeEngine：通过 get_game_session_state 获取已过滤的 current_node，无需大改；current_node=None 时返回明确错误
- 数据填充：分支起点（公共）→ 角色A/B/C分支（character_id 分别为 A/B/C）→ 汇合节点（公共）
- 向后兼容：session.character_id=NULL 时只返回 character_id=NULL 的公共节点

## Technology Decisions

| Decision | Selected | Status | Evidence |
|----------|----------|--------|----------|
| 节点角色过滤字段 | nodes.character_id UUID FK → characters(id)，可空 | Accepted | 复用 CR-028 character_id 模式，PL 确认 |
| 过滤层位置 | ScriptService.get_node_with_choices 层过滤 | Accepted | 设计决策 D-002 design.md，PL 确认，向后兼容验证通过 |
| 第 3 个选项类型 | 预设选项（非自由输入） | Not Required | 纯数据配置，无长期架构影响 |

## Document Sync

| Target Doc | Status | Summary / Evidence |
|------------|--------|-------------------|
| `docs/architecture/architecture.md` | Synced | CR-029 新增 nodes.character_id 字段依赖、ScriptService 过滤层 |
| `docs/api/api.md` | Synced | CR-029 新增错误码 NARRATIVE_NODE_NOT_VISIBLE，API/Data/Mock/Runtime 关系说明 |
| `docs/database/database.md` | Synced | CR-029 nodes 表新增 character_id 字段、索引 ix_nodes_character_id |
| `docs/security/security.md` | Synced | CR-029 节点可见性校验、character_id 参数注入防护 |
| `docs/decisions/decisions.md` | Not Required | 复用 CR-028 character_id 模式，无新 ADR |
| `docs/runtime/runtime-contract.md` | Synced | CR-029 更新 Browser E2E user actions、端点不变 |

## 1. 设计概述

本 CR 在 `nodes` 表新增 `character_id` 字段，使叙事引擎支持"分支-汇合"结构：不同角色看到不同分支节点，最终汇合到公共节点。MVP 聚焦 1 个剧本（星月奇缘）。

### 设计目标

- 节点级角色可见性过滤（character_id NULL = 公共，非 NULL = 分支专属）
- 向后兼容：旧 session（无 character_id）行为不变
- 前端零改动：过滤在后端完成，前端透明消费
- 选择项数量从 2 → 3

### 不做

- 条件触发分支（好感度阈值等，后续 CR）
- 全量 3 个剧本分支数据（CEO 条件：先 1 个剧本 MVP）
- 多结局系统
- 前端可视化分支编辑器

---

## 2. 数据库设计

### 2.1 nodes 表扩展

```sql
ALTER TABLE nodes ADD COLUMN character_id UUID REFERENCES characters(id);
CREATE INDEX ix_nodes_character_id ON nodes(character_id);
```

| 字段 | 类型 | 可空 | 说明 |
|------|------|------|------|
| `character_id` | UUID FK → characters(id) | YES | NULL = 公共节点；非 NULL = 分支节点，仅该角色可见 |

**索引**: `ix_nodes_character_id` — 加速按角色过滤查询。

**幂等性**: 迁移脚本使用 `IF NOT EXISTS` 保证可重复执行。

### 2.2 数据模型关系

```
nodes.character_id ──FK──> characters(id)
                           │
game_sessions.character_id ──FK──> characters(id)  (CR-028 已有)
```

过滤逻辑：`WHERE nodes.character_id IS NULL OR nodes.character_id = :session_character_id`

### 2.3 分支-汇合数据模型（MVP: 星月奇缘）

```
[分支起点] (character_id=NULL, 公共)
    ├── choice A → [角色A分支] (character_id=charA)
    ├── choice B → [角色B分支] (character_id=charB)
    └── choice C → [角色C分支] (character_id=charC)
                        │
                        ▼
               [汇合节点] (character_id=NULL, 公共)
```

- 分支起点：公共选择节点，3 个选项分别指向 3 个角色分支
- 角色分支节点：每个角色 1 个专属节点（character_id 分别为 A/B/C）
- 汇合节点：公共节点，3 个分支的后续选择均指向此节点

---

## 3. 后端改动

### 3.1 Node ORM 模型扩展

**文件**: `backend/app/models/script.py`

```python
class Node(Base):
    # ... existing fields ...
    character_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("characters.id"),
        nullable=True,
        index=True,
    )
```

### 3.2 ScriptService 节点过滤

**文件**: `backend/app/services/narrative/script_service.py`

#### 3.2.1 get_next_node 改造

当前 `get_next_node(choice_id)` 直接通过 choice.next_node_id 加载节点，不涉及过滤。改造方案：

**方案选择：在 `get_node_with_choices` 层增加可选 character_id 过滤**

```python
async def get_node_with_choices(
    self,
    node_id: UUID,
    session_character_id: Optional[UUID] = None,
) -> Optional[Node]:
    """Load a single node with its choices, with optional character filtering."""
    stmt = (
        select(Node)
        .options(selectinload(Node.choices))
        .where(Node.id == node_id)
    )
    # Character filtering: only return node if it's public or matches session character
    if session_character_id is not None:
        stmt = stmt.where(
            or_(
                Node.character_id.is_(None),
                Node.character_id == session_character_id,
            )
        )
    else:
        # No character session → only public nodes
        stmt = stmt.where(Node.character_id.is_(None))

    result = await self.db.execute(stmt)
    return result.scalar_one_or_none()
```

#### 3.2.2 get_game_session_state 改造

传递 `session.character_id` 到节点加载：

```python
async def get_game_session_state(self, session_id: UUID) -> Dict[str, Any]:
    # ... load session ...
    current_node = None
    if session.current_node_id:
        current_node = await self.get_node_with_choices(
            session.current_node_id,
            session_character_id=session.character_id,
        )
    # ...
```

#### 3.2.3 submit_choice 改造

`submit_choice` 中调用 `get_next_node` 后，需要验证下一节点对当前角色可见：

```python
async def submit_choice(self, session_id, choice_id, user_id):
    # ... existing logic ...
    next_node = await self.get_next_node(choice_id)
    if next_node and session.character_id is not None:
        if next_node.character_id is not None and next_node.character_id != session.character_id:
            raise AppException(
                error_code="NARRATIVE_NODE_NOT_VISIBLE",
                status_code=403,
                message="This narrative node is not available for the current character",
            )
    # ...
```

### 3.3 NarrativeEngine 改动

**文件**: `backend/app/services/narrative/narrative_engine.py`

NarrativeEngine 本身不需要大改。核心过滤在 ScriptService 层完成。NarrativeEngine 通过 `get_game_session_state` 获取已过滤的 current_node，自然只看到属于当前角色的节点。

唯一注意：当 `get_game_session_state` 返回 `current_node = None`（节点被过滤掉或不存在），需要给出明确错误：

```python
if not current_node:
    raise AppException(
        error_code="NARRATIVE_NO_NODE",
        status_code=400,
        message="No visible narrative node for current session state",
    )
```

### 3.4 新错误码

| 错误码 | HTTP 状态 | 含义 |
|--------|-----------|------|
| `NARRATIVE_NODE_NOT_VISIBLE` | 403 | 节点对当前角色不可见（character_id 不匹配） |

---

## 4. 数据填充

### 4.1 MVP 剧本：星月奇缘

**文件**: `backend/scripts/data/star_moon_branch_nodes.json`（或直接在 seed 脚本中添加）

**节点结构**:

| 节点 | node_type | character_id | 说明 |
|------|-----------|-------------|------|
| branch_start | choice | NULL | 分支起点，3 个选项 |
| branch_char_a | preset/ai_dialog | char_a | 角色A专属分支 |
| branch_char_b | preset/ai_dialog | char_b | 角色B专属分支 |
| branch_char_c | preset/ai_dialog | char_c | 角色C专属分支 |
| converge_point | preset | NULL | 汇合节点 |

**选择项配置**:

- branch_start → 3 个 choice：
  - choice_a → branch_char_a
  - choice_b → branch_char_b
  - choice_c → branch_char_c
- branch_char_a/b/c → 各 1 个 choice → converge_point

### 4.2 选择项数量扩展

现有选择节点增加第 3 个选项。第 3 个选项为**预设选项**（非自由输入），降低 LLM 成本。

---

## 5. 前端影响

**无改动**。节点过滤在后端完成，前端透明消费：
- `ChoicePanel.vue` 已支持动态数量选项
- SSE choice 事件格式不变
- 前端无需感知 character_id 过滤逻辑

---

## 6. 向后兼容

| 场景 | 行为 |
|------|------|
| 旧 session（character_id=NULL） | 只看到 character_id=NULL 的公共节点，行为与改造前一致 |
| 旧节点（character_id=NULL） | 所有角色可见，不受影响 |
| 新 session + 无分支数据的路由 | 只看到公共节点，等同于原行为 |
| 新 session + 有分支数据的路由 | 按 character_id 过滤，看到公共+专属节点 |

---

## 7. 安全

| 风险 | 缓解 |
|------|------|
| 用户通过 API 直接访问其他角色分支节点 | 后端过滤 + submit_choice 二次校验（403） |
| character_id 参数注入 | 节点 character_id 由数据库 FK 约束，不从客户端接受 |
| 旧 session 越权访问分支节点 | session.character_id=NULL 时只返回公共节点 |

---

## 8. 性能

| 维度 | 影响 |
|------|------|
| 查询性能 | `ix_nodes_character_id` 索引确保过滤查询 O(log n) |
| 数据量 | MVP 仅增加 ~5 个节点，影响可忽略 |
| 缓存 | 无需额外缓存策略 |

---

## 9. 任务拆分建议

| 任务 | 模块 | 输入 | 允许写入范围 | 验证 | 回滚 |
|------|------|------|-------------|------|------|
| T-029-01 DB Migration | DB | database.md | `backend/alembic/versions/` | `alembic upgrade head` 成功 | `alembic downgrade -1` |
| T-029-02 NarrativeEngine | BE | api.md | `backend/app/services/narrative/`, `backend/app/models/script.py` | 不同角色返回不同节点 | 回退代码 |
| T-029-03 MVP 数据填充 | BE | T-029-01/02 | `backend/scripts/data/` | 选择不同角色看到不同分支 | DELETE 数据 |
| T-029-06 选择项扩展 | BE | T-029-01 | `backend/scripts/data/` | 选择节点显示 3 选项 | DELETE 数据 |
| T-029-07 QA 回归 | QA | T-029-01~03/06 | `tests/` | 全部 AC 通过 | N/A |

---

## 10. 文档同步

| 目标文档 | 同步状态 | 说明 |
|----------|----------|------|
| `docs/architecture/architecture.md` | Synced | §CR-029 Additions 新增模块依赖 |
| `docs/api/api.md` | Synced | §CR-029 Additions 新增错误码 + API/Data/Mock/Runtime 关系 |
| `docs/database/database.md` | Synced | §CR-029 Additions nodes 表扩展 |
| `docs/security/security.md` | Synced | §CR-029 Security 新增安全分析 |
| `docs/decisions/decisions.md` | Not Required | 无新 ADR（复用 CR-028 character_id 模式） |
| `docs/runtime/runtime-contract.md` | Synced | §CR-029 Additions 更新 Browser E2E user actions |

---

## 11. 待确认问题

| Q 编号 | 问题 | 阻塞 | 建议默认 | 状态 |
|--------|------|------|----------|------|
| Q-029-001 | MVP 聚焦哪个剧本？ | 否 | 星月奇缘 | BE 数据填充时确认 |
| Q-029-002 | 第 3 个选项是自由输入还是预设？ | 否 | 预设选项 | BE 数据填充时确认 |
| Q-029-003 | 分支节点是否支持条件触发？ | 否 | MVP 不支持 | 后续 CR 考虑 |

---

**创建时间**: 2026-08-03
**Architect**: sa
**状态**: DESIGN in-progress
