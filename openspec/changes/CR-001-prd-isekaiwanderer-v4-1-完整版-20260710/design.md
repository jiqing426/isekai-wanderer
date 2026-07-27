# Design: CR-001 — Isekai Wanderer MVP

## Overview

本文记录 CR-001（Isekai Wanderer MVP）的技术设计。系统采用前后端分离架构，前端为 Vue 3 PWA，后端为 Python FastAPI 微服务，PostgreSQL 为主数据库，pgvector 为向量存储，统一 LLM 调用层支持多模型切换。

### 设计目标

- 核心游戏循环（叙事 → 选择 → 好感度 → 记忆 → 结局）可跑通
- 3 个剧本（乙女恋爱 3 路线 + 奇幻冒险 2 路线 + 悬疑推理 2 路线）全部可玩
- P0 全量 + P1 全量功能覆盖
- Mock 支付/订阅/OAuth 可验证商业意愿，架构预留真实接口
- 首屏 <3s，流式文字 ≥30fps，表情切换 <200ms

### 非目标

- 不做管理后台（CEO 裁剪）
- 不接入真实支付/OAuth
- 不做 Live2D / 3D
- 不做离线 PWA
- 不做多语言动态切换（仅英文 UI 翻译）

## Technical Approach

### 整体架构

```txt
┌─────────────────────────────────────────────────────┐
│                    CDN / Nginx                       │
│              (静态资源 + 反向代理)                     │
└────────┬────────────────────────────┬────────────────┘
         │ /                          │ /api/v1/*
         ▼                            ▼
┌─────────────────┐         ┌──────────────────────┐
│  Vue 3 PWA      │         │  FastAPI Backend      │
│  (Vite dev/     │  proxy  │  (Uvicorn)            │
│   Nginx prod)   │────────>│                      │
│  :3000 / :80    │         │  :8000                │
└─────────────────┘         └──────┬───────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
              ┌──────────┐  ┌──────────┐  ┌──────────────┐
              │PostgreSQL│  │  Redis   │  │ LLM Gateway  │
              │ +pgvector│  │ (cache/  │  │ (多模型切换)  │
              │  :5432   │  │  session)│  │              │
              └──────────┘  │  :6379   │  └──────────────┘
                            └──────────┘
```

### 后端框架选型：Python FastAPI

**选型理由**（详见 ADR-0001）：

| 维度 | FastAPI (选定) | NestJS |
|------|---------------|--------|
| AI/LLM 生态 | Python 原生，LangChain/LlamaIndex/openai SDK 直接可用 | 需 HTTP 桥接 Python AI 服务 |
| 向量操作 | pgvector Python SDK 原生支持 | 需额外适配 |
| 异步性能 | asyncio 原生，适合 LLM 调用 I/O 密集场景 | 事件循环模型也适合 |
| 开发效率 | 类型提示 + 自动文档，代码量少 | TypeScript 全栈共享类型方便 |
| 部署 | 单进程 Uvicorn，Docker 镜像小 | Node.js 镜像也小 |
| 团队 | Python AI 工程师可直接参与 | 需 TypeScript 能力 |

**结论**：Python FastAPI。AI 密集型项目用 Python 生态是最自然的选择，避免跨语言桥接复杂度。

### 向量数据库选型：pgvector

**选型理由**（详见 ADR-0002）：

| 维度 | pgvector (选定) | Pinecone | Milvus |
|------|----------------|----------|--------|
| 运维复杂度 | 复用 PostgreSQL，零额外服务 | SaaS 托管，低 | 独立集群，高 |
| MVP 数据量 | <100K 向量，pgvector 性能足够 | 足够 | 过度 |
| 成本 | 无额外费用 | $70+/月起步 | 自托管资源开销 |
| 查询灵活性 | SQL + 向量混合查询 | 纯向量 | 纯向量 |
| 迁移到专用 | 可后续迁移，embedding 列独立 | 锁定 | 锁定 |

**结论**：pgvector。MVP 阶段复用 PostgreSQL 减少运维和成本，数据量增长后可平滑迁移到专用向量数据库。

### LLM 调用层

统一 LLM Gateway 抽象层，支持多模型切换：

