# CR-016 Security Review

| 项 | 值 |
|---|---|
| CR | CR-016 |
| 审查人 | Security Agent |
| 审查时间 | 2026-07-25T09:00Z |
| 审查范围 | 9 个 API 端点 + 3 个数据表 + 3 个服务 + 迁移脚本 |
| 结论 | 🟢 **PASSED** — 无安全阻塞项，存在 2 个生产就绪警告 + 6 个 P1 建议 |

---

## 审查方法

1. 读取 `PROJECT_WORKSPACE.md` → `project_root: /root/isekai-wanderer`
2. 读取 `workflow/traceability-chain.md` 和 `workflow/failure-backtrace.md`
3. 读取 `docs/security/security.md`、`docs/api/api.md`、`docs/database/database.md`、`docs/runtime/runtime-contract.md`
4. 读取 `test-report.md`、`deploy-plan.md`、`review.md`
5. 逐文件审查 CR-016 实现代码（9 个 API 端点 + 3 个服务 + 3 个模型 + 迁移脚本）
6. 检查发布证据：`Mock API=no` ✅（test-report 确认 `DISABLE_MOCK=1`）

---

## 检查清单

### 1. 密钥 / Token / 证书泄露 ✅ PASS

- 代码中无硬编码密钥、token、证书或密码
- `.env.example` 仅含占位符
- 生产凭据通过环境变量注入（`JWT_SECRET`、`DATABASE_URL`、`LLM_API_KEY`）

### 2. 鉴权 / 授权 ✅ PASS（附 1 个 P1 建议）

| 端点 | Auth | 评估 |
|---|---|---|
| 全部 9 个 `/cr016/*` 端点 | `Depends(get_current_user_id)` | ✅ JWT Bearer 强制认证 |

- `user_id` 从 JWT token 提取，不从请求体传入 → **无水平越权风险**
- 无管理员端点暴露给普通用户

**P1 建议**：`create_subscription_cr016` 缺少速率限制。虽然创建订阅会更新（而非新增）记录，但恶意用户可高频调用导致数据库写入压力。建议加 Redis 限流（如 5 次/分钟/用户）。

### 3. 输入验证 ✅ PASS（附 1 个 P1 建议）

- `CreateSubscriptionRequest`：`tier` 和 `cycle` 有服务端白名单校验（`valid_tiers`、`monthly/yearly`）
- `FragmentPurchaseRequest`：`amount` 有 `gt=0` 校验
- `CheckTriggerRequest`：`scene` 和 `user_initiated` 有类型约束
- `RecordEventRequest`：`display_type` 有类型约束

**P1 风险**：`RecordEventRequest.display_type` 未校验枚举值（`modal/banner/toast`），可写入任意字符串到 `paywall_events.display_type`。虽然不影响核心逻辑，但会污染审计数据。

**P1 建议**：`FragmentPurchaseRequest.amount` 无上限校验。虽然受碎片余额限制，但单次传入极大值（如 `amount=999999`）会导致 `fragments_needed` 溢出检查前的计算。建议加 `le=100` 上限。

### 4. 额度消耗并发安全 ✅ PASS

| 操作 | 并发保护 | 评估 |
|---|---|---|
| `consume_quota` | `SELECT ... FOR UPDATE` on `dialogue_quotas` | ✅ 防并发扣减 |
| `fragment-purchase` | `SELECT ... FOR UPDATE` on `fragments` | ✅ 防双重消费 |
| `add_fragment_quota` | 无锁 | ⚠️ 见下方 P1 |

**P1 风险**：`add_fragment_quota` 未使用 `FOR UPDATE`。如果同一用户并发调用两次 `fragment-purchase`，两次都通过碎片余额检查后，`fragment_extra` 可能被覆盖而非累加。实际风险低（碎片扣减已锁定），但建议加锁保持一致性。

### 5. 碎片购买刷取风险 ✅ PASS

- 3 碎片 = 1 对话额度，汇率固定
- 碎片扣减使用 `FOR UPDATE` 锁，防双重消费
- 余额不足返回 402，不执行扣减
- 碎片来源无限制（可来自签到、任务、IAP），但消耗路径单一

