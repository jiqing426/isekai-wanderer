# API Contract 补充 — 碎片中心（CR-008 w10-fragment-mall）

> 时间：2026-07-21
> 用途：BE 新增接口 + FE 对接
> 基线路径：`/api/v1`
> 关联文档：`docs/api/api-contract-post-refactor.md`、`docs/api/api-contract-settings-v42.md`

---

## 0. 重复分析结论

### 与 w07 个人中心对比

| 功能 | w07 个人中心 | w10 碎片中心 | 冲突？ |
|------|-------------|-------------|--------|
| 碎片余额 | ✅ GET /users/me/asset（概览） | ✅ 复用同一接口（详情页顶部也显示） | ❌ 无冲突，互补 |
| 签到 | ✅ GET /sign/info（签到卡片） | ❌ 不渲染，仅跳转引导 | ❌ 无冲突 |
| 每日任务 | ❌ w07 不含任务模块 | ❌ 不渲染，仅跳转引导 | ❌ 无冲突 |
| 碎片商城 | ❌ 无 | ✅ 商品兑换 | ❌ 无冲突 |
| 收支流水 | ❌ 无 | ✅ 详细流水 | ❌ 无冲突 |

**结论：无功能重复，w07 做概览，w10 做专项管理，互补关系。**

### 与已有接口对比

| PRD 接口 | 已有接口 | 状态 |
|----------|---------|------|
| GET /api/user/asset | GET /api/v1/users/me/asset | ✅ 已有，直接复用 |
| GET /api/fragment/record/list | GET /api/v1/shards/transactions | ⚠️ 已有，需路径别名 |
| GET /api/user/daily-task | GET /api/v1/daily/tasks | ✅ 已有，直接复用 |
| POST /api/user/daily-task/claim | POST /api/v1/daily/tasks/{taskId}/claim | ✅ 已有，直接复用 |
| GET /api/fragment/shop/goods-list | 无 | 🆕 需新增 |
| POST /api/fragment/exchange | 无 | 🆕 需新增 |

**结论：6 个接口中 4 个已有可复用，仅需新增 2 个（商城商品列表 + 兑换道具）。**

---

## 1. 路径映射

| PRD 路径 | 实际路径 | 说明 |
|----------|---------|------|
| /api/user/asset | /api/v1/users/me/asset | 已有，复用 |
| /api/fragment/shop/goods-list | /api/v1/fragment/shop/goods | 新增 |
| /api/fragment/record/list | /api/v1/fragment/transactions | 新增（封装 shards/transactions） |
| /api/fragment/exchange | /api/v1/fragment/exchange | 新增 |
| /api/user/daily-task | /api/v1/daily/tasks | 已有，复用 |
| /api/user/daily-task/claim | /api/v1/daily/tasks/{taskId}/claim | 已有，复用 |

---

## 2. 复用接口确认（无需 BE 开发）

### 2.1 `GET /api/v1/users/me/asset` — 碎片余额

**已实现**，响应结构：
```json
{
  "balance": 580,
  "total_earned": 1200,
  "total_spent": 620
}
```

### 2.2 `GET /api/v1/daily/tasks` — 当日任务列表

**已实现**，响应结构：
```json
{
  "tasks": [
    {
      "id": "task-001",
      "title": "完成一次对话",
      "description": "与任意角色完成一次对话",
      "reward_type": "fragment",
      "reward_amount": 20,
      "progress": 1,
      "target": 1,
      "status": "claimed",
      "claimed_at": "2026-07-21T10:00:00Z"
    }
  ],
  "reset_at": "2026-07-22T00:00:00Z"
}
```

### 2.3 `POST /api/v1/daily/tasks/{taskId}/claim` — 领取任务奖励

**已实现**，响应结构：
```json
{
  "task_id": "task-001",
  "claimed": true,
  "reward": {
    "type": "fragment",
    "amount": 20
  },
  "new_balance": 600
}
```

---

## 3. 新增接口

### 3.1 `GET /api/v1/fragment/shop/goods` — 碎片商城商品列表

**用途：** 碎片中心 → 商城 Tab → 商品兑换
**认证：** Bearer

**请求参数（Query）：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| category | string | 否 | 分类筛选：`cg` / `voice` / `skin` / `item` |
| page | int | 否 | 默认 1 |
| page_size | int | 否 | 默认 20 |

