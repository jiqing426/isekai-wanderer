# AI Collaboration

本文记录 AI 协作细则。入口文件是根目录 `AGENTS.md`；如果两者冲突，以 `AGENTS.md` 的硬边界为准。

## 上下文读取

AI 修改代码或文档前读取最小必要上下文：

1. `AGENTS.md`
2. `PROJECT.md`
3. `README.md`
4. `docs/README.md`
5. `docs/architecture/architecture.md`
6. `docs/status/feature-status.md`
7. 当前任务相关的模块 README、代码文件和测试文件

按任务补读：

- API、SDK、Webhook、错误码：`docs/api/api.md`
- 数据库、迁移、数据字典：`docs/database/database.md`
- 部署、环境变量、运行时、开发流程、分支、评审：`docs/operations/operations.md`
- 测试策略、测试数据：`docs/testing/testing.md`
- 工具链选择、工具接入、输入输出和验证要求：`docs/toolchain/toolchain.md`
- 安全、密钥、权限、敏感数据：`docs/security/security.md`
- 重要技术决策和 ADR：`docs/decisions/decisions.md`
- PRD 拆解、需求同步：仅在用户明确要求或 PM 阶段读取 `docs/prd/prd.md`，并使用 `skills/pm/SKILL.md`
- 状态机、关口策略、流转、Agent 日志：`workflow/state.md`、`workflow/workflow.config.yaml`、`workflow/gates/README.md`
- OpenSpec 需求规格：当前 `openspec/changes/<CR-ID>-<change-name>/proposal.md`、`specs/**/spec.md`、`design.md`、`tasks.md`
- 变更入口、审批记录、测试先行、验收追踪、执行策略：当前 CR 的 `change.md`、`review.md`、`test-plan.md`、`acceptance.md`、`workflow/execution.config.yaml`

不要为了形式读取整个仓库。当前代码事实优先于过期文档；发现冲突时，按代码事实完成最小修改，再同步相应文档或在变更报告中说明未同步原因。

## 文档归属

根目录 `PROJECT.md` 维护项目范围、模块清单、外部依赖、数据分级和负责人。`docs/` 顶层只保留 `README.md` 索引。新增主题文档必须放入相关目录。

- `docs/architecture/`：当前架构事实、模块边界、依赖方向、核心流程。
- `docs/api/`：API 契约、错误码、鉴权、分页、兼容性。
- `docs/database/`：数据模型、迁移、索引、备份、数据保留。
- `docs/status/`：功能状态、缺口、TODO、已知限制。
- `docs/operations/`：部署、运行时、环境变量、开发和交付流程。
- `docs/testing/`：测试分层、测试命令、覆盖要求、测试数据。
- `docs/toolchain/`：工具链选择、接入边界、输入输出和验证要求。
- `docs/security/`：安全开发、密钥、权限、敏感数据。
- `docs/ai/`：AI 协作规范、工作协议、上下文规则。
- `docs/decisions/`：ADR 和重要工程决策。
- `docs/prd/`：产品需求输入和待拆解内容，不作为最终工程事实源。

`architecture/` 记录当前事实；`decisions/` 记录决策历史。不要把 ADR 当成当前架构说明，也不要把历史决策覆盖成当前事实。

`prd/` 只作为需求输入暂存。普通任务不默认读取 PRD；只有用户明确要求“PRD 拆解”“同步 PRD”“根据需求更新工程文档”或当前处于 PM 需求阶段时，才读取 `docs/prd/prd.md` 并按 `skills/pm/SKILL.md` 同步已确认需求事实。技术方案、API、数据模型和重要架构取舍由 `skills/architect/SKILL.md` 承接。

`toolchain/` 记录工具怎么接入工程流程。工具可以按项目替换，但必须说明输入、输出、失败条件和验证要求；工具生成结果影响代码或配置时，必须保持可审查并同步对应事实文档。

## 模块边界

`backend/` 负责服务端业务能力、API、鉴权授权、领域逻辑、任务队列、数据访问、外部系统集成和数据库迁移。前端和管理端不得复制后端业务判定逻辑。

`frontend/` 负责面向最终用户的客户端体验、页面路由、状态管理、可访问性、埋点入口和公开 API 调用。不得放置管理端专属权限、内部运营流程或数据库直连逻辑。

`admin/` 负责内部运营、审核、配置、权限敏感操作和管理端工作台。管理端功能必须默认考虑权限、审计、误操作保护和高风险操作确认。

`deploy/` 负责部署拓扑、容器、反向代理、环境配置和生产检查清单。业务代码不得依赖部署目录中的私有环境事实。

