# CR-027 验收追踪

| 验收编号 | 需求编号 | 优先级 | 验收标准 | 覆盖状态 | 设计落点 | OpenSpec Task | 测试用例 / 验证命令 | 状态 |
|----------|----------|--------|----------|----------|----------|---------------|---------------------|------|
| AC-LORE-001 | REQ-LORE-001 | P0 | 管理员创建 Lorebook 条目（标题/内容/标签），存入数据库并在列表显示 | covered | T-001(lorebook_entries表) + T-002(LorebookService.create) + T-003(POST /lorebook) + T-007(LorebookManage.vue) | T-001, T-002, T-003, T-007 | `test_lorebook_service.py::test_create` + `cr027-lorebook.spec.ts` | Designed |
| AC-LORE-002 | REQ-LORE-001 | P0 | 管理员编辑/删除 Lorebook 条目，删除为软删除 | covered | T-002(LorebookService.update/soft_delete) + T-003(PUT/DELETE /lorebook/{id}) | T-002, T-003 | `test_lorebook_service.py::test_update_soft_delete` | Designed |
| AC-LORE-003 | REQ-LORE-001 | P1 | 管理员按标签筛选 Lorebook 条目 | covered | T-002(match_by_tags) + T-003(GET /lorebook?tag=) + T-007(筛选UI) | T-002, T-003, T-007 | `test_lorebook_service.py::test_match_by_tags` + `cr027-lorebook.spec.ts` | Designed |
| AC-LORE-004 | REQ-LORE-002 | P0 | 根据场景标签匹配 Lorebook 条目注入 Prompt，无匹配时返回空 | covered | T-002(match_by_tags) + T-006(PromptBuilder L2) | T-002, T-006 | `test_lorebook_service.py::test_match_empty` + `test_prompt_builder.py::test_l2_lorebook` | Designed |
| AC-SCENE-001 | REQ-SCENE-001 | P0 | 管理员为剧本 Node 配置场景（名称/标签/描述），存入 scene_configs 表 | covered | T-001(scene_configs表) + T-004(upsert) + T-005(PUT) + T-007(SceneConfig.vue) | T-001, T-004, T-005, T-007 | `test_scene_config_service.py::test_upsert` + `cr027-scene-config.spec.ts` | Designed |
| AC-SCENE-002 | REQ-SCENE-001 | P0 | 场景配置随 Node 自动加载，标签用于 Lorebook 匹配，描述注入模块2 | covered | T-006(PromptBuilder L2: get_by_node → tags → match_by_tags → 拼接) | T-006 | `test_prompt_builder.py::test_l2_scene_config` | Designed |
| AC-SCENE-003 | REQ-SCENE-001 | P1 | 未配置场景的 Node 使用空世界知识，不影响其他层 | covered | T-006(PromptBuilder: get_by_node=None → L2 空字符串) | T-006 | `test_prompt_builder.py::test_l2_no_scene` | Designed |
| AC-NPC-001 | REQ-NPC-001 | P0 | Character 表新增 desire/fear/secret 字段，迁移成功 | covered | T-001(Alembic 迁移: ALTER TABLE characters ADD COLUMN) | T-001 | `test_migrations_cr027.py::test_characters_columns` | Designed |
| AC-NPC-002 | REQ-NPC-001 | P0 | 管理员配置 NPC 内在驱动，数据存入数据库 | covered | T-006(Character model + PUT /characters/{id}) + T-007(CharacterEdit.vue) | T-006, T-007 | `test_narrative_engine_cr027.py::test_character_update` + `cr027-npc-internal.spec.ts` | Designed |
| AC-NPC-003 | REQ-NPC-001 | P0 | NPC 内在驱动注入 Prompt 模块3，为空时正常降级 | covered | T-006(PromptBuilder L3: 判空降级) | T-006 | `test_prompt_builder.py::test_l3_with_without_drive` | Designed |
| AC-PROMPT-001 | REQ-PROMPT-001 | P0 | 六层 Prompt 正常拼接，总 Token ≤ 2300 | covered | T-006(PromptBuilder.build + TokenBudgetController 校验) | T-006 | `test_prompt_builder.py::test_build_total_budget` | Designed |
| AC-PROMPT-002 | REQ-PROMPT-001 | P0 | 拼接顺序固定：全局规则→世界知识→NPC档案→记忆→叙事要求→玩家输入 | covered | T-006(PromptBuilder: 固定顺序 L1→L5, L6→user_prompt) | T-006 | `test_prompt_builder.py::test_build_order` | Designed |
| AC-PROMPT-003 | REQ-PROMPT-002 | P0 | Lorebook/记忆服务不可用时降级，其他层正常 | covered | T-006(PromptBuilder: try/except 各层，异常→空字符串 + warning) | T-006 | `test_prompt_builder.py::test_degradation_lorebook_memory` | Designed |
| AC-PROMPT-004 | REQ-PROMPT-002 | P1 | 全部降级到简单 Prompt，记录 error 日志 | covered | T-006(NarrativeEngine: 整体异常→回退简单拼接 + error 日志) | T-006 | `test_narrative_engine_cr027.py::test_full_degradation` | Designed |
| AC-PROMPT-005 | REQ-PROMPT-003 | P0 | NarrativeEngine 使用新 PromptBuilder，现有角色数据兼容 | covered | T-006(NarrativeEngine 改用 PromptBuilder; 无 desire/fear/secret 兼容) | T-006 | `test_narrative_engine_cr027.py::test_backward_compat` | Designed |
| AC-TOKEN-001 | REQ-TOKEN-001 | P0 | 默认预算分配正确（200+500+300+800+300+200=2300） | covered | T-006(TokenBudgetController: 默认预算字典) | T-006 | `test_token_budget.py::test_default_budget` | Designed |
| AC-TOKEN-002 | REQ-TOKEN-001 | P0 | 单层超预算时截断，截断后可正常解码 | covered | T-006(TokenBudgetController.truncate_to_budget) | T-006 | `test_token_budget.py::test_truncate_utf8_safe` | Designed |
| AC-TOKEN-003 | REQ-TOKEN-001 | P1 | 总预算超限时报告准确 | covered | T-006(TokenBudgetController.validate_total_budget) | T-006 | `test_token_budget.py::test_over_budget_report` | Designed |
| AC-ADMIN-001 | REQ-ADMIN-001 | P0 | Lorebook 管理页 CRUD 可用（创建/编辑/删除/列表） | covered | T-007(LorebookManage.vue) + T-003(后端 API) | T-003, T-007 | `cr027-lorebook.spec.ts` | Designed |
| AC-ADMIN-002 | REQ-ADMIN-002 | P0 | 场景配置页显示剧本层级结构，可为 Node 配置场景 | covered | T-007(SceneConfig.vue) + T-005(后端 API) | T-005, T-007 | `cr027-scene-config.spec.ts` | Designed |
| AC-ADMIN-003 | REQ-ADMIN-003 | P0 | NPC 编辑页新增内在驱动区域（渴望/恐惧/秘密） | covered | T-007(CharacterEdit.vue 扩展) + T-006(后端 PUT) | T-006, T-007 | `cr027-npc-internal.spec.ts` | Designed |
| AC-ADMIN-004 | REQ-ADMIN-004 | P0 | 非管理员无法访问管理页（403） | covered | T-003/T-005(后端 Admin 权限) + T-007(前端路由守卫) | T-003, T-005, T-007 | `test_lorebook_api.py::test_forbidden` + `cr027-admin-permission.spec.ts` | Designed |
