# OpenSpec Agent 规则

根目录 `../AGENTS.md` 是所有 Agent 的硬边界。本文件只补充 OpenSpec 目录内的写作规则。

- `openspec/specs/` 描述归档后已经稳定的约定行为。
- `openspec/changes/<change-name>/` 描述实现前的拟议变化。
- `specs/**/spec.md` 必须聚焦可观察行为，并使用 `### Requirement:` 和 `#### Scenario:`。
- 实现细节、库选择、文件清单和执行顺序写入 `design.md` 或 `tasks.md`，不要写进行为规格。
- `tasks.md` 是实现任务主源，记录任务、负责人 Agent、允许写入范围、验证方式和回滚说明。
- Red/Green 记录、测试报告、安全审查、部署记录、审批和 Agent 日志等 workflow 证据写入 `../workflow/changes/<CR-ID>/`。
