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
| browser_e2e_command | `SKIP_WEB_SERVER=1 APP_BASE=http://localhost:8081 npx playwright test tests/e2e/user-journey.spec.ts tests/e2e/cr002-features.spec.ts tests/e2e/cr027-*.spec.ts tests/e2e/cr028-*.spec.ts tests/e2e/cr029-*.spec.ts tests/e2e/cr030-*.spec.ts tests/e2e/cr038-*.spec.ts tests/e2e/cr039-*.spec.ts tests/e2e/cr042-*.spec.ts tests/e2e/cr043-*.spec.ts --project=chromium --trace on` | Playwright + 真实后端 | Defined |
| browser_e2e_user_actions | CR-001: 注册→登录→选择剧本→开始游戏→做出选择→查看好感度→签到→任务→商店→mock购买→订阅; CR-002: +路线图查看+密码重置流程+语言切换+SEO meta检查+自由对话+通知权限提示; CR-027: +Lorebook CRUD+场景配置+NPC内在驱动编辑+管理员权限校验; CR-028: +角色选择+锁定角色+切换角色+存档筛选+角色信息展示; CR-030: +章节进度显示+章节切换实时更新; CR-038: +Corvus剧本开始游戏+预设角色选角(GET /game/scripts/{id}/characters)+选角确认(POST select-player character_id)+SSE逐字渲染+好感度/道具更新+SSE错误重试+无预设选项降级+Corvus会话恢复+旧数据兼容(legacy)+剧本engine_type解析; CR-039: +对话后查看选项面板(ChoicePanel显示2-4个选项)+FreeChatInput有选项时仍可见+点击选项发送(custom-input)+无playerOptions时fallback到纯自由输入+Legacy回归验证; CR-042: +Legacy submit_choice transition节点SSE逐字显示+preset/choice节点保持JSON+done事件推送好感度变化+前端无fetchDialogue二次请求+Legacy submit_custom_input SSE逐字显示+free-chat/stream新端点SSE+旧free-chat保留兼容(Deprecation header)+FreeChatView改用流式端点+model_router stream_with_fallback降级+useSSEStream composable提取+三处Legacy路径使用composable+Corvus分支迁移回归验证; CR-043: +free用户浏览CG画廊看到锁定CG(锁图标+升级提示)+standard用户浏览CG画廊全部可查看无锁图标+free用户浏览剧本列表非试用剧本锁定+点击锁定剧本显示升级提示+用户浏览角色列表不可用角色锁定+点击锁定角色显示升级提示+订阅成功后UI立即更新tier+登录成功后订阅状态自动加载 | `tests/e2e/user-journey.spec.ts`, `tests/e2e/cr002-features.spec.ts`, `tests/e2e/cr027-*.spec.ts`, `tests/e2e/cr028-*.spec.ts`, `tests/e2e/cr030-*.spec.ts`, `tests/e2e/cr038-*.spec.ts`, `tests/e2e/cr039-*.spec.ts`, `tests/e2e/cr042-*.spec.ts`, `tests/e2e/cr043-*.spec.ts` | Defined |
| api_contract_doc | `docs/api/api.md` | 68 端点 + JWT + 错误码 + SSE + 前端消费方矩阵（CR-027 新增 8 个管理端接口；CR-028 新增 1 端点 + 扩展 3 端点；CR-030 新增 1 端点 + 扩展 2 端点；CR-037 新增 1 端点 (GET /game/scripts/{id}/characters) + 扩展 2 端点 (GET /scripts 返回 engine_type) + 改造 1 端点 (select-player 改为 character_id) + 废弃 1 端点 (POST /game/player/candidates deprecated)；CR-042 新增 1 端点 (POST /game/{id}/free-chat/stream) + 改造 2 端点 Legacy 分支 (choice/custom-input 条件 SSE) + 废弃标记 1 端点 (free-chat deprecated)；CR-043 扩展 5 端点 (gallery/collections 返回 is_accessible, scripts 返回 is_accessible, game/start 新增 script_access 检查, users/me/member-info 数据源修复)） | Defined |
| database_contract_doc | `docs/database/database.md` | 37 张表 + pgvector + Alembic 迁移 + 备份策略（CR-027 新增 lorebook_entries、scene_configs，扩展 characters；CR-028 新增 user_character_unlocks，扩展 characters、game_sessions；CR-030 扩展 routes 新增 chapter_number、chapter_type；CR-037 新增 5 张表 player_candidates/corvus_game_sessions/session_npcs/inventory_items/story_flags；CR-038 扩展 corvus_game_sessions 新增 selected_character_id 字段，engine_type 为运行时虚拟字段；CR-043 无 DB 变更，is_accessible 为运行时计算字段） | Defined |
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

