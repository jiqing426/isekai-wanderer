# Deploy Record — CR-002

## 发布信息

- **发布时间**：2026-07-18T17:36:50+08:00
- **部署环境**：production
- **部署负责人**：pl

## 部署步骤执行

| 步骤 | 命令 | 结果 |
|------|------|------|
| 1. 数据库迁移 | `cd backend && alembic upgrade head` | ✅ 无新 migration 文件，数据库已是最新 |
| 2. 初始化种子数据 | `cd backend && python -m scripts.seed_data` | ✅ 已存在，跳过 |
| 3. 重启后端服务 | `kill old_pid && nohup .venv/bin/python uvicorn ...` | ✅ PID 447680 启动，端口 8000 |
| 4. 重启前端服务 | `cd frontend && nohup npx vite --port 3000` | ✅ 端口 3000，200 OK |
| 5. 验证端点 | `curl` x4 | ✅ health=200, home=200, scripts=200, plans=200 |

## 回滚方案

- 如需回滚，kill 当前进程并恢复到旧版本代码

## 发布后验证

- FE Vitest: 50/50 passed (2.98s)
- FE Build: vue-tsc 无错误 + vite build 成功
- Browser E2E: 8/8 passed (36.4s)
- Delivery E2E: 4/4 passed (no mock API)
  - DEL-1: `/api/v1/health` → 200
  - DEL-2: `http://localhost:3000` → 200
  - DEL-3: `/api/v1/scripts` (无 auth) → 200 JSON (3 scripts)
  - DEL-4: `/api/v1/subscription/plans` (无 auth) → 200 JSON (3 plans)

## P1 缺陷修复确认

| # | 缺陷 | 修复状态 | PL 实测 |
|---|------|---------|---------|
| P1-1 | Browser E2E login 选择器 | ✅ 已修复 | `button[type="button"][class*="n-button--primary-type"]` |
| P1-2 | `GET /api/v1/scripts` 无 auth 返回 401 | ✅ 已修复 | 重启后端后 200 + JSON |
| P1-3 | `GET /api/v1/subscription/plans` 无 auth 返回 404 | ✅ 已修复 | 重启后端后 200 + JSON |

## 根本原因

Backend 进程是 7月18日启动的旧版本，Wave 1+2 代码修改未重启服务器。重启后两个 BE 接口正常。

## 发布结论

✅ 已发布 — CR-002 全部 19 项验收（9 P1 + 11 Bug）通过
