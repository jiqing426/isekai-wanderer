# Spec: 前端管理界面

### Requirement: Lorebook 管理页

#### Scenario: 管理员访问 Lorebook 管理页
- **Given** 管理员登录系统
- **When** 导航到 Lorebook 管理页
- **Then** 页面显示 Lorebook 条目列表（标题、标签、状态、更新时间）
- **And** 提供"新建条目"按钮

#### Scenario: 管理员创建 Lorebook 条目
- **Given** 管理员点击"新建条目"
- **When** 填写标题、内容、场景标签（多选/输入）
- **And** 点击保存
- **Then** 条目创建成功，列表刷新显示新条目

#### Scenario: 管理员编辑 Lorebook 条目
- **Given** 管理员在列表中点击某条目的"编辑"
- **When** 修改内容并保存
- **Then** 条目更新成功

#### Scenario: 管理员删除 Lorebook 条目
- **Given** 管理员在列表中点击某条目的"删除"
- **When** 确认删除弹窗点击"确认"
- **Then** 条目软删除，列表不再显示

### Requirement: 场景配置页

#### Scenario: 管理员访问场景配置页
- **Given** 管理员登录系统
- **When** 导航到场景配置页
- **Then** 页面显示剧本列表 → 路线 → Node 的层级结构
- **And** 每个 Node 显示已配置的场景信息（或"未配置"）

#### Scenario: 管理员为 Node 配置场景
- **Given** 管理员选择某 Node
- **When** 填写场景名称、氛围标签、描述
- **And** 点击保存
- **Then** 场景配置保存成功

### Requirement: NPC 编辑页增强

#### Scenario: NPC 编辑页显示内在驱动区域
- **Given** 管理员进入 NPC 编辑页
- **Then** 页面在现有信息下方新增"内在驱动"区域
- **And** 包含"渴望"、"恐惧"、"秘密"三个文本输入框

#### Scenario: 管理员保存 NPC 内在驱动
- **Given** 管理员填写渴望/恐惧/秘密
- **When** 点击保存
- **Then** 数据保存成功，页面显示成功提示

### Requirement: 权限控制

#### Scenario: 非管理员无法访问管理页
- **Given** 用户角色为普通玩家
- **When** 尝试访问 Lorebook/场景配置/NPC 编辑页
- **Then** 返回 403 或重定向到首页
