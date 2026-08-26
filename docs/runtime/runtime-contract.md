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
| browser_e2e_command | `APP_BASE=http://localhost:8081 npx playwright test tests/e2e/user-journey.spec.ts tests/e2e/cr002-features.spec.ts tests/e2e/cr027-*.spec.ts tests/e2e/cr028-*.spec.ts tests/e2e/cr029-*.spec.ts --headed --trace on` | Playwright + 真实后端 | Defined |
| browser_e2e_user_actions | CR-001: 注册→登录→选择剧本→开始游戏→做出选择→查看好感度→签到→任务→商店→mock购买→订阅; CR-002: +路线图查看+密码重置流程+语言切换+SEO meta检查+自由对话+通知权限提示; CR-027: +Lorebook CRUD+场景配置+NPC内在驱动编辑+管理员权限校验; CR-028: +角色选择+锁定角色+切换角色+存档筛选+角色信息展示; CR-030: +章节进度显示+章节切换实时更新 | `tests/e2e/user-journey.spec.ts`, `tests/e2e/cr002-features.spec.ts`, `tests/e2e/cr027-*.spec.ts`, `tests/e2e/cr028-*.spec.ts`, `tests/e2e/cr030-*.spec.ts` | Defined |
| api_contract_doc | `docs/api/api.md` | 62 端点 + JWT + 错误码 + SSE + 前端消费方矩阵（CR-027 新增 8 个管理端接口；CR-028 新增 1 端点 + 扩展 3 端点；CR-030 新增 1 端点 + 扩展 2 端点） | Defined |
| database_contract_doc | `docs/database/database.md` | 32 张表 + pgvector + Alembic 迁移 + 备份策略（CR-027 新增 lorebook_entries、scene_configs，扩展 characters；CR-028 新增 user_character_unlocks，扩展 characters、game_sessions；CR-030 扩展 routes 新增 chapter_number、chapter_type） | Defined |
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

## CR-027 Additions

### New API Endpoints (8 endpoints, total 58)

| Method | Path | Auth | AC | Purpose |
|---|---|---|---|---|
| GET | /api/v1/lorebook | Bearer + Admin | AC-LORE-001 | Lorebook 条目列表（支持 ?tag= 筛选、分页） |
| POST | /api/v1/lorebook | Bearer + Admin | AC-LORE-001 | 创建 Lorebook 条目 |
| GET | /api/v1/lorebook/{id} | Bearer + Admin | AC-LORE-001 | Lorebook 条目详情 |
| PUT | /api/v1/lorebook/{id} | Bearer + Admin | AC-LORE-002 | 更新 Lorebook 条目 |
| DELETE | /api/v1/lorebook/{id} | Bearer + Admin | AC-LORE-002 | 软删除 Lorebook 条目 |
| GET | /api/v1/scene-configs | Bearer + Admin | AC-SCENE-002 | 场景配置列表（按 script/route 过滤） |
| PUT | /api/v1/scene-configs/node/{node_id} | Bearer + Admin | AC-SCENE-001 | 创建或更新 Node 场景配置 |
| DELETE | /api/v1/scene-configs/node/{node_id} | Bearer + Admin | AC-SCENE-001 | 删除 Node 场景配置 |

### Extended API: PUT /api/v1/characters/{id}

新增可选字段：`desire` (TEXT), `fear` (TEXT), `secret` (TEXT)。向后兼容。

### CR-027 Browser E2E User Actions

| Action | AC | Description |
|---|---|---|
| Lorebook CRUD | AC-LORE-001, AC-ADMIN-001 | 管理员登录→导航 Lorebook 管理页→新建/编辑/删除条目→列表刷新验证 |
| Lorebook 标签筛选 | AC-LORE-003 | 管理员选择标签筛选→列表仅显示匹配条目 |
| 场景配置 | AC-SCENE-001, AC-ADMIN-002 | 管理员导航场景配置页→查看剧本→路线→Node 树→为 Node 配置场景→保存 |
| NPC 内在驱动 | AC-NPC-002, AC-ADMIN-003 | 管理员进入 NPC 编辑页→填写渴望/恐惧/秘密→保存→成功提示 |
| 管理员权限校验 | AC-ADMIN-004 | 普通用户访问 Lorebook/场景配置/NPC 编辑页→403 或重定向 |

