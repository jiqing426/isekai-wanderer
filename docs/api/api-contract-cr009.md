# API Contract — CR-009 重构后页面优化（第二批）

> 更新时间：2026-07-23
> 用途：BE 实现 / FE 对接 / 联调对齐
> 基线路径：`/api/v1`

---

## 一、接口错误修复（BE 修复，无需新 API）

### 1.1 `POST /api/v1/game/{sessionId}/free-chat`

**问题：** 500 错误
**修复方向：** 检查 LLM 调用逻辑、会话状态验证
**响应结构（不变）：**
```json
{
  "reply": "AI 回复内容",
  "emotion": "happy",
  "character_id": "char-001"
}
```

### 1.2 `POST /api/v1/game/{sessionId}/choice`

**问题：** 401/500 错误
**修复方向：** 检查认证逻辑、会话有效性
**响应结构（不变）：**
```json
{
  "next_node_id": "node_015",
  "dialogue": "下一段对话",
  "choices": [...]
}
```

### 1.3 `GET /api/v1/affection`

**问题：** 500 错误
**修复方向：** 检查数据库查询、用户 ID 提取
**响应结构（不变）：**
```json
{
  "affections": [
    {
      "character_id": "char-001",
      "value": 75,
      "level": "trust"
    }
  ]
}
```

---

## 二、剧本详情数据补全（BE 补全数据，API 已存在）

### 2.1 `GET /api/v1/scripts/:id`

**用途：** 剧本详情（含角色信息）
**修复方向：** 确保角色数据完整返回

**响应结构（补全角色字段）：**
```json
{
  "id": "script-001",
  "title": "樱花纷飞的季节",
  "description": "...",
  "characters": [
    {
      "id": "char-001",
      "name": "樱",
      "avatar_url": "/assets/avatars/sakura.png",
      "description": "温柔的青梅竹马",
      "age": 18,
      "height": 162,
      "birthday": "03-15",
      "likes": ["花", "音乐"],
      "personality": {
        "gentle": 85,
        "wisdom": 60,
        "brave": 40,
        "mysterious": 30,
        "loyal": 90
      }
    }
  ],
  "routes": [...],
  "cg_preview": [
    {
      "id": "cg-001",
      "thumbnail_url": "/assets/cg/1_thumb.jpg",
      "title": "初次相遇"
    }
  ]
}
```

### 2.2 `GET /api/v1/game/{scriptId}/route-map`

**用途：** 路线探索地图
**修复方向：** 确保路线探索数据正确返回

**响应结构（不变）：**
```json
{
  "routes": [
    {
      "id": "route-001",
      "name": "A 路线",
      "explored_nodes": ["node_001", "node_002"],
      "total_nodes": 15,
      "completion_rate": 13
    }
  ]
}
```

### 2.3 `GET /api/v1/users/me/endings`

**用途：** 结局收集列表（已存在）
**修复方向：** 确保结局数据完整

**响应结构（不变）：**
```json
{
  "endings": [
    {
      "id": "ending-001",
      "script_id": "script-001",
      "script_name": "樱花纷飞的季节",
      "ending_type": "good",
      "ending_title": "永远的约定",
      "unlocked_at": "2026-07-20T10:00:00Z"
    }
  ],
  "total": 8
}
```

---

## 三、游戏内容页面（新增 API）

### 3.1 `GET /api/v1/game/{sessionId}/progress` — 进度条数据

**用途：** 游戏内容页面进度条展示
**认证：** Bearer

**响应 200：**
```json
{
  "session_id": "session-001",
  "script_id": "script-001",
  "current_node_id": "node_015",
  "total_nodes": 50,
  "explored_nodes": 15,
  "completion_rate": 30,
  "choice_count": 12,
  "dialogue_count": 45
}
```

**字段说明：**
| 字段 | 类型 | 说明 |
|------|------|------|
| session_id | string | 会话 ID |
| script_id | string | 剧本 ID |
| current_node_id | string | 当前节点 ID |
| total_nodes | number | 总节点数 |
| explored_nodes | number | 已探索节点数 |
| completion_rate | number | 完成率（0-100） |
| choice_count | number | 选择次数 |
| dialogue_count | number | 对话次数 |

**前端消费方：** `GameView.vue` → `ProgressBar`
```typescript
interface GameProgress {
  session_id: string;
  script_id: string;
  current_node_id: string;
  total_nodes: number;
  explored_nodes: number;
  completion_rate: number;
  choice_count: number;
  dialogue_count: number;
}
```

---

### 3.2 `GET /api/v1/game/{sessionId}/history` — 历史对话

