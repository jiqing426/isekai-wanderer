# API Contract 补充 — 设置页面优化（CR-008 w07-settings v4.2）

> 时间：2026-07-21
> 用途：BE 新增/扩展接口 + FE 对接
> 基线路径：`/api/v1`
> 关联文档：`docs/api/api-contract-post-refactor.md`（主 Contract）

---

## 0. 路径映射说明

PRD 使用 `/api/user/xxx` 路径，统一映射为 `/api/v1/users/me/xxx` 风格。

| PRD 路径 | 实际路径 | 说明 |
|----------|---------|------|
| /api/user/profile | /api/v1/users/me | 已有 |
| /api/user/play-setting | /api/v1/users/me/play-setting | 新增 |
| /api/user/notify-setting | /api/v1/users/me/notify-setting | 新增 |
| /api/user/login-device | /api/v1/users/me/devices | 新增 |
| /api/user/member-info | /api/v1/users/me/member-info | 新增 |
| /api/user/profile/update | PATCH /api/v1/users/me | 已有（扩展 signature） |
| /api/user/play-setting/save | PATCH /api/v1/users/me/play-setting | 新增 |
| /api/user/notify-setting.save | PATCH /api/v1/users/me/notify-setting | 新增 |
| /api/user/password/update | /api/v1/users/me/change-password | 已有 |
| /api/user/device.logout | POST /api/v1/users/me/devices/{id}/logout | 新增 |

---

## 1. 已有接口扩展

### 1.1 `PATCH /api/v1/users/me` — 扩展 signature 字段

**变更：** 在现有请求体中新增 `signature` 字段

**请求 Body（扩展后）：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| display_name | string | 否 | 2-100 字符 |
| avatar_url | string | 否 | 头像 URL |
| signature | string | 否 | 个性签名，0-200 字符（新增） |
| locale | string | 否 | `zh-CN` / `en-US` |

**响应 200（扩展后）：**
```json
{
  "id": "bd7f90f9-...",
  "email": "user@example.com",
  "display_name": "夜行者",
  "avatar_url": "https://cdn.example.com/avatars/user001.png",
  "signature": "在异世界寻找意义",
  "email_verified": true,
  "subscription_tier": "standard",
  "preferred_genre": "romance",
  "locale": "zh-CN",
  "onboarding_completed": true,
  "created_at": "2026-06-01T10:00:00Z"
}
```

**数据库变更：** `users` 表新增 `signature` 列（VARCHAR(200), nullable）

**前端消费方：**
```typescript
interface UserProfile {
  // ... 已有字段
  signature: string | null;  // 新增
}
```

---

## 2. 新增接口

### 2.1 `GET /api/v1/users/me/play-setting` — 获取播放偏好

**用途：** 设置页面 → 播放偏好模块
**认证：** Bearer

**数据来源：** `user_settings` 表（需扩展字段）

**响应 200：**
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

**字段说明：**
| 字段 | 类型 | 说明 |
|------|------|------|
| typing_speed | string | `slow` / `normal` / `fast` / `instant` |
| auto_play | boolean | 是否自动播放对话 |
| auto_play_delay_ms | number | 自动播放延迟（毫秒） |
| bgm_volume | number | 背景音乐音量 0-100 |
| sfx_volume | number | 音效音量 0-100 |
| animation_enabled | boolean | 是否启用动画 |
| animation_quality | string | `low` / `medium` / `high` |

**数据库变更：** `user_settings` 表新增：
- `typing_speed` VARCHAR(20) DEFAULT 'normal'
- `auto_play` BOOLEAN DEFAULT false
- `auto_play_delay_ms` INTEGER DEFAULT 3000
- `animation_enabled` BOOLEAN DEFAULT true
- `animation_quality` VARCHAR(20) DEFAULT 'high'

**前端消费方：** `SettingsView.vue` → `PlaySettingPanel`
```typescript
interface PlaySetting {
  typing_speed: 'slow' | 'normal' | 'fast' | 'instant';
  auto_play: boolean;
  auto_play_delay_ms: number;
  bgm_volume: number;
  sfx_volume: number;
  animation_enabled: boolean;
  animation_quality: 'low' | 'medium' | 'high';
}
```