```python
class LLMProvider(Protocol):
    async def chat(self, messages: list[Message], **kwargs) -> AsyncIterator[str]: ...
    async def embed(self, text: str) -> list[float]: ...

class OpenAIProvider(LLMProvider): ...
class AnthropicProvider(LLMProvider): ...
class LocalProvider(LLMProvider): ...  # 本地模型/Ollama
```

- MVP 默认使用 OpenAI GPT-4o-mini（成本低、延迟可控）
- Embedding 使用 OpenAI text-embedding-3-small（1536 维）
- 通过环境变量 `LLM_PROVIDER` 切换，不改业务代码
- 流式输出通过 SSE (Server-Sent Events) 推送到前端

## Technology Decisions

| Decision | Selected | Status | Evidence |
| --- | --- | --- | --- |
| 前端框架 | Vue 3 + TypeScript | Accepted | 用户确认（2026-07-18） |
| UI 框架 | Naive UI（二次元定制主题） | Accepted | 用户确认；Naive UI 主题定制灵活度高于 Element Plus |
| 状态管理 | Pinia | Accepted | 用户确认（2026-07-18） |
| 构建工具 | Vite | Accepted | 用户确认（2026-07-18） |
| 路由 | Vue Router 4 | Accepted | 用户确认（2026-07-18） |
| 部署形态 | PWA（网页端优先） | Accepted | 用户确认（2026-07-18） |
| 后端框架 | Python FastAPI | Accepted | 用户确认 + Architect 评估推荐（ADR-0001） |
| 主数据库 | PostgreSQL + pgvector | Accepted | 用户确认 PostgreSQL + Architect 推荐 pgvector（ADR-0002） |
| 缓存 | Redis | Accepted | Architect 推荐（ADR-0007）；会话缓存、签到状态、限流 |
| LLM 调用 | 统一 Gateway 抽象层 | Accepted | Architect 推荐（ADR-0008）；MVP 默认 GPT-4o-mini |
| Embedding | OpenAI text-embedding-3-small | Accepted | Architect 推荐（ADR-0008 扩展）；1536 维，性价比最优 |
| 部署方式 | Docker Compose + VPS | Accepted | 用户确认 Q-005 默认值 |
| 反向代理 | Nginx | Accepted | Architect 推荐（ADR-0008 扩展）；静态资源 + API 反代 + SSL termination |
| 邮件服务 | Resend / SendGrid（MVP 可用 mock） | Accepted | Architect 推荐 console mock for MVP；生产环境切换到 Resend（ADR-0008 扩展） |
| 前端测试 | Vitest + Playwright | Accepted | Architect 推荐（ADR-0006 扩展） |
| 后端测试 | pytest + httpx (AsyncClient) | Accepted | FastAPI 标准测试栈（ADR-0001 扩展） |

## Module Design

### 模块清单

| 模块 | 路径 | 职责 | 技术栈 |
| --- | --- | --- | --- |
| `frontend/` | `/root/isekai-wanderer/frontend` | Vue 3 PWA 用户端 | Vue 3 + TS + Vite + Pinia + Naive UI |
| `backend/` | `/root/isekai-wanderer/backend` | FastAPI 后端服务 | Python 3.12 + FastAPI + SQLAlchemy + Alembic |
| `deploy/` | `/root/isekai-wanderer/deploy` | Docker Compose + Nginx | Docker + Nginx |
| `scripts/` | `/root/isekai-wanderer/scripts` | 构建/测试/部署脚本 | Shell + Python |
| `data/` | `/root/isekai-wanderer/data` | 剧本数据（JSON/YAML） | JSON |
| `assets/` | `/root/isekai-wanderer/assets` | 美术资源 | 图片/音频 |

### 模块职责矩阵

| 模块 | 可负责 | 不负责 |
| --- | --- | --- |
| `frontend/` | 用户端页面、交互、状态、PWA manifest、Service Worker | 业务裁决、数据库访问、LLM 直接调用 |
| `backend/` | API、叙事引擎、记忆系统、好感度计算、签到/任务、mock 支付/订阅、LLM Gateway、规则引擎 | 用户界面、管理端 |
| `deploy/` | 容器编排、Nginx 配置、环境变量注入 | 业务逻辑 |
| `data/` | 剧本节点 JSON、角色配置、兜底对话 | 运行时数据 |
| `assets/` | 立绘、背景、BGM、CG 图片 | 动态生成资源 |

