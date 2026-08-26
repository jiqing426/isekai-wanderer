# CR-027 测试计划

## 测试范围概览

| 测试类型 | 覆盖 AC | 负责人 | 证据等级 |
|----------|---------|--------|----------|
| 单元测试 | AC-LORE-004, AC-SCENE-003, AC-NPC-001/003, AC-PROMPT-001/002, AC-TOKEN-001/002/003 | be | L1 |
| 集成测试 | AC-LORE-001/002, AC-SCENE-001/002, AC-NPC-002, AC-PROMPT-003/005 | be | L2 |
| Browser Interaction E2E | AC-LORE-001/003, AC-SCENE-001, AC-NPC-002, AC-ADMIN-001/002/003/004 | qa | L2 |
| Delivery E2E / Runtime Smoke | 全部 AC（环境验证） | qa | L2 |

---

## 1. 单元测试 (be)

### 1.1 TokenBudgetController

| 用例 | 输入 | 预期 | 绑定 AC |
|------|------|------|---------|
| count_tokens 英文 | "hello world" | > 0 | AC-TOKEN-001 |
| count_tokens 中文 | "你好世界" | > 0 | AC-TOKEN-001 |
| count_tokens 空字符串 | "" | 0 | AC-TOKEN-001 |
| count_tokens 中英混合 | "hello 你好" | > 0 | AC-TOKEN-001 |
| truncate_to_budget 不超限 | text=100 tokens, budget=200 | 原文返回 | AC-TOKEN-002 |
| truncate_to_budget 超限 | text=600 tokens, budget=500 | 截断到 ≤500 tokens | AC-TOKEN-002 |
| truncate_to_budget UTF-8 安全 | 中文文本截断 | 截断后可正常 decode | AC-TOKEN-002 |
| validate_total_budget 正常 | 各层合计 2300 | ok=true | AC-TOKEN-003 |
| validate_total_budget 超限 | 各层合计 2500 | ok=false, over_by=200 | AC-TOKEN-003 |
| 默认预算合计 | 初始化 | 200+500+300+800+300+200=2300 | AC-TOKEN-001 |
| get_budget_report | 各层已赋值 | 返回 total/layers/status | AC-TOKEN-003 |

### 1.2 PromptBuilder

| 用例 | 输入 | 预期 | 绑定 AC |
|------|------|------|---------|
| build 正常拼接 | 六层数据齐全 | system_prompt 含 L1-L5，user_prompt 含 L6 | AC-PROMPT-001 |
| build 拼接顺序 | 六层数据 | system_prompt 顺序：全局→世界→NPC→记忆→导演 | AC-PROMPT-002 |
| build 总 Token ≤ 2300 | 各层在预算内 | token_report.total ≤ 2300 | AC-PROMPT-001 |
| build 单层超预算截断 | lorebook=600 tokens | 截断到 500 | AC-TOKEN-002 |
| L2 降级 - LorebookService 异常 | LorebookService 抛异常 | L2 使用空字符串，其他层正常 | AC-PROMPT-003 |
| L4 降级 - MemoryService 异常 | MemoryService 抛异常 | L4 使用空字符串，其他层正常 | AC-PROMPT-003 |
| 整体降级 - PromptBuilder 异常 | PromptBuilder 抛异常 | NarrativeEngine 回退简单拼接 | AC-PROMPT-004 |
| L3 NPC 档案 - 有内在驱动 | desire/fear/secret 有值 | 包含"内在渴望""深层恐惧""隐藏秘密" | AC-NPC-003 |
| L3 NPC 档案 - 无内在驱动 | desire/fear/secret 为 NULL | 不包含内在驱动部分，其他字段正常 | AC-NPC-003 |
| L2 世界知识 - 有场景配置 | scene_tags=["森林"] | Lorebook 匹配结果注入 | AC-SCENE-002 |
| L2 世界知识 - 无场景配置 | node 无 scene_config | L2 使用空世界知识 | AC-SCENE-003 |
| L2 世界知识 - 无匹配 Lorebook | tags=["海底"]，无匹配 | 返回空字符串 | AC-LORE-004 |
| 各层独立可测试 | 单独调用 build_layer_3 | 仅返回 L3 内容 | AC-PROMPT-002 |

### 1.3 LorebookService

