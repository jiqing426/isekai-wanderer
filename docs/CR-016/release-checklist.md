# CR-016 发布检查清单

> 创建时间：2026-07-25 | 状态：进行中

---

## 🔴 阻塞项（必须修复才能发布）

| # | 问题 | 负责人 | 状态 | 说明 |
|---|------|--------|------|------|
| B-1 | 双 Subscription 表并存 | BE | 🔧 处理中 | `models/subscription.py`（CR-016 新建）与 `api/v1/subscription.py` + `api/v1/user_subscription.py`（旧代码）并存，路由前缀冲突：`/cr016/subscription` vs `/subscription` vs `/user/subscription`。需统一为 CR-016 路由，废弃旧路由或合并 |
| B-2 | 前端 API 路径更新 | FE | 🔧 处理中 | `frontend/src/api/subscription.ts` 中的端点路径需与后端最终路由对齐 |
| B-3 | 迁移脚本缺少 `returnee_activated_at` 列声明 | BE | ⏳ 待修复 | `migrations/001_cr016_subscription_paywall.py` 只声明了 `affection_decay_last_calc`，缺少技术方案 2.3 节要求的 `returnee_activated_at TIMESTAMPTZ`。回归用户功能无法工作 |
| B-4 | 迁移不在 Alembic 版本链 | BE | ⏳ 待修复 | 当前迁移是独立脚本，未接入 Alembic revision chain，生产部署时不会被自动执行 |

---

## 🟡 发布前检查（Pre-release）

### 后端

| # | 检查项 | 验证方式 | 状态 |
|---|--------|----------|------|
| P-1 | 后端服务启动无报错 | `uvicorn app.main:app` 启动成功 | ⏳ |
| P-2 | 数据库迁移执行成功 | `python migrations/001_cr016_subscription_paywall.py` 无异常 | ⏳ |
| P-3 | 3 张新表创建（subscription_plans / dialogue_quotas / paywall_events） | `\dt` 确认表存在 | ⏳ |
| P-4 | users 表新增字段（affection_decay_last_calc + returnee_activated_at） | `\d users` 确认列存在 | ⏳ |
| P-5 | CR-016 的 9 个 API 端点可访问 | curl 各端点返回非 500 | ⏳ |
| P-6 | 旧 subscription 路由已清理或合并 | 无重复路由注册 | ⏳ |
| P-7 | 并发安全：quota_service 额度扣减使用 SELECT FOR UPDATE | 代码 review ✅ 已确认 `with_for_update()` 在 L133/L198 | ✅ |
| P-8 | fragment_discount 与 PRD 一致（Free=0, Basic=0, Standard=0, Premium=0.7） | 核对 PRD | ⏳ |

### 前端

| # | 检查项 | 验证方式 | 状态 |
|---|--------|----------|------|
| P-9 | `npm run build` 0 errors | CI 或本地构建 | ⏳ |
| P-10 | API 路径与后端一致 | 检查 `api/subscription.ts` 中 baseURL | ⏳ |
| P-11 | PaywallManager 在 App.vue 或 GameView 中正确挂载 | 页面渲染验证 | ⏳ |
| P-12 | 额度重置时间前端时区转换（UTC→用户本地时间） | 检查 QuotaDisplay 组件 | ⏳ |

### 测试

| # | 检查项 | 验证方式 | 状态 |
|---|--------|----------|------|
| P-13 | 后端单元测试通过 | `pytest` | ⏳ |
| P-14 | 前端构建通过 | `npm run build` | ⏳ |

---

## 🟢 发布后验证（Post-release）

| # | 验证项 | 预期结果 | 状态 |
|---|--------|----------|------|
| R-1 | 后端服务健康 | `/api/v1/health` 返回 200 | ⏳ |
| R-2 | 订阅状态查询 | `GET /cr016/subscription/status` 返回用户档位 | ⏳ |
| R-3 | 对话额度查询 | `GET /cr016/dialogue/quota/status` 返回剩余额度 | ⏳ |
| R-4 | 额度扣减 | 完成一次对话后 consumed +1 | ⏳ |
| R-5 | 动态梯度额度 | 新注册用户首日额度 = 10 | ⏳ |
| R-6 | Paywall 触发 | 额度耗尽后弹窗展示 | ⏳ |
| R-7 | 蜜月期保护 | 注册 ≤3 天不弹 Modal | ⏳ |
| R-8 | 每日弹窗上限 | 同一天最多 2 次 Modal | ⏳ |
| R-9 | 好感度衰减 | 多日不互动后好感度下降 | ⏳ |
| R-10 | 前端页面渲染 | SubscriptionView + Paywall 组件正常显示 | ⏳ |

---

## 🔵 已知问题（不阻塞发布，但需跟踪）

| # | 问题 | 影响 | 优先级 | 处理计划 |
|---|------|------|--------|----------|
| K-1 | fragment_discount 值需 PM 确认与 PRD 一致 | Basic/Standard 折扣为 0 是否符合产品预期 | P1 | 待 PM 核对 PRD |
| K-2 | UTC 00:00 额度重置的前端展示 | 用户看到的倒计时可能因时区不准 | P2 | FE 检查时区转换 |
| K-3 | 旧 `api/v1/subscription.py` 和 `api/v1/user_subscription.py` 中的功能是否需要迁移到 CR-016 路由 | 废弃后原有功能可能丢失 | P1 | BE 评估影响范围 |

---

## 📊 统计

| 类别 | 总数 | ✅ 完成 | 🔧 进行中 | ⏳ 待处理 |
|------|------|---------|-----------|-----------|
| 阻塞项 | 4 | 0 | 2 | 2 |
| 发布前检查 | 14 | 1 | 0 | 13 |
| 发布后验证 | 10 | 0 | 0 | 10 |
| 已知问题 | 3 | 0 | 0 | 3 |

---

## 📝 签核

| 角色 | 签核 | 时间 |
|------|------|------|
| PM | ⏳ | — |
| QA | ⏳ | — |
| BE | ⏳ | — |
| FE | ⏳ | — |
| PL | ⏳ | — |