### 依赖方向

```txt
frontend ──(HTTP/SSE)──> backend ──> PostgreSQL/pgvector
                             ├──> Redis
                             └──> LLM API (外部)
deploy 依赖所有模块的配置，但业务代码不依赖 deploy。
```

## Backend Architecture

### 分层结构

```txt
backend/
├── app/
│   ├── main.py                 # FastAPI app 入口
│   ├── config.py               # 环境变量配置
│   ├── dependencies.py         # FastAPI 依赖注入
│   ├── models/                 # SQLAlchemy ORM 模型
│   │   ├── user.py
│   │   ├── script.py
│   │   ├── affection.py
│   │   ├── memory.py
│   │   ├── daily.py
│   │   └── payment.py
│   ├── schemas/                # Pydantic 请求/响应模型
│   │   ├── user.py
│   │   ├── script.py
│   │   ├── game.py
│   │   └── payment.py
│   ├── api/                    # 路由层
│   │   ├── v1/
│   │   │   ├── auth.py         # 注册/登录/OAuth mock
│   │   │   ├── scripts.py      # 剧本列表/路线/节点
│   │   │   ├── game.py         # 游戏会话/对话/选择
│   │   │   ├── affection.py    # 好感度查询/变更
│   │   │   ├── memory.py       # 记忆存储/召回（内部）
│   │   │   ├── daily.py        # 签到/任务
│   │   │   ├── payment.py      # mock 内购/订阅
│   │   │   ├── social.py       # 分享/结局卡片
│   │   │   └── health.py       # 健康检查
│   │   └── middleware.py       # CORS/日志/限流
│   ├── services/               # 业务逻辑层
│   │   ├── narrative_engine.py # 叙事引擎核心
│   │   ├── rule_engine.py      # 规则校验引擎
│   │   ├── memory_service.py   # 记忆存储/召回
│   │   ├── affection_service.py
│   │   ├── script_service.py
│   │   ├── daily_service.py
│   │   ├── payment_service.py
│   │   └── subscription_service.py
│   ├── llm/                    # LLM 调用层
│   │   ├── gateway.py          # 统一 LLM Gateway
│   │   ├── providers/          # 各模型 Provider
│   │   │   ├── openai_provider.py
│   │   │   ├── anthropic_provider.py
│   │   │   └── local_provider.py
│   │   ├── prompts/            # Prompt 模板
│   │   │   ├── narrative.py
│   │   │   ├── memory_extract.py
│   │   │   └── style.py
│   │   └── fallback.py         # 兜底机制
│   └── core/                   # 基础设施
│       ├── database.py         # DB session
│       ├── redis.py            # Redis client
│       ├── security.py         # JWT/密码哈希
│       └── email.py            # 邮件发送（mock 接口）
├── alembic/                    # 数据库迁移
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── pyproject.toml
└── Dockerfile
```

### 叙事引擎核心流程

```txt
用户选择/对话
      │
      ▼
┌─────────────────┐
│ ScriptService    │ ← 查询当前节点、判断节点类型
│ (剧本状态机)     │
└────┬────────────┘
     │
     ├── 预设节点 → 直接返回预设内容 + 触发条件检查
     │
     └── 过渡节点 → 进入 LLM 生成流程
            │
            ▼
     ┌─────────────┐
     │ LLM Gateway  │ ← 角色性格约束 + 记忆注入 + 情绪标注
     │ (AI 生成)    │
     └────┬────────┘
          │
          ▼
     ┌─────────────┐
     │ RuleEngine   │ ← 性格一致性 + 时间线 + 好感度范围
     │ (规则校验)   │
     └────┬────────┘
          │
          ├── 通过 → SSE 流式返回前端
          │
          └── 拦截 → 重试(最多2次) → 兜底对话
```

### 记忆系统流程

