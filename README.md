# Project Template

这是公司内部新项目的通用工程脚手架标准。它提供可复制的项目结构，覆盖后端、前端、管理后台、部署、测试、文档、AI 协作规范和项目级 skills 目录。

本模板不绑定具体业务、语言或框架。新项目通常由 `standard-skills/init-standard-project/SKILL.md` 初始化，再通过 `workflow/` 状态机和 `skills/` 角色能力包推进。PRD 拆解属于 PM 角色职责，不再使用独立 PRD 同步 skill。

## 标准结构

```txt
.
├── AGENTS.md
├── PROJECT.md
├── README.md
├── .env.example
├── .gitignore
├── docker-compose.yml
├── backend/
├── frontend/
├── admin/
├── deploy/
├── scripts/
├── tools/
├── openspec/
├── skills/
├── workflow/
├── tests/
└── docs/
```

## 模块职责

- `backend/`：服务端 API、领域逻辑、数据访问、任务处理、外部系统集成。
- `frontend/`：面向最终用户的前端应用、页面交互、公开 API 调用。
- `admin/`：内部管理后台、运营操作、审核配置、权限敏感流程。
- `deploy/`：容器、反向代理、生产检查清单、环境部署模板。
- `scripts/`：开发、构建、测试、部署脚本入口。
- `tools/`：代码生成、迁移辅助、数据校验和自动化工具预留目录。
- `openspec/`：OpenSpec 规格主源；每个正式需求、行为变化、高风险修复或架构调整使用独立 change。
- `skills/`：项目专属 AI skills 目录，只放当前项目有效的角色能力、工作流规则和脚本引用。
- `workflow/`：状态机、权限、执行策略和以 CR 为单位的变更证据包。
- `tests/`：跨模块、契约、端到端和系统级测试。
- `PROJECT.md`：项目事实、目标、范围、模块清单、外部依赖、数据分级和负责人。
- `docs/`：架构、API、数据库、部署、测试、PRD 输入和 AI 协作规范。
- `openspec/specs/`：完成变更后归档的长期规格事实。
- `openspec/changes/<CR-ID>-<change-name>/`：当前需求的 proposal、specs、design 和 tasks 主源。

## 项目启动流程

OpenClaw 主会话读完标准库后，先完成群集初始化。群集初始化由 HR 创建或校验角色 workspace、校验既有角色 agent、通过 MSG / `sessions_send(agentId="<project_code>-<suffix>", message="...")` 向各角色发送启动消息、配置 MSG 必备通道和飞书可见性通道、等待全部启动角色 ack，并写入通信台账。`startup_order` 使用职责名；真实 `sessions_send.agentId` 必须先按 `aliases` / `agent_suffix` 算出 suffix，再拼成完整项目 agent ID，例如 `pl -> <project_code>-pl`、`ops -> <project_code>-op`。`main` 是主会话，不属于 HR 联通测试目标。HR 不得用 `sessions_spawn` 新建角色子代理。`required_agents` 必须覆盖 `startup_order` 的全部角色，不得只列核心角色。`<cluster_root>` 必须使用绝对路径，建议示例为 `/root/.openclaw/workspace/main/openclaw-clusters/main`，不得放在 HR 或其它角色 workspace 下。该阶段不复制 project-template、不创建 CR、不进入业务 workflow，不询问项目名称或目标路径；只允许按 project_code 写空骨架和 `PROJECT_WORKSPACE.md: pending`。

