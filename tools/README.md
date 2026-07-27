# Tools

代码生成器、迁移辅助、数据校验和自动化工具预留目录。

项目专属 AI skills 放在 `../skills/`。本目录只放可运行或可审查的工程工具。

## 约定

- 每个工具必须有 README 或命令说明。
- 工具生成代码、迁移或配置时，必须产出可审查的文件，不得只修改运行时状态。
- 工具不得默认访问生产数据或真实密钥。
- 工具规则变化影响工程流程时，同步 `../docs/operations/operations.md` 或 `../docs/ai/ai-collaboration.md`。

## 工作流状态与下一步

新人不需要先记住所有 readiness 命令：

```sh
python tools/workflow-status.py
python tools/workflow-next.py
```

两个工具默认从 `workflow/state.md` 识别当前 CR 与 OpenSpec change，并只读 `workflow/state.md`、当前 CR 的 `review.md` / `test-plan.md` / `acceptance.md`、当前 OpenSpec change 的 `tasks.md`。需要覆盖当前变更时传 `--change-id CR-001 --change CR-001-example-change`；需要覆盖当前任务时传 `--task-id DEV-001`。

`workflow-status.py` 输出当前阶段、当前任务、关口结论、DEV 任务进度、Red/Green 状态和主要缺口。`workflow-next.py` 输出下一步建议以及应该执行的底层 readiness 命令，例如需求关口、设计关口、代码准入、任务完成检查或 DEV handoff 检查。

## OpenClaw 集群和通信检查

`check-cluster-readiness.py` 检查 OpenClaw / 龙虾集群配置、HR owner、required role prompts 和可选 cluster root 结构。

```sh
python tools/check-cluster-readiness.py --project-root .
```

`check-communication-readiness.py` 检查 `sessions_send` 必备通道、飞书群聊可见性和通信台账策略。
它还检查群集联通自测门禁：全部联通测试目标必须通过 MSG 自测 ack，未 ack 不得接 PRD；HR 是测试发起者，不作为 `cluster_connectivity_self_test` 目标。
联通自测通过后，HR 必须按 `standard-skills/cluster-assembly/SKILL.md` 同步更新 `runtime/health/cluster-health.json`：全部联通测试目标为 `acked_msg` 时写入 `cluster_status=ready`、`prd_intake_allowed=true`；否则保持 `not_ready/false`。

```sh
python tools/check-communication-readiness.py --project-root .
```

## PRD 自动入口

`bootstrap-openclaw-prd.py` 用于 OpenClaw 中“HR 已完成群集初始化、业务项目路径已创建且全部启动角色已 ack 后，PL 收到 PRD 就启动 workflow”的场景。群集 ready 后，主会话必须引导用户去 PL 角色会话提交 PRD；PL 收到 PRD 文件或正文后先运行它，自动创建当前 CR、PRD 摘要、OpenSpec change 骨架、`workflow/state.md`、`review.md` 和角色 `AGENTS.md`。OpenClaw 群集、角色 workspace、MSG 必备通信、runtime `AGENTS.md` / `SOUL.md` 模板覆盖和飞书群聊可见性由 HR 与 `standard-skills/cluster-assembly/SKILL.md` 负责。

事实源边界：`bootstrap-openclaw-prd.py` 只写 `--project-root` 指向的业务项目 workspace。角色 workspace 是 OpenClaw runtime shell，不得接收 `workflow/`、`openspec/`、`docs/`、代码、测试、PRD、review、acceptance、tasks、proposal 或 design 文件副本。项目初始化完成后，HR 必须按 `standard-skills/cluster-assembly/SKILL.md` 把 canonical project root 登记到每个角色 workspace 的 `PROJECT_WORKSPACE.md`。

`<cluster_root>` 必须是绝对路径，不得放在 HR 或其它角色 workspace 下。`<project_code>` 是项目代号，也是 `/root/<project_code>` 的目录名，不是项目展示名称。

PRD 文件：

```sh
python tools/bootstrap-openclaw-prd.py --project-root . --prd-file docs/prd/input.md
```

PRD 正文：

```sh
python tools/bootstrap-openclaw-prd.py --project-root . --prd-text "示例需求：实现一个可验证的业务功能，包含用户动作、系统结果和验收标准。"
```

参数：

- `--project-root`：项目/kanban workspace 根目录。
- `--prd-file` / `--prd-text`：PRD 输入，二选一；长文本优先用文件。
- `--workspace-root`：废弃参数，仅为旧命令兼容保留；不会同步任何项目文件到角色 workspace。
- `--roles`：废弃参数，仅为旧命令兼容保留；不会影响写入范围。
- `--no-sync-workspaces`：废弃 no-op；项目文件从不镜像到角色 workspace。

