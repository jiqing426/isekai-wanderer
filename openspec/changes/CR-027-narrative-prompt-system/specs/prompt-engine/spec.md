# Spec: Prompt 拼接引擎

### Requirement: 六层结构化拼接

#### Scenario: 正常拼接六层 Prompt
- **Given** 各层数据均已就绪：
  - 模块1：全局规则（~200 tokens）
  - 模块2：Lorebook 上下文（~500 tokens）
  - 模块3：NPC 档案（~300 tokens）
  - 模块4：记忆上下文（~800 tokens）
  - 模块5：叙事导演指令（~300 tokens）
  - 模块6：玩家输入（~200 tokens）
- **When** PromptBuilder.build() 被调用
- **Then** 返回完整 system_prompt（模块1-5拼接）和 user_prompt（模块6）
- **And** 总 Token 数 ≤ 2300

#### Scenario: 拼接顺序固定
- **Given** PromptBuilder 执行拼接
- **Then** system_prompt 按以下顺序拼接：
  1. 全局基础规则
  2. 【世界知识】+ Lorebook 内容
  3. 【NPC档案】+ 角色信息（含渴望/恐惧/秘密）
  4. 【记忆】+ 检索结果
  5. 【叙事要求】+ 导演指令
- **And** user_prompt 为：【玩家说】+ 玩家输入 + 回复指令

#### Scenario: 各层独立可测试
- **Given** 单元测试调用 PromptBuilder 的各层构建方法
- **When** 单独测试某层（如模块3 NPC档案）
- **Then** 该层输出仅包含该层数据
- **And** 不依赖其他层的数据

### Requirement: Prompt 降级

#### Scenario: Lorebook 服务不可用时降级
- **Given** LorebookService 抛出异常
- **When** PromptBuilder 请求 Lorebook 上下文
- **Then** 模块2 使用空字符串
- **And** 其他层正常拼接
- **And** 记录 warning 日志

#### Scenario: 记忆服务不可用时降级
- **Given** MemoryService 抛出异常
- **When** PromptBuilder 请求记忆上下文
- **Then** 模块4 使用空字符串
- **And** 其他层正常拼接

#### Scenario: 全部降级到简单 Prompt
- **Given** PromptBuilder 整体构建失败
- **When** NarrativeEngine 捕获异常
- **Then** 降级使用现有 build_narrative_prompt() 简单拼接
- **And** 记录 error 日志

### Requirement: 与现有 NarrativeEngine 集成

#### Scenario: NarrativeEngine 使用新 PromptBuilder
- **Given** CR-027 部署完成
- **When** NarrativeEngine.generate_dialogue() 被调用
- **Then** 使用 PromptBuilder.build() 替代现有 build_narrative_prompt()
- **And** LLM 调用使用新的 system_prompt + user_prompt 格式

#### Scenario: 现有角色数据兼容
- **Given** 已有角色无 desire/fear/secret 字段
- **When** PromptBuilder 构建模块3
- **Then** 使用现有 personality/traits/speak_style 数据
- **And** 内在驱动部分为空
