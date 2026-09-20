# Isekai Wanderer（异世界冒险者）API 文档

> **生成时间**: 2026-07-30 11:09 (GMT+8)  
> **项目版本**: 基于后端代码自动生成  
> **基础路径**: `/api/v1`  
> **认证方式**: Bearer Token（JWT），在请求头中添加 `Authorization: Bearer <token>`

---

## 目录

1. [健康检查 (Health)](#1-健康检查-health)
2. [认证 (Auth)](#2-认证-auth)
3. [用户资料 (User Profile)](#3-用户资料-user-profile)
4. [用户中心 (Users/me)](#4-用户中心-usersme)
5. [剧本 (Scripts)](#5-剧本-scripts)
6. [游戏 (Game)](#6-游戏-game)
7. [角色 (Characters)](#7-角色-characters)
8. [AI 对话验证](#8-ai-对话验证)
9. [好感度 (Affection)](#9-好感度-affection)
10. [记忆系统 (Memories)](#10-记忆系统-memories)
11. [签到 (Sign/Daily)](#11-签到-signdaily)
12. [每日任务 (Daily Tasks)](#12-每日任务-daily-tasks)
13. [活跃度 (Activity)](#13-活跃度-activity)
14. [成就 (Achievements)](#14-成就-achievements)
15. [画廊/收藏 (Gallery)](#15-画廊收藏-gallery)
16. [碎片商城 (Fragment)](#16-碎片商城-fragment)
17. [碎片统计 (Shards)](#17-碎片统计-shards)
18. [礼物 (Gift)](#18-礼物-gift)
19. [存档 (Saves)](#19-存档-saves)
20. [结局进度 (Ending Progress)](#20-结局进度-ending-progress)
21. [角色聊天 (Character Chat)](#21-角色聊天-character-chat)
22. [社区 (Community)](#22-社区-community)
23. [UGC 内容 (旧版)](#23-ugc-内容旧版)
24. [分享 (Share)](#24-分享-share)
25. [发现/推荐 (Discover)](#25-发现推荐-discover)
26. [内容审核 (Moderation)](#26-内容审核-moderation)
27. [冒险回顾 (Recap)](#27-冒险回顾-recap)
28. [订阅 (Subscription - 旧版)](#28-订阅-subscription---旧版)
29. [订阅 (CR-016 新版)](#29-订阅-cr-016-新版)
30. [对话额度 (CR-016 Dialogue)](#30-对话额度-cr-016-dialogue)
31. [付费墙 (Paywall - 旧版)](#31-付费墙-paywall---旧版)
32. [付费墙 (CR-016 新版)](#32-付费墙-cr-016-新版)
33. [解锁系统 (CR-017 Unlock)](#33-解锁系统-cr-017-unlock)
34. [支付 (Payment - 旧版)](#34-支付-payment---旧版)
35. [上传 (Upload)](#35-上传-upload)
36. [用户订阅 (User Subscription - 旧版)](#36-用户订阅-user-subscription---旧版)

---

## 1. 健康检查 (Health)

### GET /health
**功能**: 根级健康检查（无需认证、无需数据库）  
**认证**: ❌ 不需要  
**响应**:
```json
{ "status": "ok" }
```

### GET /api/v1/health
**功能**: API 版本健康检查  
**认证**: ❌ 不需要  
**响应**:
```json
{ "status": "ok", "version": "x.x.x" }
```

---

## 2. 认证 (Auth)

### POST /api/v1/auth/register
**功能**: 注册新用户  
**认证**: ❌ 不需要  
**请求 Body**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| email | string (email) | ✅ | 邮箱地址 |
| password | string | ✅ | 密码 |
| display_name | string | ❌ | 显示名称，默认取邮箱前缀 |

**响应**:
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "display_name": "用户名",
  "access_token": "jwt-token",
  "refresh_token": "refresh-token",
  "token_type": "bearer",
  "expires_in": 86400
}
```

---

### POST /api/v1/auth/login
**功能**: 邮箱密码登录（5次失败后锁定15分钟）  
**认证**: ❌ 不需要  
**请求 Body**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| email | string (email) | ✅ | 邮箱地址 |
| password | string | ✅ | 密码 |

**响应**:
```json
{
  "access_token": "jwt-token",
  "refresh_token": "refresh-token",
  "token_type": "bearer",
  "expires_in": 86400,
  "id": "uuid",
  "email": "user@example.com",
  "display_name": "用户名",
  "affection_decay": {}
}
```

---

### POST /api/v1/auth/refresh
**功能**: 使用 refresh_token 刷新 access_token  
**认证**: ❌ 不需要  
**请求 Body**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| refresh_token | string | ✅ | 刷新令牌 |

**响应**:
```json
{
  "access_token": "new-jwt-token",
  "refresh_token": "new-refresh-token",
  "token_type": "bearer",
  "expires_in": 86400
}
```

---

### POST /api/v1/auth/forgot-password
**功能**: 请求密码重置邮件（防枚举，始终返回200）  
**认证**: ❌ 不需要  
**请求 Body**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| email | string (email) | ✅ | 注册邮箱 |

**响应**:
```json
{ "message": "If the email exists, a reset link has been sent." }
```

---

### POST /api/v1/auth/reset-password
**功能**: 使用重置令牌修改密码  
**认证**: ❌ 不需要  
**请求 Body**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| token | string | ✅ | 重置令牌 |
| new_password | string | ✅ | 新密码 |

**响应**:
```json
{ "message": "Password reset successful" }
```

---

### POST /api/v1/auth/oauth/{provider}
**功能**: 第三方 OAuth 登录（支持 wechat/google/apple/discord）  
**认证**: ❌ 不需要  
**路径参数**: `provider` - 提供方名称  
**请求 Body**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| provider | string | ❌ | 提供方可在 body 或 path 中 |
| code | string | ✅ | 授权码（Mock） |
| redirect_uri | string | ❌ | 回调地址 |

**响应**:
```json
{
  "access_token": "jwt-token",
  "refresh_token": "refresh-token",
  "token_type": "bearer",
  "provider": "wechat",
  "user_id": "uuid",
  "new_user": false
}
```

---

## 3. 用户资料 (User Profile)

### GET /api/v1/user/profile
**功能**: 获取当前用户资料  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "display_name": "用户名",
  "avatar_url": "https://...",
  "email_verified": true,
  "subscription_tier": "free",
  "preferred_genre": "romance",
  "locale": "zh-CN",
  "onboarding_completed": true,
  "created_at": "2026-01-01T00:00:00"
}
```

---

### PUT /api/v1/user/profile
**功能**: 更新用户资料  
**认证**: ✅ Bearer Token  
**请求 Body**（所有字段可选）:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| display_name | string | ❌ | 显示名称 |
| avatar_url | string | ❌ | 头像URL |
| preferred_genre | string | ❌ | 偏好类型 |
| locale | string | ❌ | 语言地区 |
| onboarding_completed | boolean | ❌ | 是否完成引导 |

**响应**: 同 GET /user/profile

---

### PATCH /api/v1/user/preferences
**功能**: 部分更新用户偏好  
**认证**: ✅ Bearer Token  
**请求 Body**（所有字段可选）:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| preferred_genre | string | ❌ | 偏好类型 |
| locale | string | ❌ | 语言地区 |
| onboarding_completed | boolean | ❌ | 是否完成引导 |

**响应**:
```json
{
  "status": "ok",
  "preferences": {
    "preferred_genre": "romance",
    "locale": "zh-CN",
    "notification_enabled": true,
    "theme": "dark"
  }
}
```

---

### GET /api/v1/user/preferences
**功能**: 获取用户偏好设置  
**认证**: ✅ Bearer Token  
**响应**: 同 PATCH 响应的 preferences 部分

---

### PUT /api/v1/user/preferences
**功能**: 全量替换用户偏好  
**认证**: ✅ Bearer Token  
**请求 Body**: 同 PATCH /user/preferences  
**响应**: 同 PATCH /user/preferences

---

### GET /api/v1/user/subscription
**功能**: 获取当前用户订阅信息（⚠️ 已废弃，建议使用 /cr016/subscription/status）  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "currentPlanId": "free",
  "remainStamina": 50,
  "freeCycleStage": "honeymoon",
  "permissions": {
    "canAccessAllCharacters": false,
    "canAccessCGGallery": false,
    "canUseAdvancedFeatures": false,
    "canUseFreeChat": true,
    "canUseMemorySystem": false
  },
  "expiresAt": null,
  "autoRenew": false
}
```

---

### GET /api/v1/user/progress/{script_id}
**功能**: 获取用户在指定剧本中的进度  
**认证**: ✅ Bearer Token  
**路径参数**: `script_id` - 剧本 UUID  
**响应**:
```json
{
  "script_id": "uuid",
  "total_sessions": 3,
  "completed_sessions": 1,
  "latest_session": {
    "id": "uuid",
    "status": "active",
    "started_at": "2026-07-01T00:00:00"
  }
}
```

---

### GET /api/v1/user/dialogue-count
**功能**: 获取用户在指定剧本的对话次数  
**认证**: ✅ Bearer Token  
**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| script_id | string | ✅ | 剧本ID |

**响应**:
```json
{
  "dialogue_count": 2,
  "limit": 3,
  "can_continue": true
}
```

---

### POST /api/v1/user/dialogue-count
**功能**: 递增用户在指定剧本的对话次数  
**认证**: ✅ Bearer Token  
**请求 Body**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| script_id | string | ✅ | 剧本ID |

**响应**: 同 GET /user/dialogue-count

---

## 4. 用户中心 (Users/me)

### GET /api/v1/users/me
**功能**: 获取当前用户完整资料  
**认证**: ✅ Bearer Token  
**响应**: 同 GET /user/profile（额外包含 signature 字段）

---

### PATCH /api/v1/users/me
**功能**: 部分更新用户资料  
**认证**: ✅ Bearer Token  
**请求 Body**（所有字段可选）:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| display_name | string (2-100) | ❌ | 显示名称 |
| avatar_url | string | ❌ | 头像URL |
| signature | string (≤200) | ❌ | 个性签名 |
| locale | string | ❌ | 语言地区 |

**响应**: 同 GET /users/me

---

### POST /api/v1/users/me/change-password
**功能**: 修改密码  
**认证**: ✅ Bearer Token  
**请求 Body**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| old_password | string | ✅ | 当前密码 |
| new_password | string (≥8) | ✅ | 新密码 |

**响应**:
```json
{ "status": "ok", "message": "Password changed successfully" }
```

---

### DELETE /api/v1/users/me
**功能**: 注销账号（硬删除）  
**认证**: ✅ Bearer Token  
**响应**:
```json
{ "status": "deleted", "message": "Account deleted successfully" }
```

---

### GET /api/v1/users/me/subscription
**功能**: 获取订阅状态  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "tier": "free",
  "status": "active",
  "trial_started_at": null,
  "trial_ends_at": null,
  "renew_at": null
}
```

---

### GET /api/v1/users/me/achievements
**功能**: 获取成就列表（含进度和解锁状态）  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "achievements": [
    {
      "id": "ach_first_dialogue",
      "name": "初见",
      "description": "完成第一次对话",
      "icon": "🎭",
      "icon_url": "/assets/achievements/first_dialogue.png",
      "is_unlocked": true,
      "unlocked_at": "2026-07-15T10:00:00",
      "progress": { "current": 1, "target": 1, "percentage": 100 },
      "reward": { "type": "fragments", "amount": 20, "claimed": true }
    }
  ],
  "total": 8,
  "unlocked_count": 3,
  "claimed_count": 3
}
```

---

### GET /api/v1/users/me/stats
**功能**: 获取用户游戏统计数据  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "scripts_completed": 3,
  "total_play_time_minutes": 120,
  "endings_unlocked": 5,
  "cgs_collected": 10,
  "total_dialogues": 50
}
```

---

### GET /api/v1/users/me/asset
**功能**: 获取用户碎片余额  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "balance": 150,
  "total_earned": 500,
  "total_spent": 350
}
```

---

### GET /api/v1/users/me/latest-save
**功能**: 获取最近的存档快照  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "id": "uuid",
  "session_id": "uuid",
  "script_id": "uuid",
  "script_name": "剧本名",
  "character_name": "角色名",
  "character_avatar": "url",
  "current_node_id": "uuid",
  "label": "auto_save",
  "choice_count": 15,
  "created_at": "2026-07-20T10:00:00",
  "updated_at": "2026-07-20T10:00:00"
}
```

---

### GET /api/v1/users/me/memory/summary
**功能**: 获取 AI 记忆摘要（偏好、羁绊、事件）  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "preferences": [{ "category": "genre", "value": "romance", "weight": 0.8, "description": "..." }],
  "bonds": [{ "character_id": "uuid", "character_name": "角色名", "bond_level": "trust", "bond_value": 45, "description": "..." }],
  "events": [{ "event_id": "uuid", "event_type": "dialogue_memory", "description": "...", "created_at": "..." }],
  "total_memories": 20,
  "recent": [...],
  "is_full_available": false
}
```

---

### GET /api/v1/users/me/characters/bond
**功能**: 获取角色好感度/羁绊列表  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "characters": [
    {
      "id": "uuid",
      "name": "角色名",
      "avatar_url": "url",
      "affection_value": 45,
      "affection_level": "trust",
      "max_affection": 100
    }
  ],
  "total": 3
}
```

---

### GET /api/v1/users/me/endings
**功能**: 获取各剧本结局解锁追踪  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "endings": [
    {
      "script_id": "uuid",
      "script_name": "剧本名",
      "total_endings": 3,
      "unlocked_endings": 2,
      "ending_types": ["good", "normal"],
      "completion_rate": 66
    }
  ],
  "total_scripts": 5,
  "total_endings_unlocked": 8
}
```

---

### GET /api/v1/users/me/endings/recent
**功能**: 获取最近解锁的结局（最后3个）  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "recent_endings": [
    {
      "id": "uuid",
      "script_name": "剧本名",
      "character_name": "角色名",
      "ending_type": "good",
      "ending_title": "剧本名 - good ending",
      "ended_at": "2026-07-20T10:00:00"
    }
  ],
  "total": 3
}
```

---

### GET /api/v1/users/me/memory/full
**功能**: 获取完整 AI 记忆（需 Standard/Premium 订阅）  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "memories": [
    {
      "id": "uuid",
      "character_id": "uuid",
      "character_name": "角色名",
      "content": "记忆内容",
      "source": "game_event",
      "created_at": "2026-07-20T10:00:00"
    }
  ],
  "total": 50
}
```

---

### POST /api/v1/users/me/avatar
**功能**: 上传用户头像  
**认证**: ✅ Bearer Token  
**请求**: `multipart/form-data`，字段 `file`（支持 jpg/png/gif/webp，最大 5MB）  
**响应**:
```json
{
  "avatar_url": "http://47.107.174.176/static/avatars/xxx.jpg",
  "filename": "xxx.jpg",
  "size": 102400
}
```

---

### GET /api/v1/users/me/avatar/{filename}
**功能**: 获取头像文件  
**认证**: ❌ 不需要  
**路径参数**: `filename` - 文件名  
**响应**: 图片文件

---

### GET /api/v1/users/me/transactions
**功能**: 获取碎片交易记录（分页）  
**认证**: ✅ Bearer Token  
**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | ❌ | 页码，默认1 |
| page_size | int | ❌ | 每页数量，默认20 |

**响应**:
```json
{
  "transactions": [
    {
      "id": "uuid",
      "type": "income",
      "amount": 10,
      "source": "每日签到",
      "description": "每日签到",
      "created_at": "2026-07-20T10:00:00"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 100
}
```

---

### GET /api/v1/users/me/play-setting
**功能**: 获取游戏播放设置  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "typing_speed": "normal",
  "auto_play": false,
  "auto_play_delay_ms": 3000,
  "bgm_volume": 80,
  "sfx_volume": 100,
  "animation_enabled": true,
  "animation_quality": "high"
}
```

---

### PATCH /api/v1/users/me/play-setting
**功能**: 更新游戏播放设置  
**认证**: ✅ Bearer Token  
**请求 Body**（所有字段可选）:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| typing_speed | string | ❌ | 打字速度: slow/normal/fast/instant |
| auto_play | boolean | ❌ | 自动播放 |
| auto_play_delay_ms | int (1000-10000) | ❌ | 自动播放延迟(ms) |
| bgm_volume | int (0-100) | ❌ | 背景音乐音量 |
| sfx_volume | int (0-100) | ❌ | 音效音量 |
| animation_enabled | boolean | ❌ | 动画开关 |
| animation_quality | string | ❌ | 动画质量: low/medium/high |

**响应**: 同 GET play-setting

---

### GET /api/v1/users/me/notify-setting
**功能**: 获取通知设置  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "update_notify": true,
  "activity_reminder": true,
  "ending_unlock": true,
  "checkin_push": true,
  "affection_change": true,
  "new_script": true
}
```

---

### PATCH /api/v1/users/me/notify-setting
**功能**: 更新通知设置  
**认证**: ✅ Bearer Token  
**请求 Body**（所有字段可选）:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| update_notify | boolean | ❌ | 更新通知 |
| activity_reminder | boolean | ❌ | 活动提醒 |
| ending_unlock | boolean | ❌ | 结局解锁通知 |
| checkin_push | boolean | ❌ | 签到推送 |
| affection_change | boolean | ❌ | 好感度变化通知 |
| new_script | boolean | ❌ | 新剧本通知 |

**响应**: 同 GET notify-setting

---

### GET /api/v1/users/me/devices
**功能**: 获取登录设备列表  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "devices": [
    {
      "id": "uuid",
      "device_name": "iPhone 15",
      "device_type": "mobile",
      "browser": "Safari",
      "os": "iOS 17",
      "ip_address": "1.2.3.4",
      "location": "上海",
      "last_active_at": "2026-07-30T10:00:00",
      "is_current": true,
      "created_at": "2026-07-01T00:00:00"
    }
  ],
  "total": 2
}
```

---

### POST /api/v1/users/me/devices/{device_id}/logout
**功能**: 登出指定设备（不能登出当前设备）  
**认证**: ✅ Bearer Token  
**路径参数**: `device_id` - 设备 UUID  
**响应**:
```json
{ "status": "ok", "message": "Device logged out successfully", "device_id": "uuid" }
```

---

### GET /api/v1/users/me/member-info
**功能**: 获取会员信息（含碎片余额和近期账单）  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "tier": "standard",
  "status": "active",
  "member_since": "2026-07-01T00:00:00",
  "expires_at": "2026-08-01T00:00:00",
  "auto_renew": false,
  "fragment_balance": 150,
  "benefits": ["free_chat_enabled", "full_memory_access", "exclusive_cg"],
  "recent_bills": [
    {
      "id": "uuid",
      "type": "earn",
      "description": "每日签到",
      "amount": 10,
      "currency": "CNY",
      "created_at": "2026-07-20T10:00:00"
    }
  ]
}
```

---

### GET /api/v1/users/me/game-stats
**功能**: 获取用户游戏统计（个人中心展示用）  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "total_sessions": 10,
  "completed_sessions": 5,
  "total_choices": 80,
  "total_dialogues": 120,
  "total_play_time_minutes": 160,
  "favorite_character_id": "uuid",
  "favorite_character_name": "角色名",
  "favorite_script_id": "uuid",
  "favorite_script_name": "剧本名"
}
```

---

### GET /api/v1/users/me/latest-session
**功能**: 获取最近的游戏会话（快速继续游戏）  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "session_id": "uuid",
  "script_id": "uuid",
  "script_name": "剧本名",
  "current_node_id": "uuid",
  "started_at": "2026-07-20T10:00:00"
}
```

---

## 5. 剧本 (Scripts)

### GET /api/v1/scripts
**功能**: 获取剧本列表（支持搜索、分类、排序、分页）  
**认证**: ❌ 不需要  
**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| search | string | ❌ | 搜索关键词（标题/描述） |
| category | string | ❌ | 分类: 全部/恋爱/冒险/悬疑 等 |
| sort | string | ❌ | 排序: newest/popular/rating |
| sortType | string | ❌ | sort 的别名 |
| page | int | ❌ | 页码，默认1 |
| size | int | ❌ | 每页数量 (10-40)，默认12 |
| limit | int | ❌ | size 的别名（向后兼容） |

**响应**:
```json
{
  "categoryList": [
    { "id": "all", "name": "全部", "icon": "🎭" },
    { "id": "romance", "name": "恋爱", "icon": "💕" }
  ],
  "scripts": [
    {
      "id": "uuid",
      "slug": "script-slug",
      "title": "剧本标题",
      "description": "描述",
      "genre": "romance",
      "cover_image_url": "url",
      "route_count": 3,
      "hot_value": 100,
      "created_at": "2026-01-01T00:00:00"
    }
  ],
  "total": 50,
  "totalPage": 5,
  "page": 1,
  "size": 12,
  "limit": 12
}
```

---

### GET /api/v1/scripts/{script_id}
**功能**: 获取剧本详情（含路线、角色、结局、CG预览）  
**认证**: ✅ Bearer Token  
**路径参数**: `script_id` - 剧本 UUID  
**响应**:
```json
{
  "id": "uuid",
  "slug": "script-slug",
  "title": "剧本标题",
  "description": "描述",
  "genre": "romance",
  "cover_image_url": "url",
  "author": "剧本作者",
  "hot_value": 100,
  "routes": [
    {
      "id": "uuid",
      "title": "路线名",
      "description": "描述",
      "node_count": 20,
      "is_unlocked": true,
      "is_completed": false
    }
  ],
  "routes_count": 3,
  "endings": [
    {
      "id": "uuid",
      "title": "结局标题",
      "type": "good",
      "description": "描述",
      "unlock_condition": "条件",
      "route_id": "uuid",
      "is_unlocked": true
    }
  ],
  "endings_count": 5,
  "cg_previews": [...],
  "characters": [...],
  "chapters": [...],
  "totalNodes": 60,
  "unlockedNodes": 30,
  "completionRate": 50
}
```

---

### GET /api/v1/scripts/{script_id}/characters
**功能**: 获取剧本的角色列表  
**认证**: ❌ 不需要  
**路径参数**: `script_id` - 剧本 UUID  
**响应**:
```json
{
  "characters": [
    {
      "id": "uuid",
      "name": "角色名",
      "description": "描述",
      "age": "18",
      "height": "165cm",
      "birthday": "2008-03-15",
      "likes": ["书籍", "花束"],
      "personality": {},
      "avatar_url": "url",
      "is_main": true
    }
  ],
  "total": 3
}
```

---

### GET /api/v1/scripts/{script_id}/routes
**功能**: 获取剧本路线探索树（路线→章节→分支）  
**认证**: ✅ Bearer Token  
**路径参数**: `script_id` - 剧本 UUID  
**响应**:
```json
{
  "routes": [
    {
      "id": "uuid",
      "name": "路线名",
      "chapters": [
        {
          "id": "ch1",
          "title": "第一章：初遇",
          "completed": false,
          "branches": [
            {
              "id": "branch1",
              "name": "主线",
              "affection": 0,
              "unlocked": true
            }
          ]
        }
      ]
    }
  ]
}
```

---

### GET /api/v1/scripts/{script_id}/endings
**功能**: 获取剧本结局列表（含解锁状态）  
**认证**: ✅ Bearer Token  
**路径参数**: `script_id` - 剧本 UUID  
**响应**:
```json
{
  "endings": [
    {
      "id": "uuid",
      "title": "结局标题",
      "type": "good",
      "description": "描述",
      "unlockCondition": "条件",
      "routeId": "uuid",
      "routeName": "路线名",
      "unlocked": true,
      "unlockDate": "2026-07-20"
    }
  ],
  "total": 5,
  "unlockedCount": 2
}
```

---

### GET /api/v1/scripts/{script_id}/cg-preview
**功能**: 获取剧本 CG 预览缩略图（含解锁状态）  
**认证**: ✅ Bearer Token  
**路径参数**: `script_id` - 剧本 UUID  
**响应**:
```json
{
  "cgs": [
    {
      "id": "uuid",
      "name": "CG名称",
      "imageUrl": "url",
      "routeId": "uuid",
      "unlocked": false
    }
  ],
  "total": 6,
  "unlockedCount": 2
}
```

---

### GET /api/v1/scripts/{script_id}/detail
**功能**: 获取剧本详情（含章节和节点数据，用于页面渲染）  
**认证**: ✅ Bearer Token  
**路径参数**: `script_id` - 剧本 UUID  
**响应**:
```json
{
  "scriptId": "uuid",
  "title": "剧本标题",
  "cover": "url",
  "description": "描述",
  "author": "剧本作者",
  "chapters": [
    {
      "chapterId": "uuid-000",
      "title": "第1章",
      "nodes": [
        {
          "nodeId": "uuid",
          "type": "fixed_scene",
          "title": "节点标题",
          "isUnlocked": true
        }
      ]
    }
  ],
  "totalNodes": 60,
  "unlockedNodes": 30,
  "completionRate": 50
}
```

---

## 6. 游戏 (Game)

### POST /api/v1/game/start
**功能**: 开始新游戏会话（或恢复已有活跃会话）  
**认证**: ✅ Bearer Token  
**请求 Body**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| script_id | string | ✅ | 剧本 UUID |
| route_id | string | ❌ | 路线 UUID（不填则取第一条路线） |
| custom_name | string | ❌ | 自定义会话名称 |

**响应**:
```json
{
  "session_id": "uuid",
  "node_id": "uuid",
  "message": "Game started",
  "resumed": false
}
```

---

### GET /api/v1/game/{session_id}
**功能**: 获取当前游戏会话状态  
**认证**: ✅ Bearer Token  
**路径参数**: `session_id` - 会话 UUID  
**响应**:
```json
{
  "session_id": "uuid",
  "status": "active",
  "current_node_id": "uuid",
  "current_node": {
    "id": "uuid",
    "type": "preset",
    "content": {},
    "route_id": "uuid"
  },
  "is_ended": false,
  "ending_type": null
}
```

---

### GET /api/v1/game/{session_id}/dialogue
**功能**: 获取当前节点的对话内容（非流式）  
**认证**: ✅ Bearer Token  
**路径参数**: `session_id` - 会话 UUID  
**响应**:
```json
{
  "type": "dialogue",
  "text": "对话文本",
  "emotion": "happy",
  "node_id": "uuid",
  "choices": [
    { "id": "uuid", "text": "选项文本" }
  ],
  "character_id": "uuid",
  "ending_type": null,
  "session_id": "uuid",
  "current_node": {},
  "narrator_text": "旁白文本",
  "narrator_visible": true,
  "remaining_quota": 45,
  "quota_deducted": false,
  "paywall_trigger": null,
  "chapter": "第1章",
  "chapter_id": "uuid",
  "has_next_chapter": true,
  "next_chapter_id": "uuid",
  "next_chapter_title": "第2章",
  "progress": 25.5,
  "total_nodes": 60,
  "explored_nodes": 15
}
```

---

### GET /api/v1/game/{session_id}/dialogue/stream
**功能**: SSE 流式获取对话内容  
**认证**: ✅ Bearer Token  
**路径参数**: `session_id` - 会话 UUID  
**响应**: Server-Sent Events (text/event-stream)

---

### POST /api/v1/game/{session_id}/choice
**功能**: 提交玩家选择并推进游戏  
**认证**: ✅ Bearer Token  
**路径参数**: `session_id` - 会话 UUID  
**请求 Body**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| choice_id | string | ✅ | 选项 UUID |

**响应**:
```json
{
  "next_node_id": "uuid",
  "text": "下一段文本",
  "emotion": "neutral",
  "is_ended": false,
  "remaining_quota": 44,
  "quota_deducted": true,
  "paywall_trigger": null,
  "convergence_reached": false,
  "new_achievements": []
}
```

---

### POST /api/v1/game/{session_id}/free-chat
**功能**: 自由对话（与角色自由聊天）  
**认证**: ✅ Bearer Token  
**路径参数**: `session_id` - 会话 UUID  
**请求 Body**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| message | string | ✅ | 用户消息 |
| topic_id | string | ❌ | 话题ID |

**响应**:
```json
{
  "session_id": "uuid",
  "reply": "角色回复",
  "emotion": "happy",
  "character_id": "uuid",
  "new_achievements": []
}
```

---

### GET /api/v1/game/{session_id}/free-chat/topics
**功能**: 获取自由对话推荐话题  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "topics": [
    { "id": "t1", "label": "话题", "emoji": "💬", "description": "描述" }
  ]
}
```

---

### GET /api/v1/game/{session_id}/free-chat/history
**功能**: 获取自由对话消息历史  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "messages": [
    { "role": "user", "content": "消息", "timestamp": "..." }
  ]
}
```

---

### POST /api/v1/game/{session_id}/custom-input
**功能**: 玩家自由输入推进剧情  
**认证**: ✅ Bearer Token  
**路径参数**: `session_id` - 会话 UUID  
**请求 Body**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| text | string | ✅ | 自由输入文本 |

**响应**:
```json
{
  "text": "角色回复",
  "emotion": "neutral",
  "choices": [...],
  "remaining_quota": 44,
  "new_achievements": []
}
```

---

### GET /api/v1/game/{script_id}/route-map
**功能**: 获取剧本路线探索地图  
**认证**: ✅ Bearer Token  
**路径参数**: `script_id` - 剧本 UUID  
**响应**: 返回所有路线及节点图，标记已探索/未探索

---

### POST /api/v1/game/{session_id}/convergence/check
**功能**: 检查是否到达剧情收敛点  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "reached": true,
  "convergence_point": {
    "id": "uuid",
    "chapter": "第3章",
    "title": "命运交汇",
    "description": "描述"
  },
  "rounds_played": 4,
  "rounds_required": 4
}
```

---

### POST /api/v1/game/auto-save
**功能**: 自动存档（选择后保存游戏状态）  
**认证**: ✅ Bearer Token  
**请求 Body**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| session_id | string | ✅ | 会话 UUID |
| node_id | string | ✅ | 当前节点 UUID |
| choice_id | string | ✅ | 选择的选项 UUID |

**响应**:
```json
{
  "save_id": "uuid",
  "saved_at": "2026-07-30T10:00:00",
  "message": "自动存档成功"
}
```

---

### POST /api/v1/game/onboarding
**功能**: 首次游玩引导对话（AI 生成 + 预设兜底）  
**认证**: ✅ Bearer Token  
**响应**: 返回引导对话内容

---

### GET /api/v1/game/{session_id}/progress
**功能**: 获取游戏进度数据（进度条展示）  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "session_id": "uuid",
  "script_id": "uuid",
  "current_node_id": "uuid",
  "current_chapter": "第1章",
  "total_nodes": 60,
  "explored_nodes": 15,
  "completion_rate": 25.0,
  "progress_percentage": 25.0,
  "choice_count": 15,
  "dialogue_count": 20,
  "status": "active"
}
```

---

### GET /api/v1/game/{session_id}/status
**功能**: 获取游戏状态（剧本名、角色名、好感度）  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "session_id": "uuid",
  "script_id": "uuid",
  "script_name": "剧本名",
  "character_id": "uuid",
  "character_name": "角色名",
  "affection_value": 45,
  "affection_level": "trust",
  "status": "active",
  "current_node_id": "uuid"
}
```

---

### GET /api/v1/game/{session_id}/history
**功能**: 获取游戏历史记录  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "session_id": "uuid",
  "history": [
    {
      "index": 0,
      "node_id": "uuid",
      "choice_id": "uuid",
      "choice_text": "选项文本",
      "timestamp": "2026-07-20T10:00:00"
    }
  ],
  "total_entries": 15
}
```

---

### POST /api/v1/game/{session_id}/dialogue
**功能**: 存储对话消息记录  
**认证**: ✅ Bearer Token  
**请求 Body**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| role | string | ✅ | 角色: user/assistant |
| content | string | ✅ | 消息内容 |
| character_id | string | ❌ | 角色 UUID |
| character_name | string | ❌ | 角色名 |
| emotion | string | ❌ | 情感标签 |

**响应**:
```json
{
  "id": "uuid",
  "session_id": "uuid",
  "role": "user",
  "content": "消息",
  "character_id": "uuid",
  "character_name": "角色名",
  "emotion": "happy",
  "created_at": "2026-07-20T10:00:00"
}
```

---

### GET /api/v1/game/{session_id}/dialogues
**功能**: 查询会话对话历史  
**认证**: ✅ Bearer Token  
**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| limit | int | ❌ | 返回数量，默认50，最大200 |
| offset | int | ❌ | 偏移量，默认0 |

**响应**:
```json
{
  "dialogues": [...],
  "total": 50,
  "limit": 50,
  "offset": 0
}
```

---

### POST /api/v1/game/{session_id}/gift
**功能**: 在游戏中给角色送礼  
**认证**: ✅ Bearer Token  
**路径参数**: `session_id` - 会话 UUID  
**请求 Body**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| character_id | string | ✅ | 角色 UUID |
| gift_id | string | ✅ | 礼物 UUID |
| quantity | int | ❌ | 数量，默认1 |

**响应**:
```json
{
  "status": "success",
  "message": "Successfully sent 礼物名 to 角色名",
  "affection_delta": 5,
  "new_affection": 50,
  "fragments_spent": 10,
  "remaining_fragments": 140
}
```

---

### GET /api/v1/game/{session_id}/gift-history
**功能**: 获取送礼历史记录  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "gifts": [
    {
      "id": "uuid",
      "character_id": "uuid",
      "character_name": "角色名",
      "gift_id": "uuid",
      "gift_name": "礼物名",
      "quantity": 1,
      "affection_delta": 5,
      "created_at": "2026-07-20T10:00:00"
    }
  ],
  "total": 5
}
```

---

## 7. 角色 (Characters)

### GET /api/v1/characters
**功能**: 获取所有角色列表  
**认证**: ❌ 不需要  
**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| include_main | boolean | ❌ | 是否包含主角色，默认true |
| limit | int | ❌ | 返回数量，默认50 |

**响应**:
```json
{
  "characters": [
    {
      "id": "uuid",
      "name": "角色名",
      "description": "描述",
      "avatar_url": "url",
      "is_main": true,
      "age": "18",
      "height": "165cm",
      "birthday": "2008-03-15",
      "likes": ["书籍"],
      "personality": {},
      "script_count": 2
    }
  ],
  "total": 10
}
```

---

### GET /api/v1/characters/{character_id}
**功能**: 获取角色详情（含立绘、好感度、性格标签）  
**认证**: ✅ Bearer Token  
**路径参数**: `character_id` - 角色 UUID  
**响应**:
```json
{
  "id": "uuid",
  "name": "角色名",
  "description": "描述",
  "dialogueStyle": { "speechPattern": "语尾带呢", "catchphrase": "", "tone": "" },
  "portraits": { "normal": "url", "happy": "url" },
  "sprites": [{ "emotion": "happy", "image_url": "url" }],
  "age": 18,
  "height": 165,
  "birthday": "2008-03-15",
  "likes": ["书籍"],
  "personality": {},
  "personality_tags": [{ "name": "gentle", "description": "温柔体贴" }],
  "avatar_url": "url",
  "is_main": true,
  "affection": {
    "value": 45,
    "level": "trust",
    "level_label": "信赖",
    "next_level": { "level": "bond", "level_label": "羁绊", "threshold": 60, "remaining": 15 }
  },
  "preferences": { "likedGifts": [], "dislikedGifts": [], "likedTopics": [] }
}
```

---

### GET /api/v1/characters/{character_id}/personality
**功能**: 获取角色性格数据（含全局平均值）  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "character_id": "uuid",
  "personality": {
    "traits": [
      { "key": "gentle", "label": "温柔", "value": 80, "average": 50 }
    ]
  },
  "global_average": { "gentle": 50, "wisdom": 40, "brave": 60, "mysterious": 30, "loyal": 70 }
}
```

---

### GET /api/v1/characters/{character_id}/voices
**功能**: 获取角色语音资源  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "character_id": "uuid",
  "voices": [
    { "id": "voice-xxx-1", "label": "打招呼", "icon": "👋" }
  ]
}
```

---

### GET /api/v1/characters/{character_id}/detail
**功能**: 获取增强角色详情（含 AI 验证规则，CR-015）  
**认证**: ✅ Bearer Token  
**响应**: 含 aiValidationRules、dialogueStyle、preferences 等完整数据

---

### GET /api/v1/characters/gifts/catalog
**功能**: 获取礼物目录  
**认证**: ❌ 不需要  
**响应**:
```json
{
  "gifts": [
    {
      "id": "uuid",
      "name": "礼物名",
      "description": "描述",
      "price": 10,
      "affection_bonus": 5,
      "icon_url": "url"
    }
  ],
  "total": 5
}
```

---

### GET /api/v1/characters/{character_id}/gift-history
**功能**: 获取角色送礼历史  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "gifts": [...],
  "total": 5
}
```

---

## 8. AI 对话验证

### POST /api/v1/ai/validate-dialogue
**功能**: 验证 AI 对话内容是否符合角色规则（CR-015）  
**认证**: ✅ Bearer Token  
**请求 Body**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| characterId | string | ✅ | 角色 UUID |
| dialogue | string | ✅ | 对话文本 |
| context | object | ❌ | 上下文信息 |

**响应**:
```json
{
  "valid": true,
  "score": 90,
  "issues": [],
  "suggestions": ["建议使用更温柔的语气"]
}
```

---

## 9. 好感度 (Affection)

### GET /api/v1/affection
**功能**: 获取当前用户所有角色好感度  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "affections": [
    { "character_id": "uuid", "value": 45, "level": "trust" }
  ]
}
```

---

### GET /api/v1/affection/{character_id}
**功能**: 获取指定角色的好感度及变化历史  
**认证**: ✅ Bearer Token  
**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| limit | int | ❌ | 历史记录数量，默认50 |

**响应**:
```json
{
  "character_id": "uuid",
  "character_name": "角色名",
  "affection_value": 45,
  "level": "trust",
  "history": [
    {
      "delta": 5,
      "old_value": 40,
      "new_value": 45,
      "old_level": "ambiguous",
      "new_level": "trust",
      "reason": "gift",
      "created_at": "2026-07-20T10:00:00"
    }
  ]
}
```

---

### GET /api/v1/affection/history
**功能**: 获取指定角色的好感度变化历史  
**认证**: ✅ Bearer Token  
**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| character_id | string | ✅ | 角色 UUID |
| limit | int | ❌ | 历史记录数量，默认50 |

**响应**:
```json
{
  "character_id": "uuid",
  "character_name": "角色名",
  "history": [...],
  "total": 10
}
```

---

## 10. 记忆系统 (Memories)

### POST /api/v1/memories
**功能**: 创建角色记忆  
**认证**: ✅ Bearer Token  
**请求 Body**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| session_id | string | ✅ | 会话 UUID |
| content | string (1-2000) | ✅ | 记忆内容 |
| source | string | ❌ | 来源: game_event/dialogue/choice/system |
| character_id | string | ❌ | 角色 UUID |

**响应**: 返回创建的记忆对象

---

### GET /api/v1/memories
**功能**: 获取记忆列表（可按会话/角色筛选）  
**认证**: ✅ Bearer Token  
**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| session_id | string | ❌ | 会话 UUID |
| character_id | string | ❌ | 角色 UUID |
| limit | int | ❌ | 数量，默认50 |
| offset | int | ❌ | 偏移量，默认0 |

**响应**:
```json
{
  "memories": [...],
  "total": 20
}
```

---

### GET /api/v1/memories/recall
**功能**: 语义相似度搜索记忆（向量检索 + 全文回退）  
**认证**: ✅ Bearer Token  
**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string (1-500) | ✅ | 搜索查询 |
| character_id | string | ❌ | 角色 UUID |
| session_id | string | ❌ | 会话 UUID |
| limit | int | ❌ | 数量，默认5，最大20 |
| min_similarity | float | ❌ | 最小相似度，默认0.3 |

**响应**:
```json
{
  "memories": [
    { "id": "uuid", "content": "记忆", "source": "game_event", "confidence": 1.0, "similarity": 0.85 }
  ],
  "total": 3,
  "method": "vector"
}
```

---

### GET /api/v1/memories/{memory_id}
**功能**: 获取单条记忆详情  
**认证**: ✅ Bearer Token  
**路径参数**: `memory_id` - 记忆 UUID  

---

## 11. 签到 (Sign/Daily)

### POST /api/v1/sign/checkin
**功能**: 每日签到（含分层奖励）  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "status": "success",
  "streak_days": 7,
  "fragments_earned": 3,
  "milestone": {
    "milestone_day": 7,
    "title": "七日之约",
    "description": "连续签到 7 天 +20 碎片 + 隐藏对话解锁",
    "reward": { "type": "fragment", "amount": 20 },
    "special_item": "hidden_dialogue"
  },
  "message": "签到成功！获得 3 碎片，连续签到 7 天"
}
```

---

### GET /api/v1/sign/info
**功能**: 获取签到信息（个人中心用）  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "checked_in_today": true,
  "streak_days": 7,
  "total_checkins": 30,
  "total_fragments": 150,
  "this_week": [true, true, true, true, true, false, false],
  "next_milestone": {
    "days": 14,
    "reward_type": "fragment",
    "reward_amount": 30,
    "title": "两周之约",
    "description": "连续签到 14 天 +30 碎片 + 稀有CG解锁"
  }
}
```

---

### POST /api/v1/daily/checkin
**功能**: 每日签到（旧版入口）  
**认证**: ✅ Bearer Token  
**响应**: 同 POST /sign/checkin

---

### GET /api/v1/daily/tasks
**功能**: 获取每日任务进度  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "tasks": [
    {
      "id": "task_dialogue",
      "title": "完成 3 次对话",
      "description": "与角色进行 3 次对话",
      "progress": 3,
      "target": 3,
      "completed": true,
      "reward": { "type": "fragment", "amount": 10 }
    }
  ],
  "total": 3,
  "completed": 2,
  "all_completed": false,
  "reset_at": "UTC 00:00"
}
```

---

### GET /api/v1/daily/stats
**功能**: 获取签到统计  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "current_streak": 7,
  "longest_streak": 30,
  "total_days": 45,
  "today_checked_in": true
}
```

---

## 12. 每日任务 (Daily Tasks)

### GET /api/v1/daily-tasks
**功能**: 获取今日每日任务（含进度）  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "tasks": [
    {
      "id": "task_dialogue",
      "title": "完成 3 次对话",
      "progress": 2,
      "target": 3,
      "completed": false,
      "claimed": false,
      "reward_type": "fragments",
      "reward_amount": 10
    }
  ],
  "total": 3,
  "completed": 1,
  "claimed": 0,
  "reset_at": "UTC 00:00"
}
```

---

### POST /api/v1/daily-tasks/progress
**功能**: 更新任务进度（游戏引擎调用）  
**认证**: ✅ Bearer Token  
**请求 Body**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| task_type | string | ✅ | 任务类型: task_dialogue/task_choice/task_profile |
| increment | int | ❌ | 增量，默认1 |

**响应**: 返回更新后的任务状态

---

### POST /api/v1/daily-tasks/claim
**功能**: 领取任务奖励  
**认证**: ✅ Bearer Token  
**请求 Body**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| task_type | string | ✅ | 任务类型 |

**响应**:
```json
{
  "task_type": "task_dialogue",
  "claimed": true,
  "reward": { "type": "fragments", "amount": 10 }
}
```

---

## 13. 活跃度 (Activity)

### GET /api/v1/activity/progress
**功能**: 获取当前活跃度进度和宝箱资格  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "activity_points": 100,
  "chests": [
    {
      "tier": 1,
      "name": "青铜宝箱",
      "icon": "🥉",
      "threshold": 50,
      "eligible": true,
      "claimed": true,
      "can_claim": false,
      "rewards": [{ "type": "fragments", "amount": 30 }]
    }
  ],
  "reset_at": "UTC 00:00"
}
```

---

### POST /api/v1/activity/claim
**功能**: 领取活跃度宝箱奖励  
**认证**: ✅ Bearer Token  
**请求 Body**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| chest_tier | int | ✅ | 宝箱等级: 1/2/3 |

**响应**:
```json
{
  "chest_tier": 2,
  "name": "白银宝箱",
  "icon": "🥈",
  "claimed": true,
  "rewards": [{ "type": "fragments", "amount": 100 }],
  "claimed_at": "2026-07-30T10:00:00"
}
```

---

## 14. 成就 (Achievements)

### GET /api/v1/achievements
**功能**: 获取所有成就定义及用户解锁/领取状态（自动解锁进度达标的成就）  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "achievements": [
    {
      "id": "ACH-001",
      "name": "初见",
      "description": "完成第一次对话",
      "icon": "🎭",
      "rarity": "common",
      "reward": { "type": "fragments", "amount": 20 },
      "condition": { "type": "dialogue_count", "value": 1 },
      "progress": { "current": 1, "target": 1 },
      "isUnlocked": true,
      "isClaimed": false,
      "unlockedAt": "2026-07-15T10:00:00",
      "claimedAt": null
    }
  ],
  "total": 15,
  "unlocked_count": 5,
  "claimed_count": 3,
  "auto_unlocked": ["ACH-001"]
}
```

---

### POST /api/v1/achievements/unlock
**功能**: 手动触发/解锁成就  
**认证**: ✅ Bearer Token  
**请求 Body**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| achievement_id | string | ✅ | 成就ID（如 ACH-001） |

**响应**: 返回成就解锁信息

---

### POST /api/v1/achievements/claim
**功能**: 领取成就奖励（碎片）  
**认证**: ✅ Bearer Token  
**请求 Body**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| achievement_id | string | ✅ | 成就ID |

**响应**:
```json
{
  "achievement_id": "ACH-001",
  "claimed": true,
  "reward": { "type": "fragments", "amount": 20 },
  "claimed_at": "2026-07-30T10:00:00"
}
```

---

## 15. 画廊/收藏 (Gallery)

### POST /api/v1/gallery/collections
**功能**: 添加收藏物品  
**认证**: ✅ Bearer Token  
**请求 Body**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| item_type | string | ✅ | 类型: cg/character/scene |
| item_id | string | ✅ | 物品ID |
| item_name | string | ✅ | 物品名称 |
| image_url | string | ❌ | 图片URL |

---

### GET /api/v1/gallery/collections
**功能**: 获取用户收藏列表（按剧本分组）  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "collections": [
    {
      "id": "uuid",
      "name": "剧本名",
      "description": "描述",
      "cover_url": "url",
      "items_count": 10,
      "items_unlocked": 5,
      "script_id": "uuid"
    }
  ]
}
```

---

### GET /api/v1/gallery/collections/{script_id}
**功能**: 获取指定剧本的所有 CG 物品（含解锁状态）  
**认证**: ✅ Bearer Token  
**响应**:
```json
{
  "items": [
    {
      "id": "uuid",
      "collection_id": "uuid",
      "title": "CG名称",
      "thumbnail_url": "url",
      "full_url": "url",
      "script_name": "路线名",
      "unlock_status": "unlocked",
      "unlock_condition": ""
    }
  ]
}
```

---

### DELETE /api/v1/gallery/collections/{collection_id}
**功能**: 删除收藏物品  
**认证**: ✅ Bearer Token  

---

### POST /api/v1/gallery/achievements
**功能**: 解锁成就（旧版）  
**认证**: ✅ Bearer Token  

---

### GET /api/v1/gallery/achievements
**功能**: 获取成就列表（旧版）  
**认证**: ✅ Bearer Token  

---

### GET /api/v1/gallery/cgs
**功能**: 获取 CG 画廊（含解锁状态）  
**认证**: ✅ Bearer Token  

---

### GET /api/v1/gallery/memories
**功能**: 获取角色记忆列表  
**认证**: ✅ Bearer Token  
**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| character_id | string | ❌ | 角色 UUID |
| limit | int | ❌ | 数量，默认50 |

---

### GET /api/v1/achievements
**功能**: 获取成就墙（Mock 数据）  
**认证**: ✅ Bearer Token  

---

## 16. 碎片商城 (Fragment)

### GET /api/v1/fragment/shop/goods
**功能**: 获取商城商品列表  
**认证**: ✅ Bearer Token  
**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| category | string | ❌ | 分类: cg/voice/skin/item |
| page | int | ❌ | 页码，默认1 |
| page_size | int | ❌ | 每页数量，默认20 |

**响应**:
```json
{
  "goods": [
    {
      "id": "uuid",
      "name": "商品名",
      "description": "描述",
      "category": "cg",
      "icon_url": "url",
      "price": 50,
      "stock": 100,
      "limit_per_user": 1,
      "owned": false,
      "is_available": true
    }
  ],
  "total": 20,
  "page": 1,
  "page_size": 20
"""
  "success": true,
  "record_id": "uuid",
  "viewed": true
}
```

---

### POST /api/v1/cr017/unlock/batch
**功能**: 批量记录解锁事件
**认证**: ✅ Bearer Token
**请求 Body**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| unlocks | array | ✅ | 解锁记录列表，每项含 unlock_type/content_id/title/description/image_url/rarity/reward_data |

**响应**:
```json
{
  "success": true,
  "recorded_count": 3,
  "records": [...]
}
```

---

## 34. 支付 (Payment - 旧版)

### GET /api/v1/payment/plans
**功能**: 获取订阅套餐列表
**认证**: ❌ 不需要

### POST /api/v1/payment/subscribe
**功能**: Mock 订阅购买
**认证**: ✅ Bearer Token
**请求 Body**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| plan | string | ✅ | 套餐: free/basic/premium |
| billing_cycle | string | ❌ | 周期: monthly/yearly |

### POST /api/v1/payment/purchase
**功能**: Mock 内购（碎片/体力）
**认证**: ✅ Bearer Token
**请求 Body**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| item_id | string | ✅ | 物品ID: fragments_100/fragments_500/stamina_5 等 |
| item_name | string | ✅ | 物品名称 |
| price | float | ✅ | 价格 |
| currency | string | ❌ | 货币，默认USD |

### POST /api/v1/payment/recharge
**功能**: Mock 碎片充值
**认证**: ✅ Bearer Token
**请求 Body**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| shards | int | ✅ | 碎片数量 |
| amount | float | ✅ | 金额 |
| currency | string | ❌ | 货币，默认USD |
| provider | string | ❌ | 支付提供商，默认mock |

### GET /api/v1/payment/history
**功能**: 获取支付历史
**认证**: ✅ Bearer Token
**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | ❌ | 页码，默认1 |
| page_size | int | ❌ | 每页数量，默认20 |

---

## 35. 上传 (Upload)

### POST /api/v1/upload/image
**功能**: 上传图片（自动分类）
**认证**: ❌ 不需要
**请求**: multipart/form-data，字段 file
**响应**:
```json
{
  "success": true,
  "url": "http://47.107.174.176:8000/static/images/scripts/covers/xxx.jpg",
  "path": "/static/images/scripts/covers/xxx.jpg",
  "category": "scripts/covers",
  "filename": "xxx.jpg",
  "original_filename": "original.jpg"
}
```

### GET /api/v1/upload/list
**功能**: 列出所有已上传图片
**认证**: ❌ 不需要
**响应**:
```json
{
  "success": true,
  "images": [...],
  "total": 50
}
```

---

## 36. 用户订阅 (User Subscription - 旧版)

### GET /api/v1/user/subscription
**功能**: 获取用户订阅信息（⚠️ 已废弃）
**认证**: ✅ Bearer Token

### POST /api/v1/order/create
**功能**: 创建订阅订单
**认证**: ✅ Bearer Token
**请求 Body**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| planId | string | ✅ | 套餐: basic/standard/premium |
| cycleType | string | ✅ | 周期: monthly/yearly |

**响应**:
```json
{
  "orderId": "order_xxx",
  "payUrl": "https://payment.example.com/pay?order_id=xxx",
  "amount": 4.99,
  "currency": "USD"
}
```

---

## 附录

### 订阅套餐说明

| 套餐 | 月价 | 年价 | 每日对话额度 | 碎片折扣率 |
|------|------|------|------------|-----------|
| Free | /bin/sh | /bin/sh | 50次 | 0% |
| Basic | .99 | 9.99 | 200次 | 10% |
| Standard | .99 | 9.99 | 500次 | 20% |
| Premium | .99 | 9.99 | 无限 | 30% |

### 签到奖励规则

| 连续天数 | 每日基础奖励 |
|---------|------------|
| 1-6天 | 2碎片/天 |
| 7-13天 | 3碎片/天 |
| 14-29天 | 5碎片/天 |
| 30天+ | 8碎片/天 |

**里程碑奖励**:
- 3天: +10碎片
- 7天: +20碎片 + 隐藏对话
- 14天: +30碎片 + 稀有CG + 好感度+5
- 30天: +50碎片 + 独占CG + 成就

### 好感度等级

| 等级 | 范围 | 标签 |
|------|------|------|
| 相识 | 0-19 | acquaintance |
| 暧昧 | 20-39 | ambiguous |
| 信赖 | 40-59 | trust |
| 羁绊 | 60-79 | bond |
| 挚爱 | 80-100 | love |

### 活跃度宝箱

| 等级 | 名称 | 所需活跃度 | 奖励 |
|------|------|-----------|------|
| 1 | 青铜宝箱 | 50点 | 30碎片 |
| 2 | 白银宝箱 | 150点 | 100碎片 |
| 3 | 黄金宝箱 | 300点 | 250碎片 |

### 碎片兑换比例
- 3碎片 = 1次对话额度

### 付费墙触发场景

| 场景 | 类型 | 触发条件 |
|------|------|---------|
| T1 | fullscreen | 对话额度用完 |
| T2 | fullscreen | 高级功能需要订阅 |
| T3 | banner | 对话次数达到阈值 |
| T4 | fullscreen | 高级角色需要订阅 |
| T5 | toast | CG画廊需要订阅 |
| T6 | banner | 不活跃用户回归 |
| T7 | toast | 成就完成提示 |
| T8 | toast | 碎片不足 |

### 解锁类型 (CR-017)

| 类型 | 说明 |
|------|------|
| cg | CG 解锁 |
| achievement | 成就解锁 |
| hidden_story | 隐藏剧情 |
| voice | 语音解锁 |
| exclusive_script | 独占剧本 |
| reward_float | 浮动奖励 |
| multi_reward | 组合奖励 |

### 稀有度

| 等级 | 说明 |
|------|------|
| R | 普通 |
| SR | 稀有 |
| SSR | 超稀有 |

---

> **注意**: 标注为 ⚠️ 已废弃的接口仍可正常使用，但建议迁移到新版接口。
> 所有需要认证的接口均需在请求头中携带  `Authorization: Bearer <token>`。
