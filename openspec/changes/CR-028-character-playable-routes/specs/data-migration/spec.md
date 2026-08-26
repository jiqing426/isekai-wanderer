# Spec: 数据迁移 — 已有主角自动可扮演

### Requirement: 已有 is_main 角色自动 playable

#### Scenario: 数据迁移脚本执行成功
- **Given** 数据库中存在 is_main=true 的角色
- **When** 执行 CR-028 数据迁移脚本
- **Then** 该角色 playable 设为 true
- **And** playable_route_id 设为该角色当前关联的 Route
- **And** play_description 设为角色基础介绍（从现有字段生成）
- **And** unlock_type 设为 'free'

#### Scenario: 已有剧本无 is_main 角色
- **Given** 某剧本所有角色 is_main=false
- **When** 执行数据迁移脚本
- **Then** 该剧本无可扮演角色（playable_characters 为空）
- **And** 迁移脚本日志记录 warning
- **And** 该剧本开始游戏走默认流程

#### Scenario: 迁移不影响现有游戏流程
- **Given** 迁移执行前已有 GameSession
- **When** 迁移执行完成
- **Then** 已有 GameSession 的 character_id 仍为 NULL
- **And** 已有 GameSession 可正常加载和继续
- **And** 存档列表显示"默认角色"

#### Scenario: 迁移脚本幂等
- **Given** 迁移脚本已执行过一次
- **When** 再次执行迁移脚本
- **Then** 不重复修改已有数据
- **And** 不报错
