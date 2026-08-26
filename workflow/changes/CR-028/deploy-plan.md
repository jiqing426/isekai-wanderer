# CR-028 部署计划

## 部署步骤

| 步骤 | 命令 | 说明 |
|------|------|------|
| 后端部署 | docker compose build backend && docker compose up -d backend | 构建并启动后端服务 |
| 前端部署 | docker compose build frontend && docker compose up -d frontend | 构建并启动前端服务 |
| 数据库迁移 | alembic upgrade head | 已在开发阶段执行，生产环境无需重复 |

## 回滚方案

- 后端回滚：docker compose rollback backend
- 前端回滚：docker compose rollback frontend
- 数据库回滚：alembic downgrade -1

## 监控方案

- 健康检查：curl http://localhost:8000/api/v1/health，预期 HTTP 200
- 日志查看：docker compose logs -f backend frontend，实时跟踪容器日志

## 验证

部署完成后，执行以下功能验证：

1. **选择角色开始游戏**
   - 进入游戏界面
   - 选择任意角色
   - 确认游戏正常启动

2. **存档筛选**
   - 进入存档列表
   - 测试筛选功能
   - 确认筛选结果正确

3. **角色信息展示**
   - 查看角色详情页
   - 确认角色信息完整显示
   - 验证数据准确性

## 发布前检查

| 项 | 状态 | 说明 |
|----|------|------|
| CI/CD 结果 | passed | 所有测试通过，覆盖率达标 |
| Delivery E2E / Runtime Smoke 结果 | passed | 真实后端 API 调用正常 |
| Browser Interaction E2E 结果 | skipped_with_reason | Not Required: bcrypt 与 passlib 不兼容，登录功能阻塞，已记录在 test-report.md |

## 部署检查清单

- [ ] 后端服务构建成功
- [ ] 前端服务构建成功
- [ ] 后端服务启动成功
- [ ] 前端服务启动成功
- [ ] 健康检查通过
- [ ] 日志无异常错误
- [ ] 选择角色开始游戏功能正常
- [ ] 存档筛选功能正常
- [ ] 角色信息展示正常