**无刷取风险**：碎片是用户自有资产，兑换额度是合理消费路径。

### 6. Paywall 限流绕过风险 ⚠️ P1

| 规则 | 实现 | 评估 |
|---|---|---|
| 每日 modal ≤ 2 次 | `get_daily_modal_count` 查询 `paywall_events` 表 | ✅ 正确 |
| 蜜月期禁止 modal | `is_honeymoon_period` 检查 `days <= 3` | ✅ 正确 |
| 订阅用户禁用 paywall | `is_exempt_from_quota` 检查 | ✅ 正确 |
| 用户主动入口绕过限流 | `user_initiated=True` 时直接返回 modal | ⚠️ 见下方 |

**P1 风险**：`user_initiated=True` 绕过每日限流。前端传入 `user_initiated=True` 即可无限弹出 modal。虽然业务上合理（用户主动点击），但恶意前端可高频调用消耗数据库资源。建议加用户级限流（如 10 次/分钟）。

### 7. ⚠️ Mock 支付模式 — 生产就绪警告（非安全阻塞）

**现状**：`POST /cr016/subscription/create` 直接创建订阅记录，无真实支付验证。

**评估**：
- 项目 `docs/security/security.md` 明确将 "Mock payment data" 列为可接受的 mock 边界
- 现有 `/subscription/subscribe` 端点同样使用 mock 模式
- CR-016 遵循项目既定的 mock 支付架构模式
- **这不是安全漏洞，而是架构设计决策**

**生产就绪提醒**：
- 如果当前是开发/测试环境，mock 支付可接受
- 如果即将部署到公网生产环境，需 PL 决策是否集成真实支付网关（Stripe/Apple IAP）
- 此决策属于产品/商业层面，不属于安全审查阻塞项

**结论**：✅ 安全审查通过，标记为生产就绪提醒

### 8. ⚠️ 迁移脚本缺失 `returnee_activated_at` 列 — 生产部署警告（非安全阻塞）

**问题**：`QuotaService.calculate_lifecycle_stage` 引用 `user.returnee_activated_at`，但迁移脚本 `001_cr016_subscription_paywall.py` 未添加此列。

**评估**：
- 此问题已在 `deploy-plan.md` 中记录为已知部署阻塞项
- 测试环境未触发此 bug，因为 honeymoon 路径提前返回，未访问该字段
- 生产环境对注册 >3 天的用户调用 lifecycle API 时会触发 AttributeError

**结论**：✅ 安全审查通过，但生产部署前必须修复（已由 deploy-plan 跟踪）

**修复**：在迁移脚本补充：
```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS returnee_activated_at TIMESTAMPTZ;
```

### 9. 数据保留策略 ⚠️ P1

| 表 | 增长模式 | 当前策略 | 评估 |
|---|---|---|---|
| `paywall_events` | 每次 paywall 触发写入一行 | 无清理 | ⚠️ 无限增长 |
| `dialogue_quotas` | 每用户每天一行 | 无清理 | ⚠️ 无限增长 |
| `subscription_plans` | 订阅变更写入 | 无清理 | ✅ 低频 |

**P1 建议**：
- `paywall_events`：建议保留 90 天，超期归档或删除
- `dialogue_quotas`：建议保留 30 天（仅当日 + 历史审计）
- 添加 cron job 或 startup hook 清理过期数据

### 10. 迁移脚本不在 Alembic 版本链 ⚠️ 中（deploy-plan 已记录）

**问题**：`001_cr016_subscription_paywall.py` 是独立脚本，未集成到 Alembic 版本链。

**影响**：`alembic upgrade head` 不会执行 CR-016 迁移。

**退回对象**：BE / PL / Ops（deploy-plan 已记录）

### 11. 双 Subscription 表并存 ⚠️ 中

**问题**：存在 `subscriptions`（旧表）和 `subscription_plans`（新表）两张表。`SubscriptionService.on_subscription_created` 同时写入两张表。

**评估**：
- 向后兼容：旧 API 仍可访问旧表
- 数据一致性：两张表同步写入，但无事务保证（如果中间失败可能不一致）
- 长期维护：增加复杂度