| 用例 | 输入 | 预期 | 绑定 AC |
|------|------|------|---------|
| create | title/content/tags | 条目创建，status=active | AC-LORE-001 |
| get | 存在的 id | 返回条目 | AC-LORE-001 |
| list | 无筛选 | 返回所有 active 条目 | AC-LORE-001 |
| list + tag 筛选 | tag="森林" | 仅返回含"森林"标签的条目 | AC-LORE-003 |
| list + 分页 | page=2, pageSize=10 | 返回第 2 页数据 | AC-LORE-001 |
| update | 修改 content | 条目更新 | AC-LORE-002 |
| soft_delete | 删除 id | status=deleted，list 不再返回 | AC-LORE-002 |
| match_by_tags | tags=["森林","白天"] | 返回含任一标签的 active 条目，按 priority DESC | AC-LORE-004 |
| match_by_tags 无匹配 | tags=["海底"] | 返回空列表 | AC-LORE-004 |

### 1.4 SceneConfigService

| 用例 | 输入 | 预期 | 绑定 AC |
|------|------|------|---------|
| upsert_for_node | node_id + data | 创建或更新 | AC-SCENE-001 |
| get_by_node | 已配置 node_id | 返回 SceneConfig | AC-SCENE-001 |
| get_by_node 未配置 | 未配置 node_id | 返回 None | AC-SCENE-003 |
| delete_for_node | 已配置 node_id | 配置删除 | AC-SCENE-001 |
| list_by_route | route_id | 返回该 route 下所有场景配置 | AC-SCENE-002 |

---

## 2. 集成测试 (be)

### 2.1 Lorebook API

| 用例 | 方法 | 路径 | 预期 | 绑定 AC |
|------|------|------|------|---------|
| 创建条目 | POST | /api/v1/lorebook | 201, 返回新条目 | AC-LORE-001 |
| 列表查询 | GET | /api/v1/lorebook | 200, 返回列表 | AC-LORE-001 |
| 标签筛选 | GET | /api/v1/lorebook?tag=森林 | 200, 仅匹配条目 | AC-LORE-003 |
| 更新条目 | PUT | /api/v1/lorebook/{id} | 200, 内容更新 | AC-LORE-002 |
| 删除条目 | DELETE | /api/v1/lorebook/{id} | 200, 软删除 | AC-LORE-002 |
| 非管理员创建 | POST | /api/v1/lorebook | 403 | AC-ADMIN-004 |
| 非管理员列表 | GET | /api/v1/lorebook | 403 | AC-ADMIN-004 |

### 2.2 SceneConfig API

| 用例 | 方法 | 路径 | 预期 | 绑定 AC |
|------|------|------|------|---------|
| 创建场景 | PUT | /api/v1/scene-configs/node/{node_id} | 200/201 | AC-SCENE-001 |
| 查询场景 | GET | /api/v1/scene-configs?route_id=xxx | 200 | AC-SCENE-002 |
| 删除场景 | DELETE | /api/v1/scene-configs/node/{node_id} | 200 | AC-SCENE-001 |
| 非管理员操作 | PUT | /api/v1/scene-configs/node/{node_id} | 403 | AC-ADMIN-004 |

### 2.3 Character API 扩展

| 用例 | 方法 | 路径 | 预期 | 绑定 AC |
|------|------|------|------|---------|
| 更新内在驱动 | PUT | /api/v1/characters/{id} | 200, desire/fear/secret 更新 | AC-NPC-002 |
| 兼容旧数据 | PUT | /api/v1/characters/{id} (不传 desire) | 200, 原有字段更新 | AC-NPC-001 |

### 2.4 NarrativeEngine 集成

| 用例 | 输入 | 预期 | 绑定 AC |
|------|------|------|---------|
| generate_dialogue 使用新 PromptBuilder | 正常 session | 调用 PromptBuilder.build() | AC-PROMPT-005 |
| 现有角色兼容 | Character 无 desire/fear/secret | 正常生成，模块3 无内在驱动部分 | AC-PROMPT-005 |
| 场景标签注入 | Node 有 scene_config | L2 包含场景描述和 Lorebook 匹配 | AC-SCENE-002 |

---

## 3. Browser Interaction E2E (qa)

**命令**: `APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr027-*.spec.ts --headed --trace on`

**环境**: 真实浏览器 + 真实后端（docker compose up）

**禁止**: 不得使用 mock API、fixture server 或组件级替身

### 3.1 cr027-lorebook.spec.ts

