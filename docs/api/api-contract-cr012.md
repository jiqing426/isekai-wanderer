# CR-012 订阅系统重构 API Contract

## 概述

修复订阅页面价格不显示的紧急bug，按照新的订阅规范文档重构订阅系统。

## 接口定义

### 1. GET /api/v1/subscription/plans

**用途**：获取所有订阅套餐配置

**认证**：无需认证

**响应示例**：
```json
{
  "plans": [
    {
      "planId": "free",
      "name": "免费版",
      "priceMonthly": 0,
      "priceYearly": 0,
      "featureList": [
        "基础对话功能",
        "每日50次对话额度"
      ],
      "fragmentDiscountRate": 0,
      "recommend": false
    },
    {
      "planId": "basic",
      "name": "基础版",
      "priceMonthly": 1.99,
      "priceYearly": 19.99,
      "featureList": [
        "基础对话功能",
        "每日200次对话额度",
        "基础角色解锁"
      ],
      "fragmentDiscountRate": 0.1,
      "recommend": false
    },
    {
      "planId": "standard",
      "name": "标准版",
      "priceMonthly": 4.99,
      "priceYearly": 49.99,
      "featureList": [
        "高级对话功能",
        "每日500次对话额度",
        "全部角色解锁",
        "CG画廊"
      ],
      "fragmentDiscountRate": 0.2,
      "recommend": true
    },
    {
      "planId": "premium",
      "name": "高级版",
      "priceMonthly": 9.99,
      "priceYearly": 99.99,
      "featureList": [
        "全部功能",
        "无限对话额度",
        "全部角色解锁",
        "CG画廊",
        "专属客服"
      ],
      "fragmentDiscountRate": 0.3,
      "recommend": false
    }
  ]
}
```

**字段说明**：
- `planId`: 套餐ID (free/basic/standard/premium)
- `name`: 套餐名称
- `priceMonthly`: 月价格（USD）
- `priceYearly`: 年价格（USD）
- `featureList`: 权益清单
- `fragmentDiscountRate`: 碎片折扣率（0-1）
- `recommend`: 是否推荐套餐

---

### 2. GET /api/v1/user/subscription

**用途**：获取当前用户订阅信息

**认证**：需要 Bearer Token

**响应示例**：
```json
{
  "currentPlanId": "standard",
  "remainStamina": 450,
  "freeCycleStage": null,
  "permissions": {
    "canAccessAllCharacters": true,
    "canAccessCGGallery": true,
    "canUseAdvancedFeatures": true,
    "canUseFreeChat": true,
    "canUseMemorySystem": true
  },
  "expiresAt": "2026-08-23T19:00:00Z",
  "autoRenew": true
}
```

**字段说明**：
- `currentPlanId`: 当前订阅套餐ID
- `remainStamina`: 剩余对话次数
- `freeCycleStage`: 免费阶段 (honeymoon/habit/normal/null)
- `permissions`: 权限布尔字段集合
- `expiresAt`: 订阅过期时间
- `autoRenew`: 是否自动续费

---

### 3. POST /api/v1/order/create

**用途**：创建订阅订单

**认证**：需要 Bearer Token

**请求体**：
```json
{
  "planId": "standard",
  "cycleType": "monthly"
}
```

**请求参数**：
- `planId`: 套餐ID (basic/standard/premium)
- `cycleType`: 订阅周期 (monthly/yearly)

**响应示例**：
```json
{
  "orderId": "order_123456",
  "payUrl": "https://payment.example.com/pay?order_id=order_123456",
  "amount": 4.99,
  "currency": "USD"
}
```

**字段说明**：
- `orderId`: 订单ID
- `payUrl`: 支付页面URL
- `amount`: 支付金额
- `currency`: 货币类型

---

## 前端交互逻辑

### Tab 切换
- 页面顶部两个Tab：【按月订阅】、【按年订阅】
- 默认选中"按月订阅"
- 选中"按月" → 读取 `priceMonthly` 展示价格
- 选中"按年" → 读取 `priceYearly` 展示价格

### 下单流程
- 用户点击"订阅"按钮
- 传递 `planId` 和 `cycleType` (monthly/yearly)
- 调用 POST /order/create
- 跳转到 `payUrl` 完成支付

## 数据库变更

无需新增表，使用现有的 `subscriptions` 表。

## 错误码

| 错误码 | HTTP状态码 | 说明 |
|--------|-----------|------|
| PLAN_NOT_FOUND | 404 | 套餐不存在 |
| INVALID_CYCLE_TYPE | 400 | 无效的订阅周期 |
| ORDER_CREATE_FAILED | 500 | 订单创建失败 |

## 前端类型定义

```typescript
interface SubscriptionPlan {
  planId: string;
  name: string;
  priceMonthly: number;
  priceYearly: number;
  featureList: string[];
  fragmentDiscountRate: number;
  recommend: boolean;
}

interface UserSubscription {
  currentPlanId: string;
  remainStamina: number;
  freeCycleStage: 'honeymoon' | 'habit' | 'normal' | null;
  permissions: {
    canAccessAllCharacters: boolean;
    canAccessCGGallery: boolean;
    canUseAdvancedFeatures: boolean;
    canUseFreeChat: boolean;
    canUseMemorySystem: boolean;
  };
  expiresAt: string;
  autoRenew: boolean;
}

interface CreateOrderRequest {
  planId: string;
  cycleType: 'monthly' | 'yearly';
}

interface CreateOrderResponse {
  orderId: string;
  payUrl: string;
  amount: number;
  currency: string;
}
```