---

### 2.2 `PATCH /api/v1/users/me/play-setting` — 保存播放偏好

**用途：** 设置页面 → 播放偏好保存
**认证：** Bearer

**请求 Body：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| typing_speed | string | 否 | `slow` / `normal` / `fast` / `instant` |
| auto_play | boolean | 否 | |
| auto_play_delay_ms | number | 否 | 1000-10000 |
| bgm_volume | number | 否 | 0-100 |
| sfx_volume | number | 否 | 0-100 |
| animation_enabled | boolean | 否 | |
| animation_quality | string | 否 | `low` / `medium` / `high` |

**响应 200：** 同 GET 响应结构

**错误码：** VALIDATION_ERROR(422)

---

### 2.3 `GET /api/v1/users/me/notify-setting` — 获取通知设置

**用途：** 设置页面 → 通知推送模块
**认证：** Bearer

**数据来源：** `user_settings` 表（需扩展字段）

**响应 200：**
```json
{
  "update_notify": true,
  "activity_reminder": true,
  "ending_unlock": true,
  "checkin_push": true,
  "affection_change": true,
  "new_script": false
}
```

**字段说明：**
| 字段 | 类型 | 说明 |
|------|------|------|
| update_notify | boolean | 版本更新通知 |
| activity_reminder | boolean | 活动提醒 |
| ending_unlock | boolean | 结局解锁通知 |
| checkin_push | boolean | 签到推送 |
| affection_change | boolean | 好感度变化通知 |
| new_script | boolean | 新剧本上架通知 |

**数据库变更：** `user_settings` 表新增：
- `update_notify` BOOLEAN DEFAULT true
- `activity_reminder` BOOLEAN DEFAULT true
- `checkin_push` BOOLEAN DEFAULT true
（已有：`notification_affection`、`notification_cg_unlock`、`notification_new_script`）

**字段映射：**
| PRD 字段 | DB 字段 |
|----------|---------|
| update_notify | update_notify（新增） |
| activity_reminder | activity_reminder（新增） |
| ending_unlock | notification_cg_unlock（已有） |
| checkin_push | checkin_push（新增） |
| affection_change | notification_affection（已有） |
| new_script | notification_new_script（已有） |

**前端消费方：** `SettingsView.vue` → `NotifySettingPanel`
```typescript
interface NotifySetting {
  update_notify: boolean;
  activity_reminder: boolean;
  ending_unlock: boolean;
  checkin_push: boolean;
  affection_change: boolean;
  new_script: boolean;
}
```

---

### 2.4 `PATCH /api/v1/users/me/notify-setting` — 保存通知设置

**用途：** 设置页面 → 通知推送保存
**认证：** Bearer

**请求 Body：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| update_notify | boolean | 否 | |
| activity_reminder | boolean | 否 | |
| ending_unlock | boolean | 否 | |
| checkin_push | boolean | 否 | |
| affection_change | boolean | 否 | |
| new_script | boolean | 否 | |

**响应 200：** 同 GET 响应结构

---

### 2.5 `GET /api/v1/users/me/devices` — 获取登录设备列表

**用途：** 设置页面 → 隐私安全 → 登录设备管理
**认证：** Bearer

**数据来源：** 新建 `login_devices` 表 或 Redis session 存储

**响应 200：**
```json
{
  "devices": [
    {
      "id": "device-001",
      "device_name": "iPhone 15 Pro",
      "device_type": "ios",
      "browser": "Safari",
      "os": "iOS 18",
      "ip_address": "192.168.1.100",
      "location": "上海",
      "last_active_at": "2026-07-21T18:00:00Z",
      "is_current": true,
      "created_at": "2026-06-01T10:00:00Z"
    },
    {
      "id": "device-002",
      "device_name": "Chrome on macOS",
      "device_type": "web",
      "browser": "Chrome 120",
      "os": "macOS 15",
      "ip_address": "192.168.1.101",
      "location": "上海",
      "last_active_at": "2026-07-21T17:30:00Z",
      "is_current": false,
      "created_at": "2026-07-15T08:00:00Z"
    }
  ],
  "total": 2
}
```

