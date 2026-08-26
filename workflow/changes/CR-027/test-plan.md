# CR-027 测试计划

## Test-First Scope

- 所有后端 Service 层必须先写单元测试再写实现（TDD）
- PromptBuilder 各层独立可测试，降级路径必须有测试覆盖
- TokenBudgetController 截断逻辑必须保证 UTF-8 安全
- 前端管理页面 CRUD 必须有 Browser E2E 覆盖
- 权限校验（Admin vs 普通用户）必须有集成测试 + E2E 双重覆盖
- Delivery E2E / Runtime Smoke 禁止 mock API

## Test Case Artifacts

| Task ID | Test Case Artifact | 覆盖验收项 | 状态 |
|---------|-------------------|------------|------|
| T-001 | `backend/tests/test_migrations_cr027.py` | AC-NPC-001 | Ready |
| T-002 | `backend/tests/services/test_lorebook_service.py` | AC-LORE-001, AC-LORE-002, AC-LORE-003, AC-LORE-004 | Ready |
| T-003 | `backend/tests/api/test_lorebook_api.py` | AC-LORE-001, AC-LORE-002, AC-LORE-003, AC-ADMIN-004 | Ready |
| T-004 | `backend/tests/services/test_scene_config_service.py` | AC-SCENE-001, AC-SCENE-002, AC-SCENE-003 | Ready |
| T-005 | `backend/tests/api/test_scene_config_api.py` | AC-SCENE-001, AC-SCENE-002, AC-ADMIN-004 | Ready |
| T-006 | `backend/tests/services/test_token_budget.py`, `backend/tests/services/test_prompt_builder.py`, `backend/tests/services/test_narrative_engine_cr027.py` | AC-NPC-002, AC-NPC-003, AC-PROMPT-001, AC-PROMPT-002, AC-PROMPT-003, AC-PROMPT-004, AC-PROMPT-005, AC-TOKEN-001, AC-TOKEN-002, AC-TOKEN-003 | Ready |
| T-007 | `tests/e2e/cr027-lorebook.spec.ts`, `tests/e2e/cr027-scene-config.spec.ts`, `tests/e2e/cr027-npc-internal.spec.ts`, `tests/e2e/cr027-admin-permission.spec.ts` | AC-ADMIN-001, AC-ADMIN-002, AC-ADMIN-003, AC-ADMIN-004, AC-LORE-001, AC-LORE-003, AC-SCENE-001, AC-NPC-002 | Ready |
| T-008 | `tests/e2e/cr027-*.spec.ts` (执行验证) | AC-LORE-001, AC-LORE-003, AC-SCENE-001, AC-NPC-002, AC-ADMIN-001, AC-ADMIN-002, AC-ADMIN-003, AC-ADMIN-004 | Ready |

## Red Failure Records

| Task ID | Failure Scenario | Expected Behavior | 状态 |
|---------|-----------------|-------------------|------|
| T-006 | LorebookService 抛异常时 PromptBuilder 构建 | L2 使用空字符串，其他层正常，warning 日志 | Ready |
| T-006 | MemoryService 抛异常时 PromptBuilder 构建 | L4 使用空字符串，其他层正常，warning 日志 | Ready |
| T-006 | PromptBuilder 整体异常时 NarrativeEngine 降级 | 回退到现有简单 Prompt，error 日志 | Ready |
| T-006 | Lorebook 内容 600 tokens 超预算 500 | 截断到 ≤500 tokens，UTF-8 可解码 | Ready |
| T-006 | 总 Token 2500 超限 2300 | token_report 返回 ok=false, over_by=200 | Ready |
| T-003 | 非管理员访问 Lorebook API | 返回 403 | Ready |
| T-005 | 非管理员访问 SceneConfig API | 返回 403 | Ready |
| T-006 | Character 无 desire/fear/secret 时构建 L3 | 模块3 不包含内在驱动部分，其他字段正常 | Ready |

## CI/CD Evidence Plan

| 阶段 | 触发时机 | 命令 / Pipeline | 覆盖验收项 | 负责人 | 记录位置 | 状态 |
|------|----------|-----------------|------------|--------|----------|------|
| DEVELOPMENT | 代码提交 | `cd backend && pytest tests/ -v --cov=app/services/lorebook_service --cov=app/services/scene_config_service --cov=app/services/prompt_builder --cov=app/services/token_budget` | AC-LORE-001, AC-LORE-002, AC-LORE-003, AC-LORE-004, AC-SCENE-001, AC-SCENE-002, AC-SCENE-003, AC-NPC-001, AC-NPC-002, AC-NPC-003, AC-PROMPT-001, AC-PROMPT-002, AC-PROMPT-003, AC-PROMPT-004, AC-PROMPT-005, AC-TOKEN-001, AC-TOKEN-002, AC-TOKEN-003 | be | `workflow/changes/CR-027/test-report.md` | Ready |
| QA | 开发完成后 | `APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr027-*.spec.ts --headed --trace on` | AC-ADMIN-001, AC-ADMIN-002, AC-ADMIN-003, AC-ADMIN-004, AC-LORE-001, AC-LORE-003, AC-SCENE-001, AC-NPC-002 | qa | `workflow/changes/CR-027/test-report.md` | Ready |

## Delivery E2E / Runtime Smoke Plan

| 任务编号 | 命令 / 步骤 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
|----------|-------------|----------|----------|------------------|----------|------------|--------------|------|
| T-008 | `docker compose up -d && sleep 5 && curl -f http://localhost/api/v1/health` | http://localhost:8081 | http://localhost:8000 | /api/v1/health | no | AC-LORE-001, AC-SCENE-001, AC-NPC-001, AC-PROMPT-001, AC-ADMIN-001 | `workflow/changes/CR-027/test-report.md` | Ready |

## Browser Interaction E2E Plan

| 任务编号 | 命令 / 步骤 | Browser / Tool | 用户动作 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
|----------|-------------|----------------|----------|----------|----------|------------------|----------|------------|--------------|------|
| T-008 | `APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr027-lorebook.spec.ts --headed --trace on` | Playwright | 登录管理员→导航 Lorebook 页→新建/编辑/删除条目→标签筛选 | http://localhost:8081 | http://localhost:8000 | /api/v1/lorebook | no | AC-LORE-001, AC-LORE-003, AC-ADMIN-001 | `workflow/changes/CR-027/test-report.md` | Ready |
| T-008 | `APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr027-scene-config.spec.ts --headed --trace on` | Playwright | 导航场景配置页→选择 Node→配置场景→保存 | http://localhost:8081 | http://localhost:8000 | /api/v1/scene-configs | no | AC-SCENE-001, AC-ADMIN-002 | `workflow/changes/CR-027/test-report.md` | Ready |
| T-008 | `APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr027-npc-internal.spec.ts --headed --trace on` | Playwright | 进入 NPC 编辑页→填写渴望/恐惧/秘密→保存 | http://localhost:8081 | http://localhost:8000 | /api/v1/characters | no | AC-NPC-002, AC-ADMIN-003 | `workflow/changes/CR-027/test-report.md` | Ready |
| T-008 | `APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr027-admin-permission.spec.ts --headed --trace on` | Playwright | 普通用户访问管理页→403 | http://localhost:8081 | http://localhost:8000 | /api/v1/lorebook | no | AC-ADMIN-004 | `workflow/changes/CR-027/test-report.md` | Ready |