### CR-027 Mock Policy

- Delivery E2E / Browser E2E 禁止 mock API
- LLM Gateway 可在开发/测试环境使用 mock 实现
- 单元测试中 Service 层可 mock 数据库

## CR-028 Additions

### New/Extended API Endpoints (1 new + 3 extended, total 61)

| Method | Path | Auth | AC | Purpose |
|---|---|---|---|---|
| GET | /api/v1/scripts/{id} | Bearer | AC-PLAY-001 | 扩展：返回 playable_characters 列表 |
| POST | /api/v1/game/start | Bearer | AC-PLAY-002 | 扩展：接受可选 character_id 参数 |
| GET | /api/v1/saves | Bearer | AC-PLAY-004, AC-PLAY-005 | 扩展：返回角色信息 + 支持 character_id 筛选 |
| POST | /api/v1/characters/{character_id}/unlock | Bearer | AC-PLAY-009 | 新增：解锁付费角色 |

### CR-028 Browser E2E User Actions

| Action | AC | Description |
|---|---|---|
| 角色选择 | AC-PLAY-001 | 进入剧本详情页→看到可扮演角色→点击角色→角色高亮选中→按钮文案更新 |
| 锁定角色 | AC-PLAY-006 | 进入剧本详情页→查看付费角色→点击锁定角色→弹出解锁提示 |
| 切换角色 | AC-PLAY-003 | 选角色A开始游戏→返回→选角色B开始游戏→存档列表显示两条 |
| 存档筛选 | AC-PLAY-005 | 进入存档管理页→点击角色标签→列表筛选→点击全部→恢复 |
| 角色信息 | AC-PLAY-004 | 进入个人中心→查看存档→每条存档显示角色名 |

## CR-029 Additions

### Extended Behavior: Node Character Filtering

No new endpoints. Existing endpoints gain character-aware node filtering:

| Endpoint | CR-029 Behavior Change |
|----------|------------------------|
| `GET /api/v1/game/{sessionId}/dialogue` | Returns only nodes where `character_id IS NULL OR character_id = session.character_id` |
| `POST /api/v1/game/{sessionId}/choice` | Validates next node visibility; returns 403 `NARRATIVE_NODE_NOT_VISIBLE` if mismatch |

### CR-029 Browser E2E User Actions

| Action | AC | Description |
|--------|----|----|
| 角色分支选择 | AC-BRANCH-003 | 选择角色A开始游戏→到达分支起点→看到角色A专属分支→选择后汇合到公共节点 |
| 分支汇合验证 | AC-BRANCH-003 | 分别用角色A/B/C完成分支→验证汇合到相同节点 |
| 选择项数量 | AC-BRANCH-006 | 到达选择节点→验证显示3个选项（而非2个） |
| 向后兼容 | AC-BRANCH-007 | 使用旧session继续游戏→验证只看到公共节点→剧情正常推进 |

## CR-037 Additions

### New Service: Corvus-Story-Core

| Service | Port | Purpose | Access |
|---------|------|---------|---------|
| Corvus-Story-Core | 8082 | Node.js Express AI 叙事引擎 (GM 循环 + LLM 调用) | `127.0.0.1` only (systemd 守护, 公网 iptables DROP) |

### New API Endpoints (4 endpoints, total 65)

| Method | Path | Auth | AC | Purpose |
|---|---|---|---|---|
| POST | /api/v1/game/session/create | Bearer | AC-006 | 创建剧本会话 (返回 game_session_id UUID v4) |
| GET | /api/v1/game/player/candidates | Bearer | AC-005 | 获取候选角色 (最多 3 个) |
| POST | /api/v1/game/session/select-player | Bearer | AC-007 | 选定角色 + 调 Corvus 创建游戏 |
| POST | /api/v1/game/game-turn | Bearer | (备用同步版) | 游戏回合同步版 (供 API 调用) |

### Extended API: Feature Flag