```txt
对话结束
    │
    ▼
┌──────────────────┐
│ MemoryExtractor   │ ← LLM 提取关键信息（异步）
│ (记忆提取)        │
└────┬─────────────┘
     │ 有记忆
     ▼
┌──────────────────┐
│ EmbeddingService  │ ← text-embedding-3-small
│ (向量化)          │
└────┬─────────────┘
     │
     ▼
┌──────────────────┐
│ pgvector INSERT   │ ← user_id + character_id + text + vector
└──────────────────┘

对话生成时
    │
    ▼
┌──────────────────┐
│ MemoryService     │ ← 当前对话上下文 embedding
│ .recall()         │
└────┬─────────────┘
     │
     ▼
┌──────────────────┐
│ pgvector KNN      │ ← WHERE similarity > 0.8 LIMIT 3
│ (相似度检索)      │
└────┬─────────────┘
     │
     ▼
注入 LLM prompt context
```

## Frontend Architecture

### 目录结构

```txt
frontend/
├── src/
│   ├── App.vue
│   ├── main.ts
│   ├── router/
│   │   └── index.ts           # 路由配置
│   ├── stores/                # Pinia stores
│   │   ├── auth.ts            # 用户认证状态
│   │   ├── game.ts            # 游戏会话状态
│   │   ├── script.ts          # 剧本/路线数据
│   │   ├── affection.ts       # 好感度状态
│   │   ├── daily.ts           # 签到/任务状态
│   │   └── ui.ts              # UI 全局状态（音量/主题）
│   ├── views/                 # 页面组件
│   │   ├── HomeView.vue       # 首页（剧本列表）
│   │   ├── GameView.vue       # 游戏主界面
│   │   ├── LoginView.vue      # 登录/注册
│   │   ├── ProfileView.vue    # 个人中心
│   │   ├── ShopView.vue       # 内购商店
│   │   ├── SubscriptionView.vue # 订阅页面
│   │   ├── GalleryView.vue    # CG 画廊
│   │   ├── DailyView.vue      # 签到/任务
│   │   └── OnboardingView.vue # 新用户引导
│   ├── components/            # 通用组件
│   │   ├── DialogueBox.vue    # 对话框（流式文字）
│   │   ├── CharacterSprite.vue # 角色立绘（表情切换）
│   │   ├── SceneBackground.vue # 场景背景
│   │   ├── ChoicePanel.vue    # 选择面板
│   │   ├── AffectionBar.vue   # 好感度进度条
│   │   ├── AudioPlayer.vue    # BGM 播放器
│   │   ├── EndingCard.vue     # 结局卡片
│   │   └── StreakCalendar.vue # 签到日历
│   ├── composables/           # 组合式函数
│   │   ├── useSSE.ts          # SSE 流式连接
│   │   ├── useAudio.ts        # 音频控制
│   │   └── useTypewriter.ts   # 打字机效果
│   ├── api/                   # API 调用层
│   │   ├── client.ts          # Axios/fetch 封装
│   │   ├── auth.ts
│   │   ├── game.ts
│   │   └── ...
│   ├── assets/                # 静态资源引用
│   ├── styles/                # 全局样式 + 二次元主题
│   │   ├── theme.ts           # Naive UI 主题覆盖
│   │   └── global.css
│   ├── i18n/                  # 国际化（P1 英文翻译）
│   └── pwa/                   # PWA manifest + SW
├── public/
│   ├── manifest.json
│   └── favicon.ico
├── index.html
├── vite.config.ts
├── tsconfig.json
├── package.json
└── Dockerfile
```

### 关键前端交互

