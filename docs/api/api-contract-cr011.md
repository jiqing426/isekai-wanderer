# API Contract — CR-011 订阅付费体系 + 帖子页面重构

> 更新时间：2026-07-23
> 用途：BE 实现 / FE 对接 / 联调对齐
> 基线路径：`/api/v1`

---

## 一、订阅相关 API

### 1.1 `GET /api/v1/users/me/subscription` — 获取订阅信息

**用途：** 获取当前用户订阅等级、额度信息
**认证：** Bearer

**响应 200：**
```json
{
  "tier": "free",
  "quota": {
    "total": 50,
    "used": 12,
    "remaining": 38,
    "period": "honeymoon"
  },
  "expires_at": null,
  "auto_renew": false
}
```

**字段说明：**
| 字段 | 类型 | 说明 |
|------|------|------|
| tier | string | `free` / `basic` / `standard` / `premium` |
| quota.total | number | 总额度 |
| quota.used | number | 已使用额度 |
| quota.remaining | number | 剩余额度 |
| quota.period | string | `honeymoon` / `nurture` / `regular`（仅Free用户） |
| expires_at | string\|null | 订阅到期时间（Free用户为null） |
| auto_renew | boolean | 是否自动续费 |

**前端消费方：** `SubscriptionBadge.vue`, `QuotaDisplay.vue`
```typescript
interface SubscriptionInfo {
  tier: 'free' | 'basic' | 'standard' | 'premium';
  quota: {
    total: number;
    used: number;
    remaining: number;
    period: 'honeymoon' | 'nurture' | 'regular';
  };
  expires_at: string | null;
  auto_renew: boolean;
}
```

---

### 1.2 `GET /api/v1/subscription/plans` — 获取订阅套餐列表

**用途：** 展示可订阅的套餐
**认证：** None（公开）

**响应 200：**
```json
{
  "plans": [
    {
      "tier": "free",
      "price": 0,
      "currency": "USD",
      "features": [
        "基础对话功能",
        "每日50次对话额度"
      ],
      "quota": 50,
      "is_current": true
    },
    {
      "tier": "basic",
      "price": 1.99,
      "currency": "USD",
      "features": [
        "基础对话功能",
        "每日200次对话额度",
        "基础角色解锁"
      ],
      "quota": 200,
      "is_current": false
    },
    {
      "tier": "standard",
      "price": 4.99,
      "currency": "USD",
      "features": [
        "高级对话功能",
        "每日500次对话额度",
        "全部角色解锁",
        "CG画廊"
      ],
      "quota": 500,
      "is_current": false
    },
    {
      "tier": "premium",
      "price": 9.99,
      "currency": "USD",
      "features": [
        "全部功能",
        "无限对话额度",
        "全部角色解锁",
        "CG画廊",
        "专属客服"
      ],
      "quota": -1,
      "is_current": false
    }
  ]
}
```

**字段说明：**
| 字段 | 类型 | 说明 |
|------|------|------|
| tier | string | 套餐等级 |
| price | number | 价格（0表示免费） |
| currency | string | 货币单位 |
| features | string[] | 套餐权益列表 |
| quota | number | 每日额度（-1表示无限） |
| is_current | boolean | 是否当前套餐 |

**前端消费方：** `SubscriptionPlans.vue`
```typescript
interface SubscriptionPlan {
  tier: 'free' | 'basic' | 'standard' | 'premium';
  price: number;
  currency: string;
  features: string[];
  quota: number;
  is_current: boolean;
}

interface SubscriptionPlansResponse {
  plans: SubscriptionPlan[];
}
```

---

### 1.3 `POST /api/v1/subscription/subscribe` — 订阅套餐

**用途：** 订阅或升级套餐
**认证：** Bearer

**请求 Body：**
```json
{
  "tier": "standard",
  "payment_method": "stripe"
}
```

