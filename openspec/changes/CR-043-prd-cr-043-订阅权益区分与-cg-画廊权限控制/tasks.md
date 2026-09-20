# Tasks — CR-043: 订阅权益区分与 CG 画廊权限控制

## Implementation Tasks

| Task ID | Stage | Owner Agent | Requirement / AC | Consumers | Excluded AC | Allowed Write Scope | Test Case Artifact | Verification | Rollback / Revert Plan | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEV-001 | DEVELOPMENT | Cat01-be | AC-001, AC-002, AC-003, AC-004 | 前端 `GalleryView.vue`、`api/gallery.ts` | AC-005~AC-015, AC-016~AC-021 | `backend/app/api/v1/gallery.py`、`backend/app/services/subscription_service.py`（只调用，不修改核心逻辑） | `workflow/changes/CR-043/test-plan.md` | API/DB 契约验证 + Browser Interaction E2E | 回退 `gallery.py` 变更，`is_accessible` 字段移除后前端回到仅检查 `unlock_status` | Ready |
| DEV-002 | DEVELOPMENT | Cat01-fe | AC-002, AC-003, AC-010, AC-011, AC-012, AC-013, AC-014 | 用户（浏览器） | AC-001, AC-004~AC-009, AC-015, AC-016~AC-021 | `frontend/src/views/GalleryView.vue`、`frontend/src/api/gallery.ts`、`frontend/src/stores/subscription.ts`（只调用，不修改核心逻辑）、`frontend/src/views/script/` 下的剧本列表和角色选择组件 | `workflow/changes/CR-043/test-plan.md` | Browser Interaction E2E | 回退前端组件变更，锁/升级提示移除后回到无权益区分状态 | Ready |
| DEV-003 | DEVELOPMENT | Cat01-be | AC-005, AC-006, AC-007, AC-008, AC-009, AC-010, AC-015 | 前端剧本列表组件、角色选择组件、`api/scripts.ts` | AC-001~AC-004, AC-011~AC-014, AC-016~AC-021 | `backend/app/api/v1/game.py`（`start_game` 端点）、`backend/app/api/v1/scripts.py`（`list_scripts`、`get_script` 端点）、`backend/app/services/subscription_service.py`（只调用，不修改核心逻辑） | `workflow/changes/CR-043/test-plan.md` | API/DB 契约验证 + API 安全测试 | 回退 `game.py` 和 `scripts.py` 变更，权限检查移除后回到无 script_access 检查状态 | Ready |
| DEV-004 | DEVELOPMENT | Cat01-fe | AC-016, AC-017, AC-020, AC-021 | 用户（浏览器） | AC-001~AC-015, AC-018, AC-019 | `frontend/src/components/SubscriptionPlans.vue`、`frontend/src/stores/auth.ts`、`frontend/src/stores/subscription.ts`（只调用，不修改核心逻辑）、`frontend/src/router/index.ts`（路由守卫）、`frontend/src/types/user.ts`、`frontend/src/types/auth.ts` | `workflow/changes/CR-043/test-plan.md` | Browser Interaction E2E + TypeScript 编译 | 回退前端变更，订阅成功后回到只调用 loadPlans() 的状态 | Ready |
| DEV-005 | DEVELOPMENT | Cat01-be | AC-018, AC-019 | 前端 Settings 会员页面、`api/settings.ts` | AC-001~AC-017, AC-020, AC-021 | `backend/app/api/v1/settings.py`（`get_member_info` 端点）、`backend/app/services/subscription_service.py`（只调用，不修改核心逻辑） | `workflow/changes/CR-043/test-plan.md` | API/DB 契约验证 | 回退 `settings.py` 变更，`get_member_info()` 回到从 `User.trial_*` 读取的状态 | Ready |

## Task Rules

- 每个任务必须关联至少一个 AC 编号。
- 每个涉及 API、页面、管理端或用户动作的任务必须填写 `Consumers`，明确哪个页面、组件、菜单、按钮、调用方或脚本会消费这项能力。
- 不覆盖的 AC 必须显式写入 `Excluded AC`；无不覆盖项时写 `无`。
- 声明任务完成前，必须在 `workflow/changes/<CR-ID>/review.md` 写开发覆盖声明。

## Task Dependencies

```
DEV-001 (gallery.py is_accessible) ──┐
                                       ├──→ DEV-002 (前端锁/升级提示)
DEV-003 (game.py/scripts.py 权限检查) ─┘
DEV-004 (前端订阅状态同步) ── 独立
DEV-005 (后端 member-info 修复) ── 独立
```

- DEV-002 的前端锁/升级提示依赖 DEV-001 和 DEV-003 的后端 API 返回 `is_accessible` 字段
- DEV-001 和 DEV-003 可并行开发（不同文件、不同 API 端点）
- DEV-002 需等待 DEV-001 或 DEV-003 至少一个完成后才能开始联调
- DEV-004 和 DEV-005 独立于 DEV-001~003，可并行开发
- DEV-004 的前端订阅状态同步依赖 DEV-005 的后端 member-info 修复完成后才能完整联调 AC-018/AC-019

## Architect 待确认事项（来自 CEO 附条件）

| 附条件 | 待确认内容 | 影响 Task | 阻塞 Task | Q 编号 | 确认结论 |
| --- | --- | --- | --- | --- | --- |
| C1 | `is_accessible` 字段的 API 契约设计（字段名、返回位置、类型） | DEV-001 | 否 | Q-001 | ✅ 已确认：每个 CG 项内嵌 `is_accessible: boolean` 字段，见 design.md Q-001 |
| C2 | script_access 三档映射到剧本表结构的判定规则 | DEV-003 | 否 | Q-002 | ✅ 已确认：运行时虚拟判定，trial_only = genre=='romance' AND hot_value>=50，见 design.md Q-002 |
| C3 | 权限边界变更的 Security 审查 | 不阻塞开发，阻塞 RELEASE_GATE | 否 | — | ✅ 安全检查点已设计，见 design.md 安全检查点设计 |
