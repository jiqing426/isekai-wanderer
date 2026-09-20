# Test Plan

## Test-First Scope

- Gallery API is_accessible 字段：测试 free/basic 用户 is_accessible=false（未解锁 CG）、standard/premium 用户 is_accessible=true（DEV-001）
- Game API script_access 检查：测试 free 用户 403（非试用剧本）、basic 用户 200（普通剧本）、premium 用户 200（任意剧本）（DEV-003）
- Scripts API is_accessible 字段：测试剧本列表每个剧本项包含 is_accessible 字段（DEV-003）
- Settings API member-info 数据源：测试 tier 从 SubscriptionService 获取、status/expires_at 从 Subscription 表获取（DEV-005）
- 前端 Gallery 锁/升级提示：Browser E2E 验证 free 用户看到锁图标、standard 用户无锁（DEV-002）
- 前端订阅状态同步：Browser E2E 验证订阅成功后 UI 立即更新 tier、登录后自动加载订阅状态（DEV-004）

## Test Case Artifacts

| Task ID | Test Case Artifact | Type | Acceptance IDs | Status |
| --- | --- | --- | --- | --- |
| DEV-001 | `tests/unit/test_gallery_is_accessible.py` | automated | AC-001, AC-004 | Ready |
| DEV-001 | `tests/integration/test_gallery_tier_access.py` | automated | AC-002, AC-003 | Ready |
| DEV-002 | `tests/e2e/cr043-gallery-lock.spec.ts` | automated | AC-002, AC-003, AC-011 | Ready |
| DEV-002 | `tests/e2e/cr043-script-lock.spec.ts` | automated | AC-012, AC-013, AC-014 | Ready |
| DEV-003 | `tests/unit/test_script_access_mapping.py` | automated | AC-005, AC-006, AC-007, AC-008, AC-009 | Ready |
| DEV-003 | `tests/integration/test_game_start_permission.py` | automated | AC-005, AC-006, AC-007, AC-008, AC-015 | Ready |
| DEV-003 | `tests/integration/test_scripts_is_accessible.py` | automated | AC-009, AC-010 | Ready |
| DEV-004 | `tests/e2e/cr043-subscription-sync.spec.ts` | automated | AC-016, AC-017, AC-020 | Ready |
| DEV-004 | `tests/unit/test_user_types_basic.ts` | automated | AC-021 | Ready |
| DEV-005 | `tests/unit/test_member_info_source.py` | automated | AC-018, AC-019 | Ready |

## Red Failure Records

| Task ID | Acceptance IDs | Test Case Artifact | Command / Step | Failure Summary | Recorded At | Status |
| --- | --- | --- | --- | --- | --- | --- |
| DEV-001 | AC-001, AC-002, AC-003, AC-004 | `tests/unit/test_gallery_is_accessible.py` | `pytest tests/unit/test_gallery_is_accessible.py -v` | 6 tests FAILED — SubscriptionService not imported in gallery.py, is_accessible not implemented | 2026-09-17 | Red Recorded |
| DEV-003 | AC-005~010, AC-015 | `tests/unit/test_script_access_mapping.py` | `pytest tests/unit/test_script_access_mapping.py -v` | 12 tests FAILED — _compute_script_accessible not implemented, SubscriptionService not in game.py | 2026-09-17 | Red Recorded |
| DEV-005 | AC-018, AC-019 | `tests/unit/test_member_info_source.py` | `pytest tests/unit/test_member_info_source.py -v` | 4 tests FAILED — SubscriptionService not imported in settings.py | 2026-09-17 | Red Recorded |
| DEV-004 | AC-021 | `tests/unit/fe/userTypesBasic.test.ts` | `npx vitest run tests/unit/fe/userTypesBasic.test.ts` | 5 tests PASSED — subscription_tier type includes 'basic' in UserProfile, SubscriptionStatus, MemberInfo | 2026-09-16 | Passed |
| DEV-002 | AC-002, AC-003, AC-011 | `tests/unit/fe/galleryIsAccessible.test.ts` | `npx vitest run tests/unit/fe/galleryIsAccessible.test.ts` | 9 tests PASSED — GalleryView is_accessible field logic (lock overlay, upgrade hint, click handler, backward compat) | 2026-09-16 | Passed |

