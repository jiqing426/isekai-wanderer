# Workflow

`workflow/` 记录执行策略、当前状态、CR 证据包、审批、TDD 证据、安全审查、部署记录和 Agent 执行日志。它不替代 OpenSpec、`PROJECT.md` 或 `docs/`。

OpenSpec 是规格和任务主源。每个正式需求、行为变化、高风险修复或架构调整都使用一个 `openspec/changes/<change-name>/` 目录；`workflow/changes/<CR-ID>/` 保存该变更的治理证据。

## 目录结构

```txt
workflow/
├── state.md
├── workflow.config.yaml
├── execution.config.yaml
├── agents.config.yaml
├── cluster.config.yaml
├── communication.config.yaml
├── communication-ledger-template.md
├── permissions.config.yaml
├── agent-run-template.md
├── gates/
│   └── README.md
└── changes/
    └── <CR-ID>/
```

```txt
openspec/
├── config.yaml
├── project.md
├── AGENTS.md
├── specs/
├── changes/archive/
└── changes/
    └── <change-name>/
        ├── proposal.md
        ├── specs/
        ├── design.md
        └── tasks.md
```

## 边界

- `openspec/changes/<change-name>/proposal.md`：为什么做、范围、成功标准、影响和待澄清问题。
- `openspec/changes/<change-name>/specs/**/spec.md`：可观察的行为需求和场景。
- `openspec/changes/<change-name>/design.md`：技术方案、取舍和影响。
- `openspec/changes/<change-name>/tasks.md`：实现任务主源，包含负责人、允许写入范围、验证方式和回滚说明。
- `workflow/changes/<CR-ID>/change.md`：入口、影响评估和人工确认标记。
- `workflow/changes/<CR-ID>/acceptance.md`：从 OpenSpec 行为到任务、测试和发布状态的验收追踪。
- `workflow/changes/<CR-ID>/test-plan.md`：测试先行产物、Red 失败记录和 Green 通过记录。
- `workflow/changes/<CR-ID>/deploy-plan.md`：发布关口前的部署计划、回滚方案、监控方案和人工确认要求。
- `workflow/changes/<CR-ID>/deploy-record.md`：发布关口通过后的实际部署执行记录。
- `workflow/changes/<CR-ID>/review.md`：阶段结论、关口审批、风险、联调、反馈和归档状态。
- `workflow/gates/README.md`：可复用关口策略；运行时结论写在当前 CR 的 review 文件里。

## Readiness 检查

用户只需要提供原始目标或 `change.md`。Agent 负责创建或更新 OpenSpec change，并补齐推进到下一关口所需的最小 workflow 证据。

- 状态总览：`python tools/workflow-status.py`
- 下一步入口：`python tools/workflow-next.py`
- 集群结构检查：`python tools/check-cluster-readiness.py --project-root .`
- 通信配置检查：`python tools/check-communication-readiness.py --project-root .`
- 阶段流转检查：`python tools/check-transition-readiness.py --change-id <CR-ID> --change <change-name> --from-stage <FROM_STAGE> --to-stage <TO_STAGE> --action <ACTION>`
- 需求关口检查：`python tools/check-gate-readiness.py --gate requirement --change <change-name> --change-id <CR-ID>`
- 设计关口检查：`python tools/check-gate-readiness.py --gate design --change <change-name> --change-id <CR-ID>`
- 发布关口检查：`python tools/check-gate-readiness.py --gate release --change <change-name> --change-id <CR-ID>`
- 代码准入检查：`python tools/check-workflow-readiness.py --change <change-name> --change-id <CR-ID> --task-id <TASK-ID> --target-file <PATH>`
- 任务完成检查：`python tools/check-task-completion-readiness.py --change <change-name> --change-id <CR-ID> --task-id <TASK-ID>`
- DEV 任务继续检查：`python tools/check-dev-task-handoff-readiness.py --change <change-name> --change-id <CR-ID> --next-task-id <NEXT-DEV-TASK-ID>`

`workflow-status.py` 和 `workflow-next.py` 默认从 `workflow/state.md` 识别当前 CR 与 OpenSpec change；需要查看其他变更时可传 `--change-id <CR-ID>`、`--change <change-name>` 覆盖。两个工具只读文件，不会修改 workflow 或 OpenSpec 记录。

人工确认可以很短，但不能替代 readiness。检查失败时，Agent 必须列出缺口、生成缺失草案、请求确认，或记录 `returned` / `blocked`。

OpenClaw / 龙虾群集启动是项目 workflow 前置步骤，必须先过群集结构和通信配置检查。HR 负责创建或校验角色 workspace、强制覆盖全部 required agent 的 runtime `AGENTS.md` / `SOUL.md` 模板、MSG 必备通道、飞书群聊可见性和全部启动角色 ack；HR/CEO 是固有 agent，只覆盖模板、不创建项目专属 agent。`startup_order` 使用职责名；真实 `sessions_send.agentId` 必须先按 `aliases` / `agent_suffix` 算出 suffix，再拼成完整项目 agent ID，例如 `pl -> <project_code>-pl`、`ops -> <project_code>-op`。`main` 是主会话，不属于 HR 联通测试目标。`required_agents` 必须覆盖 `startup_order` 的全部角色。`<cluster_root>` 必须使用绝对路径，建议示例为 `/root/.openclaw/workspace/main/openclaw-clusters/main`，不得放在 HR 或其它角色 workspace 下。群集 ready 后，主会话必须引导用户去 PL 角色会话提交 PRD。PL 收到 PRD 后才询问项目信息、协调创建业务项目路径并推进 workflow。