`scripts/` 只放可重复执行的工程脚本模板。脚本应幂等、可读、失败即退出，不写入真实密钥。

`tools/` 预留代码生成、迁移辅助、数据校验和自动化工具。工具输出影响代码时，必须说明生成规则并提交可审查的结果。

`skills/` 放当前项目专属 AI skills，用于记录角色能力、上下文读取规则和脚本引用。项目级 skill 不得覆盖 `AGENTS.md` 的硬边界，不得保存真实密钥，也不得混入公共标准库的 `standard-skills/`。

`openspec/` 放需求规格主源。每个正式需求、行为变化、高风险修复或架构调整使用独立 `openspec/changes/<CR-ID>-<change-name>/`；完成后将稳定规格归档到 `openspec/specs/`。

`workflow/` 放状态机、关口策略、配置和以 CR 为单位的治理证据包。长期工程事实写入 `PROJECT.md` 或 `docs/` 对应目录；`workflow/changes/<CR-ID>/` 只记录本次变更的过程事实、验收追踪、测试、审批和阶段结论。实现任务主源在当前 OpenSpec change 的 `tasks.md`。

`tests/` 放跨模块、契约、端到端或系统级测试。模块内部单元测试优先放在各自模块内。

## 工作流程

修改前必须定位：

- 入口文件、调用路径和受影响模块。
- API、数据库、事件、配置、权限或部署契约是否变化。
- 现有测试、示例、文档和脚本是否需要同步。
- 是否影响 `backend/`、`frontend/`、`admin/` 之间的边界。
- 是否涉及安全、数据、生产、支付、权限、审计或兼容性风险。

## 关键提醒

- 写任何业务代码前，必须运行 `python tools/check-workflow-readiness.py --change-id <CR-ID> --change <change-name> --task-id <TASK-ID> --target-file <path>`。目标文件不止一个时重复传入 `--target-file`；未运行、参数不完整或返回失败时，不得写入业务代码。

## 开发任务完成规则

将 OpenSpec task 标记为 Done 前，必须：
1. 运行 `python tools/check-task-completion-readiness.py --change-id <CR-ID> --change <change-name> --task-id <TASK-ID>`
2. 检查通过后方可标记任务完成
3. 未通过时，必须在回复中列出缺失项，不得标记完成
4. 在 `workflow/changes/<CR-ID>/review.md` 的 `开发覆盖声明` 表写明已实现 AC、已测试 AC、未实现 AC、未测试 AC、已运行命令、失败命令、需要人工验收和已知风险
5. 在 `workflow/changes/<CR-ID>/acceptance.md` 同步每个相关 AC 的 `覆盖状态`、`未覆盖原因` 和 `PL 处理`；不得用“已完成”掩盖 `not_covered`

## 阶段暂停协议

workflow 管理的每个阶段完成后，Agent 必须暂停，不得自行推进到下一阶段。

阶段完成后必须：

1. 补齐当前阶段要求的交付物。
2. 在聊天中展示交付物清单、关键结论、缺口和风险。
3. 明确询问用户是否允许进入下一阶段或关口评审。
4. 用户确认前，不得在 `review.md` 或 `workflow/state.md` 写入 `submitted`、`passed`、`approved`、`delivered` 等推进性结论。
5. 收到用户确认后，将确认依据写入当前 CR 的 `review.md` 的 `Stage Pause Confirmations` / `阶段暂停确认` 表，再运行对应 readiness：
   - 关口结论：`python tools/check-gate-readiness.py ...`
   - 阶段流转：`python tools/check-transition-readiness.py ...`
   - 代码准入：`python tools/check-workflow-readiness.py ...`
   - 任务完成：`python tools/check-task-completion-readiness.py ...`
6. readiness 失败时只能列出缺口、补草案或请求确认，不得推进阶段。

发现未经用户确认的阶段推进时，必须停止继续执行，报告违规阶段和写入文件，并等待用户确认修正方式。

## LLM 执行协议

workflow 管理的阶段是阻断式流程。Agent 可以读取上下文、整理问题、补充待人工确认的记录，但不能用自己的判断替代关口结论，也不能在未进入 `DEVELOPMENT` 前写代码。

人工确认话术可以保持简单，但不能绕过 readiness。用户说“需求关口没有问题，允许进入设计”或“设计关口没有问题，允许进入开发”时，Agent 只能把它当成关口评审意图；写入 `passed` 和推进 `workflow/state.md` 前，必须先运行 `python tools/check-gate-readiness.py`。检查失败时，Agent 必须列出缺口、生成缺失草案、请求确认或记录 `returned`。