1. 群集初始化：使用公共标准库的 `standard-skills/cluster-assembly/SKILL.md`，从标准库 `project-template/` 读取角色模板和配置，创建或校验 OpenClaw 群集结构。HR 是群集创建者，先校验自己，再强制覆盖全部 required agent 的 runtime `AGENTS.md` / `SOUL.md` 模板；HR/CEO 是固有 agent，只覆盖模板、不创建项目专属 agent。然后按 `workflow/cluster.config.yaml` 校验其它角色的既有 agent 和 role workspace，通过 `sessions_send(agentId="<project_code>-<suffix>", message="...")` 发送启动消息、等待 ack 并写入台账。目标 agent 不存在或不可达时，群集必须保持 `not_ready`，不得用 `sessions_spawn` 替代。
2. 群集创建后必须立刻做联通自测。HR 是 `cluster_connectivity_self_test` 的唯一发起者，主会话不得替 HR 发起该测试。HR 向 `connectivity_test_targets`（10 个项目角色，不含固有角色 hr/ceo）通过 `sessions_send(agentId="<project_code>-<suffix>", message="cluster_connectivity_self_test", timeoutSeconds=15)` 发送联通测试消息；工具支持批量/并发时必须并发发出，不支持时才按短 timeout 串行发送。联通测试目标只能回复一行 `ACK cluster_connectivity_self_test <role>`，不得解释、复述规则、检查文件或输出计划。HR 等待 ack 或超时，写入 `<cluster_root>/runtime/delivery-ledger/cluster-connectivity.md`、`<cluster_root>/runtime/health/cluster-health.json` 和 `<cluster_root>/runtime/openclaw-process-status.md`。任一联通测试目标未 ack 时，群集状态必须是 `not_ready`，不得接 PRD，不得初始化业务项目 workspace；已创建的 `/root/<project_code>/workflow/` 空骨架不能作为继续推进依据。
3. 通信必须以 `sessions_send` 作为可靠底座，并尽可能同步飞书群聊。所有跨角色通知必须通过 `sessions_send(agentId="...", message="...", timeoutSeconds=...)` 等待 ack 或超时。PRD 前的群集联通证明只写 `<cluster_root>/runtime/delivery-ledger/cluster-connectivity.md`；PRD 后当前项目内的跨角色通信只写 `/root/<project_code>/workflow/changes/<CR-ID>/communication-ledger.md`。飞书失败要记录，但不能替代 `sessions_send` 投递结果。
4. 群集 ready 后，主会话必须引导用户去 PL 角色会话提交 PRD：`群集已就绪。请切换到 PL 角色会话，把 PRD、需求说明或产品草案发给 PL；PL 会接收 PRD 并继续项目初始化与 workflow。`
5. 接收 PRD 项目：用户在 PL 会话提交 PRD 后，由 PL 询问项目名称、项目代号和目标路径。项目名称用于 `--project-name`；项目代号就是 `<project_code>`，用于 `--project-code` 和 `/root/<project_code>` 目录名，不是项目展示名称；目标路径用于创建业务项目 workspace。
6. 项目初始化：PL 协调主会话/HR 使用公共标准库的 `standard-skills/init-standard-project/SKILL.md` 初始化项目目录。该步骤复制模板、生成角色 `AGENTS.md` 和模板来源记录，并把项目路径登记给已就绪的 OpenClaw 群集；不重新创建 OpenClaw agent，不绑定真实飞书凭据，不重新启动群集。
   登记后，每个角色 workspace 的 `PROJECT_WORKSPACE.md` 必须指向本业务项目 workspace。该文件至少包含 `project_root`、`source`、`updated_at` 三个字段；角色只能读取 `project_root` 字段作为项目写入根。角色 workspace 只是 runtime shell，不能保存项目中间产物；`workflow/`、`openspec/`、`docs/`、代码、测试、PRD、review、acceptance、tasks、proposal 和 design 只能写在本业务项目 workspace。
7. 项目目录就绪后，PL 运行：

```sh
python tools/bootstrap-openclaw-prd.py --project-root . --prd-file <prd.md>
```

如果 PRD 是聊天正文，PL 使用 `--prd-text` 或 stdin。
8. 自动入口创建 `workflow/changes/<CR-ID>/change.md`、`docs/prd/prd.md`、`workflow/state.md`、`review.md`、`openspec/changes/<CR-ID>-<change-name>/` 骨架，并生成 `skills/<role>/AGENTS.md`。workflow 从这里正式开始。
9. PL 不得把 PRD 自动入口视为全流程自动放行。自动入口只创建 CR、记录 PRD 和生成初始骨架；后续每个推进型阶段都必须先向用户展示交付物清单、关键结论、缺口和风险，取得用户明确同意后，才能运行 readiness 并推进。
10. PL 按 INIT / REQUIREMENT / DESIGN / DEVELOPMENT / QA / SECURITY / DEPLOY 顺序通知对应角色推进。PL 发出的每条跨角色通知都必须遵守 `workflow/communication.config.yaml`：MSG 必备、飞书尽量可见、必须 ack、失败记录。
11. 触发 PM 需求整理和拆解，并建立验收追踪：

```txt
使用 skills/pm/SKILL.md，生成 openspec proposal/specs，整理 docs/prd/prd.md 摘要，并把已确认需求事实同步到对应 docs 文档。
```

