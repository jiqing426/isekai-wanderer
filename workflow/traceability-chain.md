# 验收追踪链

本文定义从 PRD 到部署记录的一以贯之追踪机制。任何功能、修复或高风险变更都必须能沿同一条证据链追溯，不能只用“已完成”“已测试”或 Agent 自述作为交付结论。

## 追踪链主线

```text
原始 PRD / 用户输入
  -> REQ-* 需求编号
  -> AC-* 验收编号
  -> 设计落点
  -> OpenSpec Task
  -> allowed_write_scope
  -> 实现文件
  -> 测试用例产物
  -> Red / Green 记录
  -> QA 覆盖复核
  -> Release 证据
  -> Deploy 记录
```

## 每一段必须回答的问题

| 链路段 | 必须回答 | 主责 |
| --- | --- | --- |
| PRD -> REQ | 这条需求来自用户输入的哪一段？是否属于本 CR 范围？ | PM |
| REQ -> AC | 这条需求如何被写成可测试的用户行为或系统结果？ | PM |
| AC -> Design | 哪个模块、页面、API、数据或运行契约承接该验收项？ | Architect |
| Design -> Task | 哪个 OpenSpec Task 负责实现？任务是否有 owner、验证和回滚？ | Architect / PL |
| Consumer -> API Contract | 哪个前端/管理端页面、组件、测试或外部调用方会消费该 API？读、写、列表、详情和状态查询是否全量覆盖？ | Architect / Backend / Frontend |
| Task -> allowed_write_scope | 允许修改哪些文件？是否禁止跨模块乱改？ | Architect / PL |
| Task -> Code | 实际改了哪些文件？是否在允许范围内？ | BE / FE / Admin / AI |
| Code -> Test | 哪个测试用例证明代码行为？命令是否可重复？ | BE / FE / Admin / AI |
| Test -> Red / Green | Red 是否发生在业务代码前？Green 是否引用同一测试产物并真实通过？ | 实现 Agent / PL |
| Green -> Acceptance | `acceptance.md` 是否更新状态、覆盖状态、实现证据和测试证据？ | 实现 Agent / PL |
| Acceptance -> QA | QA 是否逐 AC 独立复核，而不是只看实现 Agent 自述？ | QA |
| QA -> Release | Release 证据是否包含 CI/CD、Delivery E2E / Runtime Smoke、Browser Interaction E2E 和 `Mock API=no`？ | QA / PL |
| Release -> Deploy | 发布计划、回滚、健康检查、监控和实际部署记录是否完整？ | Ops |

## 断链处理规则

- 任一 P0/P1 AC 缺少 `实现证据`、`测试用例 / 验证命令`、`覆盖状态` 或 `PL 处理`，不得进入 RELEASE_GATE passed。
- 任一任务缺少 `allowed_write_scope`、测试产物、Red/Green 记录或 Agent Run Log，不得标记为 Done / Completed / Delivered。
- 任一发布证据没有写清 `Frontend URL`、`Backend URL`、`API / Proxy Path`、`Mock API` 和覆盖 AC，不得作为 Delivery E2E 或 Browser Interaction E2E。
- 任一开发期契约缺口未关闭，或缺口要求回写的 `acceptance.md`、`tasks.md`、`docs/api/api.md`、`docs/runtime/runtime-contract.md`、`test-plan.md` 未同步，不得进入 RELEASE_GATE passed。
- 如果发现链路中某一段为空，下游不得自行猜测补齐；必须退回该段主责角色补充。

## 最低追踪检查表

| 检查项 | 合格标准 |
| --- | --- |
| 每个 P0/P1 AC 都能追到 REQ | `acceptance.md` 中 `需求编号` 非空，并能回到 OpenSpec spec |
| 每个 AC 都有设计落点 | `设计落点` 指向模块、API、页面、数据或 runtime contract |
| 每个 AC 都有任务 | `OpenSpec Task` 非空，并在 `tasks.md` 存在 |
| 每个任务都有允许写入范围 | `allowed_write_scope` 覆盖实际改动文件 |
| 每个任务都有测试产物 | `test-plan.md` 的 Test Case Artifacts 存在 |
| 每个任务都有 Red / Green | Red 失败记录和 Green 通过记录引用同一测试产物 |
| 每个 AC 都有 QA 复核 | `review.md` 的 QA 覆盖复核表逐 AC 记录 |
| 发布证据不使用 mock | Delivery E2E / Browser E2E 均记录 `Mock API=no` |
| 每个开发期契约缺口都关闭 | `review.md` 的 Contract Gaps 表状态为 `closed`，且 Required Backfill 指向的文件已回写 |