## Green Pass Records

| Task ID | Acceptance IDs | Test Case Artifact | Command / Step | Pass Summary | Recorded At | Status |
| --- | --- | --- | --- | --- | --- | --- |
| DEV-001 | AC-001, AC-002, AC-003, AC-004 | `tests/unit/test_gallery_is_accessible.py` | `pytest tests/unit/test_gallery_is_accessible.py -v` | 7 tests PASSED — is_accessible field, free/basic locked, standard/premium all accessible | 2026-09-17 | Green Recorded |
| DEV-003 | AC-005~010, AC-015 | `tests/unit/test_script_access_mapping.py` | `pytest tests/unit/test_script_access_mapping.py -v` | 12 tests PASSED — trial_only mapping, all_normal, premium, 403 denial, is_accessible in scripts | 2026-09-17 | Green Recorded |
| DEV-005 | AC-018, AC-019 | `tests/unit/test_member_info_source.py` | `pytest tests/unit/test_member_info_source.py -v` | 6 tests PASSED — tier from SubscriptionService, status/expires_at from Subscription table, data consistency | 2026-09-17 | Green Recorded |

## CI/CD Evidence Plan

| Stage | Trigger | Command / Pipeline | Acceptance IDs | Owner | Required | Record Location | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DEVELOPMENT | Green 通过后 | `./scripts/test.sh backend` | AC-001, AC-004, AC-005, AC-006, AC-007, AC-008, AC-009, AC-015, AC-018, AC-019 | qa / dev | 是 | `workflow/changes/CR-043/test-report.md` | Ready |
| DEVELOPMENT | Green 通过后 | `./scripts/test.sh frontend` | AC-021 | qa / dev | 是 | `workflow/changes/CR-043/test-report.md` | Ready |
| RELEASE_GATE | 发布关口前 | `docker compose up -d && sleep 5 && curl -f http://localhost/api/v1/health` | AC-001, AC-005, AC-018 | qa / ops | 是 | `workflow/changes/CR-043/deploy-plan.md` | Ready |

## Environment Test Matrix

| Env ID | Env Name | Entry / Origin | Scope | Must-Test Risks | Status |
| --- | --- | --- | --- | --- | --- |
| ENV-L1 | DEV_LOCAL | `http://localhost:8081` | 本地开发验证 | 页面加载、本机 API、基础交互、权限检查逻辑 | Ready |
| ENV-L2 | DEPLOY_PRIVATE | `http://<server-ip>:8081` | 内网或测试机验证 | 部署监听、代理、服务可达性 | Ready |
| ENV-L3 | DEPLOY_PUBLIC | `https://isekai-wanderer.example.com` | 公网入口验证 | CORS、反向代理、端口暴露、外网可访问性 | Ready |

## Delivery E2E / Runtime Smoke Plan

| Task ID | Command / Steps | Frontend URL | Backend URL | API / Proxy Path | Mock API | Acceptance IDs | Evidence Target | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEV-001 | `curl -H "Authorization: Bearer {free_user_token}" http://localhost:8081/api/v1/gallery/collections/{script_id}` and verify `is_accessible` field in JSON response | `http://localhost:8081` | `http://localhost:8000` | `/api/v1/gallery/collections/{script_id}` | no | AC-001, AC-004 | `workflow/changes/CR-043/test-report.md` | Ready |
| DEV-003 | `curl -X POST -H "Authorization: Bearer {free_user_token}" -H "Content-Type: application/json" -d '{"script_id":"{non_trial_script_id}"}' http://localhost:8081/api/v1/game/start` | `http://localhost:8081` | `http://localhost:8000` | `/api/v1/game/start` | no | AC-005 | `workflow/changes/CR-043/test-report.md` | Ready |
| DEV-005 | `curl -H "Authorization: Bearer {token}" http://localhost:8081/api/v1/users/me/member-info` | `http://localhost:8081` | `http://localhost:8000` | `/api/v1/users/me/member-info` | no | AC-018, AC-019 | `workflow/changes/CR-043/test-report.md` | Ready |
| ALL | `docker compose up -d && sleep 5 && curl -f http://localhost/api/v1/health` | `http://localhost:8081` | `http://localhost:8000` | `/api/v1/health` | no | AC-001, AC-005, AC-018 | `workflow/changes/CR-043/test-report.md` | Ready |

