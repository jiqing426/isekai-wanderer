# Toolchain

本文记录项目工具链选择、接入边界、输入输出、验证要求和文档同步规则。

工具链可以按项目替换，但必须满足统一工程约束：生成结果可审查、可验证、可回滚，不绕过模块边界、安全边界或文档同步规则。

## 工具矩阵

| 领域 | 默认工具 | 可替换工具 | 输入 | 输出 | 验证要求 | 文档同步 |
| --- | --- | --- | --- | --- | --- | --- |
| 需求拆解 | `skills/pm` | 项目级 PM skill | `docs/prd/prd.md` | 已确认需求事实文档更新 | 搜索旧引用、检查待确认项 | `../../PROJECT.md`、`../status/feature-status.md`、`../testing/testing.md`、`../security/security.md`、`../toolchain/toolchain.md` |
| 技术设计 | `skills/architect` | 项目级 Architect skill | 需求关口结论 | 架构、API、数据库、安全预审和决策文档 | 设计关口检查 | `../architecture/architecture.md`、`../api/api.md`、`../database/database.md`、`../security/security.md`、`../decisions/decisions.md` |
| 前端设计 | 待确认 | Penpot、Figma 或其它设计工具 | PRD、品牌规范、交互稿 | 页面结构、组件约束、设计资产 | 视觉检查、响应式检查、可访问性检查 | `../architecture/architecture.md`、`../status/feature-status.md`、`../testing/testing.md` |
| 前端开发 | 待确认 | Codex、其它 Agent、组件 CLI | PRD、API 契约、设计稿 | 前端代码和组件 | 单测、浏览器验证、截图检查 | `../api/api.md`、`../status/feature-status.md`、`../testing/testing.md` |
| 后端开发 | 待确认 | Codex、其它 Agent、框架 CLI | PRD、API 契约、数据模型 | API、服务代码、任务逻辑 | 单测、集成测试、契约测试 | `../api/api.md`、`../database/database.md`、`../testing/testing.md` |
| 数据库 | 待确认 | ORM CLI、迁移工具、数据校验工具 | 数据模型、迁移需求 | migration、schema、索引 | 迁移演练、回滚验证、数据校验 | `../database/database.md`、`../operations/operations.md` |
| 测试 | 待确认 | Playwright、Vitest、Jest、pytest、契约测试工具 | 验收标准、API 契约、用户流程 | 测试代码和报告 | 本地或 CI 可重复运行 | `../testing/testing.md`、`../status/feature-status.md` |
| 部署 | 待确认 | Docker、Compose、Kubernetes、Terraform、CI/CD | 运行配置、环境变量、制品 | 部署配置和发布流程 | 健康检查、回滚演练、日志检查 | `../operations/operations.md`、`../security/security.md` |
| 浏览器验证 | 待确认 | Playwright、Browser 插件、其它自动化工具 | URL、用例、截图基线 | 截图、交互结果、验证报告 | 桌面和移动视口通过 | `../testing/testing.md`、`../status/feature-status.md` |

## 接入规则

- 工具选择必须说明适用范围、输入、输出、失败条件和验证方式。
- 工具生成代码或配置后，必须提交可审查结果，不允许只提交不可追溯的生成产物。
- 工具不得直接写入真实密钥、生产数据、客户数据或私有凭证。
- 工具不得绕过 `backend/`、`frontend/`、`admin/`、`deploy/` 的模块边界。
- 工具输出影响 API、数据库、部署、测试、安全或功能状态时，必须同步对应文档。
- 高风险工具操作，例如生产部署、破坏性迁移、批量删除、权限变更，必须先获得明确确认。

## 选择记录

| 工具 | 领域 | 状态 | 选择原因 | 替代方案 | 验证方式 | 负责人 |
| --- | --- | --- | --- | --- | --- | --- |
| 待确认 | 待确认 | Proposed | 待确认 | 待确认 | 待确认 | 待确认 |

## 维护规则

- 本文记录“工具怎么接入工程流程”，不替代 `../operations/operations.md` 的部署事实，也不替代 `../testing/testing.md` 的测试策略。
- 具体可执行脚本放入 `../../tools/` 或对应 skill 的 `scripts/` 目录。
- AI 使用工具的稳定工作流放入 `../../skills/` 下的项目级 skill。
- 长期不可逆的工具选型或重大替换，应同步 `../decisions/decisions.md`。
