# Spec: Character 可扮演字段扩展

### Requirement: Character 表新增可扮演相关字段

#### Scenario: 数据库迁移成功执行
- **Given** 数据库迁移脚本执行
- **Then** characters 表新增以下字段：
  - playable (BOOLEAN, DEFAULT false, NOT NULL)
  - playable_route_id (UUID, nullable, FK → routes.id)
  - play_description (TEXT, nullable)
  - unlock_type (VARCHAR(20), DEFAULT 'free', NOT NULL) — 枚举值: free/paid/subscription
  - unlock_price (INT, nullable)
- **And** 已有角色 playable 默认为 false，unlock_type 默认为 'free'

#### Scenario: 管理员通过数据库设置角色为可扮演
- **Given** 管理员直接操作数据库
- **When** 执行 UPDATE characters SET playable=true, playable_route_id='<uuid>', play_description='你是...', unlock_type='free' WHERE id='<id>'
- **Then** 该角色标记为可扮演
- **And** playable_route_id 关联到对应 Route
- **And** 剧本详情接口返回该角色在 playable_characters 列表中

#### Scenario: 角色未设置 playable_route_id 时不可扮演
- **Given** 角色 playable=true 但 playable_route_id=NULL
- **When** 剧本详情接口返回该角色
- **Then** 该角色不出现在 playable_characters 列表中
- **And** 后端日志记录 warning

#### Scenario: unlock_type 为 paid 时 unlock_price 必填
- **Given** 管理员设置 unlock_type='paid'
- **When** unlock_price=NULL
- **Then** 数据校验不通过（数据库 CHECK 约束或应用层校验）
- **And** 返回错误信息"付费角色必须设置价格"

### Requirement: 角色解锁类型

#### Scenario: free 类型角色所有用户可扮演
- **Given** 角色 unlock_type='free'
- **When** 任意用户请求剧本详情
- **Then** 该角色在 playable_characters 列表中 is_unlocked=true

#### Scenario: paid 类型角色需解锁后可扮演
- **Given** 角色 unlock_type='paid'
- **When** 用户未在 user_character_unlocks 中有记录
- **Then** 该角色在 playable_characters 列表中 is_unlocked=false
- **And** 返回 unlock_price 字段

#### Scenario: subscription 类型角色需订阅后可扮演
- **Given** 角色 unlock_type='subscription'
- **When** 用户 subscription_tier 不满足要求
- **Then** 该角色在 playable_characters 列表中 is_unlocked=false