**用途：** 游戏内容页面历史对话展示
**认证：** Bearer

**请求参数（Query）：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 默认 1 |
| page_size | int | 否 | 默认 20 |

**响应 200：**
```json
{
  "history": [
    {
      "id": "dialogue-001",
      "type": "dialogue",
      "character_id": "char-001",
      "character_name": "樱",
      "content": "今天天气真好呢~",
      "emotion": "happy",
      "created_at": "2026-07-23T10:00:00Z"
    },
    {
      "id": "choice-001",
      "type": "choice",
      "choice_text": "一起去散步吧",
      "created_at": "2026-07-23T10:01:00Z"
    }
  ],
  "total": 45,
  "page": 1,
  "page_size": 20
}
```

**字段说明：**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 对话/选择 ID |
| type | string | `dialogue` / `choice` |
| character_id | string | 角色 ID（仅 dialogue） |
| character_name | string | 角色名称（仅 dialogue） |
| content | string | 对话内容（仅 dialogue） |
| emotion | string | 情绪（仅 dialogue） |
| choice_text | string | 选择内容（仅 choice） |
| created_at | string | 时间 |

**前端消费方：** `GameView.vue` → `HistoryDrawer`
```typescript
interface DialogueHistory {
  id: string;
  type: 'dialogue' | 'choice';
  character_id?: string;
  character_name?: string;
  content?: string;
  emotion?: string;
  choice_text?: string;
  created_at: string;
}

interface HistoryResponse {
  history: DialogueHistory[];
  total: number;
  page: number;
  page_size: number;
}
```

---

### 3.3 `POST /api/v1/game/{sessionId}/gift` — 送礼

**用途：** 游戏内容页面送礼功能
**认证：** Bearer

**请求 Body：**
```json
{
  "character_id": "char-001",
  "gift_id": "gift-001",
  "quantity": 1
}
```

**响应 200：**
```json
{
  "status": "ok",
  "character_id": "char-001",
  "gift_id": "gift-001",
  "affection_delta": 10,
  "new_affection": 85,
  "message": "樱收到了礼物，很开心！"
}
```

**错误码：**
| code | status | 说明 |
|------|--------|------|
| CHARACTER_NOT_FOUND | 404 | 角色不存在 |
| GIFT_NOT_FOUND | 404 | 礼物不存在 |
| INSUFFICIENT_FRAGMENTS | 402 | 碎片不足 |

**前端消费方：** `GameView.vue` → `GiftPanel`
```typescript
interface GiftRequest {
  character_id: string;
  gift_id: string;
  quantity?: number;
}

interface GiftResponse {
  status: 'ok';
  character_id: string;
  gift_id: string;
  affection_delta: number;
  new_affection: number;
  message: string;
}
```

---

### 3.4 `GET /api/v1/game/{sessionId}/gift-history` — 送礼历史

**用途：** 查看送礼记录
**认证：** Bearer

**响应 200：**
```json
{
  "gifts": [
    {
      "id": "gift-record-001",
      "character_id": "char-001",
      "character_name": "樱",
      "gift_id": "gift-001",
      "gift_name": "樱花发夹",
      "quantity": 1,
      "affection_delta": 10,
      "created_at": "2026-07-23T10:00:00Z"
    }
  ],
  "total": 5
}
```

**前端消费方：** `GameView.vue` → `GiftHistoryPanel`
```typescript
interface GiftRecord {
  id: string;
  character_id: string;
  character_name: string;
  gift_id: string;
  gift_name: string;
  quantity: number;
  affection_delta: number;
  created_at: string;
}

interface GiftHistoryResponse {
  gifts: GiftRecord[];
  total: number;
}
```

---

## 四、个人中心后端（新增 API）

### 4.1 `GET /api/v1/users/me/game-stats` — 游戏统计

**用途：** 个人中心游戏统计卡片
**认证：** Bearer

**响应 200：**
```json
{
  "total_play_time_minutes": 320,
  "total_sessions": 15,
  "completed_sessions": 8,
  "total_choices": 120,
  "total_dialogues": 450,
  "favorite_character_id": "char-001",
  "favorite_character_name": "樱"
}
```

**字段说明：**
| 字段 | 类型 | 说明 |
|------|------|------|
| total_play_time_minutes | number | 总游戏时长（分钟） |
| total_sessions | number | 总会话数 |
| completed_sessions | number | 已完成会话数 |
| total_choices | number | 总选择次数 |
| total_dialogues | number | 总对话次数 |
| favorite_character_id | string | 最常互动角色 ID |
| favorite_character_name | string | 最常互动角色名称 |