## CR-038 Additions (2026-09-10 范围变更后更新)

### New API Endpoint (1 new, total 67)

| Method | Path | Auth | AC | Purpose |
|---|---|---|---|---|
| GET | /api/v1/game/scripts/{script_id}/characters | Bearer | AC-038-026, AC-038-010, AC-038-012 | 返回剧本预设角色列表 (Character 表 playable=True) |

### Modified API: POST /game/session/select-player

| Endpoint | CR-038 Behavior Change |
|----------|------------------------|
| `POST /api/v1/game/session/select-player` | 请求体从 `player_candidate_id` 改为 `character_id`；后端从 Character 表获取角色数据 |

### Deprecated API

| Method | Path | Status | Note |
|---|---|---|---|
| POST | /api/v1/game/player/candidates | Deprecated | 2026-09-07 范围变更：移除自定义角色创建；端点保留但不再使用 |

### Extended API: GET /scripts and GET /scripts/{id}

| Endpoint | CR-038 Behavior Change |
|----------|------------------------|
| `GET /api/v1/scripts` | 每个 script 对象返回 `engine_type: 'corvus'` 字段 (运行时虚拟字段, 不持久化到 DB) |
| `GET /api/v1/scripts/{script_id}` | script 对象返回 `engine_type: 'corvus'` 字段 |

### CR-038 Browser E2E User Actions (范围变更后)

| Action | AC | Description |
|---|---|---|
| Corvus 剧本开始游戏 | AC-038-009 | 选择剧本 → 点击"开始游戏" → 进入选角/游戏界面 |
| 选角列表展示 | AC-038-010 | 等待选角页面加载 → 可见预设角色卡片列表 (GET /game/scripts/{id}/characters) |
| 选定预设角色进入游戏 | AC-038-011 | 点击角色卡片 → 点击确认 → POST select-player (character_id) → 进入游戏界面, SSE 开始 |
| 查看预设角色列表 | AC-038-012 | 打开选角界面 → 可见预设角色卡片列表 (Character 表 playable=True) |
| ~~创建新候选~~ | ~~AC-038-013~~ | ❌ 已移除：移除自定义角色创建 |
| ~~name 为空拒绝~~ | ~~AC-038-014~~ | ❌ 已移除：随创建功能移除 |
| ~~超过 3 个限制~~ | ~~AC-038-015~~ | ❌ 已移除：随创建功能移除 |
| 选择预设角色进入游戏 | AC-038-016 | 点击预设角色 → 确认 → POST select-player (character_id) → 进入游戏界面 |
| SSE 流式渲染 | AC-038-017 | 输入文字 → 发送 → 观察文字逐步渲染 |
| SSE gm_update | AC-038-018 | 对话中 → 好感度/道具列表更新 |
| SSE 错误重试 | AC-038-019 | 模拟断连 → 错误提示 → 重试可用 |
| 无预设选项降级 | AC-038-020 | 完成对话 → 输入框可见可用 |
| 恢复 Corvus 会话 | AC-038-021 | 恢复会话 → engine_type='corvus' → SSE 分支 |
| 旧数据兼容 | AC-038-022 | 恢复旧会话 → legacy 分支正常执行 |
| 剧本列表 engine_type | AC-038-023 | 选择剧本 → 开始 → 走 Corvus 流程 |
| Legacy 保留不激活 | AC-038-024/025 | 选择任意剧本 → 走 Corvus 流程; legacy 代码保留但不执行 |
| 获取预设角色列表 | AC-038-026 | GET /game/scripts/{id}/characters → code:0 + 角色列表 |

### CR-038 Browser E2E Command

```bash
APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr038-*.spec.ts --headed --trace on
```

### CR-038 API Contract Doc

`docs/api/api.md` — 新增 1 端点 (GET /game/scripts/{script_id}/characters) + 2 端点扩展 (GET /scripts, GET /scripts/{id} 返回 engine_type) + 1 端点改造 (POST /game/session/select-player 改为 character_id) + 1 端点废弃 (POST /game/player/candidates deprecated)。

### CR-038 Database Contract Doc

`docs/database/database.md` — CR-038 范围变更后：CorvusGameSession 新增 `selected_character_id` 字段 (UUID 外键 → Character 表)，保留 `selected_player_candidate_id` 向后兼容。GET /scripts 的 engine_type 为运行时虚拟字段，不持久化到数据库。