群集创建后必须执行联通自测。HR 是 `cluster_connectivity_self_test` 的唯一发起者，主会话不得替 HR 发起该测试。HR 必须向每个联通测试目标发送 `sessions_send(agentId="<project_code>-<suffix>", message="cluster_connectivity_self_test", timeoutSeconds=15)`；工具支持批量/并发时必须并发发出，不支持时才按短 timeout 串行发送。联通测试目标只能回复一行 `ACK cluster_connectivity_self_test <role>`，不得解释、复述规则、检查文件或输出计划。HR 等待 ack 或超时，并写入 `<cluster_root>/runtime/delivery-ledger/cluster-connectivity.md`、`<cluster_root>/runtime/health/cluster-health.json` 与 `<cluster_root>/runtime/openclaw-process-status.md`。任一联通测试目标未 ack，群集状态必须是 `not_ready`，PRD intake 和项目 workflow 必须阻断。全部联通测试目标为 `acked_msg` 后，HR 必须同步更新 `cluster-health.json`：`connectivity_self_test_status=passed`、`cluster_status=ready`、`prd_intake_allowed=true`。飞书可见、口头确认、截图或推测不能替代 `sessions_send` ack。主会话和 HR 绕过 PL 直接接 PRD也必须视为流程违规。

台账边界必须分清：`<cluster_root>/runtime/delivery-ledger/cluster-connectivity.md` 只记录 PRD 前的群集联通证明；`/root/<project_code>/workflow/changes/<CR-ID>/communication-ledger.md` 只记录 PRD 后当前项目内的跨角色通信。

业务项目 workspace 是唯一项目事实源。OpenClaw 角色 workspace 只是 runtime shell，项目初始化后必须通过角色 workspace 内的 `PROJECT_WORKSPACE.md` 指向 canonical project root。任何角色写项目文件前必须读取该指针；指针缺失、为 `pending` 或不可访问时必须停止并退回 PL/HR。`PROJECT_WORKSPACE.md` 必须至少包含 `project_root`、`source`、`updated_at` 三个字段；角色只能读取 `project_root` 字段作为项目写入根。`<project_code>` 是项目代号，也是 `/root/<project_code>` 的目录名，不是项目展示名称。`workflow/`、`openspec/`、`docs/`、代码、测试、PRD、review、acceptance、tasks、proposal、design 等文件只允许写在 canonical project root；写在 role workspace 的同名文件一律无效，PL 不得据此审查。

需求关口 readiness 之前，Agent 必须把所有待澄清问题、待确认项和关键假设按 Q 编号主动推送给用户，并在 OpenSpec 表中记录 `展示状态`。非阻塞 Open 问题也需要用户可见的暂缓或非阻塞依据。

## 维护规则

- 不在 `workflow/` 里维护第二套实现任务列表。
- 不把多个正式需求混进同一个 OpenSpec change。
- 进入 `DEVELOPMENT` 前，计划实现的 OpenSpec task 必须是 `Ready` 或 `Approved`。
- 业务代码变更必须由 OpenSpec task 覆盖，且允许写入范围必须覆盖目标文件。
- P0/P1、API、数据库、权限、安全、部署、生产、支付或跨模块变更必须有 `test-plan.md`。
- 补齐匹配的测试用例产物和 Red 失败记录前，不得写业务代码。
- Red/Green 记录必须来自真实命令执行，不能只写 AI 判断、人工口头判断或占位文本；自动化测试产物必须存在，Red/Green 命令必须引用并共享当前任务的测试用例产物；`acceptance.md` 必须引用 Green 命令或当前测试用例产物；声明任务完成前，任务完成检查会复跑当前 `DEV-*` 的 Green 命令且 exit code 必须为 0。
- 声明任务完成前，必须补齐 Green 通过记录、验收追踪和 Agent Run Log。
- 每完成一个 `DEV-*` 任务后，Agent 必须停下汇报；未在 `workflow/changes/<CR-ID>/review.md` 记录暂停汇报和用户明确继续确认前，不得开始下一个 `DEV-*` 任务。
- Agent Run Log 放在 `workflow/changes/<CR-ID>/logs/agent-runs/`。
- 变更完成后，必须把稳定行为合并到 `openspec/specs/`，同步长期事实到 `PROJECT.md` 和 `docs/`，再把完成的 change 移到 `openspec/changes/archive/`。
- 运行时证据保留在 `workflow/changes/<CR-ID>/`；审批、测试报告、部署记录和 Agent 日志不要移进 OpenSpec archive。
