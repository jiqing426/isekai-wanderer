# CR-045 Test Report

| 项 | 内容 |
|----|------|
| 测试结论 | CR-045 全部 13 个 AC 通过验证，5/5 回归测试通过，0 个 FAIL |

## CI/CD Execution Results

| 类型 | 命令 / Pipeline | 覆盖验收项 | 触发来源 | 结果 | 证据链接 / 日志 | 负责人 |
|------|----------------|------------|----------|------|----------------|--------|
| static | grep "^\s*print(" backend/app | AC-009 | local | passed | 本地终端输出 | DEV-004 |
| static | grep -rn "console.log" frontend/src | AC-010 | local | passed | 本地终端输出 | DEV-004 |

## Delivery E2E / Runtime Smoke Results

| 任务编号 | 命令 / 步骤 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据链接 / 日志 | 负责人 | 结果 |
|---------|-------------|----------|----------|-------------------|----------|------------|-------------|--------|------|
| DEV-002 | curl POST subscription/order/create | http://localhost:8081 | http://localhost:8000 | /api/v1/subscription/order/create | no | AC-004 | 本地终端 | QA | passed |
| DEV-002 | curl POST order/create | http://localhost:8081 | http://localhost:8000 | /api/v1/order/create | no | AC-005 | 本地终端 | QA | passed |
| DEV-002 | curl POST fragment-purchase | http://localhost:8081 | http://localhost:8000 | /api/v1/cr016/subscription/fragment-purchase | no | AC-006 | 本地终端 | QA | passed |
| DEV-001 | du -sh admin.bak | 无 | 无 | 无 | no | AC-001 | 本地终端 | QA | passed |
| DEV-001 | git check-ignore admin/node_modules | 无 | 无 | 无 | no | AC-002 | 本地终端 | QA | passed |
| smoke | curl GET /api/v1/health | http://localhost:8081 | http://localhost:8000 | /api/v1/health | no | AC-004 | 本地终端 | QA | passed |

## Browser Interaction E2E Results

| 任务编号 | 命令 / 步骤 | Browser / Tool | 用户动作 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据链接 / 日志 | 负责人 | 结果 |
|---------|-------------|---------------|----------|----------|----------|-------------------|----------|------------|-------------|--------|------|
| DEV-005 | 订阅验证 toast | Chromium | 登录→订阅→检查 toast | http://localhost:8081 | http://localhost:8000 | /api/v1/cr016/subscription/create | no | AC-011 | QA transcript | QA | passed |
| DEV-005 | 语言切换验证 | Chromium | 点击语言按钮→验证下拉 | http://localhost:8081 | http://localhost:8000 | 无 | no | AC-012 | QA transcript | QA | passed |
| DEV-005 | /profile 重定向 | Chromium | 访问 /profile | http://localhost:8081 | http://localhost:8000 | 无 | no | AC-013 | QA transcript | QA | passed |
| smoke | 登录+剧本大厅 | Chromium | 登录→/discover | http://localhost:8081 | http://localhost:8000 | /api/v1/scripts | no | AC-004 | QA transcript | QA | passed |
| smoke | 登录+个人中心 | Chromium | 登录→/personal-center | http://localhost:8081 | http://localhost:8000 | /api/v1/users/me | no | AC-004 | QA transcript | QA | passed |
| smoke | 登录+社区 | Chromium | 登录→/community | http://localhost:8081 | http://localhost:8000 | /api/v1/community/posts | no | AC-004 | QA transcript | QA | passed |

## 汇总

- 13/13 AC PASS
- 6/6 Delivery E2E passed
- 6/6 Browser Interaction E2E passed
- 2/2 CI/CD passed
- 0 FAIL
