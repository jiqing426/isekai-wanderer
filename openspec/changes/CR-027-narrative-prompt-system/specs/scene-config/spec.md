# Spec: 场景配置系统

### Requirement: 场景-标签绑定

#### Scenario: 管理员为剧本 Node 配置场景
- **Given** 管理员在场景配置页选择某剧本的某 Node
- **When** 设置场景名称、氛围标签（如 "紧张"、"温馨"）、描述
- **Then** 配置存入 scene_configs 表
- **And** 该 Node 的对话生成时自动注入场景信息

#### Scenario: 场景配置随 Node 自动加载
- **Given** 游戏进行到某 Node
- **And** 该 Node 已配置场景（名称="月光森林", 标签=["森林","夜晚","神秘"]）
- **When** NarrativeEngine 构建 Prompt
- **Then** 场景标签自动用于 Lorebook 匹配
- **And** 场景描述注入模块2（世界观层）

#### Scenario: 未配置场景的 Node 使用默认
- **Given** 某 Node 未配置场景
- **When** NarrativeEngine 构建 Prompt
- **Then** 模块2 使用空世界知识
- **And** 不影响其他层的正常拼接

### Requirement: 场景配置 CRUD

#### Scenario: 管理员编辑场景配置
- **Given** 管理员在场景配置页
- **When** 修改某 Node 的场景标签和描述
- **Then** 配置立即生效，下次对话使用新配置

#### Scenario: 管理员删除场景配置
- **Given** 管理员在场景配置页
- **When** 删除某 Node 的场景配置
- **Then** 该 Node 恢复为无场景状态
