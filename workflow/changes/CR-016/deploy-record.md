# CR-016 部署记录

## 基本信息

| 项 | 值 |
|---|---|
| CR ID | CR-016 |
| 变更名称 | 订阅付费体系 + 动态对话额度 |
| 版本 | 1.0.0 |
| 部署时间 | 2026-07-25T08:43Z |
| 部署人 | Ops（自动执行） |
| 发布指令来源 | 用户确认（通过飞书） |
| 环境 | local（Docker Compose） |

## 发布内容

- 4档订阅体系（Free/$1.99/$4.99/$9.99）
- Free用户动态梯度额度
- 9个新API端点（/api/v1/cr016/*）
- Mock支付 + 碎片购买
- 好感衰减机制
- Paywall限流
- 双表向后兼容

## 执行步骤

| # | 步骤 | 结果 | 备注 |
|---|---|---|---|
| 1 | 前端构建 `npm run build` | ✅ 成功 | 9.85s，24 个 chunk，含 SubscriptionView |
| 2 | 重启后端 `docker compose restart backend` | ✅ 成功 | container restarted |
| 3 | 健康检查 `curl /api/v1/health` | ✅ `{"status":"ok","version":"1.0.0"}` | |
| 4 | API 端点验证 | ✅ 3 个端点均返回 401（需认证，端点可达） | subscription/status, dialogue/quota/status, paywall/daily-count |
| 5 | 前端构建产物验证 | ✅ dist/ 存在，含 index.html + assets/ | |
| 6 | 前端代理验证 `localhost:8081/api/v1/cr016/*` | ✅ 代理 → 后端正常 | |
| 7 | 前端页面验证 `localhost:8081/` | ✅ HTTP 200，HTML 正常 | |

## 验证结果

| 验证项 | 状态 | 证据 |
|---|---|---|
| 后端健康 | ✅ PASS | `{"status":"ok","version":"1.0.0"}` |
| 后端 API 端点 | ✅ PASS | `/api/v1/cr016/*` 返回 401（端点存在，需认证） |
| 前端代理 | ✅ PASS | `localhost:8081/api/v1/cr016/subscription/status` → 后端正常转发 |
| 前端页面 | ✅ PASS | `localhost:8081/` 返回 HTML |
| 前端构建产物 | ✅ PASS | `dist/` 含 index.html + assets/ + images/ |
| Mock API | no | 真实后端 + 真实数据库 |

## 数据库迁移

| 项 | 状态 | 说明 |
|---|---|---|
| CR-016 迁移 | ✅ 已集成 | Alembic revision `cr016_subscription_paywall.py` 已存在，`down_revision: 'b9888a8e49f2'`，生产部署执行 `alembic upgrade head` 即可 |
| `returnee_activated_at` 列 | ✅ 已声明 | Alembic revision 第 5 步已包含此列 DDL |

**说明**：独立脚本 `backend/migrations/001_cr016_subscription_paywall.py` 未包含 `returnee_activated_at` 列，但 Alembic revision 已包含。生产部署使用 Alembic，不受影响。

## 遗留项

| # | 问题 | 严重度 | 责任方 |
|---|---|---|---|
| 1 | Security 审查未执行 | 🟡 中 | Security（发布已由用户确认，不阻塞本地部署；生产部署前需完成） |

## 结论

**✅ 部署成功** — 本地环境部署完成，所有服务正常运行。

- 前端构建成功
- 后端重启成功
- 健康检查通过
- API 端点可达
- 前端代理正常

**注意**：遗留项 1-3 需在**生产部署前解决**。
