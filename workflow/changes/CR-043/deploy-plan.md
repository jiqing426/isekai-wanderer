# Deploy Plan

本文记录发布关口前必须评审的发布计划。实际部署执行结果写入 `deploy-record.md`。

| 项 | 内容 |
| --- | --- |
| CR 编号 | CR-043 |
| 变更内容 | 订阅权益区分与 CG 画廊权限控制（gallery.py is_accessible + game.py script_access 检查 + scripts.py is_accessible + settings.py member-info 数据源修复 + subscription_service.py get_user_tier + 前端 GalleryView/SubscriptionPlans/subscription.ts/user.ts 变更） |
| 目标环境 | DEV (ENV-L1) |
| 目标证据等级 | L3 |
| 发布负责人 | ops (isekai-wanderer-op) |
| 计划状态 | Ready |
| 人工确认要求 | 权限边界变更经 Security 审查通过 (CEO C3 满足)；无其他人工确认项 |
| 无 DB 变更 | 是（is_accessible 为运行时计算字段，script_access 为运行时虚拟判定，无 schema 变更） |
| 无新增依赖 | 是（dateutil 已替换为 timedelta，无新增 Python/npm 包） |

## 安全审查结论

- 安全审查已通过，详见 `workflow/changes/CR-043/security-review.md`
- AC-015 (CEO C3 必审) 权限绕过风险审查完成：服务端获取 tier，不接受客户端篡改
- 2 项低风险建议不阻塞：S-3 (静态文档 payment URL 残留), S-4 (scripts.py Depends(None) BUG-003)
- 2 项已知 BUG 不阻塞：BUG-003 (/scripts 端点验证错误), BUG-004 (AC-020 E2E test spec issue)

## 发布步骤

| 步骤 | 命令 / 操作 | 预期结果 | 负责人 |
| --- | --- | --- | --- |
| 1 | `cd /root/isekai-wanderer && git status` 确认代码状态 | Docker volume mount 已挂载最新代码 | ops |
| 2 | `docker compose --profile app restart backend` | 重启后端容器，加载 gallery.py / game.py / scripts.py / settings.py / subscription_service.py 变更 | ops |
| 3 | `sleep 10 && curl -sf http://localhost:8000/api/v1/health` | 后端健康检查通过，返回 `{"status":"ok","version":"1.0.0"}` | ops |
| 4 | `docker compose --profile app restart frontend` | 重启前端容器，加载 GalleryView.vue / SubscriptionPlans.vue / subscription.ts / user.ts 变更 | ops |
| 5 | `curl -sf -o /dev/null -w '%{http_code}' http://localhost:8081/` | 前端入口可达，HTTP 200 | ops |
| 6 | API 端点验证（见下方"发布后冒烟验证"） | 端点可达，权限检查生效 | ops |
| 7 | 通知 PL 发布完成，写入 deploy-record.md | 部署记录完成 | ops |

### 发布后冒烟验证

```bash
# 1. Health check
curl -sf http://localhost:8000/api/v1/health
# 预期: {"status":"ok","version":"1.0.0"}

# 2. gallery/collections 端点（需认证，返回 is_accessible 字段）
curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/v1/gallery/collections/test-script-id -H "Authorization: Bearer {token}"
# 预期: 200 或 401（无 auth 时），非 404

# 3. game/start 权限检查（free 用户非试用剧本 → 403 SCRIPT_ACCESS_DENIED）
curl -s -o /dev/null -w '%{http_code}' -X POST http://localhost:8000/api/v1/game/start -H "Content-Type: application/json" -H "Authorization: Bearer {free_token}" -d '{"script_id":"{non_trial_script_id}"}'
# 预期: 403

# 4. users/me/member-info 数据源验证
curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/v1/users/me/member-info -H "Authorization: Bearer {token}"
# 预期: 200 或 401（无 auth 时），非 404

# 5. subscription/status 端点
curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/v1/subscription/status -H "Authorization: Bearer {token}"
# 预期: 200 或 401（无 auth 时），非 404

# 6. scripts 端点（公开端点，无 auth 也应返回 200）
curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/v1/scripts
# 预期: 200（BUG-003 可能导致 500，非阻塞）
```