12. PM 只同步需求事实；架构、API、数据库、安全预审和重要决策由 `skills/architect/SKILL.md` 承接。
13. PM 在当前 OpenSpec change 的 `proposal.md` 和 `specs/**/spec.md` 写入规格差异，并把 P0/P1 验收项同步到 `acceptance.md`。进入 REQ_GATE ready 前必须列出所有 Q 编号、待确认项和关键假设，并写回 `展示状态`；非阻塞问题可记录暂缓，阻塞 MVP 或高风险问题必须等用户回答。用户的一句话确认不会直接让关口 passed，Agent 必须先运行 requirement gate readiness 检查。
14. Requirement gate readiness 通过且确认依据已记录后，PL 才能把需求关口写为 `passed` 并进入 DESIGN。
15. 设计阶段内由 Architect 输出 OpenSpec `design.md`，PL 组织拆分 OpenSpec `tasks.md`，QA 或实现 Agent 在 `test-plan.md` 写入测试先行计划。
16. Design gate readiness 通过且确认依据已记录后，PL 才能把设计关口写为 `passed` 并进入 DEVELOPMENT。
17. 实现 Agent 只能在 OpenSpec task 的允许写入范围内执行，写业务代码前运行 code readiness 检查，完成后写入 Agent Run Log、验证记录和文档同步记录。
18. 技术选型必须人参与确认。Architect 可以提出候选语言/框架、数据库、缓存/队列、云服务、对象存储、模型供应商、部署方式、构建/测试工具和第三方 SaaS，但未获确认前只能写为 `Proposed` 或 `待确认`，不得写入已采纳项目事实或开发任务依据。
19. 每个 DEV 任务完成后必须停下汇报；未记录用户明确继续确认前，不得开始下一个 DEV 任务。
20. QA 依据当前 CR 的 `acceptance.md` 和 `test-report.md` 验收，安全完成发布前审查，运维在 `deploy-plan.md` 准备发布计划并在部署后写入 `deploy-record.md`。
21. 团队只需要补充阻塞 MVP 或高风险的待确认信息；非阻塞问题由 PM/PL 记录暂缓依据后继续推进。
22. 根据已确认技术栈完善模块启动、测试、部署命令和 `.env.example`，不得提交真实密钥。
23. 如需额外项目专属 AI 能力，在 `skills/` 下新增独立 skill；不要复制公共标准库的 `standard-skills/`。

## 通用命令

```sh
./scripts/dev.sh backend
./scripts/dev.sh frontend
./scripts/dev.sh admin
./scripts/build.sh all
./scripts/test.sh all
./scripts/deploy.sh staging
```

脚本是统一入口模板。具体项目应在模块内提供 `package.json`、`Makefile` 或等价命令，并在模块 README 中说明。

## 文档约束

文档记录工程事实，不写宣传介绍。每类事实只维护一个主位置：

- 项目事实：`PROJECT.md`
- 架构和模块边界：`docs/architecture/architecture.md`
- API 契约：`docs/api/api.md`
- 数据库契约：`docs/database/database.md`
- 功能状态：`docs/status/feature-status.md`
- 运维和工程流程：`docs/operations/operations.md`
- 测试策略：`docs/testing/testing.md`
- 工具链接入：`docs/toolchain/toolchain.md`
- AI 协作：`docs/ai/ai-collaboration.md`
- 重要决策：`docs/decisions/decisions.md`
- PRD 输入：`docs/prd/prd.md`，仅在 PM 做需求整理、拆解或同步时读取
- 变更入口：`workflow/changes/<CR-ID>/change.md`
- 执行任务单：`openspec/changes/<change-name>/tasks.md`
- 测试先行计划：`workflow/changes/<CR-ID>/test-plan.md`
- 验收追踪：`workflow/changes/<CR-ID>/acceptance.md`
- LLM 执行策略：`workflow/execution.config.yaml`

## AI 协作

AI 进入项目后先读 `AGENTS.md`、`PROJECT.md` 和当前 OpenSpec change。`skills/` 仅承载当前项目自己的角色能力和工作流规则，公共标准库的 `standard-skills/` 不属于生成项目。OpenSpec proposal/specs 和 PRD 摘要由 `skills/pm/SKILL.md` 承担，架构、API、数据库和安全预审由 `skills/architect/SKILL.md` 承担。workflow 管理中的代码变更必须先有 OpenSpec task，LLM 不能自批关口或自行推进阶段。任何修改都必须先定位影响范围，再按模块边界做最小修改，最后同步必要文档并输出可审查的变更报告。
