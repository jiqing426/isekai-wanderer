# CR-027: 分层 Prompt 叙事引擎系统

- 目标：构建六层分层 Prompt 叙事引擎，实现 Lorebook 世界知识库、场景配置、NPC 内在驱动和 Token 预算控制，解决当前 Prompt 结构混乱、NPC 全知、剧情单调等问题
- 成功标准：六层 Prompt 按顺序正确拼接，总 Token ≤ 2300；Lorebook CRUD 可用，场景标签注入正常；NPC 渴望/恐惧/秘密字段可配置并注入 Prompt；Token 超预算时自动截断，降级方案可用；前端管理界面可完成基础配置

## 变更类型
功能增强（Feature Enhancement）

## 变更描述
将叙事引擎的 Prompt 构建从扁平结构升级为六层分层系统，新增 Lorebook 世界知识库、场景配置、NPC 内在驱动和 Token 预算控制。

## 变更原因
- 当前 Prompt 结构混乱，难以维护和调试
- 无世界知识库，世界观信息硬编码
- NPC 人设扁平，缺少内在驱动
- 无 Token 预算控制，容易超限

## 影响范围
- 数据库：新增 lorebook_entries、scene_configs 表；Character 表新增 desire/fear/secret
- 后端：新增 LorebookService、SceneConfigService、PromptBuilder、TokenBudgetController
- 前端：新增 Lorebook/场景/NPC 管理页
- API：新增 Lorebook/Scene/NPC 相关接口
- NarrativeEngine 需重构 Prompt 构建逻辑

## 主责角色
- PM: 需求分析
- Architect: 架构设计
- Backend: 服务实现、API、数据库迁移
- Frontend: 管理界面
- QA: 测试验证

## 前置条件
- PRE-08: Lorebook 数据结构设计（建议默认：纯文本 + 标签数组）
- PRE-09: 场景配置与剧本关联模型（建议默认：Node 级绑定）
- PRE-10: Token 预算分配方案（已确认：200+500+300+800+300+200=2300）

## 风险
- 数据库迁移影响现有数据
- Prompt 重构可能影响现有对话质量
- Token 截断可能导致信息丢失

## 不做范围
- Lorebook 智能检索优化
- 动态记忆向量检索增强
- 多语言 Prompt
- Prompt 可视化编辑器
- Token 用量统计与计费
