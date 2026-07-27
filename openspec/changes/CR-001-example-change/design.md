# Design

## 设计概览

- 待填写。

## 技术方案

- 待填写。

## 技术选型

> **关键规则：技术选型必须有人工确认，Agent 不得自行决策。状态栏必须填写 Confirmed（用户/PL 确认）或 Deferred（后续阶段决定），禁止全部 Proposed 就推进 DESIGN_GATE。**

| 选型项 | 方案 | 状态 | 确认人 | 确认时间 |
| --- | --- | --- | --- | --- |
| 语言 / 框架 | 待确认 | Proposed | — | — |
| 数据库 / 存储 | 待确认 | Proposed | — | — |
| 缓存 / 队列 | 待确认 | Proposed | — | — |
| 云服务 / 部署方式 | 待确认 | Proposed | — | — |
| 模型供应商 / AI 工具 | 待确认 | Proposed | — | — |

**状态说明**：
- `Confirmed`：用户或 PL 已确认，必须标注确认人和确认时间
- `Deferred`：延期到后续阶段决定，必须在风险栏说明影响
- `Proposed`：仅 Agent 建议，**不能推进 DESIGN_GATE**，必须有人工确认

## API / 数据 / 安全 / 部署影响

| 领域 | 决策 | 目标文档 |
| --- | --- | --- |
| API | 待确认 | `docs/api/api.md` |
| Data | 待确认 | `docs/database/database.md` |
| Security | 待确认 | `docs/security/security.md` |
| Deployment | 待确认 | `docs/operations/operations.md` |

## 文档同步

| 目标文档 | 状态 | 同步说明 |
| --- | --- | --- |
| `docs/architecture/architecture.md` | Pending | 待确认设计后同步模块边界和核心流程。 |
| `docs/api/api.md` | Pending | 待确认是否有 API 契约变化。 |
| `docs/database/database.md` | Pending | 待确认是否有数据模型或迁移变化。 |
| `docs/security/security.md` | Pending | 待确认权限、敏感数据和审计影响。 |
| `docs/decisions/decisions.md` | Pending | 待确认是否产生重要取舍或不可逆决策。 |

## 风险和回滚

- 待填写。
