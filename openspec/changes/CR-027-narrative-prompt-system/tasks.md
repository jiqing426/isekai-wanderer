# CR-027 任务清单

## Implementation Tasks

| Task ID | Owner Agent | Requirement / AC | Excluded AC | Allowed Write Scope | Test Case Artifact | Verification | Rollback / Revert Plan | Status |
|---------|--------------|------------------|-------------|---------------------|-------------------|--------------|------------------------|--------|
| T-001 | be | AC-NPC-001 | 无 | `backend/alembic/versions/cr027_*.py` | 单元测试：迁移成功执行，三张表/列结构正确 | `alembic upgrade head` 成功 + 表结构验证 | `alembic downgrade -1` | Ready |
| T-002 | be | AC-LORE-001, AC-LORE-002, AC-LORE-003, AC-LORE-004 | 无 | `backend/app/services/lorebook_service.py`, `backend/app/models/lorebook.py`, `backend/app/schemas/lorebook.py` | 单元测试：CRUD + tag match + 软删除 + 分页 + 空结果 | pytest 单元测试全部通过 | 删除 service/model/schema 文件 | Ready |
| T-003 | be | AC-LORE-001, AC-LORE-002, AC-LORE-003, AC-ADMIN-004 | 无 | `backend/app/api/v1/lorebook.py`, `backend/app/api/v1/__init__.py` | 集成测试：各接口正常返回 + 403 非管理员 + 标签筛选 | pytest 集成测试全部通过 | 删除路由文件 + 取消注册 | Ready |
| T-004 | be | AC-SCENE-001, AC-SCENE-002, AC-SCENE-003 | 无 | `backend/app/services/scene_config_service.py`, `backend/app/models/scene_config.py`, `backend/app/schemas/scene_config.py` | 单元测试：upsert / get / delete / list + 未配置返回 None | pytest 单元测试全部通过 | 删除 service/model/schema 文件 | Ready |
| T-005 | be | AC-SCENE-001, AC-SCENE-002, AC-ADMIN-004 | 无 | `backend/app/api/v1/scene_configs.py`, `backend/app/api/v1/__init__.py` | 集成测试：各接口正常返回 + 403 非管理员 | pytest 集成测试全部通过 | 删除路由文件 + 取消注册 | Ready |
| T-006 | be | AC-NPC-002, AC-NPC-003, AC-PROMPT-001, AC-PROMPT-002, AC-PROMPT-003, AC-PROMPT-004, AC-PROMPT-005, AC-TOKEN-001, AC-TOKEN-002, AC-TOKEN-003, AC-LORE-004, AC-SCENE-002, AC-SCENE-003 | 无 | `backend/app/models/script.py`, `backend/app/api/v1/characters.py`, `backend/app/services/token_budget.py`, `backend/app/services/prompt_builder.py`, `backend/app/services/llm/gateway.py`, `backend/app/services/narrative/narrative_engine.py`, `backend/requirements.txt`, `backend/app/config.py` | 单元测试：TokenBudgetController + PromptBuilder 各层 + 降级；集成测试：NarrativeEngine 集成 + 兼容性 | pytest 单元测试 + 集成测试全部通过 | 回退 narrative_engine.py + gateway.py 修改 | Ready |
| T-007 | fe | AC-ADMIN-001, AC-ADMIN-002, AC-ADMIN-003, AC-ADMIN-004, AC-LORE-001, AC-LORE-003, AC-SCENE-001, AC-NPC-002 | 无 | `admin/src/views/LorebookManage.vue`, `admin/src/views/SceneConfig.vue`, `admin/src/views/CharacterEdit.vue`, `admin/src/router/index.ts`, `admin/src/api/lorebook.ts`, `admin/src/api/sceneConfig.ts` | Browser E2E：CRUD 操作 + 权限校验 + 页面渲染 | Playwright E2E 测试通过 | 回退前端文件修改 | Ready |
| T-008 | qa | AC-LORE-001, AC-LORE-003, AC-SCENE-001, AC-NPC-002, AC-ADMIN-001, AC-ADMIN-002, AC-ADMIN-003, AC-ADMIN-004 | 无 | `tests/e2e/cr027-*.spec.ts` | Browser E2E：真实浏览器 + 真实后端 + 无 mock API | `APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr027-*.spec.ts` 全部通过 | 删除测试文件 | Ready |

## 任务依赖

```
T-001 (DB迁移)
  └── T-002 (LorebookService) ── T-003 (Lorebook API)
  └── T-004 (SceneConfigService) ── T-005 (SceneConfig API)
  └── T-006 (NPC扩展 + PromptBuilder + 集成)
T-007 (Admin前端) 依赖 T-003, T-005, T-006
T-008 (E2E测试) 依赖 T-007
```

## 执行顺序

1. **T-001** → DB 迁移（所有后端任务前置）
2. **T-002 + T-004** → Service 层（可并行）
3. **T-003 + T-005** → API 层（可并行，依赖 Service）
4. **T-006** → PromptBuilder + 集成（依赖 Service）
5. **T-007** → Admin 前端（依赖 API）
6. **T-008** → E2E 测试（依赖前端完成）

## 预估工时

| 任务 | 负责人 | 优先级 | 预估工时 |
|------|--------|--------|----------|
| T-001 | be | P0 | 2h |
| T-002 | be | P0 | 4h |
| T-003 | be | P0 | 3h |
| T-004 | be | P0 | 3h |
| T-005 | be | P0 | 2h |
| T-006 | be | P0 | 10h |
| T-007 | fe | P0 | 10h |
| T-008 | qa | P1 | 6h |
| **合计** | | | **40h** |