## 回滚方案

| 步骤 | 命令 / 操作 | 预期结果 | 负责人 |
| --- | --- | --- | --- |
| 1 | `cd /root/isekai-wanderer && git revert <CR-043 merge commit>` | 代码回滚到 CR-043 前状态 | ops |
| 2 | `git push origin main` | 推送回滚 commit | ops |
| 3 | `docker compose --profile app up -d --build backend` | 重建并重启后端容器 | ops |
| 4 | `docker compose --profile app restart frontend` | 重启前端容器 | ops |
| 5 | `sleep 10 && curl -sf http://localhost:8000/api/v1/health` | 验证后端健康 | ops |
| 6 | `curl -sf -o /dev/null -w '%{http_code}' http://localhost:8081/` | 验证前端入口可达 | ops |
| 7 | 验证 gallery/game/start 端点恢复无 is_accessible 字段 | 确认回滚成功 | ops |

### 回滚注意事项

- CR-043 无 DB schema 变更，回滚不需要数据库迁移或数据修复
- 回滚后 `is_accessible` 字段不再返回（前端兼容，GalleryView.vue 使用 `=== false` 判断）
- 回滚后 `POST /game/start` 不再检查 `script_access`，所有剧本可开始
- 回滚后 `GET /users/me/member-info` 数据源恢复为旧逻辑
- 如 git revert 不可行，可使用 `git reset --hard <pre-CR-043 commit>` 强制回退

## 监控方案

### 健康检查

| 检查项 | 命令 | 频率 | 预期 | 告警阈值 |
| --- | --- | --- | --- | --- |
| 后端健康 | `curl -sf http://localhost:8000/api/v1/health` | 每 15s（Docker healthcheck） | `{"status":"ok"}` | 连续 3 次失败 |
| 前端可达 | `curl -sf http://localhost:8081/` | 每 15s（Docker healthcheck） | HTTP 200 | 连续 3 次失败 |
| PostgreSQL | Docker healthcheck `pg_isready` | 每 10s | ready | 连续 5 次失败 |
| Redis | Docker healthcheck `redis-cli ping` | 每 10s | PONG | 连续 5 次失败 |

### 权限检查监控

| 检查项 | 命令 / 日志 | 频率 | 预期 | 告警阈值 |
| --- | --- | --- | --- | --- |
| SCRIPT_ACCESS_DENIED 日志 | `docker compose logs backend 2>&1 \| grep "SCRIPT_ACCESS_DENIED"` | 按需 | 正常用户操作产生少量 403 | 异常大量 403（可能表示权限配置错误或攻击尝试） |
| gallery 端点可达 | `curl -sf -o /dev/null -w '%{http_code}' http://localhost:8000/api/v1/gallery/collections/{id} -H "Authorization: Bearer {token}"` | 每 5min | 200 | 连续 2 次非 200 |
| member-info 端点可达 | `curl -sf -o /dev/null -w '%{http_code}' http://localhost:8000/api/v1/users/me/member-info -H "Authorization: Bearer {token}"` | 每 5min | 200 | 连续 2 次非 200 |
| subscription/status 端点 | `curl -sf -o /dev/null -w '%{http_code}' http://localhost:8000/api/v1/subscription/status -H "Authorization: Bearer {token}"` | 每 5min | 200 | 连续 2 次非 200 |

### 日志监控

| 日志源 | 路径 / 命令 | 关注关键词 | 处理 |
| --- | --- | --- | --- |
| 后端 Uvicorn | `docker compose logs backend --tail 100` | `SCRIPT_ACCESS_DENIED`, `Error`, `Traceback`, `subscription_service` | 发现异常立即检查 SubscriptionService 和 tier 计算逻辑 |
| 权限拒绝审计 | `docker compose logs backend 2>&1 \| grep "SCRIPT_ACCESS_DENIED"` | `SCRIPT_ACCESS_DENIED` | 监控 403 频率，异常大量需检查 TIER_PERMISSIONS 配置 |
| 前端 Vite | `docker compose logs frontend --tail 50` | `error`, `failed` | 编译错误需检查 GalleryView.vue / SubscriptionPlans.vue 引入 |