推进 `workflow/state.md` 前还必须运行阶段流转检查：`python tools/check-transition-readiness.py --change-id <CR-ID> --change <change-name> --from-stage <FROM_STAGE> --to-stage <TO_STAGE> --action <ACTION>`。该检查只确认“这一步能不能走”，不能替代关口 readiness、代码准入或任务完成检查。

### OpenSpec Change 生成

- 用户只提供一句目标或只补了 `change.md` 时，PM 可以创建或更新 OpenSpec change：`proposal.md`、`specs/**/spec.md`；同时维护 `docs/prd/prd.md` 摘要和当前 CR 的 `acceptance.md`。未确认内容标记为 `待确认`，不得写成既定事实。
- 模板中的 `待确认` 只是占位提醒；真实 CR 进入 REQUIREMENT / REQ_GATE 后，Agent 必须扫描并消除散落的 `待确认`。确实需要人确认的点必须登记到“待澄清问题”，并在原位置引用 Q 编号，例如 `待确认，见 Q-001`。
- 进入 REQ_GATE ready 前，Agent 必须在聊天里主动列出当前 change 的所有待澄清问题、待确认项和关键假设，按 Q 编号逐条说明是否阻塞 MVP；不得只把问题写进文件后静默提交关口。
- 用户回答后，Agent 必须同步更新 `用户回答`、`处理结论`、`展示状态` 和原引用位置；非阻塞 Open 问题也必须展示给用户，并记录“暂缓/非阻塞”的确认依据。
- 如果 OpenSpec proposal 或 specs 中存在阻塞 MVP 的 Open 待澄清问题，PM 必须先向用户发起澄清；未回答、未暂缓或未标记非阻塞前不得提交 REQ_GATE。
- REQ_GATE passed 前，OpenSpec proposal/specs 和验收追踪必须通过需求关口 readiness。
- REQ_GATE passed 前，`acceptance.md` 必须完成需求编号化：每个验收项都有 `REQ-*`、`AC-*`、优先级、可测试验收标准和覆盖状态。暂未覆盖必须写成 `not_covered`，不能省略。
- REQ_GATE passed 后，Architect / PL / QA 生成 OpenSpec `design.md`、OpenSpec `tasks.md`、workflow `test-plan.md` 和补齐设计落点的 `acceptance.md`；同时使用 `skills/architect/SKILL.md` 将技术方案拆分同步到对应 `docs/` 主事实源。
- OpenSpec `design.md` 是本次设计过程主源，不是长期事实的唯一存放位置。设计完成时必须维护“文档同步”表，逐项说明 `docs/architecture/architecture.md`、`docs/api/api.md`、`docs/database/database.md`、`docs/security/security.md`、`docs/decisions/decisions.md`、`docs/runtime/runtime-contract.md` 是否已同步或无需同步，并写明依据。
- DESIGN_GATE passed 前，`docs/runtime/runtime-contract.md` 必须记录 Delivery E2E、Browser Interaction E2E、API 文档、数据库/存储契约和 mock policy；`docs/api/api.md` 与 `docs/database/database.md` 必须说明 API/数据/Mock/Runtime 的关系。
- DESIGN_GATE passed 前，OpenSpec design/tasks、设计文档同步记录和 workflow 执行追踪必须通过设计关口 readiness；其中任务状态必须是 `Ready` 或 `Approved`，测试用例产物必须是 `Ready`、`Approved` 或 `Recorded`。
- Red 失败记录属于 DEVELOPMENT 内写业务代码前的代码 readiness，不是设计关口 readiness。但进入 DEVELOPMENT 后，业务代码仍必须等 Red 记录补齐后才能写。

### 阶段阻断关系

- `INTAKE` 只建立变更入口：补齐当前 CR 的 `change.md`、目标、成功标准、影响范围和需要人工确认的问题；未进入 `INIT` 前不得拆 OpenSpec task 或写代码。
- `INIT` 只确认是否立项、投入边界和是否需要 staffing；当前 CR 的 `review.md` 未记录可继续结论时，不得进入 `TRIAGE`。
- `TRIAGE` 负责分流调度、识别风险和明确主责；它不是需求拆解、技术设计或实现计划，不得跳过 `REQUIREMENT` 直接进入设计或开发。
- `REQUIREMENT` 负责沉淀规格差异和验收追踪；提交后必须进入 `REQ_GATE`。
- `REQ_GATE` 是人工需求关口：当前 CR 的 `review.md` 关口审批表中 `REQ_GATE` 结论必须为 `passed` 才能进入 `DESIGN`；`returned` 必须退回需求，`blocked` 只能等待人工或外部条件。
- `DESIGN` 负责架构、接口、数据、安全和任务拆分依据；提交后必须进入 `DESIGN_GATE`。
- `DESIGN_GATE` 是人工设计关口：当前 CR 的 `review.md` 关口审批表中 `DESIGN_GATE` 结论必须为 `passed` 才能进入 `DEVELOPMENT`；`returned` 必须退回设计或需求，`blocked` 只能等待人工或外部条件。
- `DEVELOPMENT` 是唯一允许 workflow 管理代码变更的阶段。进入后仍必须逐任务检查 OpenSpec `tasks.md`、允许写入范围、测试计划、Red 失败记录和风险条件。
- `RELEASE_GATE` 检查 `deploy-plan.md` 中的发布步骤、回滚方案和监控方案；实际部署结果只能在 `DEPLOY` 阶段写入 `deploy-record.md`。