### CR-038 Persistence Contract

PostgreSQL (主数据) + pgvector (向量) + Redis (缓存/限流/会话) + Corvus 文件存储 (JSON/JSONL)。无新增持久化层。

### CR-038 Mock Policy

- Delivery E2E / Browser E2E / Release 证据禁止 mock API；必须使用真实 Corvus 服务 (127.0.0.1:8082)、真实后端 API、真实 PostgreSQL + pgvector
- 单元测试中 Service 层可 mock CorvusClient
- 组件测试可使用 mock SSE 事件流
- 选角流程使用真实 GET /game/scripts/{id}/characters 端点 + 真实 Character 表数据，不走 mock

## CR-039 Additions

### Overview

CR-039 在 Corvus 引擎 SSE 流式对话中增加 GM 动态生成的玩家选项。无新增端点/端口/proxy 变更。`gm_update` SSE 事件扩展携带 `playerOptions` 字段，后端透传时映射为前端期望的 `choices` 格式。

### Port & Proxy Changes

无变更。复用 CR-037/CR-038 已有端口和代理配置。

### CR-039 Browser E2E User Actions

| Action | AC | Description |
|---|---|---|
| 对话后查看选项面板 | AC-039-005, AC-039-007 | Corvus 对话结束后 → 可见 2-4 个选项 + FreeChatInput 仍可见可输入 |
| 点击选项发送 | AC-039-006 | 点击某个选项 → SSE 流式回应开始 → pendingChoices 清空 |
| 无选项时 fallback | AC-039-008 | GM 未返回 playerOptions → ChoicePanel 隐藏 → FreeChatInput 正常显示 |
| Legacy 回归 | AC-039-009 | 使用 Legacy 引擎剧本 → 选择功能不回归 |

### CR-039 Browser E2E Command

```bash
SKIP_WEB_SERVER=1 APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr039-*.spec.ts tests/e2e/cr038-*.spec.ts --project=chromium --trace on
```

### CR-039 Delivery E2E Command

```bash
docker compose up -d && sleep 5 && curl -f http://localhost:8000/api/v1/health
curl -N -X POST http://localhost:8081/api/v1/game/{id}/custom-input -H "Accept: text/event-stream" -d '{"text":"你好"}'
```

### CR-039 API Contract Doc

`docs/api/api.md` — 无新增端点。SSE `gm_update` 事件扩展：增加 `playerOptions` 字段透传，后端映射为 `choices` 格式。

### CR-039 Database Contract Doc

`docs/database/database.md` — Not Required: 无 DB 变更。playerOptions 是 LLM 动态生成的运行时数据，不持久化。

### CR-039 Persistence Contract

无变更。复用 CR-037/CR-038 已有持久化配置。

### CR-039 Mock Policy

无变更。Delivery E2E / Browser E2E / Release 证据禁止 mock API；必须使用真实 Corvus 服务、真实 LLM 网关、真实 PostgreSQL + pgvector。

## CR-042 Additions

### Overview

CR-042 将 Legacy 引擎的三条非流式路径改为 SSE 流式输出，复用 Corvus SSE 基础设施。无新增端口/proxy 变更。新增 1 个端点，改造 2 个端点的 Legacy 分支响应类型。

### New API Endpoints (1 new, total 68)

| Method | Path | Auth | AC | Purpose |
|---|---|---|---|---|
| POST | /api/v1/game/{session_id}/free-chat/stream | Bearer | AC-011, AC-013, AC-014 | 自由对话 SSE 流式端点（新增） |

### Modified API Endpoints (Legacy branches only)

| Method | Path | CR-042 Behavior Change |
|----------|------------------------|
| `POST /api/v1/game/{id}/choice` | Legacy 分支：transition/ai_dialog 节点返回 `text/event-stream` SSE；preset/choice 节点保持 JSON 响应 |
| `POST /api/v1/game/{id}/custom-input` | Legacy 分支：改为 `text/event-stream` SSE 流式响应 |
| `POST /api/v1/game/{id}/free-chat` | 保留同步 JSON 响应；追加 `Deprecation: true` 响应头标记废弃 |

### SSE Event Format (Legacy paths, same as Corvus)

