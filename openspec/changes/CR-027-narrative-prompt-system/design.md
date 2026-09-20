# CR-027 Design: 分层 Prompt 叙事引擎系统

## Overview

- 将现有 NarrativeEngine 的简单 Prompt 拼接升级为六层结构化 Prompt 系统
- 新增 Lorebook 世界知识库（基础 CRUD + 场景标签注入）
- 新增场景配置系统（Node 级场景-标签绑定）
- 扩展 NPC 人物内核（desire/fear/secret 三字段）
- 新增 PromptBuilder 六层拼接引擎 + TokenBudgetController（2300 tokens 上限）
- 新增前端管理界面（Lorebook/场景配置/NPC 编辑，最小可用）
- 降级策略：单层异常用空字符串，整体异常回退现有简单 Prompt

## Technical Approach

- PromptBuilder 作为纯 Service，只读依赖 LorebookService / MemoryService / SceneConfigService
- 六层拼接顺序固定：L1 全局规则 → L2 世界知识 → L3 NPC 档案 → L4 记忆 → L5 叙事导演 → L6 玩家输入
- Token 计数使用 tiktoken cl100k_base 编码；超预算时按 token 反向解码截断，保证 UTF-8 安全
- Lorebook 匹配采用标签数组交集（MVP），按 priority DESC 排序
- LLM Gateway 新增 generate_with_system(system_prompt, user_prompt) 方法
- NarrativeEngine._generate_validated_dialogue 改用 PromptBuilder，保留原签名不变
- 新表 lorebook_entries（软删除 status 字段）、scene_configs（node_id UNIQUE）
- characters 表新增 desire/fear/secret TEXT nullable 列
- Admin 前端复用现有 admin 工程 + Naive UI，新增三个路由

## Technology Decisions

| Decision | Selected | Status | Evidence |
|----------|----------|--------|----------|
| Token 计数库 | tiktoken cl100k_base | Accepted | 用户确认 Q-003 |
| Lorebook 标签匹配 | 数组交集（MVP） | Not Required | 纯逻辑实现，无需长期架构决策 |
| LLM 调用方式 | system+user 双消息 | Not Required | 现有 LLM Gateway 扩展，无需独立 ADR |

## Document Sync

| Target Doc | Status | Summary / Evidence |
|------------|--------|--------------------|
| `docs/architecture/architecture.md` | Synced | 新增 PromptBuilder/LorebookService/SceneConfigService/TokenBudgetController 模块 + 组装流程图 + 降级策略 |
| `docs/api/api.md` | Synced | 新增 8 个管理端接口（Lorebook 5 + SceneConfig 3）+ Character 扩展字段 |
| `docs/database/database.md` | Synced | 新增 lorebook_entries/scene_configs 表 + characters 扩展 desire/fear/secret |
| `docs/security/security.md` | Synced | 新增 Admin 权限校验 + 输入验证 + NPC secret 敏感性 |
| `docs/decisions/decisions.md` | Not Required | 本轮无新增 Accepted ADR；tiktoken 选型为 Proposed 状态 |
| `docs/runtime/runtime-contract.md` | Synced | 新增 CR-027 端点列表 + Browser E2E 命令/用户动作 + Mock Policy |