### Readiness 检查边界

- 关口 readiness 检查“能不能把关口记录为 passed 并推进阶段”。它关注 CR 证据包是否完整、可评审、可开发；设计关口还必须检查长期事实是否已拆分同步到对应 `docs/` 或明确无需同步。
- 代码 readiness 检查“某个任务能不能写某个目标文件”。它关注当前阶段、人工关口结论、任务状态、允许写入范围、测试用例产物和 Red 失败记录。
- 阶段流转 readiness 检查“当前阶段能不能按指定动作流转到目标阶段”。它关注 `workflow.config.yaml` 的合法流转、当前 CR 和必要的阶段/关口结论。
- 任务完成 readiness 检查“当前任务能不能声明完成”。它关注 Green 通过记录、验收追踪、开发覆盖声明和 Agent Run Log。
- 发布关口 readiness 还必须检查 QA 覆盖复核、PL 人工验收范围、CI/CD 执行结果、Delivery E2E / Runtime Smoke Results 和 Browser Interaction E2E Results；`not_covered` 不能进入发布通过结论。
- 关口 readiness 通过不代表可以立刻写业务代码；进入 DEVELOPMENT 后仍必须按任务运行代码 readiness。
- 代码 readiness 失败不应通过倒填 gate 来修复；应补齐 OpenSpec `tasks.md`、`test-plan.md`、Red 记录或允许写入范围。

### 轻量 TDD 节点

业务代码实现按当前任务经过四个轻量节点：

- 测试用例产物：在当前 CR 的 `test-plan.md` 记录测试文件、用例、脚本、契约样例或人工测试用例，并关联任务编号和验收项。
- Red 失败记录：实现业务代码前运行或执行上述用例，在 `test-plan.md` 记录命令 / 步骤、失败摘要、记录时间和状态。
- 代码实现：只允许修改 OpenSpec `tasks.md` 中当前任务允许写入范围覆盖的业务代码。
- Green 通过记录：实现后在 `test-plan.md` 记录同一批用例的通过命令 / 步骤和摘要，并同步验收追踪。

无法自动化的用例仍是测试用例产物，但必须在 `test-plan.md` 的“无法自动化”表中写明原因、人工验证负责人和验证记录；缺少原因或负责人时不得写业务代码。

### TDD 跳过补救

发现已经写入业务代码，但当前任务缺少测试用例产物或 Red 失败记录时，必须按流程违规处理：

- 立即停止继续开发、联调、QA 或发布推进，向用户说明违规任务、已写文件、缺失证据和风险。
- 不得事后补写 Red 失败记录并声称 TDD 合规；任何已实现后才创建或运行的测试只能记为回归测试、补救验证或 Green 验证。
- 如果仓库有可靠的实现前基线，可以在临时工作区回到实现前状态，运行同一测试得到真实 Red，再回到当前实现运行 Green；记录必须包含基线来源、命令、时间和结果。
- 如果无法恢复实现前基线，必须在 `test-plan.md` 的“TDD 流程偏差”表记录偏差，并由用户确认修正方式；后续只能补回归测试和 Green 验证，不能把任务标记为严格 TDD 完成。
- 已经被错误标记为 `Done`、`Completed` 或 `Delivered` 的任务，必须先退回待修正状态或记录偏差豁免；不得继续把后续阶段当作正常通过。

### 代码变更前置校验

workflow 管理中的代码变更必须同时满足：

