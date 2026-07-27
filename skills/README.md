# Skills

项目专属 AI skills 目录。这里放只对当前项目有效的 AI 工作流、上下文规则、检查步骤和脚本引用。

公共标准库里的 `standard-skills/` 只服务项目规范初始化和公共知识维护，不属于生成后的业务项目。

## 约定

- 每个角色使用独立子目录，并提供 `AGENTS.md` 和 `SKILL.md`。
- `AGENTS.md` 是 OpenClaw 运行主模板，必须包含角色身份、硬边界、执行方法和检查清单。`SKILL.md` 是标准库操作手册，会被追加到运行时 `AGENTS.md`，但不能替代 `AGENTS.md` 的硬边界。
- skill 引用脚本时，脚本应放在本 skill 子目录或 `../tools/`，并说明输入、输出和失败条件。
- 不写入真实密钥、token、证书、密码、客户数据或生产数据。

## 内置角色 skills

第一版采用"角色 skill + workflow 关口"，不再保留独立 PRD 同步 skill。

- `ceo/`：立项、优先级、投入边界和停止条件。
- `hr/`：角色、权限、Agent 能力缺口和 staffing。
- `pl/`：流程推进、计划、风险、关口、流转和交接。
- `pm/`：OpenSpec proposal/specs、PRD 摘要、需求拆解、验收标准和已确认需求事实同步。
- `architect/`：架构、API、数据模型、安全预审和重要决策。
- `frontend/`：前端页面、交互、状态和公开 API 对接。
- `backend/`：后端接口、业务逻辑、权限、数据访问和服务集成。
- `admin/`：管理端、内部运营、配置、权限敏感操作和审计。
- `ai-engineer/`：模型调用、Prompt、RAG、工具调用、评估和 AI 功能集成。
- `qa/`：验收、回归、边界场景和测试报告。
- `security/`：权限、敏感数据、依赖、攻击面和发布前安全结论。
- `ops/`：发布计划、部署、回滚、环境、监控和部署记录。

OpenClaw 默认入口：

```txt
把 PRD 文件或 PRD 正文发给 pl。PL 必须确认 canonical project root 已登记到角色 PROJECT_WORKSPACE.md，再在业务项目 workspace 内运行 tools/bootstrap-openclaw-prd.py 创建 CR，并按阶段触发各角色；用户不需要补充流程提示词。
```

PRD 自动入口只授权创建 CR 和初始材料，不授权阶段放行。推进型流转必须在 `review.md` 的 `阶段暂停确认` 中记录用户明确同意；不得用「PRD 自动入口授权」替代。

PM 手动触发指令（仅在需要单独补需求产物时使用）：

```txt
使用 skills/pm/SKILL.md，生成 openspec proposal/specs，整理 docs/prd/prd.md 摘要，并把已确认需求事实同步到对应 docs 文档。
```

## AGENTS.md、ROLE.md 与 SKILL.md

每个角色子目录包含以下文件：

| 文件 | 用途 |
| --- | --- |
| `AGENTS.md` | **OpenClaw 运行主模板**：身份、职责、硬边界、执行方法、检查清单、退回规则和完成标准。群集初始化会把它写入角色 workspace 根 `AGENTS.md`。 |
| `SKILL.md` | **标准库操作手册**：输入/输出、检查清单、设计/拆解/退回规则、完成标准。群集初始化会把它追加到运行时 `AGENTS.md`。 |
| `ROLE.md` | **维护参考**：角色身份摘要和边界摘要，不得用于覆盖 `AGENTS.md`。 |

`AGENTS.md` 是系统提示级运行文件，必须能独立约束运行时 agent。重要流程规则不能只写在 `SKILL.md` 或启动文档里。
`SKILL.md` 是操作级指南，定义该 Agent **怎么做**、**检查什么**、**工具和退回规则**。

运行时生成规则：`role workspace/AGENTS.md = skills/<role>/AGENTS.md + SKILL.md（去 front matter）`；`role workspace/SOUL.md = skills/<role>/AGENTS.md`。

### 当前角色模板

所有内置角色目录都应包含 `AGENTS.md`、`ROLE.md` 和 `SKILL.md`。运行关键规则必须先写入 `AGENTS.md`，再按需同步到 `SKILL.md` 或 `ROLE.md`。

## 执行约束

- 新需求、线上问题、返工和范围变更先进入当前 CR 的 `change.md`。
- 用户只给 PRD 时，由 PL 自动执行 `tools/bootstrap-openclaw-prd.py` 创建当前 CR，不要求用户手工写 `change.md`。
- 正式新需求、行为变化、高风险修复或架构调整必须进入独立 `openspec/changes/<CR-ID>-<change-name>/`。
- 需求拆解必须在当前 OpenSpec change 的 `proposal.md` 和 `specs/**/spec.md` 记录规格差异。
- 需求关口前必须主动向用户展示所有 Q 编号、待确认项和关键假设；阻塞 MVP 的 Open 待澄清问题未回答、未暂缓或未标记非阻塞前不得提交需求关口，非阻塞 Open 问题也必须记录暂缓依据。
- 人工关口确认必须先经过 `python tools/check-gate-readiness.py`；检查失败不得写 `passed` 或推进阶段。
- 代码变更必须有当前 OpenSpec change 的 `tasks.md` 任务单。
- P0/P1 验收项必须维护在当前 CR 的 `acceptance.md`。
- P0/P1、高风险或跨模块代码任务必须维护当前 CR 的 `test-plan.md`。
- Agent 执行后按 `workflow/agent-run-template.md` 在当前 CR 的 `logs/agent-runs/` 记录日志。
- LLM 不能自批关口，不能自行推进阶段为 `passed`。