| 功能 | 组件 | API 调用 | 状态管理 |
|------|------|---------|---------|
| 剧本列表 | HomeView | GET /api/v1/scripts | script store |
| 游戏对话 | GameView + DialogueBox | SSE /api/v1/game/dialogue | game store |
| 选择操作 | ChoicePanel | POST /api/v1/game/choice | game store |
| 表情切换 | CharacterSprite | 解析 SSE 情绪标签 | game store |
| 背景切换 | SceneBackground | 解析节点 scene 字段 | game store |
| 好感度 | AffectionBar | GET /api/v1/affection/:charId | affection store |
| 签到 | StreakCalendar | GET/POST /api/v1/daily/checkin | daily store |
| 任务 | DailyView | GET /api/v1/daily/tasks | daily store |
| 商店 | ShopView | GET/POST /api/v1/payment/* | auth store |
| 订阅 | SubscriptionView | GET/POST /api/v1/subscription/* | auth store |

### SSE 流式对话协议

```typescript
// 前端连接
const eventSource = new EventSource('/api/v1/game/dialogue?session_id=xxx');

// 后端推送格式
event: message
data: {"type": "text", "content": "你好，我是...", "character_id": "char_a"}

event: message
data: {"type": "emotion", "emotion": "happy", "character_id": "char_a"}

event: message
data: {"type": "scene", "scene_id": "forest_01", "bgm": "battle_theme"}

event: message
data: {"type": "choice", "options": [{"id": "c1", "text": "...", "affection_delta": 3}]}

event: message
data: {"type": "affection_update", "character_id": "char_a", "value": 45, "level": "信赖"}

event: message
data: {"type": "memory_recall", "text": "我记得你说过喜欢向日葵..."}

event: done
data: {"session_id": "xxx", "node_id": "n015"}
```

## API Design

### 端点清单

| 方法 | 路径 | 鉴权 | 用途 |
| --- | --- | --- | --- |
| POST | /api/v1/auth/register | 无 | 邮箱注册 |
| POST | /api/v1/auth/login | 无 | 邮箱登录 |
| POST | /api/v1/auth/verify-email | 无 | 邮箱验证 |
| POST | /api/v1/auth/resend-verification | Bearer | 重发验证邮件 |
| POST | /api/v1/auth/forgot-password | 无 | 密码重置请求 |
| POST | /api/v1/auth/reset-password | 无 | 密码重置 |
| POST | /api/v1/auth/refresh | Bearer | Token 刷新 |
| GET | /api/v1/auth/oauth/:provider | 无 | OAuth mock 登录入口 |
| GET | /api/v1/auth/oauth/:provider/callback | 无 | OAuth mock 回调 |
| GET | /api/v1/scripts | Bearer | 剧本列表 |
| GET | /api/v1/scripts/:id | Bearer | 剧本详情（含路线） |
| GET | /api/v1/scripts/:id/routes/:routeId | Bearer | 路线详情（含节点图） |
| POST | /api/v1/game/start | Bearer | 开始游戏（创建会话） |
| GET | /api/v1/game/:sessionId | Bearer | 获取游戏会话状态 |
| GET | /api/v1/game/:sessionId/dialogue | Bearer | SSE 流式对话 |
| POST | /api/v1/game/:sessionId/choice | Bearer | 提交选择 |
| POST | /api/v1/game/:sessionId/free-chat | Bearer | 自由对话（P1） |
| GET | /api/v1/game/:sessionId/ending | Bearer | 获取结局 |
| POST | /api/v1/game/:sessionId/restart | Bearer | 重新开始路线 |
| GET | /api/v1/affection | Bearer | 全部角色好感度 |
| GET | /api/v1/affection/:characterId | Bearer | 单角色好感度详情 |
| GET | /api/v1/daily/checkin | Bearer | 查询今日签到状态 |
| POST | /api/v1/daily/checkin | Bearer | 执行签到 |
| GET | /api/v1/daily/tasks | Bearer | 今日任务列表 |
| POST | /api/v1/daily/tasks/:taskId/claim | Bearer | 领取任务奖励 |
| GET | /api/v1/shop | Bearer | 内购商品列表 |
| POST | /api/v1/shop/purchase | Bearer | mock 购买 |
| GET | /api/v1/shop/history | Bearer | 购买历史 |
| GET | /api/v1/subscription/plans | Bearer | 订阅方案列表 |
| POST | /api/v1/subscription/subscribe | Bearer | mock 订阅 |
| POST | /api/v1/subscription/cancel | Bearer | 取消订阅 |
| GET | /api/v1/subscription/status | Bearer | 当前订阅状态 |
| GET | /api/v1/gallery | Bearer | CG 画廊（P1） |
| GET | /api/v1/gallery/:cgId | Bearer | CG 详情 |
| POST | /api/v1/share/ending | Bearer | 生成结局分享卡片（P1） |
| GET | /api/v1/share/:shareId | 无 | 查看分享卡片 |
| GET | /api/v1/user/profile | Bearer | 用户信息 |
| PUT | /api/v1/user/profile | Bearer | 更新用户信息 |
| GET | /api/v1/user/preferences | Bearer | 用户偏好 |
| PUT | /api/v1/user/preferences | Bearer | 更新偏好 |
| GET | /api/v1/health | 无 | 健康检查 |

### 认证方案

- JWT Bearer Token（Access Token 15 分钟 + Refresh Token 7 天）
- OAuth mock：Google/Discord 按钮 → mock 回调 → 创建/关联账户 → 颁发 JWT
- `IOAuthProvider` 抽象接口，mock 实现和真实实现共用

### 错误码规范

| 错误码 | HTTP 状态 | 含义 |
| --- | --- | --- |
| AUTH_INVALID_CREDENTIALS | 401 | 邮箱或密码错误 |
| AUTH_EMAIL_NOT_VERIFIED | 403 | 邮箱未验证 |
| AUTH_TOKEN_EXPIRED | 401 | Token 过期 |
| AUTH_FORBIDDEN | 403 | 无权限 |
| SCRIPT_NOT_FOUND | 404 | 剧本不存在 |
| SCRIPT_LOCKED | 403 | 剧本未解锁（需购买） |
| GAME_SESSION_EXPIRED | 410 | 游戏会话已过期 |
| GAME_INVALID_CHOICE | 400 | 无效选择 |
| LLM_GENERATION_FAILED | 503 | AI 生成失败（已触发兜底） |
| LLM_RATE_LIMITED | 429 | LLM 调用频率限制 |
| PAYMENT_FAILED | 402 | mock 支付失败 |
| SUBSCRIPTION_ACTIVE | 409 | 已有活跃订阅 |
| DAILY_ALREADY_CHECKED_IN | 409 | 今日已签到 |
| VALIDATION_ERROR | 422 | 请求参数校验失败 |
| INTERNAL_ERROR | 500 | 内部错误 |

## Database Design

### 表清单

| 表名 | 用途 | 主键 | 关键索引 |
| --- | --- | --- | --- |
| `users` | 用户账户 | `id (UUID)` | `email (unique)`, `oauth_provider+oauth_id (unique)` |
| `email_verifications` | 邮箱验证令牌 | `id` | `user_id`, `token`, `expires_at` |
| `password_resets` | 密码重置令牌 | `id` | `user_id`, `token`, `expires_at` |
| `scripts` | 剧本元数据 | `id` | `slug (unique)` |
| `routes` | 路线 | `id` | `script_id` |
| `nodes` | 剧情节点 | `id` | `route_id`, `node_type`, `parent_id` |
| `node_choices` | 选择选项 | `id` | `node_id` |
| `characters` | 角色 | `id` | `script_id` |
| `character_sprites` | 角色表情立绘 | `id` | `character_id`, `emotion` |
| `scenes` | 场景 | `id` | `script_id` |
| `game_sessions` | 游戏会话 | `id (UUID)` | `user_id`, `route_id`, `status` |
| `game_progress` | 游戏进度（选择历史） | `id` | `session_id`, `node_id` |
| `affection` | 好感度 | `id` | `user_id+character_id (unique)` |
| `character_memories` | 角色记忆（pgvector） | `id` | `user_id+character_id`, `embedding (vector)` |
| `daily_checkins` | 签到记录 | `id` | `user_id+date (unique)` |
| `streak_records` | Streak 状态 | `id` | `user_id (unique)` |
| `daily_tasks` | 每日任务实例 | `id` | `user_id+date+task_type (unique)` |
| `fragments` | 碎片余额 | `id` | `user_id (unique)` |
| `fragment_transactions` | 碎片流水 | `id` | `user_id`, `created_at` |
| `purchases` | 内购交易 | `id` | `user_id`, `created_at` |
| `subscriptions` | 订阅记录 | `id` | `user_id`, `status` |
| `unlocked_scripts` | 已解锁剧本 | `id` | `user_id+script_id (unique)` |
| `unlocked_cgs` | 已解锁 CG | `id` | `user_id+cg_id (unique)` |
| `cg_assets` | CG 资源 | `id` | `script_id`, `route_id` |
| `share_cards` | 结局分享卡片 | `id (UUID)` | `user_id` |
| `user_preferences` | 用户偏好 | `id` | `user_id (unique)` |

### 关键表结构

#### users

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),  -- nullable for OAuth-only users
    display_name VARCHAR(100),
    avatar_url TEXT,
    email_verified BOOLEAN DEFAULT FALSE,
    oauth_provider VARCHAR(50),   -- 'google' | 'discord' | NULL
    oauth_id VARCHAR(255),
    subscription_tier VARCHAR(20) DEFAULT 'free',  -- free/basic/standard/premium
    trial_started_at TIMESTAMPTZ,
    trial_ends_at TIMESTAMPTZ,
    onboarding_completed BOOLEAN DEFAULT FALSE,
    preferred_genre VARCHAR(50),
    locale VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### character_memories (pgvector)

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE character_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    character_id UUID NOT NULL REFERENCES characters(id),
    memory_text TEXT NOT NULL,
    embedding vector(1536) NOT NULL,  -- text-embedding-3-small
    source_session_id UUID,
    confidence DECIMAL(3,2) DEFAULT 1.0,
    is_compressed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_memories_user_char ON character_memories(user_id, character_id);
CREATE INDEX idx_memories_embedding ON character_memories USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

#### game_sessions

```sql
CREATE TABLE game_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    script_id UUID NOT NULL REFERENCES scripts(id),
    route_id UUID NOT NULL REFERENCES routes(id),
    current_node_id UUID REFERENCES nodes(id),
    status VARCHAR(20) DEFAULT 'active',  -- active/completed/abandoned
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    ending_type VARCHAR(20),  -- good/normal/bad
    choice_history JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}'
);
```

#### affection

```sql
CREATE TABLE affection (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    character_id UUID NOT NULL REFERENCES characters(id),
    value INTEGER NOT NULL DEFAULT 0,  -- 0-100
    level VARCHAR(20) NOT NULL DEFAULT 'acquaintance',  -- acquaintance/ambiguous/trust/bond/love
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, character_id)
);
```

### 数据迁移策略

- 使用 Alembic 管理迁移
- MVP 为全新产品，无历史数据迁移风险（Q-010）
- 所有迁移脚本可重复执行（幂等）
- 种子数据：剧本 JSON → seed script 导入

## Security Design

### 认证与授权

| 场景 | 方案 |
|------|------|
| 用户认证 | JWT (Access 15min + Refresh 7d) |
| 密码存储 | bcrypt (cost factor 12) |
| OAuth mock | 抽象 IOAuthProvider 接口，mock 实现返回固定用户 |
| API 鉴权 | Bearer Token 中间件 |
| 限流 | Redis 滑动窗口：普通 API 60/min，LLM 调用 10/min |

### 敏感数据

| 数据 | 存储 | 传输 | 日志 |
|------|------|------|------|
| 密码 | bcrypt hash | HTTPS only | 不记录 |
| JWT | 内存/cookie | HTTPS only | 不记录 |
| 邮箱 | 明文（可查询） | HTTPS only | 脱敏 |
| 对话记录 | 明文存储 | HTTPS only | 脱敏 |
| 记忆向量 | 向量存储 | 内部调用 | 不记录 |
| mock 支付 | 明文标记 mock | HTTPS only | 记录 mock 标记 |

### 安全约束

- 所有 API 走 HTTPS（生产环境 Nginx SSL termination）
- CORS 白名单：仅允许前端 origin
- SQL 注入防护：SQLAlchemy ORM 参数化查询
- XSS 防护：Vue 默认转义 + CSP header
- CSRF：JWT 模式不需要 CSRF token（无 cookie 认证）
- 暴力破解：登录 5 次失败后锁定 15 分钟（Redis 计数器）

## Runtime Contract

### 端口和地址

| Key | Value |
|-----|-------|
| frontend_origin | `http://localhost:3000` (dev) / `https://isekai-wanderer.example.com` (prod) |
| backend_origin | `http://localhost:8000` (dev) / `https://isekai-wanderer.example.com:8000` (prod internal) |
| frontend_port | 3000 (Vite dev) / 80 (Nginx prod) |
| backend_port | 8000 (Uvicorn) |
| api_base_path | `/api/v1` |
| vite_proxy_target | `http://localhost:8000` |
| proxy_mode | Vite dev proxy / Nginx reverse proxy (prod) |
| health_endpoint | `/api/v1/health` |
| persistence_contract | PostgreSQL + pgvector + Redis |

### 交付命令

| Key | Value |
|-----|-------|
| delivery_e2e_command | `docker compose up -d && sleep 5 && curl http://localhost/api/v1/health` |
| browser_e2e_command | `APP_BASE=http://localhost:3000 npx playwright test tests/e2e/smoke.spec.ts` |
| browser_e2e_user_actions | 注册 → 登录 → 选择剧本 → 开始游戏 → 做出选择 → 查看好感度变化 → 签到 → 查看任务 |
| api_contract_doc | `docs/api/api.md` |
| database_contract_doc | `docs/database/database.md` |
| mock_policy | no mock API for Delivery E2E / Release evidence; mock only for payment/OAuth providers |

## P1 Module Design

### P1 模块最小可用标准（MAS）

| 模块 | MAS | 实现方案 |
|------|-----|---------|
| S008 情感节奏 | 关键节点情绪标注 + 基础节奏曲线 | 节点 JSON 增加 emotion_tag；前端解析后驱动 BGM/表情/背景联动 |
| S009 AI 风格化对话 | 3 种预设风格（温柔/傲娇/冷静） | 角色配置 dialogue_style 字段；LLM prompt 注入风格指令 |
| S010 社交分享 | 结局分享按钮（生成链接） | 后端生成 UUID 分享链接；不做社交平台 SDK 集成 |
| S011 UGC | 自定义角色名称 + 简单外观选择 | game_sessions 增加 custom_name；5 种预设头像 |
| S012 国际化 | 英文 UI 翻译 | vue-i18n；中英双语切换 |
| S013 CG 画廊 | 解锁 CG 列表展示 | cg_assets + unlocked_cgs 表；GalleryView grid 展示 |
| S014 SEO | 基础 meta 标签 + sitemap | @vueuse/head；静态 sitemap.xml |
| S015 Discord 集成 | 官方链接 + Bot 通知 | webhook 通知（新注册/结局） |
| 自由对话 | 预设话题选择（5 个） | POST /free-chat；LLM 角色约束生成 |
| 邮件召回 | 7 天未登录自动发邮件 | cron job + 模板邮件 |
| Push 通知 | PWA 通知权限提示 | Service Worker Notification API |
| 结局分享 | 结局卡片生成（图片+文字） | Canvas/sharp 生成 PNG 卡片 |

## Document Sync

| Target Doc | Status | Summary / Evidence |
|-----------|--------|-------------------|
| `docs/architecture/architecture.md` | Synced | 模块边界、依赖方向、核心流程已同步 |
| `docs/api/api.md` | Synced | 41 个端点、JWT 认证、错误码、SSE 协议、前端消费矩阵已同步 |
| `docs/database/database.md` | Synced | 24 张表、pgvector、Alembic 迁移、备份策略已同步 |
| `docs/security/security.md` | Synced | 认证授权、敏感数据分级、安全约束已同步 |
| `docs/decisions/decisions.md` | Synced | ADR-0001~0008 全部 Accepted 已同步 |
| `docs/runtime/runtime-contract.md` | Synced | 端口、代理、健康检查、E2E 命令、Mock 策略已同步 |

### P1 依赖关系

- S008 → 复用 S006 表情/背景/BGM 切换
- S009 → 复用 LLM Gateway prompt 注入
- S010 + 结局分享 → 复用 share_cards 表
- S013 → 复用 cg_assets + unlocked_cgs 表
- S011 → 复用 game_sessions metadata
- S014 → 纯前端
- S015 → 后端 webhook
- 邮件召回 → 后端 cron
- Push 通知 → 前端 Service Worker