- 有当前 CR 的 `change.md` 或明确用户请求作为入口。
- 有当前 OpenSpec change 的 `tasks.md` 任务单，包含负责人、允许写入范围、关联验收项、测试先行计划、验证方式和回滚方案。
- 任务单必须绑定 AC，并显式写明不覆盖的 AC；无不覆盖项时写 `无`。
- `workflow/state.md` 的当前阶段必须是 `DEVELOPMENT`。
- `workflow/state.md` 的当前变更和当前 OpenSpec Change 必须匹配本次 `--change-id` / `--change`。
- 当前 CR 的 `review.md` 中 `REQ_GATE` 结论必须是 `passed`。
- 当前 CR 的 `review.md` 中 `DESIGN_GATE` 结论必须是 `passed`。
- 当前 OpenSpec change 的 `tasks.md` 必须存在，并能找到本次对应任务。
- 本次对应任务状态必须是 `Ready` 或 `Approved`。
- 本次对应任务的允许写入范围必须覆盖目标文件；不覆盖时只能退回 PL 更新任务单。
- 当前任务必须在 `test-plan.md` 有测试用例产物。
- 当前任务必须在 `test-plan.md` 有 Red 失败记录；没有 Red 记录不得写业务代码。
- P0/P1、API、数据库、权限、安全、部署或跨模块变更必须有当前 CR 的 `test-plan.md`。
- 每次只允许一个主写 Agent 处理同一任务。
- LLM 只能在 OpenSpec task 允许写入范围内修改；发现需要越界时先退回 PL 更新任务单。
- LLM 不能自批关口，不能自行把阶段推进为 `passed`。
- 执行后按 `workflow/agent-run-template.md` 在当前 CR 的 `logs/agent-runs/` 记录上下文、改动、命令、验证、文档同步和风险。
- 任务完成前必须在 `test-plan.md` 补 Green 通过记录；未 Green 时不得声明任务完成。
- 任务完成前必须在 `review.md` 补开发覆盖声明；未实现、未测试或需要人工验收的 AC 必须明确列出。
- 把 OpenSpec task 标记为 `Done`、`Completed` 或 `Delivered` 前，必须运行 `python tools/check-task-completion-readiness.py --change-id <CR-ID> --change <change-name> --task-id <TASK-ID>`。
- P0/P1 验收项必须同步当前 CR 的 `acceptance.md`，QA 负责最终验证状态和覆盖复核。

任一前置校验不满足时，Agent 只能说明缺口、列出需要人工确认或补齐的文件，并等待人工确认；不得写代码、不得伪造关口通过。

低风险局部文档修订可以不创建 OpenSpec task，但仍必须遵守 `AGENTS.md`、文档归属和输出要求。

低风险局部非代码修改可以直接处理。涉及代码、公共 API、数据库结构、认证授权、生产配置或跨模块行为时，必须在变更报告中明确影响范围和验证方式；高风险破坏性操作必须先获得明确确认。

## 文档同步

设计或代码行为变化后按单一事实源同步：

- 项目范围、模块清单、外部依赖变化：`PROJECT.md`
- 系统边界、模块职责、核心流程变化：`docs/architecture/architecture.md`
- API 路由、请求响应、错误码、鉴权变化：`docs/api/api.md`
- 表、字段、索引、迁移、数据保留策略变化：`docs/database/database.md`
- API base、前后端端口、proxy、health、Delivery E2E、Browser Interaction E2E、mock policy、数据库/存储契约变化：`docs/runtime/runtime-contract.md`
- 功能状态、缺口、TODO、已知限制变化：`docs/status/feature-status.md`
- 部署、环境变量、健康检查、回滚、开发、评审、发布流程变化：`docs/operations/operations.md`
- 测试策略、测试命令、覆盖要求变化：`docs/testing/testing.md`
- 工具选择、工具接入、生成链路或验证工具变化：`docs/toolchain/toolchain.md`
- 安全、权限、密钥、敏感数据规则变化：`docs/security/security.md`
- 重要取舍、不可逆决策、架构转向：`docs/decisions/decisions.md`
- PRD 需求输入变化：先更新 `docs/prd/prd.md`；需要工程落地时使用 `skills/pm/SKILL.md` 同步已确认需求事实，技术设计部分交由 `skills/architect/SKILL.md`。

不要在多个文档中重复维护同一事实；其它位置只链接到主事实源。

## 输出要求

最终报告包含：

- 修改摘要。
- 影响范围。
- 验证结果。
- 文档同步情况。
- 风险、假设和后续建议。

无法验证时必须说明原因和剩余风险。

## 禁止事项

- 不跨模块乱改。
- 不在 `docs/` 顶层散放主题 Markdown。
- 不凭空新增业务规则。
- 不绕过安全、权限、审计、数据归属或支付边界。
- 不隐藏验证失败或未验证事实。
- 不提交真实密钥、token、证书、密码或生产数据。
