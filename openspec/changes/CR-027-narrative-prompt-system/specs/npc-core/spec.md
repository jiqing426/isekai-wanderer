# Spec: NPC 人物内核扩展

### Requirement: NPC 内在驱动字段

#### Scenario: Character 表新增 desire/fear/secret 字段
- **Given** 数据库迁移执行成功
- **Then** characters 表新增 desire (text, nullable)、fear (text, nullable)、secret (text, nullable) 三个字段
- **And** 已有角色三个字段默认为 NULL

#### Scenario: 管理员配置 NPC 内在驱动
- **Given** 管理员在 NPC 编辑页
- **When** 填写某角色的渴望="被认可"、恐惧="被遗忘"、秘密="其实是异世界人"
- **Then** 数据存入 characters 表对应字段
- **And** 下次 Prompt 拼接时注入模块3

#### Scenario: NPC 内在驱动注入 Prompt
- **Given** 角色 desire="被认可", fear="被遗忘", secret="其实是异世界人"
- **When** PromptBuilder 构建模块3（NPC档案）
- **Then** Prompt 中包含：
  - "内在渴望：被认可"
  - "深层恐惧：被遗忘"
  - "隐藏秘密：其实是异世界人"

#### Scenario: NPC 内在驱动为空时正常降级
- **Given** 角色 desire/fear/secret 均为 NULL
- **When** PromptBuilder 构建模块3
- **Then** 模块3 不包含内在驱动部分
- **And** 其他字段（name/traits/speak_style）正常注入

### Requirement: NPC 编辑页

#### Scenario: NPC 编辑页显示内在驱动区域
- **Given** 管理员进入 NPC 编辑页
- **Then** 页面显示"渴望"、"恐惧"、"秘密"三个文本输入框
- **And** 输入框预填当前值（可为空）

#### Scenario: NPC 编辑页保存内在驱动
- **Given** 管理员填写完渴望/恐惧/秘密
- **When** 点击保存
- **Then** 调用 PUT /characters/{id} 更新字段
- **And** 页面显示保存成功提示
