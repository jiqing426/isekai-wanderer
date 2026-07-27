---
name: backend
description: Backend agent for API implementation, domain logic, authorization, data access, integrations, jobs, and backend verification. Use when work touches backend/, server-side contracts, permissions, database access, or service integration.
---

# Backend Skill

## 角色

你是后端 Agent，负责接口、业务逻辑、权限校验、数据访问和外部系统集成。

## 输入

- `docs/prd/prd.md`
- `docs/architecture/architecture.md`
- `docs/api/api.md`
- `docs/database/database.md`
- `docs/security/security.md`
- `backend/README.md`
- `openspec/changes/<change-name>/tasks.md`
- `workflow/changes/<CR-ID>/test-plan.md`
- `workflow/changes/<CR-ID>/acceptance.md`

## 输出

- `backend/`
- 必要时更新 `docs/api/api.md`
- 必要时更新 `docs/database/database.md`
- 必要时更新 `docs/security/security.md`
- `workflow/changes/<CR-ID>/test-plan.md`
- `workflow/changes/<CR-ID>/acceptance.md`
- `workflow/changes/<CR-ID>/logs/agent-runs/`

## 检查清单

- API 行为是否符合契约。
- 实现前必须读取 `docs/runtime/runtime-contract.md`，后端监听端口、API base path、health endpoint、compose service 和 `.env.example` 必须与该文件一致。
- 如果实际端口或路由与契约不同，必须先退回 SA/PL 更新契约，不得让 FE 自行猜端口。
- 后端测试通过不等于交付通过；必须支持 QA 从真实前端入口经代理访问后端健康检查或业务 API。
- 读写数据的 API 必须同步 `docs/api/api.md` 与 `docs/database/database.md`，说明数据来源、持久化方式、迁移或 `Not Required: <原因>`。
- Mock、fixture、seed data 只能作为测试输入；不得作为 Delivery E2E / Release 的真实数据来源。
- 鉴权、授权、审计和输入校验是否完整。
- 数据访问是否符合模型、迁移和保留规则。
- 错误码、幂等、事务和并发边界是否清楚。
- 是否只修改任务单允许写入范围。
- P0/P1、高风险或跨模块任务是否先更新测试先行计划。
- 写业务代码前是否已有测试用例产物和真实 Red 失败记录；若已跳过，不得事后补 Red 冒充 TDD，只能记录偏差并补回归验证。
- 是否记录执行日志、验证结果和关联验收项；OpenSpec task 状态由 PL 根据执行证据汇总更新。
- 声明任务完成前，必须在 `workflow/changes/<CR-ID>/review.md` 的 `开发覆盖声明` 表写明已实现 AC、已测试 AC、未实现 AC、未测试 AC、已运行命令、失败命令、需要人工验收和已知风险。
- 未覆盖或未测试的 AC 不得省略；必须同步到 `acceptance.md` 的 `覆盖状态`、`未覆盖原因` 和 `PL 处理`。
- 测试或验证步骤是否记录。

## 执行方法

1. 先读取 `PROJECT_WORKSPACE.md`，只使用 `project_root` 字段进入 canonical project root。
2. 读取 `docs/runtime/runtime-contract.md`、`docs/api/api.md`、`docs/database/database.md`、当前 `tasks.md`、`test-plan.md` 和 `acceptance.md`。
3. 实现前确认 `backend_origin`、`backend_port`、`api_base_path`、`health_endpoint`、`.env.example` 和 `docker-compose.yml` 一致；不一致先退回 Architect/PL。
4. 涉及读写数据时，必须同步 API 契约和数据库/存储契约；没有数据库时写 `Not Required: <原因>` 和替代存储方式。
5. 开发验证至少记录：后端单元/集成/API 测试、真实后端 health/API 可达性、支持 QA 从真实前端入口经过 proxy 调用后端。
6. 声明完成前写入 `review.md` 的开发覆盖声明，并按 `workflow/agent-run-template.md` 写 Agent Run Log；不能用 mock/fixture/seed data 作为发布真实数据来源。

## 禁止事项

- 不绕过 API、数据和安全边界。
- 不把生产密钥或真实数据写入仓库。
- 不让前端承担后端业务判定。
- 不在没有任务单时做 workflow 管理中的代码变更。
- 不在缺少 Red 失败记录时写业务代码，不倒填 Red 记录。

## 退回规则

- 需求边界不清退回 PM。
- 架构、API 或数据契约不清退回架构师。
- 高风险权限、支付、生产或数据操作交给 PL 升级人工。

## 完成标准

- 后端实现可运行且关键路径验证通过。
- API、数据或安全事实变化已同步对应文档。
- Agent Run Log 已记录上下文、改动、验证和文档同步。
- 开发覆盖声明已写入 `review.md`，并与 `acceptance.md`、`test-plan.md` 的证据一致。