**响应 200：**
```json
{
  "goods": [
    {
      "id": "goods-001",
      "name": "樱花 CG 解锁",
      "description": "解锁樱花专属 CG「月下誓言」",
      "category": "cg",
      "icon_url": "/assets/shop/cg_sakura.png",
      "price": 100,
      "stock": -1,
      "limit_per_user": 1,
      "owned": false,
      "is_available": true
    },
    {
      "id": "goods-002",
      "name": "角色语音包 — 樱",
      "description": "解锁樱的全部语音",
      "category": "voice",
      "icon_url": "/assets/shop/voice_sakura.png",
      "price": 200,
      "stock": -1,
      "limit_per_user": 1,
      "owned": true,
      "is_available": false
    },
    {
      "id": "goods-003",
      "name": "碎片补给包",
      "description": "获得 50 碎片",
      "category": "item",
      "icon_url": "/assets/shop/fragment_pack.png",
      "price": 0,
      "stock": 1,
      "limit_per_user": 1,
      "owned": false,
      "is_available": true
    }
  ],
  "total": 3,
  "user_balance": 580
}
```

**字段说明：**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 商品 ID |
| name | string | 商品名称 |
| description | string | 商品描述 |
| category | string | `cg` / `voice` / `skin` / `item` |
| icon_url | string | 商品图标 |
| price | number | 碎片价格（0 = 免费） |
| stock | number | 库存（-1 = 无限） |
| limit_per_user | number | 每人限购（0 = 不限） |
| owned | boolean | 用户是否已拥有 |
| is_available | boolean | 是否可购买（库存够 + 未限购） |

**数据来源：** 新建 `shop_goods` 表 + 查询用户持有状态

**数据库变更：**
```sql
CREATE TABLE shop_goods (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  category VARCHAR(50) NOT NULL,
  icon_url TEXT,
  price INTEGER NOT NULL DEFAULT 0,
  stock INTEGER NOT NULL DEFAULT -1,
  limit_per_user INTEGER NOT NULL DEFAULT 1,
  item_type VARCHAR(50),
  item_id VARCHAR(255),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE user_goods (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  goods_id UUID NOT NULL REFERENCES shop_goods(id),
  quantity INTEGER NOT NULL DEFAULT 1,
  acquired_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, goods_id)
);
CREATE INDEX idx_user_goods_user ON user_goods(user_id);
```

**前端消费方：** `FragmentMallView.vue` → `ShopTab`
```typescript
interface ShopGood {
  id: string;
  name: string;
  description: string;
  category: 'cg' | 'voice' | 'skin' | 'item';
  icon_url: string;
  price: number;
  stock: number;
  limit_per_user: number;
  owned: boolean;
  is_available: boolean;
}

interface ShopGoodsList {
  goods: ShopGood[];
  total: number;
  user_balance: number;
}
```

---

### 3.2 `POST /api/v1/fragment/exchange` — 兑换道具

**用途：** 碎片中心 → 商城 → 兑换商品
**认证：** Bearer

**请求 Body：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| goods_id | string | 是 | 商品 ID |
| quantity | number | 否 | 数量，默认 1 |

**请求示例：**
```json
{
  "goods_id": "goods-001",
  "quantity": 1
}
```

**响应 200：**
```json
{
  "status": "ok",
  "goods_id": "goods-001",
  "goods_name": "樱花 CG 解锁",
  "price": 100,
  "quantity": 1,
  "new_balance": 480,
  "message": "兑换成功"
}
```

**错误码：**
| code | status | 说明 |
|------|--------|------|
| GOODS_NOT_FOUND | 404 | 商品不存在 |
| INSUFFICIENT_BALANCE | 402 | 碎片余额不足 |
| GOODS_OUT_OF_STOCK | 409 | 库存不足 |
| GOODS_LIMIT_REACHED | 409 | 已达限购上限 |
| GOODS_NOT_AVAILABLE | 400 | 商品不可购买 |

**业务逻辑：**
1. 检查商品是否存在且 is_active=true
2. 检查库存（stock != -1 时检查 stock > 0）
3. 检查限购（用户已购数量 < limit_per_user）
4. 检查余额（balance >= price * quantity）
5. 扣减碎片（Fragment 表 balance 减少）
6. 记录交易（FragmentTransaction 表，amount 为负数，reason = "shop_exchange:{goods_id}"）
7. 记录购买（user_goods 表，quantity 增加）
8. 扣减库存（shop_goods 表 stock - 1，stock != -1 时）
9. 发放道具（根据 item_type 发放 CG/voice/skin/item）

**前端消费方：** `FragmentMallView.vue` → `ExchangeButton`
```typescript
interface ExchangeRequest {
  goods_id: string;
  quantity?: number;
}

interface ExchangeResponse {
  status: 'ok';
  goods_id: string;
  goods_name: string;
  price: number;
  quantity: number;
  new_balance: number;
  message: string;
}
```

---

### 3.3 `GET /api/v1/fragment/transactions` — 碎片收支流水

**用途：** 碎片中心 → 收支明细 Tab
**认证：** Bearer

**说明：** 封装已有 `/shards/transactions`，增加分类字段

**请求参数（Query）：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 否 | 筛选：`income` / `expense` / 全部 |
| page | int | 否 | 默认 1 |
| page_size | int | 否 | 默认 20 |

