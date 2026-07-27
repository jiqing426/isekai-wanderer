# API Contract — 重构后页面优化（CR-008）

> 更新时间：2026-07-21
> 用途：BE 实现 / FE 对接 / 联调对齐
> 基线路径：`/api/v1`

---

## 0. 决策说明

### 路径策略：新增 `/users/me` 系列，保留旧 `/user/profile`

| 考量 | 结论 |
|------|------|
| 现有 `GET /user/profile` / `PUT /user/profile` | 保留不动，向后兼容 |
| 新增 `GET /api/v1/users/me` 等 | 新增，前端统一使用 `/users/me` |
| 原因 | RESTful 惯例 `/users/me` 表示当前认证用户；旧路径供老客户端兼容 |
| 实现方式 | 新路由内部复用同一 service 逻辑，不重复代码 |

### 认证策略

所有 `/users/me/*` 接口均需 `Authorization: Bearer <JWT>` 头。

---

## 1. 用户相关接口（设置页面消费）

### 1.1 `GET /api/v1/users/me` — 获取当前用户信息

**用途：** 设置页面 / 个人中心顶部渲染用户基本信息
**认证：** Bearer

**请求参数：** 无（从 JWT 提取 user_id）

**响应 200：**
```json
{
  "id": "bd7f90f9-1234-5678-abcd-ef0123456789",
  "email": "user@example.com",
  "display_name": "夜行者",
  "avatar_url": "https://cdn.example.com/avatars/user001.png",
  "email_verified": true,
  "subscription_tier": "standard",
  "preferred_genre": "romance",
  "locale": "zh-CN",
  "onboarding_completed": true,
  "created_at": "2026-06-01T10:00:00Z"
}
```

**错误码：** AUTH_TOKEN_EXPIRED(401), USER_NOT_FOUND(404)

**前端消费方：** `SettingsView.vue`, `ProfileHeader.vue`
```typescript
interface UserProfile {
  id: string;
  email: string;
  display_name: string | null;
  avatar_url: string | null;
  email_verified: boolean;
  subscription_tier: 'free' | 'standard' | 'premium';
  preferred_genre: string | null;
  locale: string;
  onboarding_completed: boolean;
  created_at: string;
}
```

---

### 1.2 `PATCH /api/v1/users/me` — 修改用户信息

**用途：** 修改用户名、头像（部分更新）
**认证：** Bearer

**请求 Body：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| display_name | string | 否 | 2-100 字符 |
| avatar_url | string | 否 | 头像 URL |
| locale | string | 否 | `zh-CN` / `en-US` |

**响应 200：** 同 GET /users/me

**错误码：** AUTH_TOKEN_EXPIRED(401), USER_NOT_FOUND(404), VALIDATION_ERROR(422)

---

### 1.3 `POST /api/v1/users/me/change-password` — 修改密码

**用途：** 已登录用户修改密码
**认证：** Bearer

**请求 Body：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| old_password | string | 是 | 当前密码 |
| new_password | string | 是 | ≥8 字符 |

**响应 200：** `{ "status": "ok", "message": "Password changed successfully" }`

**错误码：** AUTH_INVALID_CREDENTIALS(401), VALIDATION_ERROR(422)

---

### 1.4 `DELETE /api/v1/users/me` — 注销账号

**用途：** 用户主动注销
**认证：** Bearer

**响应 200：** `{ "status": "deleted", "message": "Account deleted successfully" }`

---

### 1.5 `GET /api/v1/users/me/subscription` — 获取订阅状态

**用途：** 设置页面展示订阅等级和状态
**认证：** Bearer

**响应 200：**
```json
{
  "tier": "standard",
  "status": "active",
  "trial_started_at": "2026-06-01T10:00:00Z",
  "trial_ends_at": "2026-07-01T10:00:00Z",
  "renew_at": "2026-08-01T10:00:00Z"
}
```

---

## 2. 个人中心相关接口

### 2.1 `GET /api/v1/users/me/stats` — 游玩统计

**用途：** 个人中心统计卡片
**认证：** Bearer

**数据来源：** `game_sessions` 表 + `gallery/collections` 表

**响应 200：**
```json
{
  "scripts_completed": 5,
  "total_play_time_minutes": 320,
  "endings_unlocked": 8,
  "cgs_collected": 12,
  "total_dialogues": 156
}
```

**字段说明：**
| 字段 | 类型 | 说明 |
|------|------|------|
| scripts_completed | number | 已完成剧本数 |
| total_play_time_minutes | number | 总游戏时长（分钟） |
| endings_unlocked | number | 已解锁结局数 |
| cgs_collected | number | 已收集 CG 数 |
| total_dialogues | number | 总对话次数 |