**字段说明：**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 设备唯一标识 |
| device_name | string | 设备显示名称 |
| device_type | string | `ios` / `android` / `web` / `desktop` |
| browser | string | 浏览器名称 |
| os | string | 操作系统 |
| ip_address | string | 最后 IP |
| location | string | 地理位置（可选） |
| last_active_at | string | 最后活跃时间 |
| is_current | boolean | 是否当前设备 |
| created_at | string | 首次登录时间 |

**数据库变更：** 新建 `login_devices` 表
```sql
CREATE TABLE login_devices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  device_name VARCHAR(255),
  device_type VARCHAR(50),
  browser VARCHAR(100),
  os VARCHAR(100),
  ip_address VARCHAR(50),
  location VARCHAR(255),
  refresh_token_hash VARCHAR(255),
  last_active_at TIMESTAMPTZ DEFAULT NOW(),
  is_current BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**前端消费方：** `SettingsView.vue` → `PrivacyPanel` → `DeviceList`
```typescript
interface LoginDevice {
  id: string;
  device_name: string;
  device_type: 'ios' | 'android' | 'web' | 'desktop';
  browser: string;
  os: string;
  ip_address: string;
  location: string | null;
  last_active_at: string;
  is_current: boolean;
  created_at: string;
}

interface DeviceList {
  devices: LoginDevice[];
  total: number;
}
```

---

### 2.6 `POST /api/v1/users/me/devices/{deviceId}/logout` — 下线指定设备

**用途：** 设置页面 → 隐私安全 → 踢出设备
**认证：** Bearer

**路径参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| deviceId | string | 是 | 设备 ID |

**约束：** 不能下线当前设备（is_current=true 的设备）

**响应 200：**
```json
{
  "status": "ok",
  "message": "Device logged out successfully",
  "device_id": "device-002"
}
```

**错误码：**
| code | status | 说明 |
|------|--------|------|
| DEVICE_NOT_FOUND | 404 | 设备不存在 |
| DEVICE_IS_CURRENT | 400 | 不能下线当前设备 |

---

### 2.7 `GET /api/v1/users/me/member-info` — 获取会员详情

**用途：** 设置页面 → 会员管理模块
**认证：** Bearer

**数据来源：** `users` 表 + `Fragment` 表 + 订阅记录

**响应 200：**
```json
{
  "tier": "standard",
  "status": "active",
  "member_since": "2026-06-01T10:00:00Z",
  "expires_at": "2026-08-01T10:00:00Z",
  "auto_renew": true,
  "fragment_balance": 580,
  "benefits": [
    "free_chat_enabled",
    "full_memory_access",
    "exclusive_cg",
    "priority_support"
  ],
  "recent_bills": [
    {
      "id": "bill-001",
      "type": "subscription",
      "description": "Standard 月度订阅",
      "amount": 30,
      "currency": "CNY",
      "created_at": "2026-07-01T00:00:00Z"
    }
  ]
}
```

**字段说明：**
| 字段 | 类型 | 说明 |
|------|------|------|
| tier | string | `free` / `standard` / `premium` |
| status | string | `active` / `inactive` / `cancelled` / `trialing` |
| member_since | string\|null | 成为会员的时间 |
| expires_at | string\|null | 到期时间 |
| auto_renew | boolean | 是否自动续费 |
| fragment_balance | number | 碎片余额 |
| benefits | string[] | 当前等级权益列表 |
| recent_bills | array | 最近账单（最近 5 条） |

**前端消费方：** `SettingsView.vue` → `MemberPanel`
```typescript
interface BillRecord {
  id: string;
  type: 'subscription' | 'purchase' | 'refund';
  description: string;
  amount: number;
  currency: string;
  created_at: string;
}