```
data: {"type":"text","content":"..."}\n\n          ← 逐字推送
data: {"type":"emotion","emotion":"...","character_id":"..."}\n\n  ← 情绪标签
data: {"type":"affection_update","character_id":"...","value":45,"level":"trust"}\n\n  ← 好感度
data: {"type":"done","session_id":"...","node_id":"...","affection_change":{...},"choices":[...]}\n\n  ← 流结束 + 元数据
data: {"type":"error","message":"..."}\n\n           ← 错误事件
```

注意：Legacy 路径不使用 `gm_update` 事件（Corvus 特有）。Legacy 路径的元数据通过 `done` 事件一次性推送。

### Response Headers (all streaming endpoints)

| Header | Value |
|-------|-------|
| Content-Type | text/event-stream |
| Cache-Control | no-cache |
| Connection | keep-alive |
| X-Accel-Buffering | no |

### CR-042 Browser E2E User Actions

| Action | AC | Description |
|---|---|---|
| Legacy submit_choice SSE | AC-001, AC-003 | 打开 Legacy 剧本游戏页面 → 点击选项 → 观察对话逐字显示 → 确认 SSE 事件格式 |
| Legacy preset/choice JSON | AC-002 | 点击选项 → 观察 JSON 响应快速返回，无逐字显示 |
| Legacy done 元数据 | AC-004 | SSE 流结束 → 查询好感度确认更新 → 查询对话历史确认写入 |
| 前端无 fetchDialogue | AC-005 | 点击选项 → Network 面板确认无 fetchDialogue 请求 |
| Legacy submit_custom_input SSE | AC-006, AC-008 | 填写自由文本 → 提交 → 观察角色回应逐字显示 |
| Legacy custom_input done 元数据 | AC-009 | SSE 流结束 → 查询好感度确认更新 |
| free-chat/stream 新端点 | AC-011, AC-013 | 自由对话 → 发送消息 → 观察回复逐字显示 |
| 旧 free-chat 兼容 | AC-015 | 调用旧端点 → 确认 JSON 200 + Deprecation header |
| FreeChatView 流式 | AC-016 | 打开自由对话 → 发送消息 → 观察逐字显示 |
| model_router stream | AC-017, AC-018, AC-019 | 单元测试验证 stream_with_fallback 方法 |
| useSSEStream composable | AC-020 | 单元测试验证 composable 解析 SSE 事件 |
| 三处使用 composable | AC-021 | 代码审查确认 submitChoice/submitCustomInput/FreeChatView 使用 composable |
| Corvus 回归 | AC-022 | Corvus 路径完整对话流程回归测试 |

### CR-042 Browser E2E Command

```bash
SKIP_WEB_SERVER=1 APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr042-*.spec.ts --project=chromium --trace on
```

### CR-042 Delivery E2E Command

```bash
docker compose up -d && sleep 5 && curl -f http://localhost:8000/api/v1/health
curl -N -X POST http://localhost:8081/api/v1/game/{session_id}/free-chat/stream -H "Content-Type: application/json" -H "Authorization: Bearer {token}" -d '{"message":"你好"}'
curl -N -X POST http://localhost:8081/api/v1/game/{session_id}/choice -H "Content-Type: application/json" -H "Authorization: Bearer {token}" -d '{"choice_id":"{uuid}"}'  # SSE for transition nodes
curl -N -X POST http://localhost:8081/api/v1/game/{session_id}/custom-input -H "Content-Type: application/json" -H "Authorization: Bearer {token}" -d '{"text":"你好"}'  # SSE
curl -X POST http://localhost:8081/api/v1/game/{session_id}/free-chat -H "Content-Type: application/json" -H "Authorization: Bearer {token}" -d '{"message":"你好"}'  # Old endpoint, JSON 200 + Deprecation header
```

### CR-042 API Contract Doc

`docs/api/api.md` — 新增 1 端点 (POST /game/{id}/free-chat/stream) + 2 端点 Legacy 分支改造 (choice/custom-input 条件 SSE) + 1 端点废弃标记 (free-chat deprecated) + SSE 事件格式说明 (Legacy done 事件一次性推送元数据)。

### CR-042 Database Contract Doc

`docs/database/database.md` — Not Required: 无 DB 表结构变更。对话历史写入复用现有 `DialogueHistory` 表；好感度更新复用现有 `Affection` 表；free_chat 消息保存复用现有 `FreeChatSession` 表。Deferred DB 写入使用独立 session，不影响现有表结构。

### CR-042 Persistence Contract

无变更。复用 CR-037/CR-038 已有持久化配置。PostgreSQL (主数据) + Redis (缓存/限流/会话)。

### CR-042 Mock Policy