**前端消费方：** `PersonalCenterView.vue` → `StatsCard`
```typescript
interface UserStats {
  scripts_completed: number;
  total_play_time_minutes: number;
  endings_unlocked: number;
  cgs_collected: number;
  total_dialogues: number;
}
```

---

### 2.2 `GET /api/v1/users/me/asset` — 碎片余额

**用途：** 个人中心资产卡片
**认证：** Bearer

**数据来源：** 复用 `/shards/balance` 逻辑

**响应 200：**
```json
{
  "balance": 580,
  "total_earned": 1200,
  "total_spent": 620
}
```

**前端消费方：** `PersonalCenterView.vue` → `AssetCard`
```typescript
interface UserAsset {
  balance: number;
  total_earned: number;
  total_spent: number;
}
```

---

### 2.3 `GET /api/v1/sign/info` — 签到信息

**用途：** 个人中心签到卡片
**认证：** Bearer

**数据来源：** 复用 `/daily/checkin` + `StreakRecord` 表

**响应 200：**
```json
{
  "checked_in_today": true,
  "streak_days": 7,
  "total_checkins": 30,
  "this_week": [true, true, true, false, true, true, true],
  "next_milestone": {
    "days": 14,
    "reward_type": "fragment",
    "reward_amount": 250
  }
}
```

**字段说明：**
| 字段 | 类型 | 说明 |
|------|------|------|
| checked_in_today | boolean | 今日是否已签到 |
| streak_days | number | 连续签到天数 |
| total_checkins | number | 累计签到天数 |
| this_week | boolean[] | 本周 7 天签到状态（周一开始） |
| next_milestone | object\|null | 下一个里程碑奖励 |

**前端消费方：** `PersonalCenterView.vue` → `CheckinCard`
```typescript
interface SignInfo {
  checked_in_today: boolean;
  streak_days: number;
  total_checkins: number;
  this_week: boolean[];
  next_milestone: {
    days: number;
    reward_type: string;
    reward_amount: number;
  } | null;
}
```

---

### 2.4 `GET /api/v1/users/me/latest-save` — 最近存档

**用途：** 个人中心"继续游玩"卡片
**认证：** Bearer

**数据来源：** 复用 `/saves` 逻辑，取最新一条

**响应 200：**
```json
{
  "id": "save-uuid-001",
  "session_id": "session-uuid-001",
  "script_id": "script-uuid-001",
  "script_name": "樱花纷飞的季节",
  "character_name": "樱",
  "character_avatar": "/assets/avatars/sakura.png",
  "current_node_id": "node_015",
  "label": "Auto Save",
  "choice_count": 12,
  "created_at": "2026-07-20T14:30:00Z",
  "updated_at": "2026-07-21T10:00:00Z"
}
```

**响应 200（无存档）：** `null`

**前端消费方：** `PersonalCenterView.vue` → `ContinuePlayCard`
```typescript
interface LatestSave {
  id: string;
  session_id: string;
  script_id: string;
  script_name: string;
  character_name: string;
  character_avatar: string;
  current_node_id: string;
  label: string;
  choice_count: number;
  created_at: string;
  updated_at: string;
}
```

---

### 2.5 `GET /api/v1/users/me/memory/summary` — AI 记忆摘要

**用途：** 个人中心 AI 记忆卡片（简要版）
**认证：** Bearer

**数据来源：** 复用 `/memories` 逻辑，取最近 5 条

**响应 200：**
```json
{
  "total_memories": 42,
  "recent": [
    {
      "id": "mem-001",
      "character_id": "char-001",
      "character_name": "樱",
      "content": "用户喜欢在樱花树下散步",
      "created_at": "2026-07-20T14:30:00Z"
    }
  ],
  "is_full_available": true
}
```

**字段说明：**
| 字段 | 类型 | 说明 |
|------|------|------|
| total_memories | number | 总记忆数 |
| recent | array | 最近 5 条记忆 |
| is_full_available | boolean | 是否可查看完整记忆（会员限定） |

**前端消费方：** `PersonalCenterView.vue` → `MemoryCard`
```typescript
interface MemorySummary {
  total_memories: number;
  recent: Array<{
    id: string;
    character_id: string;
    character_name: string;
    content: string;
    created_at: string;
  }>;
  is_full_available: boolean;
}
```

---

### 2.6 `GET /api/v1/users/me/characters/bond` — 角色羁绊列表

**用途：** 个人中心角色羁绊卡片
**认证：** Bearer

**数据来源：** 复用 `/affection` 逻辑

**响应 200：**
```json
{
  "characters": [
    {
      "id": "char-001",
      "name": "樱",
      "avatar_url": "/assets/avatars/sakura.png",
      "affection_value": 75,
      "affection_level": "trust",
      "max_affection": 100
    }
  ],
  "total": 3
}
```