| Endpoint | CR-037 Behavior Change |
|----------|------------------------|
| `POST /api/v1/game/start` | 新增 engine_type 参数；engine_type=corvus 时创建 corvus_game_sessions |
| `GET /api/v1/game/{id}/dialogue` | engine_type=corvus 时调 CorvusClient.get_game() 映射 |
| `POST /api/v1/game/{id}/custom-input` | engine_type=corvus 时 SSE 流式透传 (含向量召回注入) |
| `POST /api/v1/game/{id}/choice` | engine_type=corvus 时 SSE 流式透传 (choice_text 作为 input) |

### SSE Proxy Configuration

Nginx SSE proxy (已配置 `proxy_buffering off; proxy_cache off; proxy_read_timeout 300s;`) 支持长连接 SSE 流式透传。Vite dev proxy 也支持 SSE。

### CR-037 Delivery E2E

| Command | Frontend Entry | Backend | API/Proxy Path | Mock API |
|---|---|---|---|---|
| `systemctl status corvus-story && curl -f http://127.0.0.1:8082/api/health` | 无 | `127.0.0.1:8082` | `/api/health` | no |
| `curl --connect-timeout 5 http://<server-ip>:8082/api/health` (外部主机) | 无 | `<server-ip>:8082` | `/api/health` | no |
| `curl http://localhost:8081/api/v1/game/player/candidates?user_id={uuid}` | `http://localhost:8081` | `http://localhost:8000` | `/api/v1/game/player/candidates` | no |
| `curl -N -X POST http://localhost:8081/api/v1/game/{id}/custom-input -H "Accept: text/event-stream" -d '{"text":"你好"}'` | `http://localhost:8081` | `http://localhost:8000` → `127.0.0.1:8082` | `/api/v1/game/{id}/custom-input` (SSE) | no |

### CR-037 Browser Interaction E2E User Actions

| Action | AC | Description |
|---|---|---|
| 候选角色列表展示 | AC-005 | 打开角色选择页面 → 可见 3 个角色卡片 |
| 选定角色进入游戏 | AC-007 | 点击角色卡片选择 → 页面切换到游戏界面 |
| SSE 流式逐字渲染 | AC-009 | 输入文本 → 点击发送 → 观察文字逐字出现 |
| SSE 中断错误处理 | AC-011 | 模拟断连 → 观察错误提示 → 点击重试 → 可重新发送 |
| 旧引擎回归测试 | AC-019 | 打开旧剧本 → 正常推进剧情 → 验证功能不变 |
| 页面路由不变 | AC-023 | 浏览器输入 `/game?script={uuid}` → 页面正常加载 |
| choices 为空降级 | AC-024 | 完成对话后 → 无选项按钮 → 可在输入框自由输入 |

### CR-037 Browser E2E Command

```bash
APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr037-*.spec.ts --headed --trace on
```

### CR-037 API Contract Doc

`docs/api/api.md` — 新增 4 端点 + 4 端点扩展 feature flag + SSE 事件映射表。

### CR-037 Database Contract Doc

`docs/database/database.md` — 新增 5 张表 (player_candidates, corvus_game_sessions, session_npcs, inventory_items, story_flags) + character_memories embedding 维度 1536→512 重建。

### CR-037 Persistence Contract

PostgreSQL (主数据) + pgvector (向量, 512 维) + Redis (缓存/限流/会话) + Corvus 文件存储 (JSON/JSONL, 会话内剧情对话, 用完即弃)。

### CR-037 Mock Policy

- Delivery E2E / Browser E2E / Release 证据禁止 mock API；必须使用真实 Corvus 服务 (127.0.0.1:8082)、真实 LLM 网关 (thoushub → deepseek-v4-flash)、真实 PostgreSQL + pgvector
- 单元测试中 Service 层可 mock CorvusClient 和 EmbeddingService
- 组件测试可使用 mock SSE 事件流

## 规则

- 前端、后端、Vite proxy、`.env.example`、`docker-compose.yml` 必须和本表一致。
- Delivery E2E 必须从真实前端入口访问真实后端；不得用 mock API、fixture server 或组件级替身作为 release 证据。
- Browser Interaction E2E 必须打开真实浏览器并执行用户动作；只用 fetch/curl/API smoke 不能替代前端验收项的浏览器交互证据。
- API、数据库/存储、mock 策略和 runtime 配置必须互相引用。