**响应 200：**
```json
{
  "transactions": [
    {
      "id": "tx-001",
      "amount": 20,
      "type": "income",
      "reason": "daily_checkin",
      "description": "每日签到奖励",
      "created_at": "2026-07-21T10:00:00Z"
    },
    {
      "id": "tx-002",
      "amount": -100,
      "type": "expense",
      "reason": "shop_exchange:goods-001",
      "description": "兑换：樱花 CG 解锁",
      "created_at": "2026-07-20T14:30:00Z"
    }
  ],
  "total": 56,
  "page": 1,
  "page_size": 20
}
```

**字段说明：**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 交易 ID |
| amount | number | 金额（正=收入，负=支出） |
| type | string | `income` / `expense` |
| reason | string | 原始原因码 |
| description | string | 人类可读描述 |
| created_at | string | 交易时间 |

**reason → description 映射表：**
| reason | description |
|--------|-------------|
| daily_checkin | 每日签到奖励 |
| achievement_claim:* | 成就奖励：{name} |
| shop_exchange:* | 兑换：{goods_name} |
| fragment_purchase | 碎片购买 |

**前端消费方：** `FragmentMallView.vue` → `TransactionTab`
```typescript
interface FragmentTransaction {
  id: string;
  amount: number;
  type: 'income' | 'expense';
  reason: string;
  description: string;
  created_at: string;
}

interface TransactionList {
  transactions: FragmentTransaction[];
  total: number;
  page: number;
  page_size: number;
}
```

---

## 4. 数据库变更汇总

### 4.1 新建 `shop_goods` 表
```sql
CREATE TABLE shop_goods (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  category VARCHAR(50) NOT NULL,
  icon_url TEXT,
  price INTEGER NOT NULL DEFAULT 0,
  stock INTEGER NOT NULL DEFAULT -1,
  limit_per_user INTEGER NOT NULL DEFAULT 1,
  item_type VARCHAR(50),
  item_id VARCHAR(255),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 4.2 新建 `user_goods` 表
```sql
CREATE TABLE user_goods (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  goods_id UUID NOT NULL REFERENCES shop_goods(id),
  quantity INTEGER NOT NULL DEFAULT 1,
  acquired_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, goods_id)
);
```

### 4.3 种子数据（示例商品）
```sql
INSERT INTO shop_goods (name, description, category, icon_url, price, stock, limit_per_user, item_type, item_id) VALUES
('樱花 CG 解锁', '解锁樱花专属 CG「月下誓言」', 'cg', '/assets/shop/cg_sakura.png', 100, -1, 1, 'cg', 'cg-004'),
('角色语音包 — 樱', '解锁樱的全部语音', 'voice', '/assets/shop/voice_sakura.png', 200, -1, 1, 'voice_pack', 'char-001'),
('碎片补给包', '获得 50 碎片', 'item', '/assets/shop/fragment_pack.png', 0, 1, 1, 'fragment', '50');
```

---

## 5. 实现优先级

| 优先级 | 接口 | 类型 | 说明 |
|--------|------|------|------|
| P0 | GET /fragment/shop/goods | 新增 | 商城商品列表 |
| P0 | POST /fragment/exchange | 新增 | 兑换道具 |
| P0 | GET /fragment/transactions | 新增 | 收支流水（封装 shards/transactions） |

**复用接口（无需 BE 开发）：**
- GET /users/me/asset — 碎片余额
- GET /daily/tasks — 当日任务列表
- POST /daily/tasks/{taskId}/claim — 领取任务奖励

---

## 6. 前端页面结构

### 碎片中心页面

**PC 端：** 左右分栏
```
┌─────────────────────────────────────────────┐
│  碎片中心              余额：580 💎           │
├──────────┬──────────────────────────────────┤
│ 碎片商城  │  [商品卡片列表]                   │
│ 收支明细  │                                  │
│ 获取碎片  │                                  │
└──────────┴──────────────────────────────────┘
```

**移动端：** 顶部 Tab 切换
```
┌─────────────────────────┐
│ 碎片中心    余额：580 💎  │
├─────────────────────────┤
│ [碎片商城] [收支明细] [获取碎片] │
├─────────────────────────┤
│  [当前 Tab 内容]          │
└─────────────────────────┘
```

### 3 个 Tab 对应的 API 调用

| Tab | API |
|-----|-----|
| 碎片商城 | GET /fragment/shop/goods + POST /fragment/exchange |
| 收支明细 | GET /fragment/transactions |
| 获取碎片 | 纯前端引导页（跳转签到/任务页） |

---

## 7. 变更日志

| 时间 | 变更 |
|------|------|
| 2026-07-21 | 碎片中心 PRD 接口分析 + Contract 补充 |
