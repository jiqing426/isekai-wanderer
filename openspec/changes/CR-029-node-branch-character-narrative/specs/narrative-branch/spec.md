# Spec: 节点分支标记与角色专属叙事

### Requirement: REQ-BRANCH-001 — 节点角色可见性标记

系统必须支持按角色过滤叙事节点，使不同角色只能看到属于自己的分支剧情。

#### Scenario: 公共节点对所有角色可见

- **Given**: 存在 `character_id = NULL` 的公共节点
- **When**: 任意角色（或无角色 session）请求下一个节点
- **Then**: 返回该公共节点

#### Scenario: 分支节点仅对指定角色可见

- **Given**: 存在 `character_id = A` 的分支节点
- **When**: 角色A 的 session 请求下一个节点
- **Then**: 返回该分支节点

#### Scenario: 分支节点对其他角色不可见

- **Given**: 存在 `character_id = A` 的分支节点
- **When**: 角色B 的 session 请求下一个节点
- **Then**: 不返回该节点，返回匹配的公共节点或其他角色B可见节点

#### Scenario: 无角色 session 仅见公共节点

- **Given**: session 的 `character_id` 为 NULL
- **When**: 请求下一个节点
- **Then**: 仅返回 `character_id = NULL` 的公共节点

---

### Requirement: REQ-BRANCH-002 — 叙事引擎节点过滤

`NarrativeEngine` 在获取下一节点时，必须根据当前 session 的角色 ID 过滤可见节点。

#### Scenario: 过滤逻辑正确应用

- **Given**: 数据库中存在公共节点 N1（character_id=NULL）和分支节点 N2（character_id=A）、N3（character_id=B）
- **When**: 角色A session 调用 `get_next_node()`
- **Then**: 返回 N1 或 N2，不返回 N3

#### Scenario: 向后兼容旧 session

- **Given**: 旧 session 无 `character_id`（NULL）
- **When**: 调用 `get_next_node()`
- **Then**: 仅返回 `character_id = NULL` 的节点，行为与改造前一致

---

### Requirement: REQ-BRANCH-003 — MVP 剧本分支数据（P0，1 个剧本）

为 MVP 剧本创建分支-汇合节点数据，验证分支叙事结构可行。

> **待确认 Q-029-001**: MVP 聚焦哪个剧本？建议默认：星月奇缘。展示状态=非阻塞/暂缓，PRD 自动入口已记录，暂缓到数据填充阶段确认。

#### Scenario: 分支起点所有角色可见

- **Given**: 分支起点节点 character_id = NULL
- **When**: 任意角色到达该节点
- **Then**: 所有角色看到相同的分支起点内容

#### Scenario: 角色专属分支内容不同

- **Given**: 分支起点后接 3 个角色专属节点（character_id 分别为 A/B/C）
- **When**: 角色A/B/C 分别进入分支
- **Then**: 各角色看到不同的分支内容

#### Scenario: 分支结束后汇合到公共节点

- **Given**: 3 个角色分支节点的后续选择均指向同一汇合节点（character_id = NULL）
- **When**: 任意角色完成分支选择
- **Then**: 所有角色到达相同的汇合节点

---

### Requirement: REQ-BRANCH-004 — 选择项数量扩展为 3 个（P1）

选择节点的选项数量从 2 个扩展为 3 个。

> **待确认 Q-029-002**: 第 3 个选项是"自由输入"还是预设选项？建议默认：预设选项。展示状态=非阻塞/暂缓，PRD 自动入口已记录，暂缓到数据填充阶段确认。

#### Scenario: 选择节点显示 3 个选项

- **Given**: 选择节点已配置 3 个选项
- **When**: 用户到达该选择节点
- **Then**: 前端展示 3 个选项按钮

#### Scenario: 第 3 个选项可正常选择

- **Given**: 选择节点有 3 个选项
- **When**: 用户选择第 3 个选项
- **Then**: 正常跳转到对应下一节点

---

### Requirement: REQ-BRANCH-005 — 向后兼容（P1）

现有节点和 session 在新功能上线后不受影响。

#### Scenario: 现有节点 character_id 为 NULL

- **Given**: 数据库迁移完成
- **When**: 查询现有节点
- **Then**: 所有现有节点的 `character_id` 为 NULL

#### Scenario: 旧 session 正常运行

- **Given**: 存在迁移前创建的 session（无 character_id）
- **When**: 继续游戏
- **Then**: 剧情正常推进，仅看到公共节点

---

## 不做（Out of Scope）

- 多结局系统（后续 CR）
- 条件触发分支（如好感度阈值，后续 CR，Q-029-003 已标记非阻塞/暂缓）
- 全量 3 个剧本分支数据（CEO 条件：先 1 个剧本 MVP）
- 前端可视化分支编辑器
