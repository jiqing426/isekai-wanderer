# 关口策略

`workflow/gates/` 只保存可复用关口策略。运行时关口结论属于当前 CR 证据包，通常写在 `workflow/changes/<CR-ID>/review.md`。

## 运行时记录

每个 CR 的 review 文件都应包含 `关口审批` 表：

| 关口 | 主责 | 评审人 | Readiness 命令 | 结论 | 下一阶段 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| INIT | ceo | pl | manual | draft | TRIAGE | 待填写 |
| REQ_GATE | pl | pl | `python tools/check-gate-readiness.py --gate requirement --change <change-name> --change-id <CR-ID>` | draft | DESIGN | 待填写 |
| DESIGN_GATE | pl | architect | `python tools/check-gate-readiness.py --gate design --change <change-name> --change-id <CR-ID>` | draft | DEVELOPMENT | 待填写 |
| INTEGRATION | pl | pl | **手动验证**：路由链完整性 + E2E 冒烟 + 前后端集成 | draft | QA | 必须验证完整用户路径和部署可运行 |
| RELEASE_GATE | pl | qa / security / ops | `python tools/check-gate-readiness.py --gate release --change <change-name> --change-id <CR-ID>` | draft | DEPLOY | 待填写 |

## 规则

- 关口结论变成 `passed` 前必须有人工确认。
- 人工确认不能替代需求、设计或发布关口的 readiness 检查。
- 需求关口 readiness 前，当前 OpenSpec change 的所有待澄清问题、待确认项和关键假设必须已按 Q 编号主动展示给用户，并记录 `展示状态`。
- Readiness 检查失败必须记录为 `returned` 或 `blocked`，并写明负责人、原因和预期修复。
- REQ_GATE 的评审人是 PL，表示 PL 独立审查 PM 的需求交付物；不通过时退回 REQUIREMENT/PM 补需求；业务补充需要用户输入时由 PL 记录 blocked。
- 需求关口必须检查 `acceptance.md` 的 `REQ-*` / `AC-*` 编号、优先级、覆盖状态和未覆盖原因；未编号或缺覆盖状态不得通过。
- 任务完成必须先有开发覆盖声明；发布关口必须先有 QA 覆盖复核和 PL 人工验收范围。`not_covered` 不能进入发布通过结论。
- DESIGN_GATE 必须有 `docs/runtime/runtime-contract.md`，明确前端入口、后端地址、API base、Vite proxy、健康检查、Delivery E2E 命令、Browser Interaction E2E 命令/用户动作、API 文档、数据库/存储契约和 mock policy。
- DESIGN_GATE 必须检查前端/管理端消费方与 API 契约是否闭环：凡用户界面需要展示、刷新、查询状态、查看详情或列表的数据，都必须在 `acceptance.md`、`docs/api/api.md`、`tasks.md` 和 `test-plan.md` 中有对应项。只写创建/更新/删除不等于 CRUD 闭环。
- RELEASE_GATE 必须有 Delivery E2E / Runtime Smoke 结果，从真实前端入口访问真实后端；mock API、组件级替身或静态假数据不能作为发布证据。
- 存在前端页面、管理端页面或用户交互 AC 时，RELEASE_GATE 还必须有 Browser Interaction E2E 结果，证明真实浏览器执行用户动作；API/fetch/curl/Runtime Smoke 不能替代。Browser Interaction E2E 必须保留首页、AC 动作结果和失败上下文截图或 trace，并在 `test-report.md` 写明相对路径。
- LLM Agent 不得自批关口；没有记录审批时，不得推进 `workflow/state.md`。
- 关口记录是 CR 证据，不是长期产品事实或架构事实。
- `review.md` 存在未关闭的 `Contract Gaps Discovered During Development` 时，不得通过 RELEASE_GATE；若缺口要求回写设计产物，必须重新运行 DESIGN_GATE readiness。

## INTEGRATION 关口检查清单

INTEGRATION 关口必须在 DEVELOPMENT 完成后、QA 开始前通过，检查以下内容：

### 路由链完整性（前端 SPA）

- [ ] 所有前端页面的导航链路完整，不存在断链（404 / 白屏）
- [ ] 完整用户路径可走通：打开入口 → 进入关键业务页面 → 执行核心操作 → 验证结果
- [ ] 侧边栏/顶部导航中的所有菜单项都有对应路由
- [ ] URL 参数（如 `?workspaceId=`、`?view=board`）正确处理

### E2E 冒烟验证

- [ ] `tests/e2e/smoke.test.ts` 全部通过
- [ ] E2E 测试使用环境变量配置端口，不硬编码
- [ ] 前端浏览器测试真正打开页面并验证交互，不仅 API 调用
- [ ] Delivery E2E 从真实前端入口访问真实后端，例如 `<frontend_origin>/api/v1/health`
- [ ] Delivery E2E 记录 `Mock API=no`；使用 mock 的测试不得作为发布证据
- [ ] Browser Interaction E2E 记录真实浏览器、用户动作、API/Proxy Path、证据链接和 `Mock API=no`
- [ ] E2E 截图或 trace 已归档：`home-ready.png`、`ac-action-result.png`，失败时有 `failure-context.png` 或 trace

### Docker 部署可运行

- [ ] `docker compose build` 成功（所有 Dockerfile 存在）
- [ ] `docker compose up -d` 成功，所有服务 Up
- [ ] 后端 `/health` 返回 200
- [ ] 前端页面可访问

### 前后端集成

- [ ] 前端 API 服务层与后端路由完全对接，无 NOT_FOUND
- [ ] 前端页面展示所需的读接口、列表接口、详情接口、状态查询接口均在 `docs/api/api.md` 和 `tasks.md` 中有记录
- [ ] 前端测试在 mock 环境通过，且有独立的 API 集成验证
- [ ] 前端业务数据只通过 `docs/api/api.md` 记录的 API 访问，不直连数据库、JSON 数据文件或未记录数据源
