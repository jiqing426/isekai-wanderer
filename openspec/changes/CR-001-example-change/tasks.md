# Tasks

OpenSpec `tasks.md` 是本次变更的实现任务主源。workflow 文件只记录测试、安全、部署、审批和执行证据，不维护第二套实现任务列表。

## 实现任务

| 任务编号 | 阶段 | 负责人 Agent | 关联验收项 | Consumers | 不覆盖验收项 | 允许写入范围 | 测试用例产物 | 验证方式 | 回滚 / 撤销方案 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEV-001 | DEVELOPMENT | 待填写 | AC-001 | 待填写 | 无 | 待填写 | `workflow/changes/CR-001/test-plan.md` | 待填写 | 待填写 | Pending |

## 依赖顺序

- [ ] DEV-001 待填写。

## 任务规则

- 每个任务必须关联至少一个 Requirement、Scenario 或 AC 编号。
- 每个涉及 API、页面、管理端或用户动作的任务必须填写 `Consumers`，明确哪个页面、组件、菜单、按钮、调用方或脚本会消费这项能力。
- 每个任务必须显式写明覆盖哪些 AC；不覆盖的 AC 必须列在 `不覆盖验收项` 并说明原因，不能省略。
- `允许写入范围` 必须足够具体，让 `tools/check-workflow-readiness.py` 能匹配目标文件。
- 在 `workflow/changes/<CR-ID>/test-plan.md` 补齐测试用例产物和 Red 失败记录前，不得写业务代码。
- 声明任务完成前，实现 Agent 必须在 `workflow/changes/<CR-ID>/review.md` 的 `开发覆盖声明` 表写明已实现、已测试、未实现和未测试的 AC。
- Green 记录、测试报告、安全审查、部署记录和 Agent 执行日志都留在 `workflow/changes/<CR-ID>/`。

## E2E 和跨模块测试约定

- **E2E 测试文件必须放在 `tests/e2e/` 目录**，不得放入 `backend/__tests__/e2e/` 或任何模块测试目录。
- 冒烟级 E2E：`tests/e2e/smoke.test.ts`
- 用户旅程 E2E：`tests/e2e/user-journey.test.ts`
- E2E 测试的端口必须通过环境变量配置（`APP_BASE`、`API_BASE`），禁止硬编码。
- E2E 测试必须覆盖真实前端交互（打开浏览器、点击、拖拽），不仅 API 调用。
- 涉及 Docker 部署的任务必须包含 `Dockerfile` 的创建，不得只写 `docker-compose.yml` 而不写 Dockerfile。
