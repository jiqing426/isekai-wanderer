# CR-045 Test Plan

## 测试范围

CR-045 是工程清理变更，测试重点是**回归验证**——确保清理和修复没有破坏现有功能。

## Test-First Scope

- AC-001~003: 静态验证（文件不存在 + gitignore + docker cache）
- AC-004~006: API 端点删除验证（grep + curl 404）
- AC-007~008: 组件删除验证（grep + 文件不存在）
- AC-009~010: 代码质量验证（grep print/console.log 计数）
- AC-011~013: E2E 浏览器验证（toast/语言下拉/重定向）

## Test Case Artifacts

| 任务编号 | 测试用例产物 | 覆盖验收项 | 状态 |
|----------|-------------|------------|------|
| DEV-001 | du -sh admin.bak 返回不存在 | AC-001 | Ready |
| DEV-001 | git check-ignore admin/node_modules | AC-002 | Ready |
| DEV-001 | docker system df 回收量减少 | AC-003 | Ready |
| DEV-002 | grep create_order subscription.py 返回空 | AC-004 | Ready |
| DEV-002 | grep create_order user_subscription.py 返回空 | AC-005 | Ready |
| DEV-002 | grep fragment-purchase 返回空 | AC-006 | Ready |
| DEV-003 | grep QuotaExhaustedModal 返回空 | AC-007 | Ready |
| DEV-003 | ls QuotaExhaustedModal.vue 不存在 | AC-008 | Ready |
| DEV-004 | grep "^\s*print(" backend/app 返回 0 | AC-009 | Ready |
| DEV-004 | console.log count < 5 | AC-010 | Ready |
| DEV-005 | E2E: 订阅后 1 条 toast | AC-011 | Ready |
| DEV-005 | E2E: 语言下拉正常 | AC-012 | Ready |
| DEV-005 | E2E: /profile → /settings | AC-013 | Ready |

## Red Failure Records

| AC | Red 验证 | 状态 |
|----|----------|------|
| AC-004~006 | 开发前 curl 3 个端点返回 200（存在） | 待验证 |
| AC-009 | 开发前 grep print() 返回 18 | 待验证 |
| AC-010 | 开发前 console.log 数量 23 | 待验证 |

Red 记录在 DEVELOPMENT 阶段写代码前补充。

## CI/CD Evidence Plan

| 阶段 | 触发时机 | 命令 / Pipeline | 覆盖验收项 | 负责人 | 记录位置 | 状态 |
|------|----------|----------------|------------|--------|----------|------|
| static | pre-commit | `grep -rn "^\s*print(" backend/app/ --include="*.py"` 返回 0 行 | AC-009 | DEV-004 | CI log | Ready |
| static | pre-commit | `grep -rn "console.log" frontend/src/ --include="*.vue" --include="*.ts"` 返回 < 5 行 | AC-010 | DEV-004 | CI log | Ready |
| api | pre-merge | `curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/api/v1/subscription/order/create` == 404 | AC-004,AC-005,AC-006 | QA | CI log | Ready |

## Delivery E2E / Runtime Smoke Plan

| 任务编号 | 命令 / 步骤 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
|---------|-------------|----------|----------|-------------------|----------|------------|-------------|------|
| DEV-002 | `curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8081/api/v1/subscription/order/create` | http://localhost:8081 | http://localhost:8000 | /api/v1/subscription/order/create | no | AC-004 | test-report.md | Ready |
| DEV-002 | `curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8081/api/v1/order/create` | http://localhost:8081 | http://localhost:8000 | /api/v1/order/create | no | AC-005 | test-report.md | Ready |
| DEV-002 | `curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8081/api/v1/cr016/subscription/fragment-purchase` | http://localhost:8081 | http://localhost:8000 | /api/v1/cr016/subscription/fragment-purchase | no | AC-006 | test-report.md | Ready |
| DEV-001 | `du -sh admin.bak 2>&1` 返回不存在 | 无 | 无 | 无 | no | AC-001 | test-report.md | Ready |
| DEV-001 | `git check-ignore admin/node_modules` | 无 | 无 | 无 | no | AC-002 | test-report.md | Ready |
| smoke | `curl -s http://localhost:8081/api/v1/health` 返回 200 | http://localhost:8081 | http://localhost:8000 | /api/v1/health | no | AC-004 | test-report.md | Ready |

## Browser Interaction E2E Plan

| 任务编号 | 命令 / 步骤 | Browser / Tool | 用户动作 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
|---------|-------------|---------------|----------|----------|----------|-------------------|----------|------------|-------------|------|
| DEV-005 | 浏览器登录→订阅操作→验证 toast 数量 | Chromium | 登录→订阅→检查 toast 只显示 1 条 | http://localhost:8081 | http://localhost:8000 | /api/v1/cr016/subscription/create | no | AC-011 | test-report.md | Ready |
| DEV-005 | 浏览器点击语言切换→验证下拉 | Chromium | 点击语言按钮→验证下拉选项出现 | http://localhost:8081 | http://localhost:8000 | 无 | no | AC-012 | test-report.md | Ready |
| DEV-005 | 浏览器访问 /profile→验证重定向 | Chromium | 直接访问 /profile→验证跳转 /settings | http://localhost:8081 | http://localhost:8000 | 无 | no | AC-013 | test-report.md | Ready |
| smoke | 浏览器登录→访问社区→验证帖子 | Chromium | 登录→访问 /community→验证帖子显示 | http://localhost:8081 | http://localhost:8000 | /api/v1/community/posts | no | AC-004 | test-report.md | Ready |
| smoke | 浏览器登录→访问剧本大厅→验证剧本 | Chromium | 登录→访问 /discover→验证 3 个剧本 | http://localhost:8081 | http://localhost:8000 | /api/v1/scripts | no | AC-004 | test-report.md | Ready |
| smoke | 浏览器登录→访问个人中心→验证数据 | Chromium | 登录→访问 /personal-center→验证会员/碎片 | http://localhost:8081 | http://localhost:8000 | /api/v1/users/me | no | AC-004 | test-report.md | Ready |
| smoke | 浏览器登录→访问设置→验证 4 tab | Chromium | 登录→访问 /settings→验证 4 个 tab | http://localhost:8081 | http://localhost:8000 | /api/v1/users/me | no | AC-004 | test-report.md | Ready |

## AC 覆盖矩阵

| AC | 验证方式 | 负责人 |
|----|----------|--------|
| AC-001 | du -sh admin.bak → 不存在 | DEV-001 |
| AC-002 | git check-ignore admin/node_modules | DEV-001 |
| AC-003 | docker system df → reclaimable 减少 | DEV-001 |
| AC-004 | grep create_order subscription.py → 空 | DEV-002 |
| AC-005 | grep create_order user_subscription.py → 空 | DEV-002 |
| AC-006 | grep fragment-purchase → 空 | DEV-002 |
| AC-007 | grep QuotaExhaustedModal → 空 | DEV-003 |
| AC-008 | ls QuotaExhaustedModal.vue → 不存在 | DEV-003 |
| AC-009 | grep "^\s*print(" backend/app → 0 | DEV-004 |
| AC-010 | console.log count < 5 | DEV-004 |
| AC-011 | E2E: 订阅后 1 条 toast | QA |
| AC-012 | E2E: 语言下拉正常 | QA |
| AC-013 | E2E: /profile → /settings | QA |
