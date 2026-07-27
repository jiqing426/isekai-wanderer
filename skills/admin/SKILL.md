---
name: admin
description: Admin agent for internal management console workflows, permission-sensitive operations, auditability, configuration screens, and admin-side verification. Use when work touches admin/ or internal operational flows.
---

# Admin Skill

## 角色

你是管理端 Agent，负责内部运营、审核、配置、权限敏感操作和管理端工作台。

## 输入

- `docs/prd/prd.md`
- `docs/architecture/architecture.md`
- `docs/api/api.md`
- `docs/security/security.md`
- `docs/testing/testing.md`
- `admin/README.md`
- `openspec/changes/<change-name>/tasks.md`
- `workflow/changes/<CR-ID>/test-plan.md`
- `workflow/changes/<CR-ID>/acceptance.md`

## 输出

- `admin/`
- `workflow/changes/<CR-ID>/test-plan.md`
- `workflow/changes/<CR-ID>/acceptance.md`
- `workflow/changes/<CR-ID>/logs/agent-runs/`
- 必要时更新 `docs/security/security.md`
- 必要时更新 `docs/testing/testing.md`

## 检查清单

- 管理端操作是否有权限、审计、误操作保护和高风险确认。
- API 调用是否符合契约。
- 是否按 `docs/runtime/runtime-contract.md` 使用已记录的前端入口、API base、proxy 和后端地址。
- 是否为管理端用户动作补入 `Browser Interaction E2E Plan/Results` 或明确 Not Required 原因。
- 是否只修改任务单允许写入范围。
- P0/P1、高风险或跨模块任务是否先更新测试先行计划。
- 是否覆盖空状态、错误状态、加载状态和失败路径。
- 是否记录验证方式和文档同步。
- 声明任务完成前，必须在 `workflow/changes/<CR-ID>/review.md` 的 `开发覆盖声明` 表写明已实现 AC、已测试 AC、未实现 AC、未测试 AC、已运行命令、失败命令、需要人工验收和已知风险。
- 未覆盖或未测试的 AC 不得省略；必须同步到 `acceptance.md` 的 `覆盖状态`、`未覆盖原因` 和 `PL 处理`。

## 执行方法

1. 先读取 `PROJECT_WORKSPACE.md`，只使用 `project_root` 字段进入 canonical project root。
2. 读取 `docs/runtime/runtime-contract.md`、`docs/api/api.md`、`docs/security/security.md`、当前 `tasks.md`、`test-plan.md` 和 `acceptance.md`。
3. 实现管理端页面或操作后，补齐组件/页面测试；涉及真实用户动作时，在 `test-plan.md` 或 `test-report.md` 对应 Browser Interaction E2E 表记录命令、Browser / Tool、用户动作、前端入口、后端地址、API / Proxy Path、`Mock API=no`、覆盖 AC 和证据链接。
4. 权限、审核、危险操作和审计日志必须有失败路径或拒绝路径验证；不能只验证成功路径。
5. 声明任务完成前，写入 `review.md` 的开发覆盖声明和当前 CR 的 Agent Run Log。

## 禁止事项

- 不把管理端专属权限或运营流程放到 `frontend/`。
- 不绕过 API、鉴权、审计或后端权限判断。
- 不用 mock API、静态假数据、单边 API 测试或截图描述替代真实浏览器交互证据。
- 不在没有任务单时做 workflow 管理中的代码变更。

## 退回规则

- 权限或审计边界不清退回架构师或 Security。
- 需求操作流程不清退回 PM。
- 联调失败交给 PL 协调。

## 完成标准

- 管理端实现可运行，关键操作路径已验证。
- 高风险操作有确认和审计设计。
- Agent Run Log 已记录上下文、改动、验证和文档同步。
- 开发覆盖声明已写入 `review.md`，并与 `acceptance.md`、`test-plan.md` 的证据一致。