无变更。Delivery E2E / Browser E2E / Release 证据禁止 mock API；必须使用真实后端 API、真实 LLM 网关、真实 PostgreSQL + Redis。单元测试中 Service 层可 mock LLM Gateway 和 Provider stream 方法。

## CR-043 Additions

### Overview

CR-043 在现有 API 端点层增加订阅权益强制检查逻辑。无新增端点、端口或 proxy 变更。扩展现有 5 个端点的行为。

### Extended API Endpoints (0 new, 5 extended)

| Method | Path | Auth | AC | CR-043 Behavior Change |
|---|---|---|---|---|
| GET | /api/v1/gallery/collections/{script_id} | Bearer | AC-001~004 | 每个 CG 项新增 `is_accessible: boolean` 字段 |
| GET | /api/v1/scripts | Optional Bearer | AC-009 | 每个剧本项新增 `is_accessible: boolean` 字段（已认证时） |
| GET | /api/v1/scripts/{script_id} | Bearer | AC-010 | 剧本对象新增 `is_accessible: boolean` 字段 |
| POST | /api/v1/game/start | Bearer | AC-005~008, AC-015 | 创建 GameSession 前检查 `script_access`，权限不足返回 403 `SCRIPT_ACCESS_DENIED` |
| GET | /api/v1/users/me/member-info | Bearer | AC-018, AC-019 | `tier` 从 `SubscriptionService.get_user_tier()` 获取；`status`/`expires_at` 从 Subscription 表获取 |

### New Error Code

| Error Code | HTTP Status | Meaning |
|---|---|---|
| SCRIPT_ACCESS_DENIED | 403 | 订阅等级不足以游玩此剧本 |

### CR-043 Browser E2E User Actions

| Action | AC | Description |
|---|---|---|
| free 用户浏览 CG 画廊看到锁定 CG | AC-002, AC-011 | free 用户打开画廊→查看未解锁 CG→显示锁图标和升级提示→点击锁定 CG 不展开完整图片 |
| standard 用户浏览 CG 画廊全部可查看 | AC-003 | standard 用户打开画廊→全部 CG 无锁图标→点击任意 CG→预览完整图片 |
| free 用户浏览剧本列表非试用剧本锁定 | AC-012 | free 用户浏览剧本列表→非试用剧本显示锁定→点击锁定剧本→显示升级提示 |
| 用户浏览角色列表不可用角色锁定 | AC-010, AC-013 | 用户浏览角色列表→不可用角色显示锁定→点击锁定角色→显示升级提示 |
| 订阅成功后 UI 立即更新 tier | AC-016, AC-017 | 用户订阅成功→UI 立即显示新 tier→无需手动刷新页面 |
| 登录成功后订阅状态自动加载 | AC-020 | 用户登录→订阅状态自动加载→无需手动触发或页面刷新 |

### CR-043 Browser E2E Command

```bash
SKIP_WEB_SERVER=1 APP_BASE=http://localhost:8081 npx playwright test tests/e2e/cr043-*.spec.ts --project=chromium --trace on
```

### CR-043 Delivery E2E Command

```bash
docker compose up -d && sleep 5 && curl -f http://localhost:8000/api/v1/health
curl -H "Authorization: Bearer {free_user_token}" http://localhost:8081/api/v1/gallery/collections/{script_id} | python -m json.tool | grep is_accessible
curl -X POST -H "Authorization: Bearer {free_user_token}" -H "Content-Type: application/json" -d '{"script_id":"{non_trial_script_id}"}' http://localhost:8081/api/v1/game/start
curl -H "Authorization: Bearer {token}" http://localhost:8081/api/v1/users/me/member-info
```

### CR-043 API Contract Doc

`docs/api/api.md` — 0 新增 + 5 扩展（gallery/collections 返回 is_accessible, scripts 返回 is_accessible, game/start 新增 script_access 检查, users/me/member-info 数据源修复）+ 1 新错误码 (SCRIPT_ACCESS_DENIED)。

### CR-043 Database Contract Doc

`docs/database/database.md` — Not Required: 无 DB 表结构变更。is_accessible 为运行时计算字段；script_access 三档映射为运行时虚拟判定；member-info 数据源修复只改变后端读取逻辑。

### CR-043 Persistence Contract

无变更。复用现有 PostgreSQL (主数据) + Redis (缓存/限流/会话)。

### CR-043 Mock Policy

无变更。Delivery E2E / Browser E2E / Release 证据禁止 mock API；必须使用真实后端 API、真实 PostgreSQL + Redis。
