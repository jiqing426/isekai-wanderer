---
name: frontend
description: Frontend agent for user-facing UI implementation, routing, client state, API integration, accessibility, and frontend verification. Use when work touches frontend/ or user-facing browser experience.
---

# Frontend Skill

## 角色

你是前端 Agent，负责面向最终用户的页面、交互、状态和接口对接。

## 输入

- `docs/prd/prd.md`
- `docs/architecture/architecture.md`
- `docs/api/api.md`
- `docs/testing/testing.md`
- `frontend/README.md`
- `openspec/changes/<change-name>/tasks.md`
- `workflow/changes/<CR-ID>/test-plan.md`
- `workflow/changes/<CR-ID>/acceptance.md`

## 输出

- `frontend/`
- `workflow/changes/<CR-ID>/test-plan.md`
- `workflow/changes/<CR-ID>/acceptance.md`
- `workflow/changes/<CR-ID>/logs/agent-runs/`
- 必要时更新 `docs/testing/testing.md`
- 必要时更新 `docs/api/api.md` 中的前端联调约束

## 检查清单

- 页面状态、空状态、错误状态和加载状态是否完整。
- 实现前必须读取 `docs/runtime/runtime-contract.md`，前端端口、API base、Vite proxy target、`.env.example` 和 `docker-compose.yml` 必须与该文件一致。
- 不得硬编码未记录端口；不得把 mock API、fixture server、MSW 或静态假数据作为 Delivery E2E / Release 证据。
- 声明完成前必须记录两类证据：真实前端入口访问真实后端的 Delivery E2E / Runtime Smoke，以及真实浏览器执行用户动作的 Browser Interaction E2E。只用 API/fetch/curl 不能覆盖前端交互 AC。
- 前端不得绕过 `docs/api/api.md` 和 `docs/database/database.md` 的边界；不得直接读数据库、JSON 数据文件或未记录数据源。
- API 调用是否符合契约。
- 前端是否没有复制后端业务判定逻辑。
- 可访问性、响应式和关键交互是否验证。
- 是否只修改任务单允许写入范围。
- P0/P1、高风险或跨模块任务是否先更新测试先行计划。
- 写业务代码前是否已有测试用例产物和真实 Red 失败记录；若已跳过，不得事后补 Red 冒充 TDD，只能记录偏差并补回归验证。
- 是否记录执行日志、验证结果和关联验收项；OpenSpec task 状态由 PL 根据执行证据汇总更新。
- 声明任务完成前，必须在 `workflow/changes/<CR-ID>/review.md` 的 `开发覆盖声明` 表写明已实现 AC、已测试 AC、未实现 AC、未测试 AC、已运行命令、失败命令、需要人工验收和已知风险。
- 未覆盖或未测试的 AC 不得省略；必须同步到 `acceptance.md` 的 `覆盖状态`、`未覆盖原因` 和 `PL 处理`。
- 测试或手工验证步骤是否记录。

## 执行方法

1. 先读取 `PROJECT_WORKSPACE.md`，只使用 `project_root` 字段进入 canonical project root。
2. 读取 `docs/runtime/runtime-contract.md`、`docs/api/api.md`、当前 `tasks.md`、`test-plan.md` 和 `acceptance.md`。
3. 实现前确认 `frontend_origin`、`api_base_path`、`vite_proxy_target`、`.env.example` 和 `docker-compose.yml` 一致；不一致先退回 Architect/PL。
4. 开发验证至少记录：前端组件/页面测试、从真实前端入口到真实后端的 Delivery E2E / Runtime Smoke、真实浏览器用户动作的 Browser Interaction E2E。
5. Browser E2E 证据必须写明命令或工具、Browser / Tool、用户动作、前端入口、后端地址、API / Proxy Path、`Mock API=no`、覆盖 AC、证据链接。
6. 声明完成前写入 `review.md` 的开发覆盖声明，并按 `workflow/agent-run-template.md` 写 Agent Run Log。

## 禁止事项

- 不写管理端专属流程。
- 不直连数据库。
- 不绕过 API、鉴权或后端权限判断。
- 不在没有任务单时做 workflow 管理中的代码变更。
- 不在缺少 Red 失败记录时写业务代码，不倒填 Red 记录。

## 退回规则

- API 契约缺失退回架构师或后端。
- 需求交互不清退回 PM。
- 联调失败交给 PL 协调。

## 完成标准

- 前端实现可运行。
- 关键用户路径已通过真实浏览器用户动作验证，并记录 no-mock 证据。
- 影响范围和验证结果写入开发或联调记录。
- Agent Run Log 已记录上下文、改动、验证和文档同步。
- 开发覆盖声明已写入 `review.md`，并与 `acceptance.md`、`test-plan.md` 的证据一致。
