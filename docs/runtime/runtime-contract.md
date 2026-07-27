| Key | Value | Evidence / Source | Status |
| --- | --- | --- | --- |
| frontend_origin | `http://localhost:8081` (dev) / `https://isekai-wanderer.example.com` (prod) | `.env.example`, `vite.config.ts`, `docker-compose.yml` | Defined |
| backend_origin | `http://localhost:8000` (dev) / `https://isekai-wanderer.example.com:8000` (prod internal) | `.env.example`, backend listen config, `docker-compose.yml` | Defined |
| frontend_port | 8081 (Vite dev) / 80 (Nginx prod) | `vite.config.ts`, `docker-compose.yml` | Defined |
| backend_port | 8000 (Uvicorn) | backend listen config, `docker-compose.yml` | Defined |
| api_base_path | `/api/v1` | `docs/api/api.md` | Defined |
| frontend_to_backend_url | `http://localhost:8081/api/v1/health` (dev) / `https://isekai-wanderer.example.com/api/v1/health` (prod) | Vite proxy (dev) / Nginx proxy (prod) | Defined |
| vite_proxy_target | `http://localhost:8000` | `vite.config.ts` proxy target | Defined |
| proxy_mode | Vite dev proxy + Nginx reverse proxy (prod) | `vite.config.ts`, `deploy/nginx/nginx.conf` | Defined |
| cors_allowed_origins | `${CORS_ORIGINS}` (env var, default: `http://localhost:8081`) | `backend/app/middleware.py`, `.env.example` | Defined |
| health_endpoint | `/api/v1/health` | `backend/app/api/v1/health.py` | Defined |
| delivery_e2e_command | `docker compose up -d && sleep 5 && curl -f http://localhost/api/v1/health` | `docker-compose.yml`, Nginx 反代 | Defined |
| browser_e2e_command | `APP_BASE=http://localhost:8081 npx playwright test tests/e2e/user-journey.spec.ts tests/e2e/cr002-features.spec.ts --headed --trace on` | Playwright + 真实后端 | Defined |
| browser_e2e_user_actions | CR-001: 注册→登录→选择剧本→开始游戏→做出选择→查看好感度→签到→任务→商店→mock购买→订阅; CR-002: +路线图查看+密码重置流程+语言切换+SEO meta检查+自由对话+通知权限提示 | `tests/e2e/user-journey.spec.ts`, `tests/e2e/cr002-features.spec.ts` | Defined |
| api_contract_doc | `docs/api/api.md` | 41 个端点 + JWT + 错误码 + SSE + 前端消费方矩阵 | Defined |
| database_contract_doc | `docs/database/database.md` | 24 张表 + pgvector + Alembic 迁移 + 备份策略 | Defined |
| persistence_contract | PostgreSQL (主数据) + pgvector (向量) + Redis (缓存/限流/会话) | `docs/database/database.md`, `docker-compose.yml` | Defined |
| mock_policy | no mock API for Delivery E2E / Release evidence; mock only for IPaymentProvider/ISubscriptionProvider/IOAuthProvider/MockEmailService/MockDiscordService implementations | `design.md` Mock 抽象层设计 | Defined |

# Runtime Contract — Isekai Wanderer

## Overview

This document defines the runtime environment contract for Isekai Wanderer. All ports, paths, proxy configurations, and E2E verification commands are specified here to ensure QA, Dev, and Ops can independently validate the system.

---

## Ports & Addresses

| Service | Port | Purpose |
|---------|------|---------|
| PostgreSQL | 5432 | Primary database + pgvector |
| Redis | 6379 | Cache + rate limiting + sessions |
| Vite Dev Server | 8081 | Frontend development |
| Uvicorn | 8000 | Backend API |
| Nginx (prod) | 80/443 | Reverse proxy + SSL |

## Proxy Configuration

### Development

```ts
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

### Production

```nginx
# deploy/nginx/nginx.conf
location /api/v1/ {
    proxy_pass http://backend:8000;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    # SSE support
    proxy_buffering off;
    proxy_cache off;
    proxy_read_timeout 300s;
}
```

## Health Check

```bash
curl -f http://localhost:8000/api/v1/health
# Response: {"status": "ok", "version": "1.0.0"}
```

## Environment Variables

| Variable | Dev Default | Prod Required |
|----------|-------------|---------------|
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@db:5432/isekai` | Yes |
| `REDIS_URL` | `redis://redis:6379/0` | Yes |
| `JWT_SECRET` | `dev-secret-key` | Yes (random) |
| `CORS_ORIGINS` | `http://localhost:8081` | Yes |
| `LLM_API_KEY` | (test key) | Yes |
| `SMTP_HOST` | (mock) | Yes (Resend) |

## CR-002 Additions

### New API Endpoints (4 endpoints, total 45)

| Method | Path | Auth | AC | Purpose |
|---|---|---|---|---|
| GET | /api/v1/game/{scriptId}/route-map | Bearer | AC-045 | Route exploration map |
| POST | /api/v1/auth/forgot-password | None | AC-047 | Password reset request |
| POST | /api/v1/auth/reset-password | None | AC-047 | Password reset execution |
| POST | /api/v1/game/{sessionId}/free-chat | Bearer | AC-058 | Free chat with character |

### New Mock Services

| Mock Service | AC | Replaces | Log File |
|---|---|---|---|
| MockEmailService | AC-047, AC-057 | SMTP / Resend | `logs/mock-email.log` |
| MockDiscordService | AC-055 | Discord Webhook | `logs/mock-discord.log` |

### CR-002 Browser E2E User Actions

| Action | AC | Description |
|---|---|---|
| 路线图查看 | AC-045 | 剧本详情页→点击路线探索→查看高亮/灰色分支 |
| 密码重置 | AC-047 | 登录页→忘记密码→输入邮箱→提交→重置页→输入新密码→提交 |
| 语言切换 | AC-052 | 设置页→选择 English→验证 UI 文本变化→切换回中文 |
| SEO meta 检查 | AC-054 | 查看页面源码→验证 title/description/og:image 存在 |
| 自由对话 | AC-058 | 首页→自由对话→选择角色→选择话题→发送消息→查看流式回复 |
| 通知权限 | AC-056 | 首次进入游戏→查看通知权限提示→点击启用 |

## 规则

- 前端、后端、Vite proxy、`.env.example`、`docker-compose.yml` 必须和本表一致。
- Delivery E2E 必须从真实前端入口访问真实后端；不得用 mock API、fixture server 或组件级替身作为 release 证据。
- Browser Interaction E2E 必须打开真实浏览器并执行用户动作；只用 fetch/curl/API smoke 不能替代前端验收项的浏览器交互证据。
- API、数据库/存储、mock 策略和 runtime 配置必须互相引用。
