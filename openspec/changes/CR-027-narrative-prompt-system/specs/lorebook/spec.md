# Spec: Lorebook 世界知识库

### Requirement: Lorebook 条目 CRUD

#### Scenario: 管理员创建 Lorebook 条目
- **Given** 管理员在 Lorebook 管理页点击"新建条目"
- **And** 填写标题、内容、场景标签（如 "森林"、"城堡"）
- **When** 点击保存
- **Then** 条目存入数据库，状态为 active
- **And** 列表页显示新条目

#### Scenario: 管理员编辑 Lorebook 条目
- **Given** 管理员在 Lorebook 列表点击某条目的"编辑"
- **When** 修改内容并保存
- **Then** 条目内容更新，下次 Prompt 拼接使用新内容

#### Scenario: 管理员删除 Lorebook 条目
- **Given** 管理员在 Lorebook 列表点击某条目的"删除"
- **When** 确认删除
- **Then** 条目标记为 deleted（软删除），不再注入 Prompt

#### Scenario: 管理员按标签筛选 Lorebook 条目
- **Given** 管理员在 Lorebook 管理页
- **When** 选择标签 "森林" 筛选
- **Then** 列表仅显示包含 "森林" 标签的条目

### Requirement: Lorebook 场景标签注入

#### Scenario: 根据场景标签匹配 Lorebook 条目
- **Given** 当前游戏场景标签为 ["森林", "白天"]
- **When** Prompt 拼接引擎请求 Lorebook 上下文
- **Then** 返回所有包含 "森林" 或 "白天" 标签的 active 条目内容
- **And** 条目按优先级排序（priority 字段）

#### Scenario: 无匹配 Lorebook 条目时返回空
- **Given** 当前游戏场景标签为 ["海底"]
- **And** 无任何 Lorebook 条目包含 "海底" 标签
- **When** Prompt 拼接引擎请求 Lorebook 上下文
- **Then** 返回空字符串，Prompt 中显示"（无特定世界知识）"
