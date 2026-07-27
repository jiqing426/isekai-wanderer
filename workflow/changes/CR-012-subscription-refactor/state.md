# CR-012 订阅系统重构 - 状态追踪

## 当前状态
**状态**: 已完成  
**阶段**: DEVELOPMENT  
**负责人**: BE  
**更新时间**: 2026-07-23 20:15

## 任务清单

### P0 紧急任务（已完成）

#### 1. GET /subscription/plans ✅
- [x] 返回4个套餐配置（free/basic/standard/premium）
- [x] 包含月价(priceMonthly)和年价(priceYearly)
- [x] 包含权益清单(featureList)
- [x] 包含碎片折扣率(fragmentDiscountRate)
- [x] 包含推荐标识(recommend)

#### 2. GET /user/subscription ✅
- [x] 返回用户当前订阅信息
- [x] 包含当前套餐(currentPlanId)
- [x] 包含剩余对话次数(remainStamina)
- [x] 包含免费阶段(freeCycleStage)
- [x] 包含所有权限布尔字段(permissions)
- [x] 包含过期时间(expiresAt)
- [x] 包含自动续费状态(autoRenew)

#### 3. POST /order/create ✅
- [x] 创建支付订单
- [x] 接收 planId 和 cycleType(monthly/yearly)
- [x] 返回 orderId、payUrl、amount、currency
- [x] 支持错误处理（PLAN_NOT_FOUND、INVALID_CYCLE_TYPE）

## 实现接口

### 新增/修改接口
1. `GET /api/v1/subscription/plans` - 获取订阅计划列表（已重构）
2. `GET /api/v1/user/subscription` - 获取用户订阅信息（已更新格式）
3. `POST /api/v1/order/create` - 创建订阅订单（新增）

### 修改文件
- `backend/app/api/v1/subscription.py` - 重构 plans 接口，返回新格式
- `backend/app/api/v1/user.py` - 更新 subscription 接口返回格式
- `backend/app/api/v1/user_subscription.py` - 新增订单创建接口
- `backend/app/api/v1/__init__.py` - 注册新路由

## 测试结果
- ✅ GET /subscription/plans - 200 OK，返回4个套餐，所有必需字段存在
- ✅ GET /user/subscription - 200 OK，返回用户订阅信息，所有必需字段存在
- ✅ POST /order/create - 200 OK，创建订单成功，返回订单信息
- ✅ 错误处理 - 404/400 正常返回

## 下一步
等待前端对接
