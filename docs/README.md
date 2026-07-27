# Docs

项目工程事实目录。顶层只保留本索引，具体 Markdown 必须放到相关子目录中，避免文档散落。项目级总体事实维护在根目录 `../PROJECT.md`。

## 必备目录

- `architecture/architecture.md`：模块边界、依赖方向、核心流程和架构约束。
- `api/api.md`：API、错误码、鉴权、分页、兼容性和契约变更规则。
- `database/database.md`：数据模型、迁移、索引、备份、数据保留和敏感数据规则。
- `status/feature-status.md`：功能状态、缺口、TODO 和已知限制。
- `operations/operations.md`：部署、运行时、开发、评审、发布和回滚规则。
- `testing/testing.md`：测试分层、命令、覆盖要求和测试数据。
- `toolchain/toolchain.md`：工具链选择、接入边界、输入输出和验证要求。
- `ai/ai-collaboration.md`：AI 协作上下文、边界和输出要求。
- `security/security.md`：安全开发、密钥和敏感数据规范。
- `decisions/decisions.md`：ADR 和重要工程决策规则。

## 工作流

- `../workflow/state.md`：当前阶段、状态、负责人、关口和流转日志。
- `../workflow/workflow.config.yaml`：状态机、阶段主责、交付物和允许流转。
- `../workflow/agents.config.yaml`：角色 Agent 和对应 skill。
- `../workflow/permissions.config.yaml`：角色读写边界。
- `../workflow/execution.config.yaml`：LLM 执行约束、任务单要求、关口通过条件和人工确认条件。
- `../openspec/changes/<CR-ID>-<change-name>/proposal.md`：本次需求的动机、范围、成功标准和待澄清问题。
- `../openspec/changes/<CR-ID>-<change-name>/specs/**/spec.md`：本次需求的 Requirement 和 Scenario 规格。
- `../openspec/changes/<CR-ID>-<change-name>/design.md`：本次需求的 OpenSpec 技术设计。
- `../openspec/changes/<CR-ID>-<change-name>/tasks.md`：本次需求的 OpenSpec 实现任务。
- `../workflow/changes/<CR-ID>/change.md`：变更入口和影响评估。
- `../workflow/changes/<CR-ID>/test-plan.md`：测试先行计划。
- `../workflow/changes/<CR-ID>/acceptance.md`：需求、设计、实现、测试之间的验收追踪。
- `../workflow/changes/<CR-ID>/review.md`：阶段结论、关口审批、风险、联调和归档记录。
- `../workflow/agent-run-template.md`：Agent 执行日志模板。

## 需求输入

- `prd/prd.md`：产品需求输入和待拆解内容。它不作为最终工程事实源，只在 PM 做需求整理、拆解或同步时读取；已确认的项目总体事实必须同步到 `../PROJECT.md`，其它事实同步到上面的对应文档。

## 维护规则

- 不在 `docs/` 顶层新增主题 Markdown；新增内容必须进入相关目录。项目总体事实只更新根目录 `PROJECT.md`。
- 除 `README.md`、`AGENTS.md`、`SKILL.md` 等约定入口文件外，主题文档统一使用小写 kebab-case。
- 只保留经典必备目录。领域、历史、模式、评审、供应链、版本等专题目录等项目真实需要时再创建。
- 每类事实只维护一个主位置。其它文档需要引用时只放链接或摘要，不重复维护完整内容。
- 代码与文档冲突时，以当前代码为准，并在同次变更中同步文档或记录未同步原因。