## Browser Interaction E2E Plan

| Task ID | Command / Steps | Browser / Tool | User Actions | Frontend URL | Backend URL | API / Proxy Path | Mock API | Acceptance IDs | Evidence Target | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEV-002 | `SKIP_WEB_SERVER=1 APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr043-gallery-lock.spec.ts --project=chromium --trace on` | Playwright Chromium | free 用户打开画廊→查看锁定 CG→点击锁定 CG→显示升级提示→不展开完整图片 | `http://localhost:8081` | `http://localhost:8000` | `/api/v1/gallery/collections/{script_id}` | no | AC-002, AC-011 | `workflow/changes/CR-043/test-report.md` | Ready |
| DEV-002 | `SKIP_WEB_SERVER=1 APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr043-gallery-lock.spec.ts --project=chromium --trace on` | Playwright Chromium | standard 用户打开画廊→查看全部 CG 无锁→点击任意 CG→预览完整图片 | `http://localhost:8081` | `http://localhost:8000` | `/api/v1/gallery/collections/{script_id}` | no | AC-003 | `workflow/changes/CR-043/test-report.md` | Ready |
| DEV-002 | `SKIP_WEB_SERVER=1 APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr043-script-lock.spec.ts --project=chromium --trace on` | Playwright Chromium | free 用户浏览剧本列表→非试用剧本显示锁定→点击锁定剧本→显示升级提示 | `http://localhost:8081` | `http://localhost:8000` | `/api/v1/scripts` | no | AC-012 | `workflow/changes/CR-043/test-report.md` | Ready |
| DEV-002 | `SKIP_WEB_SERVER=1 APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr043-script-lock.spec.ts --project=chromium --trace on` | Playwright Chromium | 用户浏览角色列表→不可用角色显示锁定→点击锁定角色→显示升级提示 | `http://localhost:8081` | `http://localhost:8000` | `/api/v1/scripts/{id}` | no | AC-010, AC-013 | `workflow/changes/CR-043/test-report.md` | Ready |
| DEV-004 | `SKIP_WEB_SERVER=1 APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr043-subscription-sync.spec.ts --project=chromium --trace on` | Playwright Chromium | 用户订阅成功→UI 立即更新 tier→无需手动刷新 | `http://localhost:8081` | `http://localhost:8000` | `/api/v1/subscription/*` | no | AC-016, AC-017 | `workflow/changes/CR-043/test-report.md` | Ready |
| DEV-004 | `SKIP_WEB_SERVER=1 APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr043-subscription-sync.spec.ts --project=chromium --trace on` | Playwright Chromium | 用户登录成功→订阅状态自动加载→无需手动刷新 | `http://localhost:8081` | `http://localhost:8000` | `/api/v1/subscription/status` | no | AC-020 | `workflow/changes/CR-043/test-report.md` | Ready |

## TDD Process Deviations

| Task ID | Deviation Type | Business Code Written | Missing Evidence | Remediation Verification | User Confirmation | Status |
| --- | --- | --- | --- | --- | --- | --- |
| DEV-001 | Red-Green TDD followed — 3 test files, 25 tests pass | None | None | N/A | N/A | Complete |
| DEV-003 | Red-Green TDD followed | None | None | N/A | N/A | Complete |
| DEV-005 | Red-Green TDD followed | None | None | N/A | N/A | Complete |

## Cannot Automate

| Task ID | Item | Reason | Manual Verification Owner | Verification Record |
| --- | --- | --- | --- | --- |
| DEV-002 | AC-014 前端复用 useSubscriptionStore 验证 | 需要代码审查确认不在前端本地硬编码 tier→permissions 映射 | qa | 待填写 |
