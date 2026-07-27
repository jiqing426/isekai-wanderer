# CR-012: 订阅系统重构（价格显示修复）

## 变更概述

修复订阅页面价格不显示的紧急bug，按照新的订阅规范文档重构订阅系统。

## 当前问题

**P0 紧急bug**：前端订阅页面不显示价格数据

## 需求分析

### 一、订阅接口规范 [P0] [BE]

**接口1：GET /subscription/plans（套餐配置）**
- 返回4个套餐：free/basic/standard/premium
- 包含月价(priceMonthly)、年价(priceYearly)
- 包含权益清单(featureList)
- 包含折扣率(fragmentDiscountRate)
- 包含推荐标识(recommend)

**接口2：GET /user/subscription（用户实时订阅信息，鉴权）**
- 返回当前套餐(currentPlanId)
- 返回剩余对话次数(remainStamina)
- 返回免费阶段(freeCycleStage: honeymoon/habit/normal/null)
- 返回所有权限布尔字段

**接口3：POST /order/create（创建支付订单）**
- 请求：planId + cycleType(monthly/yearly)
- 返回：orderId + payUrl

### 二、前端交互逻辑 [P0] [FE]

- 页面顶部两个Tab：【按月订阅】、【按年订阅】
- 默认选中按月
- 选中「按月」→ 读取 priceMonthly 展示价格
- 选中「按年」→ 读取 priceYearly 展示价格
- 下单时传递 cycleType: monthly/yearly

## API约定

### 接口1：GET /subscription/plans

**响应示例：**
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

### 接口2：GET /user/subscription

**响应示例：**
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

### 接口3：POST /order/create

**请求：**
```json
{
  "planId": "standard",
  "cycleType": "monthly"
}
```

**响应：**
```json
{
  "orderId": "order_123456",
  "payUrl": "https://payment.example.com/pay?order_id=order_123456",
  "amount": 4.99,
  "currency": "USD"
}
```

## 任务分配

### BE任务（P0：8小时）

1. **实现 GET /subscription/plans**（3小时）
   - 返回4个套餐配置
   - 包含月价、年价、权益清单、折扣率、推荐标识

2. **实现 GET /user/subscription**（3小时）
   - 返回用户当前订阅信息
   - 包含当前套餐、剩余对话次数、免费阶段、权限字段

3. **实现 POST /order/create**（2小时）
   - 创建支付订单
   - 返回订单ID和支付URL

### FE任务（P0：6小时）

1. **修复价格不显示bug**（2小时）
   - 检查API调用是否正确
   - 检查数据绑定是否正确

2. **实现Tab切换**（2小时）
   - 按月订阅/按年订阅Tab
   - 默认选中按月
   - 切换时更新价格显示

3. **渲染套餐卡片**（2小时）
   - 展示4个套餐
   - 展示价格（根据Tab选择月价或年价）
   - 展示权益清单
   - 高亮推荐套餐

## 执行顺序

1. **BE**：立即实现3个订阅接口
2. **FE**：立即修复价格不显示bug，实现Tab切换和套餐卡片渲染
3. **联调**：BE完成后立即联调测试

## 验收标准

- 订阅页面正确显示价格数据
- Tab切换功能正常
- 套餐卡片渲染正确
- 下单流程正常

## 时间估算

- BE：8小时
- FE：6小时
- 联调：2小时
- **总计：16小时（2天）**