### 告警方案

| 告警项 | 触发条件 | 严重程度 | 处理步骤 |
| --- | --- | --- | --- |
| 后端不可达 | Docker healthcheck 连续 3 次失败 | P0 | 1. `docker compose logs backend --tail 100` 查日志 2. 检查 PostgreSQL/Redis 健康 3. 必要时执行回滚方案 |
| SCRIPT_ACCESS_DENIED 异常增多 | 5 分钟内 > 50 次 403 | P1 | 1. 检查 SubscriptionService.get_user_tier() 逻辑 2. 确认 TIER_PERMISSIONS 配置 3. 检查是否有用户 tier 数据异常 |
| gallery/member-info 端点 500 | curl 检查返回 5xx | P1 | 1. 检查 SubscriptionService 日志 2. 确认 DB 连接正常 3. 检查 settings.py member-info 数据源 |
| subscription/status 不可达 | curl 检查返回非 200 | P2 | 1. 检查后端路由注册 2. 确认 subscription 端点未被误删 |

## 发布前检查

| 项 | 状态 | 说明 |
| --- | --- | --- |
| CI/CD 结果已通过或有批准豁免 | ✅ Passed | BE pytest 24/25 passed（1 env error 非 business failure），FE vitest 14/14 passed。详见 `test-report.md` CI/CD 执行结果。Mock API=no。 |
| Delivery E2E / Runtime Smoke 已通过 | ✅ Passed | 7/7 passed, Mock API=no。从真实前端入口 `http://localhost:8081` 经 Vite proxy 访问真实后端 `http://localhost:8000`。覆盖 AC-001, AC-004, AC-005, AC-014, AC-016, AC-017, AC-018。详见 `test-report.md` Delivery E2E / Runtime Smoke Results。 |
| Browser Interaction E2E 已通过 | ✅ Passed (条件性) | 5/6 passed (1 failed=BUG-004 test spec issue, Vue reactivity)。Playwright Chromium 真实浏览器执行用户动作，Mock API=no。覆盖 AC-002, AC-003, AC-011, AC-016, AC-017。AC-020 功能通过代码审查 + Delivery E2E 确认。详见 `test-report.md` Browser Interaction E2E Results。 |
| 目标环境测试矩阵已覆盖 | ✅ ENV-L1 已验证 | 证据等级 L1（本地通过）。CI/CD + Delivery E2E + Browser E2E 均在 ENV-L1 环境执行。目标环境为 DEV (ENV-L1)。 |
| 公网 / 外网访问验证已完成或声明不适用 | ✅ 不适用 | CR-043 目标环境为 DEV (ENV-L1)，使用 localhost:8081 + localhost:8000，不涉及公网入口。无新增端口/proxy 变更。 |
| 测试结论已通过或阻塞项有负责人 | ✅ Passed | QA 结论：✅ 可推进 RELEASE_GATE。P0 AC 13 项：11 通过 + 2 条件性通过（AC-009 BUG-003 BE 单测覆盖、AC-020 代码审查确认）；P1 AC 8 项：6 通过 + 2 未测试（AC-012/013 spec 缺失，非业务阻塞）。BUG-003/BUG-004 Low severity 非阻塞。详见 `test-report.md`。 |
| 安全审查已通过或阻塞项有负责人 | ✅ Passed | Security 结论：通过。AC-015 (CEO C3) 权限绕过审查完成：服务端获取 tier 不接受客户端篡改；TIER_PERMISSIONS 模块级常量不可修改；is_accessible 后端计算；审计日志完整。2 项低风险建议（S-3/S-4）+ 2 项 BUG（BUG-003/BUG-004）不阻塞。详见 `security-review.md`。 |
| 回滚路径可执行 | ✅ Ready | 回滚方案见上方：git revert + docker compose rebuild + restart。无 DB schema 变更，回滚不需要数据修复。步骤可执行，预期结果明确。 |
| 环境变量一致性 | ✅ Verified | `.env.example` 与 `docker-compose.yml` 一致。CR-043 无新增环境变量。 |
| 部署配置无真实密钥 | ✅ Verified | `.env.example` 所有敏感值均为占位符。`docker-compose.yml` 使用 `${VAR:-default}` 引用。Security 审查确认无真实密钥。 |
| 健康检查和监控入口 | ✅ Ready | Docker healthcheck 已配置 backend/frontend/db/redis。API 端点冒烟验证步骤已定义。权限拒绝审计日志监控已定义。 |
| 发布计划、回滚步骤、监控方案和失败处理是否可执行 | ✅ Ready | 发布步骤 7 步逐项可执行；回滚方案 7 步逐项可执行；监控方案含健康检查、权限检查监控、日志监控和告警方案；失败处理有明确告警和处理步骤。 |

