# 阶段契约交接

本文定义每个阶段如何接收上游契约、审核输入、补充本阶段契约，并把可消费的输出交给下游。下游不得猜测上游没有给出的字段、路径、范围、端口、API、验收标准或测试证据。

## 全局原则

- 上游必须明确给出下游执行所需的事实和约束。
- 下游收到输入后必须先审核输入是否足够，不足时退回上游，不得自行假设。
- 每个阶段都必须在当前 CR 证据包或长期事实文档中留下可审计记录。
- PL 负责检查阶段契约是否断链；发现断链时不得推进 `workflow/state.md`。

## 阶段交接表

| 阶段 | 输入契约 | 输入审核 | 本阶段补充 | 输出契约 | 下游消费方 |
| --- | --- | --- | --- | --- | --- |
| 群集初始化 | 标准库路径、项目代号、cluster root | HR/CEO 是否存在，模板是否当前，10 个项目角色是否可创建或校验 | 角色 workspace、模板覆盖、ACK-only 联通自测 | `cluster-connectivity.md`、`cluster-health.json`、`openclaw-process-status.md` | PL |
| INTAKE | 用户 PRD、群集 ready | 是否有项目目标、范围、成功标准和明显风险 | 创建 CR，记录 PRD 和初始影响范围 | `change.md`、`docs/prd/prd.md`、`workflow/state.md` | CEO |
| INIT | `change.md` | 业务价值、目标用户、本轮边界、非目标是否清楚 | 做不做、先做什么、投入到哪里为止 | `review.md` INIT 结论、停止条件 | PL / PM |
| TRIAGE | INIT 结论 | 是否足以分派角色和识别风险 | 变更分类、主责分配、前置条件、风险 | `review.md` TRIAGE 记录 | PM |
| REQUIREMENT | PRD、INIT / TRIAGE 边界 | 是否有未确认范围、阻塞问题或不可测试描述；是否已按实体或关键流程检查 R/C/U/D 和用户可见结果 | REQ/AC 编号、OpenSpec proposal/spec、验收矩阵、Q 编号、R/C/U/D 完整性检查 | `proposal.md`、`spec.md`、`acceptance.md`、`PROJECT.md`、feature status | PL / Architect |
| REQ_GATE | PM 需求产物 | Q 编号是否展示，P0/P1 是否可测试，acceptance 是否完整 | 需求关口审查结论 | `review.md` REQ_GATE 记录 | Architect |
| DESIGN | 需求关口 passed、acceptance | 需求是否足以设计，技术选型是否需确认；前端/管理端消费方、环境矩阵和交付级证据标准是否已映射 | 架构、API、数据、运行契约、任务、测试计划、消费契约 | `design.md`、`tasks.md`、`runtime-contract.md`、API/DB/Security/Decision 文档、`test-plan.md` | PL / 实现 Agent / QA |
| DESIGN_GATE | 设计产物 | runtime contract、tasks、test-plan、文档同步是否完整 | 设计关口审查结论 | `review.md` DESIGN_GATE 记录 | BE / FE / Admin / AI |
| DEVELOPMENT | tasks、allowed write scope、test-plan | 当前阶段是否 DEVELOPMENT，需求/设计关口是否 passed，Red 是否已记录；若发现前端/后端消费方需要但上游未定义的 API、页面、数据或权限，是否已登记开发期契约缺口 | 代码、测试、Green、Agent Run Log、开发覆盖声明；必要时登记 `Contract Gaps Discovered During Development` 并退回上游补契约 | 实现文件、测试文件、`acceptance.md` 更新、`review.md` 开发覆盖声明和缺口关闭记录 | PL / QA |
| INTEGRATION | 开发完成证据、runtime contract | 路由链、proxy、真实入口、真实后端、零 P0 是否满足；API 路由与前端调用是否全量对齐 | 联调 Go/No-Go；发现断链时登记契约缺口并退回 REQUIREMENT / DESIGN / DEVELOPMENT | `review.md` 联调记录和缺口关闭记录 | QA |
| QA | test-plan、acceptance、runtime contract、开发覆盖声明 | 测试类型是否完整，是否存在 mock 发布证据；是否存在未关闭开发期契约缺口 | 独立测试和覆盖复核；缺口未关闭时不得给 covered / release-ready | `test-report.md`、`acceptance.md`、`review.md` QA 覆盖复核 | Security / PL |
| SECURITY | API/DB/Runtime、test-report、deploy-plan | 密钥、权限、敏感数据、mock、未记录数据源是否有风险 | 安全审查 | `security-review.md` | PL / Ops |
| RELEASE_GATE | test-report、security-review、deploy-plan、acceptance | CI/CD、Delivery E2E、Browser E2E、QA 覆盖复核、人工验收范围是否完整 | 发布关口结论 | `review.md` RELEASE_GATE 记录、`deploy-plan.md` | Ops |
| DEPLOY | release passed、deploy-plan | 回滚、健康检查、监控和环境是否明确 | 实际部署或本地交付记录 | `deploy-record.md` | PL |
| FEEDBACK | deploy-record、用户反馈、偏差记录 | 完成/未完成/暂缓/新需求是否清楚 | 复盘、归档、新 CR 入口 | `review.md` FEEDBACK、OpenSpec archive | 后续 CR |

