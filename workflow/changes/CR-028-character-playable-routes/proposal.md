# CR-028: 剧本角色选择与多故事线系统

## 1. 需求概述

### 1.1 核心功能
- **角色选择**：玩家在剧本详情页选择扮演剧本中的角色（复用现有角色展示区域）
- **多故事线**：不同角色对应不同的故事线（Route），剧情、对话、结局各不相同
- **角色切换**：同一剧本可以切换角色重新游玩，生成新的游戏存档
- **存档管理**：个人中心展示所有角色的存档，支持继续/删除/重命名，标签栏筛选
- **付费预留**：当前免费，预留角色付费解锁能力

### 1.2 不在本期范围
- ~~管理后台配置界面~~（后续迭代，本期直接操作数据库）
- ~~游戏页内切换角色~~（只能在剧本详情页切换）
- ~~付费支付流程~~（预留接口，暂不实现）

---

## 2. 数据模型设计

### 2.1 Character 表加字段

```sql
ALTER TABLE characters ADD COLUMN playable BOOLEAN DEFAULT FALSE;
ALTER TABLE characters ADD COLUMN playable_route_id UUID REFERENCES routes(id);
ALTER TABLE characters ADD COLUMN play_description TEXT;
ALTER TABLE characters ADD COLUMN unlock_type VARCHAR(20) DEFAULT 'free';
ALTER TABLE characters ADD COLUMN unlock_price INT DEFAULT 0;
```

### 2.2 GameSession 表加字段

```sql
ALTER TABLE game_sessions ADD COLUMN character_id UUID REFERENCES characters(id);
ALTER TABLE game_sessions ADD COLUMN character_name VARCHAR(100);
CREATE INDEX idx_game_sessions_character ON game_sessions(character_id);
CREATE INDEX idx_game_sessions_script_character ON game_sessions(script_id, character_id);
```

### 2.3 用户角色解锁记录表（预留付费）

```sql
CREATE TABLE user_character_unlocks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  character_id UUID REFERENCES characters(id),
  unlocked_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, character_id)
);
```

### 2.4 数据迁移（已有剧本）

```sql
-- 原主角自动设为 playable
UPDATE characters 
SET playable = true,
    playable_route_id = (
      SELECT id FROM routes 
      WHERE script_id = characters.script_id 
      ORDER BY created_at LIMIT 1
    ),
    play_description = '以' || name || '的视角体验故事',
    unlock_type = 'free'
WHERE is_main = true;
```

### 2.5 新增多角色（直接操作数据库）

```sql
-- 示例：为剧本「侦探之谜」增加角色B
INSERT INTO characters (id, script_id, name, description, is_main, playable, playable_route_id, play_description, unlock_type)
VALUES (
  gen_random_uuid(),
  '<script_id>',
  '角色B',
  '角色描述',
  false,
  true,
  '<route_b_id>',  -- 需要预先创建对应的 Route
  '扮演凶手，隐藏身份',
  'free'
);
```

---

## 3. 后端 API 设计

### 3.1 剧本详情接口扩展

**接口**：`GET /api/v1/scripts/{script_id}`

**返回字段新增**：
```json
{
  "playable_characters": [
    {
      "id": "uuid",
      "name": "角色名",
      "avatar_url": "头像URL",
      "play_description": "玩法描述",
      "unlock_type": "free",
      "is_unlocked": true,
      "route_id": "uuid",
      "route_title": "故事线标题"
    }
  ]
}
```

### 3.2 开始游戏接口扩展

**接口**：`POST /api/v1/game/start`

**请求体新增字段**：
```json
{
  "script_id": "uuid",
  "character_id": "uuid"
}
```

**逻辑**：
1. 传了 `character_id` → 查 `playable_route_id` → 作为 `route_id`
2. 校验角色已解锁
3. 创建 GameSession 记录 `character_id` 和 `character_name`
4. 该剧本+角色已有 active 存档 → 返回现有 session

### 3.3 存档列表接口扩展

