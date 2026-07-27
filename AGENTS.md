# AGENTS

AI 入口文件。这里只说明从哪里开始，不承载完整规范。

## 先读这些

- 详细 AI 协作规则以 `docs/ai/ai-collaboration.md` 为准。
- 项目事实、范围、模块清单、外部依赖和负责人以 `PROJECT.md` 为准。
- 需求规格主源以 `openspec/` 为准；每个正式需求、行为变化、高风险修复或架构调整都应先进入独立 `openspec/changes/<CR-ID>-<change-name>/`。
- 项目专属 AI skills 放在 `skills/`；它们不能覆盖本文件的硬边界。

## 角色机器人

- 每个角色目录 `skills/<role>/` 下至少有三个文件：`AGENTS.md` 是 OpenClaw 运行主模板，必须包含身份、硬边界、执行方法和检查清单；`SKILL.md` 是标准库操作手册，会被群集初始化追加进运行时 `AGENTS.md`；`ROLE.md` 是维护参考和角色身份摘要，不得覆盖 `AGENTS.md`。
- OpenClaw 预设机器人运行时读取自己 role workspace 根目录的 `AGENTS.md`。该文件由群集初始化从 `skills/<role>/AGENTS.md` + `skills/<role>/SKILL.md` 合并生成；`SOUL.md` 由 `skills/<role>/AGENTS.md` 生成；`.openclaw-agent/AGENTS.md` 和 `.openclaw-agent/SOUL.md` 是兼容副本。HR/CEO 是固有 agent，不随项目创建，但每次群集初始化仍必须强制覆盖这四个模板文件。任何脚本不得用 `ROLE.md` 回写或覆盖 `skills/<role>/AGENTS.md`。
- HR 是群集创建者。OpenClaw / 龙虾主会话读取标准库后应先完成群集初始化：由 HR 按 `workflow/cluster.config.yaml` 创建或校验角色 workspace、agent/binding 计划和通信通道，校验其它角色的既有 agent，通过 MSG / `sessions_send(agentId="<project_code>-<suffix>", message="...")` 发送启动消息、等待 ack、写入通信台账。`startup_order` 使用职责名；真实 `sessions_send.agentId` 必须先按 `aliases` / `agent_suffix` 算出 suffix，再拼成完整项目 agent ID，例如 `pl -> <project_code>-pl`、`ops -> <project_code>-op`。`main` 是主会话，不属于 HR 联通测试目标。HR 不得用 `sessions_spawn` 新建角色子代理。群集初始化不依赖业务项目路径。
- 机器人之间不能只用一句 `@<role>` 视为通知成功。跨角色通信必须遵守 `workflow/communication.config.yaml`：`sessions_send` 是可靠投递底座，本文简称 MSG；飞书群聊是尽可能保证的人类可见协同界面，并且必须记录通信台账。
- 调度规则与跨角色路由见 `skills/pl/ROLE.md` 的「各阶段职责与必须产出物」表；具体执行规则见 `skills/pl/SKILL.md`。
- PL 自己 Owner 的阶段（INTAKE / TRIAGE / REQ_GATE / DESIGN_GATE / INTEGRATION / RELEASE_GATE / FEEDBACK）必须按 `skills/pl/SKILL.md` 的「各阶段必须产出物」段在 `review.md` 写完整审查记录，不得只写一句结论就过。
- 跨阶段交付必须遵守 `workflow/handoff-contracts.md`、`workflow/traceability-chain.md` 和 `workflow/failure-backtrace.md`：上游必须把下游执行所需的范围、编号、运行契约、测试证据和放行条件交清；下游不得猜测缺失内容；发现结果问题时必须按失败倒查链回溯到最早断链环节。

## 集群启动入口