## 下游不得猜测的内容

| 下游角色 | 不得猜测 | 应退回 |
| --- | --- | --- |
| PM | 业务方向、投入边界、是否属于本轮范围 | PL；需要业务补充时由 PL 记录 blocked 并请求用户补充 |
| Architect | 技术选型是否已接受、API base、数据来源、前端入口 | PL / 用户 / PM |
| Backend | API base、后端端口、数据存储策略、权限边界 | Architect / PL |
| Frontend | 后端端口、proxy target、API 字段、数据来源 | Architect / Backend |
| QA | 用户动作、覆盖 AC、是否允许 mock、前后端入口 | PM / Architect / PL |
| Security | 数据来源、权限边界、是否真实后端、是否 mock | Architect / QA / PL |
| Ops | 发布步骤、健康检查、回滚、E2E 证据 | PL / QA / Security |

## 开发期契约缺口回溯

开发、联调或 QA 阶段发现“实际需要但上游未定义”的内容时，不得只在当前角色本地补实现，也不得直接归咎最后执行者。发现者必须在当前 CR 的 `review.md` 追加 `Contract Gaps Discovered During Development` 记录，并由 PL 判定最早断链阶段。

| 字段 | 要求 |
| --- | --- |
| Gap ID | 稳定编号，例如 `GAP-001` |
| Discovered Stage | 发现阶段：`DEVELOPMENT`、`INTEGRATION`、`QA` |
| Symptom | 可观察现象，例如前端调用后端 404、页面缺数据、权限缺拒绝路径 |
| Missing Upstream Contract | 缺失的上游契约，例如 AC、API、runtime、数据、权限、测试计划 |
| Earliest Broken Stage | 最早断链阶段：`REQUIREMENT`、`DESIGN`、`DEVELOPMENT` |
| Return To | 需补救角色：PM、Architect、Backend、Frontend、QA、Security、PL |
| Required Backfill | 必须回写的文件，例如 `acceptance.md`、`docs/api/api.md`、`tasks.md`、`test-plan.md` |
| Verification Required | 关闭缺口前必须执行的验证 |
| Status | `open`、`returned`、`backfilled`、`verified`、`closed` |

关闭规则：

- 缺口状态不是 `closed` 时，不得推进 RELEASE_GATE。
- 缺口影响 `acceptance.md`、`tasks.md`、`docs/api/api.md`、`docs/runtime/runtime-contract.md` 或 `test-plan.md` 时，DESIGN_GATE 视为需要重新检查；PL 必须重新运行对应 readiness 命令。
- 下游可以提出补救草案，但不能替 PM/Architect/Backend 自行消除上游责任；必须留下回写证据和验证记录。
- 读接口、列表接口、查询状态接口和详情接口属于前端消费契约；只定义创建/更新/删除，不足以说明 CRUD 能闭环。

## REQUIREMENT 完整性最小检查

PM 在 REQUIREMENT 阶段至少要完成以下检查，避免把缺口直接带入 DESIGN：

| 检查项 | 要求 |
| --- | --- |
| R/C/U/D 完整性 | 实体型需求默认检查 `Read`、`Create`、`Update`、`Delete` 四类动作；不存在的动作必须写不做原因 |
| 用户可见结果 | 每个关键 AC 必须说明用户看什么、在哪里看、何时刷新或验证结果 |
| 页面 / API 对应 | 存在前端或管理端页面时，必须标出对应页面、组件或菜单入口 |
| 环境敏感项 | 涉及公网、CORS、代理、端口、回调、Webhook、上传下载时，必须标记为 runtime 敏感需求 |
| 验收可测性 | AC 必须能区分本地通过、联调通过和交付通过，不能只写“功能正常” |

## 推进前检查

阶段推进前，PL 至少检查：

1. 上游输入契约是否存在。
2. 输入审核是否记录在 `review.md` 或对应事实文档。
3. 本阶段新增契约是否写入规范路径。
4. 输出契约是否能被下游直接消费。
5. 下游不得猜测项是否仍有空白。