**前端消费方：** `PersonalCenterView.vue` → `BondCard`
```typescript
interface CharacterBond {
  id: string;
  name: string;
  avatar_url: string;
  affection_value: number;
  affection_level: string;
  max_affection: number;
}

interface BondList {
  characters: CharacterBond[];
  total: number;
}
```

---

### 2.7 `GET /api/v1/users/me/endings` — 结局追踪列表

**用途：** 个人中心结局追踪卡片
**认证：** Bearer

**数据来源：** 复用 `/ending-progress` 逻辑

**响应 200：**
```json
{
  "endings": [
    {
      "script_id": "script-001",
      "script_name": "樱花纷飞的季节",
      "total_endings": 3,
      "unlocked_endings": 2,
      "ending_types": ["good", "normal"],
      "completion_rate": 67
    }
  ],
  "total_scripts": 5,
  "total_endings_unlocked": 8
}
```

**前端消费方：** `PersonalCenterView.vue` → `EndingTrackerCard`
```typescript
interface EndingProgress {
  script_id: string;
  script_name: string;
  total_endings: number;
  unlocked_endings: number;
  ending_types: string[];
  completion_rate: number;
}

interface EndingsList {
  endings: EndingProgress[];
  total_scripts: number;
  total_endings_unlocked: number;
}
```

---

### 2.8 `GET /api/v1/users/me/endings/recent` — 新解锁结局

**用途：** 个人中心"新解锁结局"卡片（分享用）
**认证：** Bearer

**数据来源：** `game_sessions` 表，按 `ended_at` 倒序取最近 3 条

**响应 200：**
```json
{
  "recent_endings": [
    {
      "id": "session-001",
      "script_name": "樱花纷飞的季节",
      "character_name": "樱",
      "ending_type": "good",
      "ending_title": "永远的约定",
      "ended_at": "2026-07-21T10:00:00Z"
    }
  ],
  "total": 1
}
```

**前端消费方：** `PersonalCenterView.vue` → `RecentEndingCard`
```typescript
interface RecentEnding {
  id: string;
  script_name: string;
  character_name: string;
  ending_type: 'good' | 'normal' | 'bad' | 'true';
  ending_title: string;
  ended_at: string;
}

interface RecentEndings {
  recent_endings: RecentEnding[];
  total: number;
}
```

---

### 2.9 `GET /api/v1/users/me/memory/full` — 完整 AI 记忆

**用途：** 会员中心完整记忆查看
**认证：** Bearer

**权限：** 仅 `subscription_tier` 为 `standard` 或 `premium` 可访问

**数据来源：** 复用 `/memories` 逻辑，返回全量

**响应 200：**
```json
{
  "memories": [
    {
      "id": "mem-001",
      "character_id": "char-001",
      "character_name": "樱",
      "content": "用户喜欢在樱花树下散步",
      "source": "dialogue",
      "created_at": "2026-07-20T14:30:00Z"
    }
  ],
  "total": 42
}
```

**错误码：**
| code | status | 说明 |
|------|--------|------|
| AUTH_TOKEN_EXPIRED | 401 | Token 过期 |
| SUBSCRIPTION_REQUIRED | 403 | 需要会员 |

**前端消费方：** `MemoryFullView.vue`
```typescript
interface FullMemory {
  id: string;
  character_id: string;
  character_name: string;
  content: string;
  source: string;
  created_at: string;
}

interface FullMemoryList {
  memories: FullMemory[];
  total: number;
}
```

---

## 3. 修复 / 新增接口

### 3.1 `GET /api/v1/characters` — 角色列表（新增）

**用途：** 剧本大厅 / 角色选择页
**认证：** None

**请求参数（Query）：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| include_main | boolean | 否 | 默认 true |
| limit | int | 否 | 默认 50 |

**响应 200：**
```json
{
  "characters": [
    {
      "id": "char-uuid-001",
      "name": "樱",
      "description": "温柔的青梅竹马",
      "avatar_url": "/assets/avatars/sakura.png",
      "is_main": true,
      "age": "18",
      "height": "162cm",
      "birthday": "03-15",
      "likes": ["花", "音乐"],
      "personality": {"gentle": 85, "wisdom": 60, "brave": 40, "mysterious": 30, "loyal": 90},
      "script_count": 2
    }
  ],
  "total": 3
}
```

---

### 3.2 `GET /api/v1/ugc/posts` — 修复 500 错误

**用途：** 社区帖子列表
**认证：** None

**请求参数（Query）：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 默认 1 |
| page_size | int | 否 | 默认 20，最大 100 |

