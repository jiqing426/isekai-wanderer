# Spec: 个人中心角色信息展示

### Requirement: 个人中心展示最近扮演角色

#### Scenario: 个人中心显示最近一次游戏使用的角色信息
- **Given** 用户最近一次游戏使用了角色"白夜"（character_id 不为空）
- **When** 用户进入个人中心页面
- **Then** 个人中心显示该角色信息：
  - 角色名称：白夜
  - 角色头像：从 characters.avatar_url 获取
  - 显示标签"最近扮演"
- **And** 信息从 game_sessions 表查询最近一条 character_id 不为空的记录

#### Scenario: 用户从未使用过角色
- **Given** 用户所有 game_sessions 的 character_id 均为空
- **When** 用户进入个人中心页面
- **Then** 个人中心不显示"最近扮演"模块

#### Scenario: 角色信息快照一致性
- **Given** 用户最近一次游戏使用了角色"白夜"
- **When** 管理员在后台修改了角色名称为"白昼"
- **Then** 个人中心仍显示"白夜"（使用 game_sessions.character_name 快照）