**响应 200：**
```json
{
  "status": "success",
  "subscription_id": "sub_123456",
  "tier": "standard",
  "expires_at": "2026-08-23T19:00:00Z",
  "quota_updated": true
}
```

**错误码：**
| code | status | 说明 |
|------|--------|------|
| PAYMENT_FAILED | 402 | 支付失败 |
| SUBSCRIPTION_ALREADY_ACTIVE | 409 | 已有活跃订阅 |
| INVALID_TIER | 400 | 无效的套餐等级 |

**前端消费方：** `SubscribeButton.vue`
```typescript
interface SubscribeRequest {
  tier: 'basic' | 'standard' | 'premium';
  payment_method: string;
}

interface SubscribeResponse {
  status: 'success' | 'pending';
  subscription_id: string;
  tier: string;
  expires_at: string;
  quota_updated: boolean;
}
```

---

### 1.4 `POST /api/v1/fragment/exchange` — 购买额外对话

**用途：** 使用碎片购买额外对话额度
**认证：** Bearer

**请求 Body：**
```json
{
  "goods_id": "dialogue_quota_10",
  "quantity": 1
}
```

**响应 200：**
```json
{
  "status": "success",
  "new_quota": 48,
  "fragments_spent": 50,
  "quota_added": 10
}
```

**错误码：**
| code | status | 说明 |
|------|--------|------|
| INSUFFICIENT_FRAGMENTS | 402 | 碎片不足 |
| GOODS_NOT_FOUND | 404 | 商品不存在 |

**前端消费方：** `BuyQuotaButton.vue`
```typescript
interface ExchangeRequest {
  goods_id: string;
  quantity: number;
}

interface ExchangeResponse {
  status: 'success';
  new_quota: number;
  fragments_spent: number;
  quota_added: number;
}
```

---

### 1.5 `GET /api/v1/paywall/check` — 检查付费触发

**用途：** 检查是否应该显示Paywall
**认证：** Bearer

**请求参数（Query）：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| scene | string | 是 | 触发场景（T1-T8） |

**响应 200：**
```json
{
  "should_show": true,
  "type": "fullscreen",
  "message": "您的对话额度已用完，升级套餐获得无限额度",
  "scene": "T3",
  "cooldown_remaining": 0
}
```

**字段说明：**
| 字段 | 类型 | 说明 |
|------|------|------|
| should_show | boolean | 是否显示Paywall |
| type | string | `fullscreen` / `banner` / `toast` |
| message | string | 提示消息 |
| scene | string | 触发场景 |
| cooldown_remaining | number | 冷却时间（秒） |

**触发场景说明：**
| 场景 | 触发条件 | 类型 |
|------|---------|------|
| T1 | 额度用完时尝试对话 | fullscreen |
| T2 | 访问高级功能 | fullscreen |
| T3 | 对话次数达到阈值 | banner |
| T4 | 尝试解锁高级角色 | fullscreen |
| T5 | 访问CG画廊 | toast |
| T6 | 连续3天未登录 | banner |
| T7 | 完成特定成就 | toast |
| T8 | 碎片不足 | toast |

**前端消费方：** `PaywallManager.vue`
```typescript
interface PaywallCheckResponse {
  should_show: boolean;
  type: 'fullscreen' | 'banner' | 'toast';
  message: string;
  scene: string;
  cooldown_remaining: number;
}
```

---

## 二、帖子相关 API

### 2.1 `GET /api/v1/community/posts` — 获取帖子列表

**用途：** 获取帖子列表（支持Tab分类和搜索）
**认证：** None（公开，但登录用户返回更多数据）

**请求参数（Query）：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| tab | string | 否 | `recommend` / `latest` / `hot` / `mine`，默认 `recommend` |
| page | int | 否 | 页码，默认 1 |
| page_size | int | 否 | 每页数量，默认 20 |
| search | string | 否 | 搜索关键词 |