**建议**：PL 决定是否在后续 CR 中废弃旧表。当前不阻塞发布。

### 12. 发布证据检查 ✅ PASS

| 证据类型 | 状态 | 说明 |
|---|---|---|
| CI/CD | ⏳ 待确认 | deploy-plan 标记待确认 |
| Delivery E2E | ✅ PASS | `Mock API=no`，真实后端 + 真实数据库 |
| Browser Interaction E2E | ✅ PASS | BUG-006 已修复，前端路径已更新 |
| Mock API | ✅ no | `DISABLE_MOCK=1` |

---

## 风险汇总

| # | 风险 | 严重度 | 类别 | 状态 |
|---|---|---|---|---|
| 1 | Mock 支付模式（生产就绪提醒） | 🟡 提醒 | 架构决策 | PL 决策是否集成真实支付 |
| 2 | 迁移缺失 `returnee_activated_at` 列 | 🟡 提醒 | 部署问题 | deploy-plan 已跟踪，生产部署前修复 |
| 3 | `record-event` 未校验 `display_type` 枚举 | 🟡 P1 | 数据完整性 | 建议修复 |
| 4 | `fragment-purchase` 的 `amount` 无上限 | 🟡 P1 | 输入验证 | 建议修复 |
| 5 | `user_initiated` 绕过限流无用户级限速 | 🟡 P1 | 资源消耗 | 建议修复 |
| 6 | `add_fragment_quota` 未使用 FOR UPDATE | 🟡 P1 | 并发一致性 | 建议修复 |
| 7 | `create_subscription` 无速率限制 | 🟡 P1 | 资源消耗 | 建议修复 |
| 8 | `paywall_events` / `dialogue_quotas` 无数据保留策略 | 🟡 P1 | 存储增长 | 建议修复 |
| 9 | 迁移脚本不在 Alembic 版本链 | 🟡 中 | 部署 | deploy-plan 已记录 |

---

## 结论

### 🟢 PASSED

CR-016 安全审查通过，无安全阻塞项。

**安全评估**：
- ✅ 鉴权：所有端点强制 JWT Bearer 认证
- ✅ 授权：无水平越权风险（user_id 从 JWT 提取）
- ✅ 输入验证：核心参数有白名单/范围校验
- ✅ 并发安全：关键操作使用 SELECT FOR UPDATE
- ✅ 无密钥泄露
- ✅ 发布证据：Mock API=no，Delivery E2E 和 Browser E2E 通过

**生产就绪提醒**（非安全阻塞，已由 deploy-plan 跟踪）：
- ⚠️ Mock 支付模式：PL 需决策是否在上线前集成真实支付网关
- ⚠️ 迁移缺失 `returnee_activated_at` 列：生产部署前必须补充 DDL

**P1 改进建议**（可选修复，不阻塞发布）：
- 输入校验加强（`display_type` 枚举、`amount` 上限）
- 并发一致性（`add_fragment_quota` 加锁）
- 速率限制（`create`、`user_initiated`）
- 数据保留策略（`paywall_events`、`dialogue_quotas`）

**Security 审查结论**：✅ **passed** — 可进入 RELEASE_GATE

---

## 附录：审查文件清单

| 文件 | 路径 |
|---|---|
| API 路由 | `backend/app/api/v1/cr016_subscription.py` |
| API 路由 | `backend/app/api/v1/cr016_dialogue.py` |
| API 路由 | `backend/app/api/v1/cr016_paywall.py` |
| 服务 | `backend/app/services/subscription_service.py` |
| 服务 | `backend/app/services/quota_service.py` |
| 服务 | `backend/app/services/paywall_service.py` |
| 模型 | `backend/app/models/subscription.py` |
| 模型 | `backend/app/models/dialogue_quota.py` |
| 模型 | `backend/app/models/paywall_event.py` |
| 迁移 | `backend/migrations/001_cr016_subscription_paywall.py` |
| 测试报告 | `workflow/changes/CR-016/test-report.md` |
| 部署计划 | `workflow/changes/CR-016/deploy-plan.md` |
| PL Review | `workflow/changes/CR-016/review.md` |
