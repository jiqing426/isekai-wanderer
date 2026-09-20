# Spec: 游戏页角色信息展示

### Requirement: 游戏页展示当前扮演角色

#### Scenario: 游戏页顶部展示角色信息
- **Given** 玩家以选定角色身份进入游戏
- **When** 游戏页加载完成
- **Then** 页面顶部展示角色名和立绘
- **And** 展示文案"以{角色名}身份探索"

#### Scenario: 游戏页不展示切换角色按钮
- **Given** 玩家在游戏中
- **When** 查看游戏页 UI
- **Then** 不存在"切换角色"按钮或入口
- **And** 玩家只能以当前角色身份继续游戏

#### Scenario: 默认角色进入游戏时不展示角色信息
- **Given** 玩家未选择角色（character_id=NULL）进入游戏
- **When** 游戏页加载完成
- **Then** 不展示角色信息区域（保持现有 UI）

### Requirement: NarrativeEngine 角色身份注入

#### Scenario: 有角色身份时注入 Prompt
- **Given** GameSession.character_id 不为 NULL
- **When** NarrativeEngine 构建 Prompt
- **Then** Prompt 包含"玩家当前扮演角色：{character_name}"
- **And** NPC 对话根据角色身份调整态度（由角色设定决定）

#### Scenario: 无角色身份时走原逻辑
- **Given** GameSession.character_id 为 NULL
- **When** NarrativeEngine 构建 Prompt
- **Then** 不注入角色身份信息
- **And** 使用现有 Prompt 逻辑（向后兼容）
