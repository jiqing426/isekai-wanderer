# Spec: 剧本详情页可扮演角色选择

### Requirement: 剧本详情接口返回 playable_characters 列表

#### Scenario: 剧本详情接口返回可扮演角色
- **Given** 剧本存在 playable=true 且 playable_route_id 不为 NULL 的角色
- **When** 客户端调用 GET /scripts/{script_id}
- **Then** 响应包含 playable_characters 数组
- **And** 每个元素包含：id, name, avatar_url, play_description, unlock_type, unlock_price, is_unlocked
- **And** is_unlocked 根据 user_character_unlocks 和用户 subscription 计算

#### Scenario: 剧本无可扮演角色时返回空列表
- **Given** 剧本所有角色 playable=false
- **When** 客户端调用 GET /scripts/{script_id}
- **Then** playable_characters 为空数组
- **And** 开始游戏按钮使用默认流程（不显示角色选择）

#### Scenario: 未登录用户查看可扮演角色
- **Given** 用户未登录
- **When** 客户端调用 GET /scripts/{script_id}
- **Then** playable_characters 正常返回
- **And** paid/subscription 类型角色 is_unlocked=false
- **And** free 类型角色 is_unlocked=true

### Requirement: 前端剧本详情页角色选择交互

#### Scenario: 剧本详情页展示可扮演角色
- **Given** 用户进入剧本详情页
- **When** 页面加载完成
- **Then** 复用现有角色展示区域展示 playable_characters
- **And** 每个可扮演角色显示「🎮可玩」标识
- **And** free 角色正常展示，paid 角色显示锁定遮罩

#### Scenario: 玩家选中可扮演角色
- **Given** 用户看到可扮演角色列表
- **When** 点击某个 is_unlocked=true 的角色
- **Then** 该角色高亮选中（选中态样式）
- **And** 「开始游戏」按钮文案变为 `🎮 开始游戏（以{角色名}身份）`

#### Scenario: 玩家点击锁定角色
- **Given** 某角色 is_unlocked=false, unlock_type='paid'
- **When** 玩家点击该角色
- **Then** 弹出提示"该角色需付费解锁（{unlock_price}碎片）"
- **And** 不触发角色选中
- **And** 不触发开始游戏

#### Scenario: 玩家未选中角色直接开始游戏
- **Given** 剧本存在可扮演角色，玩家未选中任何角色
- **When** 玩家点击「开始游戏」按钮
- **Then** 使用默认主角开始游戏（现有逻辑不变）
- **And** 按钮文案为 `🎮 开始游戏`（无角色名后缀）

#### Scenario: 玩家选中角色后开始游戏
- **Given** 玩家已选中某 is_unlocked=true 的角色
- **When** 玩家点击「🎮 开始游戏（以{角色名}身份）」
- **Then** 调用 POST /game/start 传入 character_id
- **And** 跳转到游戏页