- 路径门禁：如果当前标准库或模板路径位于 OpenClaw 上传/拖拽产生的 `inbound/`、`*_extracted/` 临时导入层，不得直接作为标准库根、群集 source root 或业务项目根。必须先把标准库安装/复制到稳定短路径，例如 `/root/.openclaw/workspace/main/standards/ai_base_common`。`<cluster_root>` 必须使用绝对路径，建议示例为 `/root/.openclaw/workspace/main/openclaw-clusters/main`，不得放在 HR 或其它角色 workspace 下。业务项目根必须创建在 `/root/<project_code>`，不得放在 OpenClaw workspace 内部；`<project_code>` 是项目代号和目录名，不是项目展示名称。
- 事实源硬边界：业务项目 workspace 是唯一项目事实源。角色 workspace 只是 OpenClaw 运行壳，只能放 `.openclaw-agent/`、`PROJECT_WORKSPACE.md`、运行日志或临时执行元数据。任何角色不得在自己的 workspace 下创建或修改 `workflow/`、`openspec/`、`docs/`、代码目录、测试目录、`PROJECT.md` 或 `.env*`。
- 所有角色写项目文件前必须先读取自己 role workspace 下的 `PROJECT_WORKSPACE.md`，解析 canonical project root，并只在该项目根目录下写入规范路径。`PROJECT_WORKSPACE.md` 必须至少包含 `project_root`、`source`、`updated_at` 三个字段；角色只能读取 `project_root` 字段作为项目写入根。`PROJECT_WORKSPACE.md` 缺失、值为 `pending` 或项目根不可访问时，必须停止并退回 PL/HR 登记项目路径。
- 角色 workspace 中误生成的项目文件不得作为事实源。发现后必须报告 PL，并把内容迁移或重新生成到 canonical project root；PL 审查只读取 canonical project root。
- 第一步是群集初始化：OpenClaw 主会话读完标准库后，使用公共标准库的 `standard-skills/cluster-assembly/SKILL.md` 从标准库模板创建或校验 OpenClaw 群集结构。HR 校验自己可通信后，先把全部 required agent 的 runtime `AGENTS.md` / `SOUL.md` 覆盖为当前标准库模板；固有 HR/CEO 只覆盖模板、不创建新 agent。随后再校验 `startup_order` 中各职责角色的既有 agent 与 role workspace，并通过 MSG / `sessions_send(agentId="<project_code>-<suffix>", message="...")` 发送启动消息。目标 agent 不存在或不可达时，必须记录缺口并保持 `not_ready`，不得用 `sessions_spawn` 替代。
- 群集创建完成后，HR 必须立即执行联通自测：`required_agents` 必须覆盖 `startup_order` 的全部项目角色，`connectivity_test_targets` 必须是 10 个项目角色且不得包含固有角色 hr/ceo。HR 是 `cluster_connectivity_self_test` 的唯一发起者，主会话不得替 HR 发起该测试。HR 向联通测试目标通过 `sessions_send(agentId="<project_code>-<suffix>", message="cluster_connectivity_self_test", timeoutSeconds=15)` 发送联通测试消息；工具支持批量/并发时必须并发发出，不支持时才按短 timeout 串行发送。联通测试目标只能回复一行 `ACK cluster_connectivity_self_test <role>`，不得解释、复述规则、检查文件或输出计划。HR 等待 ack 或超时，写入 `<cluster_root>/runtime/delivery-ledger/cluster-connectivity.md`、`<cluster_root>/runtime/health/cluster-health.json` 和 `<cluster_root>/runtime/openclaw-process-status.md`。任一联通测试目标未 ack，群集状态必须为 `not_ready`，不得接收 PRD，不得初始化业务项目 workspace，不得进入 workflow；已创建的 `/root/<project_code>/workflow/` 空骨架不能作为继续推进依据。全部联通测试目标为 `acked_msg` 后，HR 必须同步更新 health：`connectivity_self_test_status=passed`、`cluster_status=ready`、`prd_intake_allowed=true`。
- 台账边界必须分清：`<cluster_root>/runtime/delivery-ledger/cluster-connectivity.md` 只记录 PRD 前的群集联通证明；`/root/<project_code>/workflow/changes/<CR-ID>/communication-ledger.md` 只记录 PRD 后当前项目内的跨角色通信。
- 群集 ready 后，主会话必须引导用户去 PL 角色会话提交 PRD，不得自己接收并处理 PRD。推荐话术：`群集已就绪。请切换到 PL 角色会话，把 PRD、需求说明或产品草案发给 PL；PL 会接收 PRD 并继续项目初始化与 workflow。`
- 第二步是接收 PRD 项目：用户在 PL 会话提交 PRD、需求说明或产品草案后，由 PL 询问项目名称、项目代号和目标路径。项目名称用于 `--project-name`，项目代号用于 `--project-code` 和目录名，目标路径用于创建业务项目 workspace。
- 项目初始由公共标准库的 `standard-skills/init-standard-project/SKILL.md` 完成，只生成项目目录，并把项目路径登记给已就绪的 OpenClaw 群集；不重新创建 OpenClaw 群集。PL 负责触发和验收该步骤，不亲自创建 OpenClaw 群集。
- HR 必须确认全部启动角色已 ack；当前阶段必需角色未 ack 时，流程不得继续。
- `sessions_send` 是必须存在的可靠通信底座，飞书群聊是尽可能保证的人类可见协同界面。任何真实密钥、飞书 token、webhook 或 chat secret 不得写入仓库。
- `角色启动消息` 只表示可审计通信动作，不表示创建或启动新会话：校验既有 OpenClaw agent session，绑定该角色 workspace，用 `skills/<role>/AGENTS.md` + `skills/<role>/SKILL.md` 强制覆盖 role workspace 根目录 `AGENTS.md`，用 `skills/<role>/AGENTS.md` 强制覆盖 `SOUL.md`，再通过 `sessions_send(agentId="<project_code>-<suffix>", message="...", timeoutSeconds=...)` 发送启动消息，等待 ack 或超时，并把 `sessions_send` 与飞书同步结果写入通信台账。目标 agent 不存在或不可达时，不得 `sessions_spawn` 替代；不得用 `ROLE.md` 生成运行时 `AGENTS.md`。
- 协议违规必须停止：直接从 `inbound/*_extracted/project-template` 初始化群集或项目、把业务项目根建在 `inbound/` 或 `*_extracted/` 下、`required_agents` 未覆盖全部 `startup_order`、群集 ready 前接收 PRD、主会话绕过 PL 直接接 PRD、PRD 前询问项目名称/目标路径、PRD 前创建业务项目路径、跳过联通自测、只更新联通台账不更新 health、把口头回复当 MSG ack、未写台账却声称通知成功、任一启动角色未 ack 仍推进，均不得继续执行。
- 写入位置违规必须停止：角色把 `proposal.md`、`tasks.md`、`review.md`、PRD、acceptance、test-plan、docs 或代码写在自己的 role workspace 下，均视为无效交付物；必须重写到 canonical project root。