**接口**：`GET /api/v1/game/saves`

**返回字段新增**：
```json
{
  "saves": [
    {
      "session_id": "uuid",
      "script_id": "uuid",
      "script_title": "剧本标题",
      "character_id": "uuid",
      "character_name": "角色名",
      "character_avatar": "头像URL",
      "route_id": "uuid",
      "route_name": "路线名",
      "status": "active|completed",
      "progress_percent": 50,
      "last_played_at": "ISO时间"
    }
  ]
}
```

### 3.4 角色解锁接口（预留）

**接口**：`POST /api/v1/characters/{character_id}/unlock`

**逻辑**：`unlock_type=free` 直接返回成功，`paid`/`subscription` 暂返回提示。

---

## 4. 前端交互设计

### 4.1 剧本详情页（ScriptDetailView）— 复用现有角色展示区域

**不修改页面布局**，在现有角色卡片上增加：
1. 可扮演角色显示「🎮可玩」标识
2. 点击可扮演角色卡片 → 选中高亮
3. 「开始游戏」按钮文案变化：`🎮 开始游戏（以{角色名}身份）`
4. 未解锁角色显示 🔒 遮罩

### 4.2 游戏页（GameView）

- 左侧栏 CharacterInfo 显示扮演角色信息
- 顶部标题栏显示当前角色头像 + 名字
- **不放置**切换角色按钮

### 4.3 个人中心（PersonalCenterView）

- 「继续游玩」卡片显示角色信息
- 统计卡片新增「扮演角色数」

### 4.4 存档管理页（SaveManagerView）

- 新增角色筛选标签栏：`[全部] [角色A] [角色B] [角色C]`
- 每个存档卡片显示角色头像 + 名字 + 路线名

---

## 5. NarrativeEngine 角色身份注入

- Prompt 构建时注入当前扮演角色的身份信息（名字、描述、desire/fear/secret）
- 未配置角色时走原逻辑（向后兼容）

---

## 6. 影响范围与工时预估

| 层 | 改动 | 工时 |
|---|---|---|
| DB | Character 加 5 字段 + GameSession 加 2 字段 + user_character_unlocks 表 + 迁移脚本 | 2h |
| BE | 剧本详情接口 + 开始游戏接口 + 存档列表接口 + 解锁接口 | 6h |
| BE | NarrativeEngine 角色身份注入 | 4h |
| FE | ScriptDetailView 角色选择改造 | 3h |
| FE | GameView 角色信息展示 | 2h |
| FE | PersonalCenterView + SaveManagerView | 3h |
| QA | E2E 测试 | 4h |
| **合计** | | **24h** |

---

## 7. 验收标准

### P0（必须）
- AC-PLAY-001：玩家可在剧本详情页选择可扮演角色（现有角色展示区域）
- AC-PLAY-002：不同角色进入不同故事线，剧情内容不同
- AC-PLAY-003：同一剧本可切换角色重新游玩，生成新存档
- AC-PLAY-004：个人中心存档展示角色信息
- AC-PLAY-005：存档管理页可按角色筛选

### P1（重要）
- AC-PLAY-006：未解锁角色显示锁定状态
- AC-PLAY-007：已有剧本数据迁移后，原主角自动可扮演
- AC-PLAY-008：可直接操作数据库新增可扮演角色和关联 Route

### P2（预留）
- AC-PLAY-009：付费角色解锁接口（暂不实现支付）

---

## 8. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|---|---|---|
| 已有剧本无 playable 角色 | 无法选择 | 数据迁移脚本默认设置 |
| NarrativeEngine 改造影响现有对话 | 对话质量下降 | 角色身份注入为可选，未配置时走原逻辑 |
| 已有 GameSession 无 character_id | 存档展示异常 | 允许 NULL，显示「默认角色」 |

---

## 9. 下一步

1. 用户确认方案 → 创建 CR-028 进入 workflow
2. PM 细化需求 → SA 设计架构 → 分配开发任务
