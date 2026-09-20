# Spec: 存档角色信息展示

### Requirement: 存档列表接口返回角色信息

#### Scenario: 存档列表包含角色信息
- **Given** 用户有 GameSession 记录
- **When** 客户端调用 GET /game/saves
- **Then** 每条存档记录包含 character_name 字段
- **And** character_id 不为 NULL 时返回实际角色名
- **And** character_id 为 NULL 时返回 "默认角色"

#### Scenario: 存档详情接口返回角色信息
- **Given** 用户查看某条存档
- **When** 客户端调用 GET /game/saves/{session_id}
- **Then** 响应包含 character_name 和 character_id
- **And** character_name 为创建时快照（不受角色改名影响）

### Requirement: 个人中心展示角色信息

#### Scenario: 个人中心展示最近扮演角色
- **Given** 用户有以角色身份进行的游戏记录
- **When** 用户进入个人中心
- **Then** 展示"最近扮演角色"区域
- **And** 显示角色名和立绘
- **And** 点击可跳转到对应剧本详情页

#### Scenario: 用户无角色游戏记录
- **Given** 用户所有 GameSession 的 character_id 均为 NULL
- **When** 用户进入个人中心
- **Then** 不展示"最近扮演角色"区域（保持现有 UI）