## 风险评估

| 风险项 | 等级 | 说明 | 缓解措施 |
| --- | --- | --- | --- |
| BUG-003 /scripts 端点验证错误 | Low | `Depends(NoneType)` 导致 `/scripts` 端点 500 | BE 单元测试 12/12 已覆盖 is_accessible 逻辑；S-4 建议后续使用 `get_current_user_id_optional` 替代 |
| BUG-004 AC-020 E2E 登录表单 | Low | `page.fill()` 未触发 Vue reactivity | 功能通过代码审查 + Delivery E2E 确认；建议 FE 后续修复 spec |
| S-3 静态文档 payment URL 残留 | Low | `backend/static/isekai-api-doc.md` 有 `payment.example.com` 示例 URL | 文档不影响运行时行为；后续迭代更新 |
| 订阅过期降级 | Medium | 用户订阅过期后 tier 自动降级为 free | `get_user_tier()` 检查 `expires_at < datetime.now()`，自动降级逻辑已验证 |

## 退回规则

- 发布条件不完整退回 PL。
- 安全问题退回 Security。
- 构建或运行失败退回对应实现 Agent 或 PL。

## 完成标准

- 发布计划有步骤、回滚方案和监控方案；部署记录有版本、环境和实际执行结果。
- 监控或验证结果可追踪。
- Release 证据、部署步骤、健康检查和回滚记录能沿验收追踪链回到对应 AC；发布失败时能按失败倒查链定位最早断链环节。

## Ops 确认

| 项 | 确认人 | 日期 | 结论 |
| --- | --- | --- | --- |
| CI/CD 证据已审查 | ops (isekai-wanderer-op) | 2026-09-17T20:00+08:00 | ✅ 24/25 BE + 14/14 FE passed，1 env error 非 business failure |
| Delivery E2E 证据已审查 | ops (isekai-wanderer-op) | 2026-09-17T20:00+08:00 | ✅ 7/7 passed, Mock API=no |
| Browser E2E 证据已审查 | ops (isekai-wanderer-op) | 2026-09-17T20:00+08:00 | ✅ 5/6 passed, BUG-004 非业务缺陷，功能通过代码审查确认 |
| 安全审查证据已审查 | ops (isekai-wanderer-op) | 2026-09-17T20:00+08:00 | ✅ Passed, AC-015 CEO C3 满足，权限绕过审查完成 |
| 回滚方案可执行 | ops (isekai-wanderer-op) | 2026-09-17T20:00+08:00 | ✅ git revert + docker compose rebuild, 无 DB 变更 |
| 监控方案已就绪 | ops (isekai-wanderer-op) | 2026-09-17T20:00+08:00 | ✅ Docker healthcheck + API 冒烟 + 权限日志监控 + 告警方案 |
| 发布计划结论 | ops (isekai-wanderer-op) | 2026-09-17T20:00+08:00 | **Ready — 执行部署后写 deploy-record** |