## PRD 自动入口

- 用户把 PRD、需求说明或产品草案发给 PL 时，PL 默认视为一次新的工作流输入；不得要求用户再提供流程提示词。若业务项目路径尚未创建，PL 先询问项目名称、项目代号和目标路径，再协调主会话/HR 完成项目初始化。
- PL 首先确认 HR 已完成群集初始化和 required agents ack。未完成时，PL 退回 HR 处理群集就绪，不自行创建群集。
- PL 运行或等价执行 `python tools/bootstrap-openclaw-prd.py --project-root <project-workspace> --prd-file <prd-file>`，把 PRD 写入 `workflow/changes/<CR-ID>/change.md`、`docs/prd/prd.md`，刷新 `workflow/state.md`，生成角色 `AGENTS.md`。
- 如果 PRD 是聊天正文而不是文件，PL 可以先把正文记录进当前 CR 的 `change.md`，或用 `--prd-text` / stdin 调用自动入口工具。
- 自动入口完成后，PL 停在 INTAKE：先向用户展示交付物清单、关键结论、缺口和风险，取得用户明确同意后，才能运行阶段流转检查并进入 INIT 阶段。
- 每次触发角色都必须记录通信结果：MSG 是否发送并 ack、飞书是否同步可见、是否阻塞当前阶段。
- 不得用“PRD 自动入口授权”替代阶段放行。PRD 自动入口只授权创建 CR 和初始材料，不授权通过 INIT、TRIAGE、REQ_GATE、DESIGN_GATE、RELEASE_GATE、DEPLOY 或 FEEDBACK。

## 关键提醒

