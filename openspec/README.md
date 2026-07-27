# OpenSpec

`openspec/` 是本模板的规格驱动主目录。每个正式新需求、行为变化、高风险修复或架构调整都必须进入一个独立 OpenSpec change。

## 目录结构

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
        │   └── capability/spec.md
        ├── design.md
        └── tasks.md
```

## 规则

- 一个正式需求对应一个独立 change，命名建议为语义化名称；如果绑定 CR，可使用 `CR-编号-语义名称`，例如 `CR-001-add-user-login`。
- `proposal.md` 先澄清为什么做、做什么、不做什么、成功标准和待澄清问题。
- 待澄清问题必须按 Q 编号在聊天里主动展示给用户，并在表中记录 `展示状态`；非阻塞 Open 问题也要记录暂缓或非阻塞依据。
- `specs/**/spec.md` 使用 Requirement + Scenario 表达可验收规格。
- `design.md` 和 `tasks.md` 必须在阻塞型待澄清问题关闭后再生成或确认。
- `tasks.md` 是实现任务主源，记录任务编号、负责人、允许写入范围、验证方式和回滚说明。
- 完成后将稳定规格沉淀到 `openspec/specs/`，并将长期事实同步到 `PROJECT.md` 和 `docs/`。
- 归档顺序：先把稳定 Requirement / Scenario 合并到 `openspec/specs/`，再确认 `PROJECT.md` 和 `docs/` 已同步，最后将完成的 change 移动到 `openspec/changes/archive/`。

## 与 workflow 的边界

- `openspec/` 是规格事实和变化说明的主源。
- `workflow/` 是状态机、权限、TDD、测试、安全、部署、关口结论和 Agent 执行证据。
- `docs/prd/prd.md` 只保留产品输入摘要，不作为推进需求的唯一依据。
