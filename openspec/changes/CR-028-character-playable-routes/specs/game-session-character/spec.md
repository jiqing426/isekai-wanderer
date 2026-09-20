# Spec: GameSession 角色关联

### Requirement: GameSession 表新增角色字段

#### Scenario: 数据库迁移成功执行
- **Given** 数据库迁移脚本执行
- **Then** game_sessions 表新增以下字段：
  - character_id (UUID, nullable, FK → characters.id)
  - character_name (VARCHAR(100), nullable)
- **And** 已有 GameSession 两个字段默认为 NULL（向后兼容）

#### Scenario: 开始游戏时传入 character_id
- **Given** 玩家选择了可扮演角色（character_id 有效）
- **When** 调用 POST /game/start 传入 character_id
- **Then** 后端验证 character_id 对应角色 playable=true
- **And** 创建 GameSession 时写入 character_id 和 character_name（快照）
- **And** 根据角色 playable_route_id 自动匹配 Route

#### Scenario: 开始游戏时未传 character_id（向后兼容）
- **Given** 客户端未传 character_id（旧版本或默认流程）
- **When** 调用 POST /game/start
- **Then** 创建 GameSession 时 character_id=NULL, character_name=NULL
- **And** 使用默认 Route（现有逻辑不变）

#### Scenario: character_name 为快照不受角色改名影响
- **Given** GameSession 创建时 character_name='爱丽丝'
- **When** 管理员修改 characters 表该角色 name='艾丽丝'
- **Then** 已有 GameSession 的 character_name 仍为 '爱丽丝'
- **And** 仅新创建的 GameSession 使用新名称

### Requirement: 新建 user_character_unlocks 表

#### Scenario: 数据库迁移创建 user_character_unlocks 表
- **Given** 数据库迁移脚本执行
- **Then** 创建 user_character_unlocks 表，字段：
  - id (UUID, PK)
  - user_id (UUID, FK → users.id, NOT NULL)
  - character_id (UUID, FK → characters.id, NOT NULL)
  - unlocked_at (TIMESTAMP, NOT NULL, DEFAULT NOW())
  - unlock_type (VARCHAR(20), NOT NULL) — 记录解锁方式: paid/subscription/gift
- **And** UNIQUE 约束 (user_id, character_id)

#### Scenario: 用户解锁付费角色
- **Given** 用户调用解锁接口
- **When** 解锁成功
- **Then** user_character_unlocks 插入一条记录
- **And** 后续剧本详情接口返回该角色 is_unlocked=true

#### Scenario: 重复解锁同一角色幂等
- **Given** 用户已解锁某角色
- **When** 再次调用解锁接口
- **Then** 不插入重复记录（UNIQUE 约束）
- **And** 返回成功（幂等）