**响应 200：**
```json
{
  "posts": [
    {
      "id": "post-uuid-001",
      "user_id": "user-uuid-001",
      "title": "我的第一次异世界冒险",
      "content": "今天第一次玩了异世界之旅...",
      "image_urls": "https://cdn.example.com/img1.jpg",
      "like_count": 42,
      "comment_count": 8,
      "created_at": "2026-07-20T14:30:00Z"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 56
}
```

**修复验证：** `DISABLE_MOCK=1` 启动后端，`curl /api/v1/ugc/posts` 返回 200

---

### 3.3 `GET /api/v1/gallery/collections` — 认证确认

**用途：** 收藏馆 → 收藏品列表
**认证：** Bearer

**响应 200：**
```json
{
  "collections": [
    {
      "id": "col-uuid-001",
      "item_type": "cg",
      "item_id": "cg-001",
      "item_name": "初次相遇",
      "image_url": "/assets/cg/1_thumb.jpg",
      "unlocked_at": "2026-07-15T10:00:00Z"
    }
  ]
}
```

---

## 4. ImportError 修复

### 4.1 `get_free_chat_service` 不存在

**状态：** ✅ 已修复

在 `backend/app/services/free_chat_service.py` 末尾添加了工厂函数和模块级实例。

---

## 5. 前端 API 层对接清单

### 5.1 新增 API 函数（`frontend/src/api/user.ts`）

```typescript
import http from './http';

// 用户信息
export function getMe() { return http.get<UserProfile>('/users/me'); }
export function updateMe(data: ProfileUpdateRequest) { return http.patch<UserProfile>('/users/me', data); }
export function changePassword(data: { old_password: string; new_password: string }) { return http.post('/users/me/change-password', data); }
export function deleteAccount() { return http.delete('/users/me'); }
export function getMySubscription() { return http.get<SubscriptionStatus>('/users/me/subscription'); }

// 个人中心
export function getMyStats() { return http.get<UserStats>('/users/me/stats'); }
export function getMyAsset() { return http.get<UserAsset>('/users/me/asset'); }
export function getSignInfo() { return http.get<SignInfo>('/sign/info'); }
export function getLatestSave() { return http.get<LatestSave | null>('/users/me/latest-save'); }
export function getMemorySummary() { return http.get<MemorySummary>('/users/me/memory/summary'); }
export function getCharacterBond() { return http.get<BondList>('/users/me/characters/bond'); }
export function getMyEndings() { return http.get<EndingsList>('/users/me/endings'); }
export function getRecentEndings() { return http.get<RecentEndings>('/users/me/endings/recent'); }
export function getFullMemory() { return http.get<FullMemoryList>('/users/me/memory/full'); }
```

---

## 6. 实现优先级

| 优先级 | 接口 | 状态 |
|--------|------|------|
| P0 | `GET /api/v1/ugc/posts` 500 修复 | 待修复 |
| P0 | `GET /api/v1/characters` 列表新增 | ✅ 已实现 |
| P0 | `GET /api/v1/gallery/collections` 认证确认 | 待确认 |
| P0 | `get_free_chat_service` ImportError | ✅ 已修复 |
| P0 | `GET /api/v1/users/me` | 待新增 |
| P0 | `PATCH /api/v1/users/me` | 待新增 |
| P0 | `POST /api/v1/users/me/change-password` | 待新增 |
| P0 | `DELETE /api/v1/users/me` | 待新增 |
| P0 | `GET /api/v1/users/me/subscription` | 待新增 |
| P0 | `GET /api/v1/users/me/stats` | 待新增 |
| P0 | `GET /api/v1/users/me/asset` | 待新增 |
| P0 | `GET /api/v1/sign/info` | 待新增 |
| P0 | `GET /api/v1/users/me/latest-save` | 待新增 |
| P0 | `GET /api/v1/users/me/memory/summary` | 待新增 |
| P0 | `GET /api/v1/users/me/characters/bond` | 待新增 |
| P0 | `GET /api/v1/users/me/endings` | 待新增 |
| P0 | `GET /api/v1/users/me/endings/recent` | 待新增 |
| P0 | `GET /api/v1/users/me/memory/full` | 待新增 |

---

## 7. Mock 中间件注意事项

当前 `MockMiddleware` 会拦截部分路径返回 mock 数据。

- **开发环境（DISABLE_MOCK 未设置）：** 前端拿到 mock 数据
- **生产 / 测试环境（DISABLE_MOCK=1）：** 走真实路由
- `/users/me/*` 新路由不在 mock 中间件中，始终走真实逻辑

---

## 8. 变更日志

| 时间 | 变更 |
|------|------|
| 2026-07-21 | 初始版本，覆盖 9 个接口 |
| 2026-07-21 | 扩展至 18 个接口（新增个人中心 9 个） |