自动入口只授权创建 CR、记录 PRD 和生成初始 workflow / OpenSpec 骨架。它不授权自动通过阶段、关口、DEV 任务继续或发布；推进型流转仍必须记录用户明确同意，并通过对应 readiness。

## 代码准入检查

`check-workflow-readiness.py` 用于业务代码变更前的准入检查。它读取当前 CR 状态、`review.md` 中的关口结论、OpenSpec `tasks.md`、允许写入范围和测试先行记录；未通过时 Agent 不得写业务代码。

```sh
python tools/check-workflow-readiness.py --change-id CR-001 --change CR-001-example-change --task-id DEV-001 --target-file backend/src/example.py
```

常用参数：

- `--project-root`：项目根目录，默认从 `tools/` 推断。
- `--change-id`：workflow CR 编号，例如 `CR-001`。
- `--change`：OpenSpec change 目录名，例如 `CR-001-example-change`；未传时按 `--change-id` 前缀查找。
- `--task-id`：当前任务编号，必须能在 `openspec/changes/<change-name>/tasks.md` 找到。
- `--target-file`：本次计划写入的文件；可重复传入，必须被 OpenSpec task 的允许写入范围覆盖。
- `--priority P0|P1|P2|P3` 或 `--high-risk`：用于触发高风险测试计划要求。

## 关口检查

`check-gate-readiness.py` 用于关口结论写入前的准入检查。它检查 OpenSpec change 与当前 CR 证据包是否完整；代码准入则检查单个 OpenSpec task 是否可以写业务代码。

人工确认话术可以保持简单，例如“需求关口没有问题，允许进入设计”。Agent 收到后必须先运行对应检查；检查失败时只能列出缺口、生成缺失草案、请求确认或记录 `returned`，不得把 gate 写成 `passed`。

```sh
python tools/check-gate-readiness.py --gate requirement --change-id CR-001 --change CR-001-example-change
python tools/check-gate-readiness.py --gate design --change-id CR-001 --change CR-001-example-change
python tools/check-gate-readiness.py --gate release --change-id CR-001 --change CR-001-example-change
```

边界：

- 需求关口 readiness：检查 `change.md`、OpenSpec proposal/specs、待澄清问题的 Q 编号和展示记录、阻塞澄清问题、非阻塞暂缓结论、裸露的 `待确认` 和 `acceptance.md`。
- 设计关口 readiness：检查 REQ_GATE 结论、OpenSpec design/tasks、`design.md` 文档同步表、`test-plan.md` 和 `acceptance.md`；文档同步表必须覆盖架构、API、数据库、安全和决策主事实源，并标记为已同步或无需同步。
- 发布关口 readiness：检查 DESIGN_GATE 结论、验收状态、测试报告、安全审查、发布计划、回滚方案、监控方案和 Agent Run Log。
- 代码 readiness：进入 `DEVELOPMENT` 后针对具体 `TaskId` 和 `TargetFile` 检查，要求 OpenSpec task 允许写入范围覆盖目标文件，并且测试用例产物和 Red 失败记录已补齐。

## 阶段流转检查

`check-transition-readiness.py` 用于修改 `workflow/state.md` 前，确认当前阶段、目标阶段和动作符合 `workflow.config.yaml`，并检查推进型流转是否已在当前 CR 的 `review.md` 记录阶段暂停确认。

```sh
python tools/check-transition-readiness.py --change-id CR-001 --change CR-001-example-change --from-stage REQ_GATE --to-stage DESIGN --action approve
```

它会检查当前 CR 是否匹配、当前阶段是否匹配、动作是否允许、需要审批的阶段是否已经有对应结论，以及 `Stage Pause Confirmations` / `阶段暂停确认` 表中是否记录了已向用户展示交付物并获得推进确认。退回、停止、阻塞和回滚动作不受阶段暂停确认表阻断。

## 任务完成检查

`check-task-completion-readiness.py` 用于把 OpenSpec task 标记为完成前，确认 Green 通过记录、验收追踪和 Agent Run Log 都已补齐。

```sh
python tools/check-task-completion-readiness.py --change-id CR-001 --change CR-001-example-change --task-id DEV-001
```

未通过时，不得把任务状态改为 `Done`、`Completed` 或 `Delivered`。已经写入业务代码后补写的 Red 记录不能作为合规 TDD Red；如发生跳过，必须在 `test-plan.md` 记录 TDD 流程偏差，并补回归测试或从实现前基线重新取得真实 Red。

## Readiness 工具样例

维护工具规则后运行可执行样例：

```sh
python tests/tools/test_readiness.py
```

样例覆盖模板空 CR 失败关闭、完整成功路径通过阶段流转、需求/设计/发布关口、代码准入和任务完成检查，以及 active OpenSpec change 不匹配时拒绝写代码。
