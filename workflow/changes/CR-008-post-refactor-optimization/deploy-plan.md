# CR-008 发布计划

**变更名称**: post-refactor-optimization  
**CR-ID**: CR-008  
**创建时间**: 2026-07-23T14:00:00Z  
**状态**: ⛔ RETURNED（退回 PL）

---

## 发布前检查

| # | 检查项 | 状态 | 证据/说明 |
|---|--------|------|-----------|
| 1 | CI/CD 执行结果 | ⚠️ 未验证 | 无 CI/CD pipeline 执行记录 |
| 2 | Delivery E2E / Runtime Smoke | ✅ PASS | `curl -f http://localhost:8081/api/v1/health` → 200 OK, Mock API=no |
| 3 | Browser Interaction E2E | ✅ PASS | 10/10 通过, Playwright headless, Mock API=no |
| 4 | 安全审查 | ❌ **缺失** | `security-review.md` 文件不存在，Security Agent 未执行安全审查 |
| 5 | 验收确认 | ❌ **缺失** | `acceptance.md` 文件不存在，无 P0 验收签字 |
| 6 | Gate Readiness Check | ❌ **失败** | `check-gate-readiness.py --gate release` 失败：缺少 `openspec/changes/post-refactor-optimization/` |
| 7 | 回滚步骤 | ⏳ 待定义 | 发布计划未批准，回滚方案暂不执行 |
| 8 | 健康检查 | ✅ 已定义 | `/api/v1/health` endpoint 存在，docker-compose healthcheck 已配置 |
| 9 | 监控和告警 | ⏳ 待定义 | 发布计划未批准，监控方案暂不定义 |
| 10 | 环境变量检查 | ✅ PASS | `.env.example` 无真实密钥，仅占位符 |
| 11 | 部署配置检查 | ✅ PASS | `docker-compose.yml` 无生产私有数据 |

---

## 测试报告摘要

- **总测试**: 38 项，通过 37 项，失败 1 项（97.4%）
- **后端接口**: 26 个接口中 25 个 PASS，1 个 P2 缺陷（devices logout UUID 500→400）
  - P2 缺陷：state.md 记录 BE 已修复，但 test-report.md 中仍标记为 FAIL
- **前端构建**: TypeScript 0 错误，Vite 构建成功
- **Browser E2E**: 10/10 全部通过
- **Mock 策略**: Mock API=no（真实后端）

---

## 退回原因

### 1. ❌ 安全审查缺失（阻塞项 — P0）

`workflow/changes/CR-008-post-refactor-optimization/security-review.md` 不存在。

**OPS 规则**: "不接收未通过测试和安全的发布"、"安全问题退回 Security"。

**要求**: PL 需触发 Security Agent 执行安全审查，生成 `security-review.md` 并确认无 P0/P1 安全问题。

### 2. ❌ 验收确认缺失（阻塞项 — P0）

`workflow/changes/CR-008-post-refactor-optimization/acceptance.md` 不存在。

**要求**: PL 需组织 P0 验收并生成 `acceptance.md`，确认所有 AC 已满足。

### 3. ❌ Gate Readiness Check 失败（阻塞项 — P0）

`python tools/check-gate-readiness.py --gate release --change post-refactor-optimization --change-id CR-008` 返回失败：

```
关口检查：未通过
关口：release
- 缺少 openspec/changes/post-refactor-optimization/
```

**要求**: PL 需补充 `openspec/changes/post-refactor-optimization/` 目录（至少包含 `design.md` 和 `tasks.md`），或确认此 CR 的 OpenSpec 豁免流程。

### 4. ⚠️ P2 缺陷状态不一致（非阻塞 — 需确认）

- `test-report.md` 记录 BUG-001（devices logout UUID 返回 500）为 FAIL
- `state.md` 流转日志记录 "BE 修复 P2 缺陷" 为 completed
- 缺少回归测试验证记录

**要求**: PL 确认 P2 修复已通过回归测试，或更新 test-report.md。

---

## 退回动作

| 动作 | 目标 | 说明 |
|------|------|------|
| 触发安全审查 | Security Agent | PL 通知 Security 执行安全审查 |
| 组织 P0 验收 | QA/PM | PL 组织验收并记录 acceptance.md |
| 补充 OpenSpec | PL/SA | 补充 openspec/changes/post-refactor-optimization/ 或确认豁免 |
| 确认 P2 修复 | QA | 回归验证 devices logout UUID 修复 |
| 重新触发 Gate Check | PL | 上述完成后运行 `check-gate-readiness.py` |

---

## 发布结论

**⛔ RETURNED** — 发布条件不满足，退回 PL 组织补全。

待安全审查通过、验收确认完成、Gate Readiness Check 通过后，OPS 可重新接收发布任务。

---

## 预批准发布步骤（待条件满足后执行）

### 1. 数据库迁移
- [ ] 确认 Alembic 迁移脚本存在
- [ ] 执行 `alembic upgrade head`
- [ ] 验证表结构（posts, collections, user_settings 扩展, users.signature）

### 2. 后端部署
- [ ] `docker compose build backend`
- [ ] `docker compose up -d backend`
- [ ] 验证 `/api/v1/health` → 200
- [ ] 验证 26 个接口响应正常

### 3. 前端部署
- [ ] `docker compose build frontend`
- [ ] `docker compose up -d frontend`
- [ ] 验证 http://localhost:8081 可访问
- [ ] 验证 Vite proxy → backend 转发正常

### 4. 发布验证
- [ ] Delivery E2E: `curl -f http://localhost:8081/api/v1/health`
- [ ] Browser E2E: Playwright 核心用例回归
- [ ] 检查后端日志无异常

### 5. 回滚方案
- [ ] 数据库: `deploy/db-backup-pre-deploy.sql` 已备份
- [ ] 后端: `docker compose restart backend` 回退到上一镜像
- [ ] 前端: `docker compose restart frontend` 回退到上一构建
- [ ] 回滚命令: `deploy/restart-be.sh`