**响应 200：**
```json
{
  "posts": [
    {
      "id": "post-001",
      "title": "我的第一次异世界冒险",
      "content": "今天第一次玩了异世界之旅，感觉很棒...",
      "images": [
        "https://cdn.example.com/images/post1.jpg"
      ],
      "author": {
        "id": "user-001",
        "name": "冒险者",
        "avatar": "https://cdn.example.com/avatars/user1.png"
      },
      "stats": {
        "likes": 42,
        "comments": 8,
        "views": 156
      },
      "is_liked": true,
      "created_at": "2026-07-23T10:00:00Z"
    }
  ],
  "total": 156,
  "has_more": true
}
```

**字段说明：**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 帖子ID |
| title | string | 标题 |
| content | string | 内容 |
| images | string[] | 图片URL列表 |
| author | object | 作者信息 |
| stats | object | 统计数据 |
| is_liked | boolean | 当前用户是否点赞（未登录为false） |
| created_at | string | 创建时间 |

**前端消费方：** `CommunityView.vue`, `PostCard.vue`
```typescript
interface Post {
  id: string;
  title: string;
  content: string;
  images: string[];
  author: {
    id: string;
    name: string;
    avatar: string;
  };
  stats: {
    likes: number;
    comments: number;
    views: number;
  };
  is_liked: boolean;
  created_at: string;
}

interface PostsResponse {
  posts: Post[];
  total: number;
  has_more: boolean;
}
```

---

### 2.2 `POST /api/v1/community/posts/{id}/like` — 点赞帖子

**用途：** 点赞帖子
**认证：** Bearer（游客不可用）

**路径参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 帖子ID |

**响应 200：**
```json
{
  "status": "success",
  "likes_count": 43
}
```

**错误码：**
| code | status | 说明 |
|------|--------|------|
| POST_NOT_FOUND | 404 | 帖子不存在 |
| ALREADY_LIKED | 409 | 已点赞 |
| AUTH_REQUIRED | 401 | 需要登录 |

**前端消费方：** `LikeButton.vue`
```typescript
interface LikeResponse {
  status: 'success';
  likes_count: number;
}
```

---

### 2.3 `DELETE /api/v1/community/posts/{id}/like` — 取消点赞

**用途：** 取消点赞
**认证：** Bearer（游客不可用）

**路径参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 帖子ID |

**响应 200：**
```json
{
  "status": "success",
  "likes_count": 42
}
```

**错误码：**
| code | status | 说明 |
|------|--------|------|
| POST_NOT_FOUND | 404 | 帖子不存在 |
| NOT_LIKED | 409 | 未点赞 |
| AUTH_REQUIRED | 401 | 需要登录 |

---

### 2.4 `DELETE /api/v1/community/posts/{id}` — 删除帖子

**用途：** 删除帖子（仅作者可删除）
**认证：** Bearer

**路径参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 帖子ID |

**响应 200：**
```json
{
  "status": "success",
  "message": "帖子已删除"
}
```

**错误码：**
| code | status | 说明 |
|------|--------|------|
| POST_NOT_FOUND | 404 | 帖子不存在 |
| PERMISSION_DENIED | 403 | 无权限删除（非作者） |
| AUTH_REQUIRED | 401 | 需要登录 |

**前端消费方：** `DeletePostButton.vue`
```typescript
interface DeletePostResponse {
  status: 'success';
  message: string;
}
```

---

### 2.5 `GET /api/v1/community/posts/search` — 搜索帖子

**用途：** 搜索帖子
**认证：** None（公开）

**请求参数（Query）：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 是 | 搜索关键词 |
| page | int | 否 | 页码，默认 1 |
| page_size | int | 否 | 每页数量，默认 20 |

**响应 200：**
```json
{
  "posts": [
    {
      "id": "post-001",
      "title": "我的第一次异世界冒险",
      "content": "...",
      "author": {...},
      "stats": {...},
      "is_liked": false,
      "created_at": "2026-07-23T10:00:00Z"
    }
  ],
  "total": 12,
  "suggestions": [
    "异世界",
    "冒险",
    "攻略"
  ]
}
```

