# CR-045 Deploy Plan

## 发布步骤

| 步骤 | 命令 | 状态 |
|------|------|------|
| 1. git commit | git add -A && git commit -m "CR-045" | Ready |
| 2. git push | git push origin main | Ready |
| 3. docker cp | docker cp 变更文件到容器 | Done |
| 4. docker restart | docker restart isekai-wanderer-backend-1 | Done |

## 监控方案

- 健康检查: curl http://localhost:8000/api/v1/health
- 前端首页: curl http://localhost:8081/
- 废弃端点 404: curl -X POST http://localhost:8000/api/v1/subscription/order/create

## 回滚方案

- git revert 回滚代码
- docker restart 重启容器加载旧代码

## 发布前检查

| 项 | 状态 | 说明 |
|--------|------|------|
| CI/CD 结果 | passed | 2/2 static checks passed |
| Delivery E2E / Runtime Smoke 结果 | passed | 6/6 passed |
| Browser Interaction E2E 结果 | passed | 6/6 passed |
