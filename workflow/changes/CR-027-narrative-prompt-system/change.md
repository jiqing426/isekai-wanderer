# CR-027: 分层 Prompt 叙事引擎系统

## 变更目标
构建完整的分层 Prompt 叙事引擎，实现六层 Prompt 动态拼接（全局规则 → 世界观 → NPC档案 → 动态记忆 → 叙事导演 → 玩家输入），包含 Lorebook 世界知识库、场景配置系统、NPC 人物内核扩展。

## 影响范围
- 后端：新增 Lorebook 系统、场景配置系统、Prompt 拼接引擎；修改 Character 模型、Chat 服务
- 前端：新增 Lorebook 管理界面、场景配置界面；修改角色编辑页面
- 数据库：新增 lorebook_entries、scene_configs 表；修改 characters 表
- API：新增 Lorebook/场景 CRUD 接口；修改 Chat 接口

## 成功标准
- 六层 Prompt 按顺序正确拼接
- Lorebook 支持按场景标签智能注入
- NPC 档案包含渴望/恐惧/秘密字段
- Token 预算控制在 2300 tokens 以内

## 功能清单
1. Lorebook 世界知识库系统
2. 场景配置系统
3. NPC 人物内核扩展（personality_traits）
4. Prompt 拼接引擎（六层结构）
5. Token 预算控制器
6. 前端管理界面

## 风险
- Prompt 过长导致生成质量下降
- Lorebook 检索结果不相关
- Token 预算超限

## 来源
用户直接需求（2026-07-31）

## 创建时间
2026-07-31T17:09:00+08:00

## 优先级
P0 - 核心叙事能力

## 前置依赖
CR-005（TTS 集成）完成后开始