**字段说明：**
| 字段 | 类型 | 说明 |
|------|------|------|
| posts | array | 搜索结果列表 |
| total | number | 总结果数 |
| suggestions | string[] | 搜索建议 |

**前端消费方：** `SearchBar.vue`
```typescript
interface SearchResponse {
  posts: Post[];
  total: number;
  suggestions: string[];
}
```

---

## 三、实现优先级

| 优先级 | 接口 | 负责人 | 说明 |
|--------|------|--------|------|
| P0 | GET /users/me/subscription | BE | 获取订阅信息 |
| P0 | GET /subscription/plans | BE | 获取套餐列表 |
| P0 | POST /subscription/subscribe | BE | 订阅套餐 |
| P0 | POST /fragment/exchange | BE | 购买额外对话 |
| P0 | GET /paywall/check | BE | 检查付费触发 |
| P1 | GET /community/posts | BE | 获取帖子列表 |
| P1 | POST /community/posts/{id}/like | BE | 点赞帖子 |
| P1 | DELETE /community/posts/{id}/like | BE | 取消点赞 |
| P1 | DELETE /community/posts/{id} | BE | 删除帖子 |
| P1 | GET /community/posts/search | BE | 搜索帖子 |

---

## 四、数据库变更

### 4.1 订阅相关表

```sql
-- 订阅表
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  tier VARCHAR(20) NOT NULL DEFAULT 'free',
  status VARCHAR(20) NOT NULL DEFAULT 'active',
  quota_total INTEGER NOT NULL DEFAULT 50,
  quota_used INTEGER NOT NULL DEFAULT 0,
  quota_period VARCHAR(20) DEFAULT 'honeymoon',
  expires_at TIMESTAMPTZ,
  auto_renew BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 付费触发计数表
CREATE TABLE paywall_triggers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  scene VARCHAR(10) NOT NULL,
  trigger_count INTEGER NOT NULL DEFAULT 0,
  last_triggered_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 4.2 帖子相关表

```sql
-- 帖子表
CREATE TABLE community_posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  content TEXT NOT NULL,
  images TEXT, -- JSON array
  likes_count INTEGER DEFAULT 0,
  comments_count INTEGER DEFAULT 0,
  views_count INTEGER DEFAULT 0,
  is_deleted BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 点赞表
CREATE TABLE post_likes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  post_id UUID NOT NULL REFERENCES community_posts(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, post_id)
);
```

---

## 五、前端组件清单

### P0 组件
1. **PaywallManager.vue** - Paywall管理器
   - 全屏弹窗
   - 横幅
   - Toast
   - 触发逻辑

2. **SubscriptionBadge.vue** - 订阅等级徽章
   - 显示当前等级
   - 额度进度条

3. **SubscriptionPlans.vue** - 订阅套餐展示
   - 4档套餐卡片
   - 价格展示
   - 权益对比
   - 订阅按钮

4. **QuotaDisplay.vue** - 额度显示
   - 剩余额度
   - 刷新按钮
   - 购买额外额度

### P1 组件
1. **CommunityView.vue** - 帖子列表页
   - Tab切换
   - 无限滚动
   - 搜索框

2. **PostCard.vue** - 帖子卡片
   - 图片展示
   - 点赞/评论数
   - 作者信息

3. **SearchBar.vue** - 搜索组件
   - 搜索输入框
   - 搜索按钮
   - 搜索建议

4. **LikeButton.vue** - 点赞按钮
   - 点赞/取消点赞
   - 点赞数显示

5. **DeletePostButton.vue** - 删除按钮
   - 删除确认
   - 权限检查

---

## 六、变更日志

| 时间 | 变更 |
|------|------|
| 2026-07-23 | 初始版本，覆盖订阅付费和帖子页面API |