**前端消费方：** `PersonalCenterView.vue` → `GameStatsCard`
```typescript
interface GameStats {
  total_play_time_minutes: number;
  total_sessions: number;
  completed_sessions: number;
  total_choices: number;
  total_dialogues: number;
  favorite_character_id: string;
  favorite_character_name: string;
}
```

---

### 4.2 `GET /api/v1/users/me/latest-session` — 快速继续游玩

**用途：** 个人中心快速继续游玩卡片
**认证：** Bearer

**响应 200：**
```json
{
  "session_id": "session-001",
  "script_id": "script-001",
  "script_name": "樱花纷飞的季节",
  "script_cover_url": "/assets/covers/sakura.jpg",
  "current_node_id": "node_015",
  "last_played_at": "2026-07-23T10:00:00Z",
  "progress": 30
}
```

**响应 200（无会话）：** `null`

**前端消费方：** `PersonalCenterView.vue` → `ContinuePlayCard`
```typescript
interface LatestSession {
  session_id: string;
  script_id: string;
  script_name: string;
  script_cover_url: string;
  current_node_id: string;
  last_played_at: string;
  progress: number;
}
```

---

## 五、签到功能（已有 API，需确认逻辑）

### 5.1 `POST /api/v1/daily/checkin` — 签到

**用途：** 个人中心签到功能
**认证：** Bearer

**响应 200（签到成功）：**
```json
{
  "status": "ok",
  "fragments_earned": 10,
  "streak_days": 7,
  "message": "签到成功，获得 10 碎片！"
}
```

**响应 409（已签到）：**
```json
{
  "error_code": "DAILY_ALREADY_CHECKED_IN",
  "message": "今日已签到"
}
```

**前端处理：**
- 签到成功：显示获得碎片数量，更新余额
- 已签到：显示"今日已签到"，禁用签到按钮

---

## 六、实现优先级

| 优先级 | 任务 | 负责人 | 说明 |
|--------|------|--------|------|
| P0 | 接口错误修复（3个） | BE | 修复 500/401 错误 |
| P0 | 剧本详情数据补全 | BE | 补全角色、路线、结局数据 |
| P0 | 游戏进度 API | BE | GET /game/{sessionId}/progress |
| P0 | 历史对话 API | BE | GET /game/{sessionId}/history |
| P0 | 送礼功能 API | BE | POST /game/{sessionId}/gift + GET gift-history |
| P0 | 角色详情页修复 | BE | 修复加载问题 |
| P0 | 游戏统计 API | BE | GET /users/me/game-stats |
| P0 | 快速继续 API | BE | GET /users/me/latest-session |
| P0 | 签到逻辑确认 | BE | 确认碎片获取规则 |

---

## 七、前端对接清单

### FE P0 任务（对接 BE 新 API）

1. **剧本详情页面**
   - 对接 GET /scripts/:id（角色数据）
   - 对接 GET /game/{scriptId}/route-map（路线探索）
   - 对接 GET /users/me/endings（结局收集）
   - CG 预览：取消最大宽度，一行多个，自动换行

2. **游戏内容页面**
   - 对接 GET /game/{sessionId}/progress（进度条）
   - 对接 GET /game/{sessionId}/history（历史对话）
   - 对接 POST /game/{sessionId}/gift（送礼）
   - 对接 GET /game/{sessionId}/gift-history（送礼历史）
   - 左侧栏展示角色名称和好感度
   - 隐藏设置按钮

3. **个人中心**
   - 对接 POST /daily/checkin（签到）
   - 对接 GET /users/me/game-stats（游戏统计）
   - 对接 GET /users/me/latest-session（快速继续）
   - 已签到日期高亮，禁止重复签到
   - AI 记忆添加说明提示

### FE P1 任务（纯前端优化）

1. **剧本大厅**
   - 搜索改为点击按钮触发，不要实时搜索

2. **订阅计划**
   - 确认 PRD 中的四个等级
   - 修复 i18n 显示问题（faq.a7, faq.q7）

3. **设置页面**
   - 头像上传限制 5MB
   - 用户名限制 20 字符
   - 播放偏好：删除动画选项，添加保存按钮

4. **Header 优化**
   - Tab 顺序：剧本大厅 > 角色馆 > 收藏 > 碎片 > 订阅 > 社区
   - 个人中心、设置入口放到退出登录的上面
   - CSS 样式：.header-inner 最大宽度设置 1600px
   - 删除未登录状态下的多余登录注册按钮
   - 订阅和碎片不要用同一个 icon

---

## 八、变更日志

| 时间 | 变更 |
|------|------|
| 2026-07-23 | 初始版本，覆盖 CR-009 所有新增/修复接口 |
