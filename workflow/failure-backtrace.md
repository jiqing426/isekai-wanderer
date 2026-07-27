# 失败倒查链

本文定义交付失败后的倒果为因追溯机制。发现结果问题时，不直接把问题丢给最后一个执行者，而是从失败现象向上游逐层检查：发布证据、QA、集成、实现、设计、需求和 PRD 是否断链。

## 通用倒查步骤

```text
结果问题
  -> Release Gate 是否应该拦截
  -> QA 是否独立复核并分类记录
  -> Integration 是否验证真实用户路径
  -> 实现角色是否按 runtime/task/test-plan 执行
  -> Architect 是否给出可执行运行契约和任务
  -> PM 是否写清可测试 AC 和用户动作
  -> PRD / INIT 是否明确本轮范围
```

## 常见事故倒查表

| 失败现象 | 第一步查 | 第二步查 | 上游根因可能在 | 退回原则 |
| --- | --- | --- | --- | --- |
| 首页打不开 | `test-report.md` 是否有 Browser Interaction E2E 和真实前端入口证据 | `runtime-contract.md` 的 frontend/proxy/backend/health 是否一致 | FE、BE、Architect、PL | 缺 Browser E2E 退 QA；入口/proxy 不一致退 FE/Architect；后端不可达退 BE |
| 功能漏做 | `acceptance.md` 覆盖状态和实现证据 | `tasks.md` 是否有对应 task 和 allowed_write_scope | PM、Architect、实现 Agent、PL | AC 未拆退 PM；无任务退 Architect；任务未做退实现 Agent |
| 前端需要的 API 缺失或 404 | `review.md` 是否登记 Contract Gap；`docs/api/api.md` 是否有对应读/写/列表/详情契约 | `acceptance.md` 是否把前端可见数据展示写成 AC，`tasks.md` 是否拆到对应 BE/FE 任务 | PM、Architect、Backend、Frontend、PL | AC 漏用户可见结果退 PM；API 漏契约退 Architect/Backend；前端调用未按契约退 Frontend；缺口未登记退发现者/PL |
| 测试有记录但无证明力 | `test-report.md` 是否分类记录覆盖 AC、Mock API 和证据链接 | `test-plan.md` 是否定义正确测试类型 | QA、Architect、PM | 类型不对退 QA；计划缺失退 Architect；AC 不可测退 PM |
| Mock 被当发布证据 | Delivery E2E / Browser E2E 是否记录 `Mock API=no` | API/DB/Runtime mock policy 是否一致 | QA、Security、PL、Architect | 发布证据退 QA/PL；安全放行错误退 Security |
| 任务越界改文件 | Agent Run Log 和 git diff 是否超出 allowed_write_scope | `tasks.md` 的 allowed_write_scope 是否清楚 | 实现 Agent、Architect、PL | 范围不清退 Architect；越界执行退实现 Agent |
| Agent 不响应或没按要求执行 | communication ledger 是否有 `sessions_send` ack | HR 群集 health 和模板覆盖是否通过 | HR、PL、对应角色 | ACK 缺失退 HR/PL；角色越界退 PL |
| 发布后才发现缺安全/权限 | `security-review.md` 是否检查权限拒绝、审计和敏感数据 | `docs/security.md`、API/DB/Runtime 是否同步 | Security、Architect、Backend/Admin | 审查缺失退 Security；设计缺失退 Architect |

## 首页打不开专项倒查

出现“功能都测了但首页打不开”时，按以下顺序倒查：

1. `test-report.md` 是否存在 `Browser Interaction E2E Results`。
2. Browser E2E 是否记录真实浏览器、用户动作、前端入口、后端地址、API / Proxy Path、覆盖 AC 和 `Mock API=no`。
3. `Delivery E2E / Runtime Smoke Results` 是否从 `frontend_origin` 经 proxy 或运行配置访问真实后端。
4. `review.md` 的 INTEGRATION 联调记录是否验证完整用户路径：打开入口 -> 进入关键页面 -> 执行核心操作 -> 验证结果。
5. `docs/runtime/runtime-contract.md` 是否在 DESIGN 阶段写清 frontend origin/port、backend origin/port、api_base_path、vite_proxy_target、health_endpoint。
6. FE 实现是否硬编码未记录端口，或绕过 API 读取 JSON / 未记录数据源。
7. BE 实现是否按 runtime contract 暴露 health 和业务 API。
8. PM 是否在 AC 里写清用户动作和可观察结果。

任何一步缺失，都不得把问题归为“已测但偶发”。必须退回对应阶段补证据或修复。

## 记录格式

发现失败时，在当前 CR 的 `review.md` 追加：

| 字段 | 内容 |
| --- | --- |
| failure_id | 例如 `FAIL-001` |
| symptom | 用户或系统观察到的失败现象 |
| affected_ac | 受影响 AC |
| first_failed_gate | 最早应该拦截但未拦截的阶段 |
| missing_contract | 缺失或错误的上游契约 |
| responsible_agent | 需补救的角色 |
| remediation | 修复或补证据动作 |
| verification_required | 修复后必须运行的命令或人工验证 |
| status | returned / blocked / fixed |

如果失败是在 DEVELOPMENT、INTEGRATION 或 QA 阶段发现的上游契约漏项，还必须同步填写 `Contract Gaps Discovered During Development` 表。失败倒查表说明“为什么漏”，Contract Gap 表说明“回写哪些前置契约、谁来关掉”。

## 证据等级

所有“已通过”“已验证”“可发布”都必须标注证据等级，避免把局部通过误判成交付通过。

| 等级 | 名称 | 定义 | 不能证明什么 |
| --- | --- | --- | --- |
| L1 | 本地通过 | localhost 或单机环境下功能可用，允许使用本地配置和开发入口 | 不能证明真实前后端集成、内网部署或公网访问可用 |
| L2 | 联调通过 | 真实前端、真实后端、真实 API / Proxy 链路可用，非 mock | 不能证明公网 origin、外网入口、生产代理或域名访问可用 |
| L3 | 交付通过 | 真实部署入口、真实运行拓扑、真实访问方式下可用；覆盖发布目标环境 | 才能作为 RELEASE_GATE 和交付结论的直接证据 |

规则：

- 如果证据只能达到 L1，不得写成“可发布”。
- 如果目标环境包含内网部署、公网访问、域名/IP 访问或跨域访问，至少需要对应环境下的 L3 证据。
- 失败倒查时必须先判断引用的证据等级是否足够，再判断责任归属。

## 禁止事项

- 不得只把失败归因给最后修改代码的角色。
- 不得用“已经测过”关闭失败，除非能指出对应测试类型、命令、证据链接和覆盖 AC。
- 不得用截图、口头描述或 Agent 自述替代 Browser Interaction E2E。
- 不得把 mock、fixture、MSW、静态数据或 mock 模型作为发布级修复证明。
- 不得只在开发阶段补代码而不回写前置契约；凡是影响 AC、任务、API、runtime、数据、权限或测试计划的补足，都必须追溯到对应上游文件。