interface MemberInfo {
  tier: 'free' | 'standard' | 'premium';
  status: 'active' | 'inactive' | 'cancelled' | 'trialing';
  member_since: string | null;
  expires_at: string | null;
  auto_renew: boolean;
  fragment_balance: number;
  benefits: string[];
  recent_bills: BillRecord[];
}
```

---

## 3. 数据库变更汇总

### 3.1 `users` 表扩展
```sql
ALTER TABLE users ADD COLUMN signature VARCHAR(200);
```

### 3.2 `user_settings` 表扩展
```sql
ALTER TABLE user_settings ADD COLUMN typing_speed VARCHAR(20) DEFAULT 'normal';
ALTER TABLE user_settings ADD COLUMN auto_play BOOLEAN DEFAULT false;
ALTER TABLE user_settings ADD COLUMN auto_play_delay_ms INTEGER DEFAULT 3000;
ALTER TABLE user_settings ADD COLUMN animation_enabled BOOLEAN DEFAULT true;
ALTER TABLE user_settings ADD COLUMN animation_quality VARCHAR(20) DEFAULT 'high';
ALTER TABLE user_settings ADD COLUMN update_notify BOOLEAN DEFAULT true;
ALTER TABLE user_settings ADD COLUMN activity_reminder BOOLEAN DEFAULT true;
ALTER TABLE user_settings ADD COLUMN checkin_push BOOLEAN DEFAULT true;
```

### 3.3 新建 `login_devices` 表
```sql
CREATE TABLE login_devices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  device_name VARCHAR(255),
  device_type VARCHAR(50),
  browser VARCHAR(100),
  os VARCHAR(100),
  ip_address VARCHAR(50),
  location VARCHAR(255),
  refresh_token_hash VARCHAR(255),
  last_active_at TIMESTAMPTZ DEFAULT NOW(),
  is_current BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_login_devices_user_id ON login_devices(user_id);
```

---

## 4. 实现优先级

| 优先级 | 接口 | 类型 | 说明 |
|--------|------|------|------|
| P0 | PATCH /users/me（扩展 signature） | 扩展 | 个人资料模块 |
| P0 | GET /users/me/play-setting | 新增 | 播放偏好模块 |
| P0 | PATCH /users/me/play-setting | 新增 | 播放偏好保存 |
| P0 | GET /users/me/notify-setting | 新增 | 通知推送模块 |
| P0 | PATCH /users/me/notify-setting | 新增 | 通知推送保存 |
| P0 | GET /users/me/devices | 新增 | 登录设备管理 |
| P0 | POST /users/me/devices/{id}/logout | 新增 | 下线设备 |
| P0 | GET /users/me/member-info | 新增 | 会员管理 |

---

## 5. 前端页面结构

### 设置页面改造（w07-settings v4.2）

**PC 端：** 左右分栏布局
```
┌─────────────────────────────────────────────┐
│  设置                                        │
├──────────┬──────────────────────────────────┤
│ 个人资料  │  [头像上传]                       │
│ 播放偏好  │  昵称：______                    │
│ 通知推送  │  个性签名：______                │
│ 隐私安全  │  [保存]                          │
│ 会员管理  │                                  │
└──────────┴──────────────────────────────────┘
```

**移动端：** 横向 Tab 切换
```
┌─────────────────────────┐
│ 设置                     │
├─────────────────────────┤
│ [个人资料] [播放偏好] ... │
├─────────────────────────┤
│  [当前 Tab 内容]          │
│                         │
└─────────────────────────┘
```

### 5 个模块对应的 API 调用

| 模块 | 初始化 API | 保存 API |
|------|-----------|---------|
| 个人资料 | GET /users/me | PATCH /users/me |
| 播放偏好 | GET /users/me/play-setting | PATCH /users/me/play-setting |
| 通知推送 | GET /users/me/notify-setting | PATCH /users/me/notify-setting |
| 隐私安全 | GET /users/me/devices | POST /users/me/devices/{id}/logout |
| 会员管理 | GET /users/me/member-info | — (跳转订阅页) |

---

## 6. 变更日志

| 时间 | 变更 |
|------|------|
| 2026-07-21 | 设置页面优化 PRD 接口补充 Contract |
