# CR-016 订阅付费体系 + 动态对话额度

## 变更目标
实现 4 档订阅体系（Free/Basic/Standard/Premium）、动态梯度对话额度、Paywall 触发引擎和付费引导 UI。

## 影响范围
- 后端：新增 3 个数据模型 + 3 个服务 + 3 个 API 路由 + 1 个迁移脚本
- 前端：新增 6 个组件/视图 + 1 个 store + 1 个 API 层 + 类型定义
- 配置：subscription_config.json + paywall_copy.json

## 成功标准
- 24 项 AC 验收通过（10 P0 + 4 P1）
- 数据库迁移执行成功
- 前后端联调通过

## 功能清单
- M1: 订阅档位 & 权限模型
- M2: 动态梯度对话额度
- M3: Paywall 触发引擎
- M4: 付费引导组件
- M5: 全局限流计数
- M6: 碎片购买联动
- M7: 订阅管理

## 风险
1. 双 Subscription 模型并存（payment.py vs subscription.py）
2. 额度重置 UTC 00:00 前端时区转换
3. 额度扣减并发安全

## 状态
- 开发完成：24/24 文件
- QA 回归测试：19 PASS / 0 FAIL / 1 INFO
- 当前阶段：QA passed → 待 Security + RELEASE_GATE
