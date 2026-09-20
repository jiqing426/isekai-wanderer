# CR-028 测试报告

| 项 | 内容 |
|----|------|
| 测试结论 | passed — API/DB 测试 9/9 通过，Bug 修复回归 2/2 通过，Browser E2E 5/5 通过 |

## 测试结论

- 状态：passed
- API/DB 测试：9/9 通过
- Bug 修复回归：2/2 通过
- Browser E2E：5/5 通过

## CI/CD 执行结果

| 类型 | 命令 / Pipeline | 覆盖验收项 | 触发来源 | 结果 | 证据链接 / 日志 | 负责人 |
|------|-----------------|------------|----------|------|-----------------|--------|
| 语法检查 | python -m py_compile backend/app/api/v1/saves.py | AC-PLAY-004, AC-PLAY-005 | 手动执行 | passed | exit code 0 | qa |
| 前端构建 | cd frontend && npm run build | AC-PLAY-001, AC-PLAY-003, AC-PLAY-004, AC-PLAY-005, AC-PLAY-006 | 手动执行 | passed | exit code 0 | qa |
| 健康检查 | docker compose ps | AC-PLAY-002, AC-PLAY-007, AC-PLAY-008, AC-PLAY-009 | 手动执行 | passed | 全部 healthy | qa |

## Delivery E2E / Runtime Smoke Results

| 命令 / 步骤 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 结果 | 证据链接 / 日志 | 负责人 |
|-------------|----------|----------|------------------|----------|------------|------|-----------------|--------|
| curl http://localhost:8081/api/v1/health | http://localhost:8081 | http://localhost:8000 | /api/v1/health | no | AC-PLAY-002 | passed | 返回 {"status":"ok"} | qa |
| curl http://localhost:8000/api/v1/scripts | http://localhost:8081 | http://localhost:8000 | /api/v1/scripts | no | AC-PLAY-001, AC-PLAY-003 | passed | 返回 playable_characters | qa |
| curl http://localhost:8000/api/v1/saves?character_id=xxx | http://localhost:8081 | http://localhost:8000 | /api/v1/saves | no | AC-PLAY-004, AC-PLAY-005 | passed | total=count=3 | qa |

## Browser Interaction E2E Results

| 命令 / 步骤 | Browser / Tool | 用户动作 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 结果 | 证据链接 / 日志 | 负责人 |
|-------------|----------------|----------|----------|----------|------------------|----------|------------|------|-----------------|--------|
| npx playwright test tests/e2e/cr028-character-playable.spec.ts | Playwright/Chromium | 进入剧本详情页查看角色图鉴和可扮演标识 | http://localhost:8081 | http://localhost:8000 | /api/v1 | no | AC-PLAY-001 | passed | test-results/cr028-ac-play-001-script-detail.png | qa |
| npx playwright test tests/e2e/cr028-character-playable.spec.ts | Playwright/Chromium | 选择不同角色开始游戏，验证生成新存档 | http://localhost:8081 | http://localhost:8000 | /api/v1 | no | AC-PLAY-003 | passed | test-results/cr028-ac-play-003-saves.png | qa |
| npx playwright test tests/e2e/cr028-character-playable.spec.ts | Playwright/Chromium | 进入个人中心查看存档列表和角色信息 | http://localhost:8081 | http://localhost:8000 | /api/v1 | no | AC-PLAY-004 | passed | test-results/cr028-ac-play-004-profile.png | qa |
| npx playwright test tests/e2e/cr028-character-playable.spec.ts | Playwright/Chromium | 在存档管理页按角色筛选 | http://localhost:8081 | http://localhost:8000 | /api/v1 | no | AC-PLAY-005 | passed | test-results/cr028-ac-play-005-saves-filter.png | qa |
| npx playwright test tests/e2e/cr028-character-playable.spec.ts | Playwright/Chromium | 查看剧本详情页角色图鉴（所有角色为 free 类型） | http://localhost:8081 | http://localhost:8000 | /api/v1 | no | AC-PLAY-006 | passed | test-results/cr028-ac-play-006-character-gallery.png | qa |