| 用例 | 用户动作 | 预期 | 绑定 AC |
|------|----------|------|---------|
| 管理员访问 Lorebook 页 | 登录管理员 → 导航到 /lorebook | 页面显示列表，有"新建条目"按钮 | AC-ADMIN-001 |
| 创建 Lorebook 条目 | 点击"新建条目" → 填写标题/内容/标签 → 保存 | 列表刷新显示新条目 | AC-LORE-001, AC-ADMIN-001 |
| 编辑 Lorebook 条目 | 点击某条目"编辑" → 修改内容 → 保存 | 条目更新成功 | AC-ADMIN-001 |
| 删除 Lorebook 条目 | 点击某条目"删除" → 确认弹窗 | 列表不再显示该条目 | AC-ADMIN-001 |
| 按标签筛选 | 选择标签"森林"筛选 | 列表仅显示含"森林"标签的条目 | AC-LORE-003 |

### 3.2 cr027-scene-config.spec.ts

| 用例 | 用户动作 | 预期 | 绑定 AC |
|------|----------|------|---------|
| 访问场景配置页 | 登录管理员 → 导航到 /scene-configs | 显示剧本→路线→Node 树形结构 | AC-ADMIN-002 |
| 为 Node 配置场景 | 选择某 Node → 填写场景名称/标签/描述 → 保存 | 保存成功，Node 显示已配置场景 | AC-SCENE-001, AC-ADMIN-002 |
| 编辑场景配置 | 修改某 Node 的场景标签 → 保存 | 配置更新 | AC-ADMIN-002 |
| 删除场景配置 | 删除某 Node 的场景配置 | Node 恢复为"未配置" | AC-ADMIN-002 |

### 3.3 cr027-npc-internal.spec.ts

| 用例 | 用户动作 | 预期 | 绑定 AC |
|------|----------|------|---------|
| NPC 编辑页显示内在驱动区域 | 进入 NPC 编辑页 | 页面显示"渴望""恐惧""秘密"输入框 | AC-ADMIN-003 |
| 保存 NPC 内在驱动 | 填写渴望/恐惧/秘密 → 保存 | 保存成功，显示成功提示 | AC-NPC-002, AC-ADMIN-003 |

### 3.4 cr027-admin-permission.spec.ts

| 用例 | 用户动作 | 预期 | 绑定 AC |
|------|----------|------|---------|
| 非管理员访问 Lorebook 页 | 登录普通用户 → 访问 /lorebook | 返回 403 或重定向 | AC-ADMIN-004 |
| 非管理员访问场景配置页 | 登录普通用户 → 访问 /scene-configs | 返回 403 或重定向 | AC-ADMIN-004 |
| 非管理员访问 NPC 编辑页 | 登录普通用户 → 访问 NPC 编辑 | 返回 403 或重定向 | AC-ADMIN-004 |

---

## 4. Delivery E2E / Runtime Smoke (qa)

**命令**: `docker compose up -d && sleep 5 && curl -f http://localhost/api/v1/health`

**预期**: `{"status": "ok", "version": "..."}`

**绑定**: 所有 AC（环境验证）

---

## 5. 测试数据

| 数据集 | 用途 | 清理方式 |
|--------|------|----------|
| 管理员账号 | E2E 登录 | 测试后删除 |
| 普通用户账号 | 权限测试 | 测试后删除 |
| Lorebook 测试条目 | CRUD 测试 | 测试后删除 |
| SceneConfig 测试数据 | CRUD 测试 | 测试后删除 |
| Character 测试数据 | NPC 扩展测试 | 测试后恢复原值 |

---

## 6. 测试通过标准

| 层级 | 通过标准 |
|------|----------|
| 单元测试 | 所有用例 100% 通过 |
| 集成测试 | 所有用例 100% 通过 |
| Browser E2E | 所有用例 100% 通过 |
| Delivery E2E | health 返回 ok |

---

## 7. Mock Policy

| 场景 | 是否允许 Mock | 说明 |
|------|---------------|------|
| 单元测试 | ✅ 允许 | Service 层 mock 数据库 |
| 集成测试 | ❌ 禁止 | 使用真实数据库 |
| Browser E2E | ❌ 禁止 | 真实后端 + 真实浏览器 |
| Delivery E2E | ❌ 禁止 | 真实部署 + 真实后端 |
| LLM 调用 | ✅ 允许 | 开发/测试环境可用 |
