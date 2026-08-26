# Spec: Token 预算控制器

### Requirement: 各层 Token 预算分配

#### Scenario: 默认预算分配
- **Given** TokenBudgetController 初始化
- **Then** 各层默认预算为：
  - global_rules: 200 tokens
  - lorebook: 500 tokens
  - npc_profile: 300 tokens
  - memory: 800 tokens
  - narrative_director: 300 tokens
  - user_message: 200 tokens
- **And** 总预算 = 2300 tokens

#### Scenario: 单层超预算时截断
- **Given** Lorebook 上下文实际为 600 tokens（预算 500）
- **When** TokenBudgetController.truncate_to_budget("lorebook", text) 被调用
- **Then** 文本被截断到 500 tokens
- **And** 截断后文本可正常解码

#### Scenario: 总预算超限时报告
- **Given** 各层实际 Token 总和为 2500（超限 200）
- **When** TokenBudgetController.validate_total_budget() 被调用
- **Then** 返回 ok=false, total_tokens=2500, over_by=200
- **And** layer_details 中显示各层具体超限情况

### Requirement: Token 计数

#### Scenario: 中英文混合文本 Token 计数
- **Given** 文本包含中文和英文混合内容
- **When** TokenBudgetController.count_tokens(text) 被调用
- **Then** 返回准确的 Token 数（使用 tiktoken cl100k_base 编码）

#### Scenario: 空文本 Token 计数
- **Given** 文本为空字符串
- **When** count_tokens("") 被调用
- **Then** 返回 0

### Requirement: 预算报告

#### Scenario: 生成预算报告
- **Given** 各层文本已拼接
- **When** TokenBudgetController.get_budget_report() 被调用
- **Then** 返回格式化报告，包含：
  - 总 Token 数 / 总预算
  - 状态（OK 或 OVER BUDGET）
  - 各层 Token 数 / 预算 / 状态
