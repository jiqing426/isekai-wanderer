# CR-016 开发进度跟踪

> 最后更新：2026-07-25 06:30 UTC

## 一、文件完成清单

### 后端（/root/isekai-wanderer/backend/）

| 文件 | 状态 | 行数 | 最后修改 |
|------|------|------|----------|
| app/models/subscription.py | ✅ 已完成 | 55 | 07-25 04:55 |
| app/models/dialogue_quota.py | ✅ 已完成 | 44 | 07-25 04:55 |
| app/models/paywall_event.py | ✅ 已完成 | 46 | 07-25 04:55 |
| app/schemas/subscription.py | ✅ 已完成 | 48 | 07-25 04:56 |
| app/schemas/dialogue_quota.py | ✅ 已完成 | 44 | 07-25 04:56 |
| app/schemas/paywall_event.py | ✅ 已完成 | 44 | 07-25 04:56 |
| app/services/subscription_service.py | ✅ 已完成 | 262 | 07-25 05:21 |
| app/services/quota_service.py | ✅ 已完成 | 271 | 07-25 04:57 |
| app/services/paywall_service.py | ✅ 已完成 | 309 | 07-25 05:21 |
| app/services/affection_service.py | ✅ 已完成 | 186 | 07-25 05:22 |
| app/api/v1/cr016_subscription.py | ✅ 已完成 | 293 | 07-25 05:24 |
| app/api/v1/cr016_dialogue.py | ✅ 已完成 | 96 | 07-25 05:24 |
| app/api/v1/cr016_paywall.py | ✅ 已完成 | 166 | 07-25 05:24 |
| migrations/001_cr016_subscription_paywall.py | ✅ 已完成 | 105 | 07-25 |

### 前端（/root/isekai-wanderer/frontend/src/）

| 文件 | 状态 | 行数 | 最后修改 |
|------|------|------|----------|
| types/subscription.ts | ✅ 已完成 | 130 | 07-25 04:55 |
| stores/subscription.ts | ✅ 已完成 | 87 | 07-25 04:59 |
| api/subscription.ts | ✅ 已完成 | 102 | 07-25 05:21 |
| components/paywall/QuotaExhaustedModal.vue | ✅ 已完成 | 531 | 07-25 05:27 |
| components/paywall/PaywallBanner.vue | ✅ 已完成 | 129 | 07-25 04:58 |
| components/paywall/PaywallToast.vue | ✅ 已完成 | 60 | 07-25 04:58 |
| components/paywall/PaywallManager.vue | ✅ 已完成 | 181 | 07-25 04:59 |
| components/paywall/TierComparison.vue | ✅ 已完成 | 276 | 07-25 04:58 |
| views/SubscriptionView.vue | ✅ 已完成 | 747 | 07-25 05:23 |
| views/GameView.vue（已修改） | ✅ 已完成 | 973 | 07-25 05:54 |

### 配置（/root/isekai-wanderer/docs/CR-016/）

| 文件 | 状态 | 最后修改 |
|------|------|----------|
| subscription_config.json | ✅ 已完成 | 07-25 04:55 |
| paywall_copy.json | ✅ 已完成 | 07-25 04:55 |
| technical-design.md | ✅ 已完成 | 07-25 05:19 |
| README.md | ✅ 已完成 | 07-25 04:56 |

**总计：24/24 文件全部完成，共 5,080 行代码**

---

## 二、开发时间线

| 时间 (UTC) | 里程碑 |
|------------|--------|
| 07-25 04:55 | 数据模型 + Schema + 类型定义 + 配置文件完成 |
| 07-25 04:56~04:59 | 前端 Paywall 组件 + Store 完成 |
| 07-25 05:19 | 技术方案文档定稿 |
| 07-25 05:21~05:24 | 后端 Service 层 + API 路由完成 |
| 07-25 05:27 | QuotaExhaustedModal 完成 |
| 07-25 05:54 | GameView 集成改造完成 |

---

## 三、待验收项

### P0（阻塞发布）

| # | 验收项 | 状态 |
|---|--------|------|
| 1 | 数据库迁移可执行（subscription_plans / dialogue_quotas / paywall_events 建表成功） | ⏳ 待验证 |
| 2 | Free 用户动态梯度额度正确（蜜月10/养成5/常规3/回归5） | ⏳ 待验证 |
| 3 | Basic 用户 30次/天额度正确 | ⏳ 待验证 |
| 4 | Standard/Premium 无限额度正确 | ⏳ 待验证 |
| 5 | 额度耗尽后 Paywall 弹窗正确触发 | ⏳ 待验证 |
| 6 | 每日弹窗上限 2 次限制生效 | ⏳ 待验证 |
| 7 | 蜜月期（注册≤3天）不弹 Paywall | ⏳ 待验证 |
| 8 | 订阅状态变更（active→expired）权限正确降级 | ⏳ 待验证 |
| 9 | 碎片购买额外对话次数正确叠加 | ⏳ 待验证 |
| 10 | 好感度衰减逻辑正确 | ⏳ 待验证 |

### P1（不阻塞发布）

| # | 验收项 | 状态 |
|---|--------|------|
| 11 | PaywallBanner 样式正确 | ⏳ 待验证 |
| 12 | PaywallToast 自动消失 | ⏳ 待验证 |
| 13 | TierComparison 对比表正确展示 4 档差异 | ⏳ 待验证 |
| 14 | SubscriptionView 购买/续费/降级流程 | ⏳ 待验证 |

---

## 四、已知问题 & 风险

| # | 类型 | 描述 | 影响 | 处理建议 |
|---|------|------|------|----------|
| 1 | 数据一致性 | TIER_PERMISSIONS 中 Basic 的 fragment_discount 在技术方案中标为 0，但 subscription_config.json 中也为 0，需确认是否与 PRD 一致 | 低 | 验收时核对 PRD |
| 2 | 时区 | 额度重置使用 UTC 00:00，需确认前端展示是否做了时区转换 | 中 | 验收时检查 |
| 3 | 回归用户 | returnee_activated_at 字段需要 migration 执行后才能测试 | 中 | 先跑 migration |
| 4 | 并发 | 额度扣减是否有乐观锁/事务保护，需检查 quota_service.py | 中 | 代码 review |

---

## 五、当前阻塞项 & Agent 处理状态

| # | 阻塞项 | 处理 Agent | 状态 | 预计完成 |
|---|--------|-----------|------|----------|
| 1 | 双 Subscription 表并存（`models/subscription.py` vs `api/v1/subscription.py` + `api/v1/user_subscription.py`） | BE | 🔧 处理中 | 待 BE 报告 |
| 2 | 前端 API 路径与后端路由未对齐 | FE | 🔧 处理中 | 待 FE 报告 |
| 3 | 迁移脚本缺少 `returnee_activated_at` 列声明 | BE | ⏳ 待修复 | 随 B-1 一并处理 |
| 4 | 迁移不在 Alembic 版本链 | BE | ⏳ 待修复 | 随 B-1 一并处理 |

**详细检查清单**：见 `docs/CR-016/release-checklist.md`

---

## 六、下一步

1. **BE**：修复双 Subscription 表 + 补 `returnee_activated_at` + 接入 Alembic 版本链
2. **FE**：对齐 API 路径
3. **BE/FE**：联调通过后执行数据库迁移
4. **QA**：按验收计划 24 项 AC 执行测试
5. **PM**：核对 fragment_discount 与 PRD 一致性（K-1）