- workflow 管理的每个阶段完成后必须暂停：先补齐交付物，在聊天中展示交付物清单、关键结论、缺口和风险，明确等用户确认后，才能运行对应 readiness 并推进。用户确认前，不得在 `review.md` 或 `workflow/state.md` 写入 `submitted`、`passed`、`approved`、`delivered` 等推进性结论。
- 必须人参与放行的关键点至少包括：INTAKE→INIT、INIT→TRIAGE、TRIAGE→REQUIREMENT、REQ_GATE→DESIGN、DESIGN_GATE→DEVELOPMENT、每个 DEV 任务完成后开始下一个 DEV 任务、RELEASE_GATE→DEPLOY、DEPLOY→FEEDBACK、FEEDBACK→DONE。关口仍必须先通过 readiness，人工确认不能替代检查。
- 技术选型必须人参与确认。Agent 可以提出候选方案、对比依据、风险和推荐，但不得自行决定或写成已采纳事实。语言/框架、数据库、缓存/队列、云服务、对象存储、模型供应商、部署方式、构建/测试工具、第三方 SaaS 和长期不可逆架构取舍，都必须在 `docs/decisions/` 先记录为 `Proposed`，经用户/PL/Architect 明确接受后才可标记 `Accepted`，并同步到 `PROJECT.md`、`docs/architecture/`、`docs/toolchain/` 或任务单。
- 代码变更前必须通过 `workflow/execution.config.yaml` 定义的前置校验；未通过不得写代码。
- 已写业务代码但缺少测试用例产物或 Red 失败记录时，必须视为 TDD 流程违规；不得事后补写 Red 并声称 TDD 合规，只能记录偏差、补回归测试和 Green 验证，并等待用户确认修正方式。
- 没有覆盖证明就没有完成状态。任何 DEV 任务声明完成前，必须在 `review.md` 写入开发覆盖声明，并让 `acceptance.md` 的每个相关 AC 明确处于 `covered`、`manual_pending`、`deferred_with_approval` 或 `out_of_scope_with_reason`；不得用“已完成”掩盖 `not_covered`。
- 没有阶段契约交接就没有有效输入。每个阶段开始前必须按 `workflow/handoff-contracts.md` 审核上游输入契约；缺少下游必需的字段、范围、端口、API、用户动作、测试证据或放行结论时，必须退回上游补齐，不得由下游自行猜测。
- 没有验收追踪链就没有可发布功能。每个 P0/P1 AC 必须能按 `workflow/traceability-chain.md` 从 PRD 追到 REQ、AC、设计落点、OpenSpec Task、allowed_write_scope、实现文件、测试用例、Red/Green、QA 覆盖复核、Release 证据和 Deploy 记录。
- 发现交付结果问题时必须按 `workflow/failure-backtrace.md` 倒查。首页打不开、功能漏做、测试无证明力、mock 被当发布证据、任务越界、Agent 不响应等问题，必须定位最早断链环节和责任角色，不得只归咎于最后一个执行者。
- 存在前端页面、管理端页面或用户交互验收项时，E2E 证据必须拆成两类：`Delivery E2E / Runtime Smoke` 证明真实前端入口经过代理访问真实后端，`Browser Interaction E2E` 证明真实浏览器执行用户动作并验证结果。API/fetch/curl/Runtime Smoke 不能替代浏览器交互证据。
- 数据库/存储、API、Mock 和 Runtime 不能分开各写各的：`docs/runtime/runtime-contract.md` 必须列出 API、数据库/存储和 browser E2E 契约；`docs/api/api.md` 与 `docs/database/database.md` 必须互相引用并说明 mock 不能作为交付或发布证据。
- 进入发布或人工验收前，QA 必须在 `review.md` 写入独立覆盖复核，PL 必须写明人工验收范围：已覆盖、明确未覆盖、已批准暂缓、不属于本 CR、需要人工只验证。
- 进入设计或开发前必须读取当前 OpenSpec change 的 `proposal.md`、`specs/**/spec.md`、`design.md` 和 `tasks.md`；进入 REQ_GATE ready 前必须主动向用户展示所有 Q 编号、待确认项和关键假设，并记录 `展示状态`。阻塞 MVP 的 Open 待澄清问题未关闭、暂缓或标记非阻塞前不得推进。
- 人工说"需求关口没问题"或"设计关口没问题"只代表允许评审；Agent 必须先运行 `python tools/check-gate-readiness.py`。检查失败时不得记录 `passed`，也不得推进 `workflow/state.md`。
- LLM 不能自批关口，不能自行把阶段推进为 `passed`；关口结论由对应主责 Agent 在 readiness 通过并捕获人工确认后记录，涉及高风险项必须人工确认。发现未经用户确认的阶段推进时，必须停止继续执行，报告违规阶段和写入文件，并等待用户确认修正方式。
- 执行后按 `workflow/agent-run-template.md` 在当前 CR 的 `logs/agent-runs/` 记录上下文、改动、命令、验证、文档同步和风险。
- 不在 `docs/` 顶层新增主题 Markdown。
- 不跨模块乱改，不凭空假设业务规则。
- 不写入真实密钥、token、密码、证书或生产数据。
- 高风险操作先确认，包括生产、数据删除、破坏性迁移、认证授权、支付账务和公共 API 破坏性变更。

## 输出

完成后说明：改了什么、验证了什么、同步了哪些文档、还有什么风险。
