# Architecture — Isekai Wanderer

## Overview

Isekai Wanderer uses a decoupled frontend/backend architecture. The frontend is a Vue 3 PWA (Vite dev / Nginx prod). The backend is a Python FastAPI microservice (Uvicorn). PostgreSQL with pgvector serves as the primary database and vector store. Redis handles caching and session state. A unified LLM Gateway supports multi-model switching.

### High-Level Topology

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

---

## Module List

| Module | Path | Responsibility | Tech Stack |
| --- | --- | --- | --- |
| `frontend/` | `/root/isekai-wanderer/frontend` | Vue 3 PWA user-facing client | Vue 3 + TS + Vite + Pinia + Naive UI |

**CR-028 additions:**
- `frontend/src/components/LockedCharacterOverlay.vue` — Locked character overlay with unlock price
- `frontend/src/components/UnlockPromptDialog.vue` — Unlock prompt dialog for paid characters
| `backend/` | `/root/isekai-wanderer/backend` | FastAPI backend service | Python 3.12 + FastAPI + SQLAlchemy + Alembic |
| `deploy/` | `/root/isekai-wanderer/deploy` | Docker Compose + Nginx | Docker + Nginx |
| `scripts/` | `/root/isekai-wanderer/scripts` | Build/test/deploy scripts | Shell + Python |
| `data/` | `/root/isekai-wanderer/data` | Script data (JSON) | JSON |
| `assets/` | `/root/isekai-wanderer/assets` | Art assets (images, audio) | Image/Audio |

**CR-002 additions:**
- `backend/app/services/free_chat_service.py` — Free chat business logic (AC-058)
- `backend/app/services/discord_service.py` — Mock Discord webhook (AC-055)
- `backend/app/services/recall_service.py` — Cron recall email job (AC-057)
- `backend/app/core/email.py` — MockEmailService (AC-047/AC-057)
- `frontend/src/i18n/` — vue-i18n integration (AC-052)
- `frontend/src/views/RouteMap.vue` — Route exploration view (AC-045)
- `frontend/src/views/FreeChatView.vue` — Free chat view (AC-058)
- `frontend/src/views/ForgotPasswordView.vue` — Password reset request (AC-047)
- `frontend/src/views/ResetPasswordView.vue` — Password reset execution (AC-047)
- `frontend/src/components/NotificationPrompt.vue` — PWA notification prompt (AC-056)
- `frontend/src/composables/useNotification.ts` — Notification API wrapper (AC-056)

### Module Responsibility Matrix

| Module | Responsible For | NOT Responsible For |
| --- | --- | --- |
| `frontend/` | User-facing pages, interactions, state, PWA manifest, Service Worker, i18n, SEO meta, route map, free chat UI, notification prompt | Business logic decisions, database access, direct LLM calls |
| `backend/` | API, narrative engine, memory system, affection calculation, daily/tasks, mock payment/subscription, LLM Gateway, rule engine, free chat service, discord service, recall service, mock email service | User interface, admin panel |
| `deploy/` | Container orchestration, Nginx config, env var injection | Business logic |
| `data/` | Script node JSON, character config, fallback dialogues | Runtime data |
| `assets/` | Character sprites, backgrounds, BGM, CG images | Dynamically generated assets |

---

## Dependency Direction

```txt
frontend ──(HTTP/SSE)──> backend ──> PostgreSQL/pgvector
                             ├──> Redis
                             └──> LLM API (external)
deploy depends on all module configs, but business code does NOT depend on deploy.
```

---

## Backend Layer Structure

```txt
backend/
├── app/
│   ├── main.py                 # FastAPI app entry
│   ├── config.py               # Environment variable config
│   ├── dependencies.py         # FastAPI dependency injection
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── script.py
│   │   ├── affection.py
│   │   ├── memory.py
│   │   ├── daily.py
│   │   └── payment.py
│   ├── schemas/                # Pydantic request/response models
│   │   ├── user.py
│   │   ├── script.py
│   │   ├── game.py
│   │   └── payment.py
│   ├── api/                    # Route layer
│   │   ├── v1/
│   │   │   ├── auth.py         # Register/login/OAuth mock
│   │   │   ├── scripts.py      # Script list/routes/nodes
│   │   │   ├── game.py         # Game session/dialogue/choices
│   │   │   ├── affection.py    # Affection query/update
│   │   │   ├── memory.py       # Memory storage/recall (internal)
│   │   │   ├── daily.py        # Check-in/tasks
│   │   │   ├── payment.py      # Mock IAP/subscription
│   │   │   ├── social.py       # Share/ending cards
│   │   │   └── health.py       # Health check
│   │   └── middleware.py       # CORS/logging/rate-limiting
│   ├── services/               # Business logic layer
│   │   ├── narrative_engine.py # Narrative engine core
│   │   ├── rule_engine.py      # Rule validation engine
│   │   ├── memory_service.py   # Memory store/recall
│   │   ├── affection_service.py
│   │   ├── script_service.py
│   │   ├── daily_service.py
│   │   ├── payment_service.py
│   │   ├── subscription_service.py
│   │   ├── free_chat_service.py  # CR-002: Free chat (AC-058)
│   │   ├── discord_service.py    # CR-002: Mock Discord (AC-055)
│   │   └── recall_service.py     # CR-002: Recall email cron (AC-057)
│   ├── llm/                    # LLM call layer
│   │   ├── gateway.py          # Unified LLM Gateway
│   │   ├── providers/          # Model providers
│   │   │   ├── openai_provider.py
│   │   │   ├── anthropic_provider.py
│   │   │   └── local_provider.py
│   │   ├── prompts/            # Prompt templates
│   │   │   ├── narrative.py
│   │   │   ├── memory_extract.py
│   │   │   └── style.py
│   │   └── fallback.py         # Fallback mechanism
│   └── core/                   # Infrastructure
│       ├── database.py         # DB session
│       ├── redis.py            # Redis client
│       ├── security.py         # JWT/password hashing
│       └── email.py            # Email sending (MockEmailService: CR-002 AC-047/057)
├── alembic/                    # Database migrations
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── pyproject.toml
└── Dockerfile
```

## Frontend Layer Structure

```txt
frontend/
├── src/
│   ├── App.vue
│   ├── main.ts
│   ├── router/
│   │   └── index.ts
│   ├── stores/                # Pinia stores
│   │   ├── auth.ts            # Auth state
│   │   ├── game.ts            # Game session state
│   │   ├── script.ts          # Script/route data
│   │   ├── affection.ts       # Affection state
│   │   ├── daily.ts           # Check-in/task state
│   │   └── ui.ts              # UI global state (volume/theme)
│   ├── views/                 # Page components
│   │   ├── HomeView.vue       # Home (script list)
│   │   ├── GameView.vue       # Game main view
│   │   ├── LoginView.vue      # Login/Register
│   │   ├── ProfileView.vue    # Profile center
│   │   ├── ShopView.vue       # IAP shop
│   │   ├── SubscriptionView.vue # Subscription page
│   │   ├── GalleryView.vue    # CG gallery
│   │   ├── DailyView.vue      # Check-in/tasks
│   │   ├── OnboardingView.vue # New user onboarding
│   │   ├── RouteMap.vue       # CR-002: Route exploration (AC-045)
│   │   ├── FreeChatView.vue   # CR-002: Free chat (AC-058)
│   │   ├── ForgotPasswordView.vue # CR-002: Password reset request (AC-047)
│   │   ├── ResetPasswordView.vue  # CR-002: Password reset execution (AC-047)
│   │   └── SettingsView.vue   # CR-002: Settings (i18n switch AC-052 + Discord link AC-055)
│   ├── components/            # Shared components
│   │   ├── DialogueBox.vue    # Dialogue box (streaming text)
│   │   ├── CharacterSprite.vue # Character sprite (emotion switching)
│   │   ├── SceneBackground.vue # Scene background
│   │   ├── ChoicePanel.vue    # Choice panel
│   │   ├── AffectionBar.vue   # Affection progress bar
│   │   ├── AudioPlayer.vue    # BGM player
│   │   ├── EndingCard.vue     # Ending card
│   │   └── StreakCalendar.vue # Check-in calendar
│   ├── composables/           # Composable functions
│   │   ├── useSSE.ts          # SSE streaming connection
│   │   ├── useAudio.ts        # Audio control
│   │   ├── useTypewriter.ts   # Typewriter effect (CR-002: +emotion speed AC-048)
│   │   └── useNotification.ts # CR-002: Notification API (AC-056)
│   ├── api/                   # API call layer
│   │   ├── client.ts          # Axios/fetch wrapper
│   │   ├── auth.ts
│   │   ├── game.ts
│   │   └── ...
│   ├── assets/                # Static asset references
│   ├── styles/                # Global styles + anime theme
│   │   ├── theme.ts           # Naive UI theme override
│   │   └── global.css
│   ├── i18n/                  # CR-002: vue-i18n (AC-052) zh.json + en.json + index.ts
│   └── pwa/                   # PWA manifest + SW (CR-002: +notification events AC-056)
├── public/
│   ├── manifest.json
│   └── favicon.ico
├── index.html
├── vite.config.ts
├── tsconfig.json
├── package.json
└── Dockerfile
```

---

## Core Flows

### Narrative Engine Flow

```txt
User choice/dialogue
      │
      ▼
┌─────────────────┐
│ ScriptService    │ ← Query current node, determine node type
│ (Script FSM)     │
└────┬────────────┘
     │
     ├── Preset node → Return preset content directly + trigger condition check
     │
     └── Transition node → Enter LLM generation flow
            │
            ▼
     ┌─────────────┐
     │ LLM Gateway  │ ← Character personality constraints + memory injection + emotion tagging
     │ (AI gen)     │
     └────┬────────┘
          │
          ▼
     ┌─────────────┐
     │ RuleEngine   │ ← Personality consistency + timeline + affection range
     │ (Validation) │
     └────┬────────┘
          │
          ├── Pass → SSE stream return to frontend
          │
          └── Blocked → Retry (max 2x) → Fallback dialogue
```

### Memory System Flow

```txt
Dialogue ends
    │
    ▼
┌──────────────────┐
│ MemoryExtractor   │ ← LLM extracts key information (async)
│ (Memory extract)  │
└────┬─────────────┘
     │ Memory found
     ▼
┌──────────────────┐
│ EmbeddingService  │ ← text-embedding-3-small
│ (Vectorize)       │
└────┬─────────────┘
     │
     ▼
┌──────────────────┐
│ pgvector INSERT   │ ← user_id + character_id + text + vector
└──────────────────┘

During dialogue generation
    │
    ▼
┌──────────────────┐
│ MemoryService     │ ← Current dialogue context embedding
│ .recall()         │
└────┬─────────────┘
     │
     ▼
┌──────────────────┐
│ pgvector KNN      │ ← WHERE similarity > 0.8 LIMIT 3
│ (Similarity       │
│  search)          │
└────┬─────────────┘
     │
     ▼
Inject into LLM prompt context
```

### Affection System Flow

The affection system tracks user-character relationships on a 0–100 scale with 5 levels: `acquaintance`, `ambiguous`, `trust`, `bond`, `love`. Affection changes are triggered by user choices and free-chat interactions. The `AffectionBar` component displays real-time progress, and the backend persists changes atomically via the `affection` table.

---

## P1 Module Minimal Available Standard (MAS)

| Module | MAS | Implementation |
|--------|-----|----------------|
| S008 Emotional Rhythm | Key node emotion tagging + basic rhythm curve | Node JSON adds emotion_tag; frontend parses to drive BGM/expression/BG sync |
| S009 AI Stylized Dialogue | 3 preset styles (gentle/tsundere/calm) | Character config dialogue_style field; LLM prompt style injection |
| S010 Social Sharing | Ending share button (generate link) | Backend generates UUID share link; no social SDK integration |
| S011 UGC | Custom character name + simple appearance selection | game_sessions adds custom_name; 5 preset avatars |
| S012 i18n | English UI translation | vue-i18n; Chinese-English bilingual toggle |
| S013 CG Gallery | Unlocked CG list display | cg_assets + unlocked_cgs tables; GalleryView grid display |
| S014 SEO | Basic meta tags + sitemap | @vueuse/head; static sitemap.xml |
| S015 Discord Integration | Official link + Bot notification | Webhook notification (new registration/ending) |
| Free Chat | Preset topic selection (5) | POST /free-chat; LLM character-constrained generation |
| Email Recall | 7-day inactivity auto-email | Cron job + template email |
| Push Notification | PWA notification permission prompt | Service Worker Notification API |
| Ending Share | Ending card generation (image + text) | Canvas/sharp PNG card generation |

### P1 Dependency Relationships

- S008 → Reuses S006 expression/background/BGM switching
- S009 → Reuses LLM Gateway prompt injection
- S010 + Ending Share → Reuses share_cards table
- S013 → Reuses cg_assets + unlocked_cgs tables
- S011 → Reuses game_sessions metadata
- S014 → Pure frontend
- S015 → Backend webhook
- Email Recall → Backend cron
- Push Notification → Frontend Service Worker

---

## CR-027 Additions: Layered Prompt Narrative Engine

### New Modules

| Module | Path | Responsibility | Tech Stack |
|--------|------|----------------|------------|
| LorebookService | `backend/app/services/lorebook_service.py` | World knowledge CRUD + tag-based matching | SQLAlchemy + PostgreSQL JSONB |
| SceneConfigService | `backend/app/services/scene_config_service.py` | Scene-to-node binding management | SQLAlchemy + PostgreSQL JSONB |
| PromptBuilder | `backend/app/services/prompt_builder.py` | Six-layer structured prompt assembly | Pure Python |
| TokenBudgetController | `backend/app/services/token_budget.py` | Per-layer token counting + truncation | tiktoken (cl100k_base) |

### Prompt Assembly Flow

```
┌─────────────────────────────────────────────────────────────┐
│ PromptBuilder.build(session_id, user_id, node, character)   │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
  │ L1: Global  │ │ L2: World   │ │ L3: NPC     │
  │ Rules       │ │ Knowledge   │ │ Profile     │
  │ (200 tok)   │ │ (500 tok)   │ │ (300 tok)   │
  └─────────────┘ └──────┬──────┘ └─────────────┘
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
       ┌───────────┐ ┌────────┐ ┌──────────┐
       │SceneConfig│→│Lorebook│→│Token     │
       │Service    │ │Service │ │Budget    │
       │(tags)     │ │(match) │ │Controller│
       └───────────┘ └────────┘ └──────────┘
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
       ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
       │ L4: Memory  │ │ L5: Narr.   │ │ L6: User    │
       │ (800 tok)   │ │ Director    │ │ Input       │
       │             │ │ (300 tok)   │ │ (200 tok)   │
       └─────────────┘ └─────────────┘ └─────────────┘
              │               │               │
              ▼               ▼               ▼
       ┌─────────────────────────────────────────────┐
       │ system_prompt (L1-L5) + user_prompt (L6)    │
       │ Total budget: ≤ 2300 tokens                 │
       └─────────────────────────────────────────────┘
```

### Degradation Strategy

| Failure | Handling | Log Level |
|---------|----------|----------|
| LorebookService exception | L2 uses empty string, other layers normal | warning |
| MemoryService exception | L4 uses empty string, other layers normal | warning |
| SceneConfigService exception | L2 scene part empty, Lorebook match skipped | warning |
| PromptBuilder overall exception | NarrativeEngine falls back to simple prompt | error |

### Dependency Direction (CR-027)

```
NarrativeEngine
  └── PromptBuilder
        ├── LorebookService ──→ lorebook_entries (DB)
        ├── SceneConfigService ──→ scene_configs (DB)
        ├── MemoryService ──→ character_memories (DB/pgvector)
        ├── TokenBudgetController (tiktoken)
        └── Character model ──→ characters (DB, extended)
```

### CR-028 Additions: Character Playable / Multi-Route

#### New Module Dependencies

```
NarrativeEngine
  └── PromptBuilder
        └── [NEW] L3 Player Identity ──→ game_sessions.character_id + characters.play_description

ScriptService ──→ characters (playable, playable_route_id, unlock_type)
                ──→ user_character_unlocks (is_unlocked calculation)

GameService ──→ characters (playable validation, playable_route_id)
              ──→ game_sessions (character_id, character_name)

SavesService ──→ game_sessions (character_name)
               ──→ characters (character lookup)

CharacterService ──→ characters (unlock_type validation)
                   ──→ user_character_unlocks (unlock record)
```

### CR-029 Additions: Node Branch Character Filtering

#### New Module Dependencies

```
ScriptService
  └── get_node_with_choices() ──→ nodes.character_id (filter by session.character_id)
  └── submit_choice() ──→ nodes.character_id (validate visibility, 403 on mismatch)

NarrativeEngine
  └── [no new dependencies] — filtering happens in ScriptService layer
```

#### Node Visibility Flow

```
GET /game/{sessionId}/dialogue
  └── NarrativeEngine.generate_dialogue()
        └── ScriptService.get_game_session_state()
              └── ScriptService.get_node_with_choices(node_id, session_character_id)
                    └── WHERE character_id IS NULL OR character_id = session_character_id

POST /game/{sessionId}/choice
  └── ScriptService.submit_choice()
        └── ScriptService.get_next_node(choice_id)
              └── Validate: next_node.character_id matches session.character_id
              └── 403 NARRATIVE_NODE_NOT_VISIBLE on mismatch
```

#### PromptBuilder Layer Update

No changes to PromptBuilder. Node filtering is transparent to prompt assembly.

### Admin Frontend Pages (CR-027)

| Route | Component | Purpose |
|-------|-----------|--------|
| /lorebook | LorebookManage.vue | World knowledge CRUD + tag filter |
| /scene-configs | SceneConfig.vue | Script→Route→Node tree + scene editing |
| /characters/:id | CharacterEdit.vue (extended) | NPC desire/fear/secret editing |

### CR-030 Additions: Chapter Structure Refactor

#### New Module Dependencies

```
ScriptService
  └── get_chapters() ──→ routes.chapter_number, routes.chapter_type (group by chapter)

GameService
  └── get_session_status() ──→ routes.chapter_number, routes.chapter_type (via session.route_id)
  └── get_dialogue() ──→ routes.chapter_number, routes.chapter_type (via current_node.route_id)

Frontend
  └── ChapterProgress.vue ──→ GET /game/{session_id}/status (chapter_number, chapter_title)
```

#### Chapter Information Flow

```
GET /game/{sessionId}/status
  └── GameService.get_session_status()
        └── Query route via session.route_id
              └── Read route.chapter_number, route.chapter_type
              └── Map chapter_type → chapter_title (encounter→相遇, daily→日常, conflict→冲突, convergence→收束)
              └── Return chapter_number, chapter_type, chapter_title (null if route has no chapter info)

GET /scripts/{scriptId}/chapters
  └── ScriptService.get_chapters(script_id)
        └── Query routes WHERE script_id = ? AND chapter_number IS NOT NULL
        └── Group by chapter_number, order ascending
        └── Return chapters array with routes per chapter
```

#### Backward Compatibility

- Old sessions (route without chapter info) return `chapter_number: null, chapter_type: null, chapter_title: null`
- Frontend detects null → fallback to display route.title (existing behavior)
- Existing `chapter` (route.title) and `chapter_id` (route.id) fields preserved for transition period

### CR-037 Additions: Corvus-Story-Core 集成

#### New Modules

| Module | Path | Responsibility |
|--------|------|----------------|
| CorvusClient | `backend/app/services/corvus_client.py` | Corvus HTTP + SSE 客户端，仅访问 127.0.0.1:8082 |
| CorvusAdapter | `backend/app/services/corvus_adapter.py` | SSE 翻译 + world_state DB 同步 + 向量记忆写入/召回 + NPC knownInfo 注入/恢复 |
| EmbeddingService | `backend/app/services/embedding_service.py` | bge-small-zh-v1.5 本地 embedding 推理 (512 维) + pgvector KNN 召回 |
| CorvusModels | `backend/app/models/corvus.py` | 5 张新表 SQLAlchemy 模型 |

#### Engine Dispatcher (Feature Flag)

```
Engine Dispatcher (backend/app/api/v1/game.py)
  ├── engine_type='legacy' → NarrativeEngine (现有路径不变)
  └── engine_type='corvus'  → CorvusAdapter (新路径)
```

#### Data Flow: Corvus 游戏回合

```
用户输入 → CorvusAdapter.stream_turn()
  1. recall_and_inject(): pgvector KNN 召回 Top-5 → NPC knownInfo 注入 (PATCH Corvus)
  2. CorvusClient.stream_message(): POST Corvus /api/games/{gameId}/messages → SSE 事件流
  3. SSETranslator: Corvus SSE 事件 → 前端格式 (text/done/gm_update/stream_end/error)
  4. 异步副作用:
     - assistant-complete → write_memory (LLM 提取 → bge embedding → pgvector 存储)
     - gm_update → sync_world_state (session_npcs / inventory_items / story_flags)
     - done/error → restore_npc_knowninfo (恢复 NPC knownInfo 原始值)
```

#### Corvus Service Topology

```
┌──────────────────────┐  SSE 透传 (127.0.0.1:8082)  ┌──────────────────────┐
│ isekai 后端 (Python)  │ ←────────────────────────→ │ Corvus (Node.js)     │
│ FastAPI :8000         │                             │ Express :8082        │
│ + pgvector 512维      │                             │ + LLM → thoushub     │
│ + 5 张新表            │                             │ + 文件存储 JSON/JSONL │
└──────────────────────┘                             └──────────────────────┘
```

### CR-038 Additions: Corvus Frontend Entry

#### New Frontend Modules

| Module | Path | Responsibility |
|--------|------|----------------|
| PlayerCandidateModal | `frontend/src/components/PlayerCandidateModal.vue` | 角色候选管理 UI：查看列表、创建新候选（name 必填校验）、≤3 限制、选择候选进入游戏 |
| startGame Corvus 分支 | `frontend/src/stores/game.ts` (改造) | Corvus 剧本走 POST /game/session/create → 选角 Modal → POST /game/session/select-player 流程 |
| SSE gm_update UI | `frontend/src/stores/game.ts` + `frontend/src/components/StoryPanel.vue` (改造) | SSE gm_update 事件处理：好感度/道具/标记 UI 更新 |
| resumeSession engine_type | `frontend/src/stores/game.ts` (改造) | 恢复会话时写入 engine_type；旧数据兼容处理（无 engine_type 视为 'legacy'） |

#### Engine Dispatcher (Frontend)

```
Frontend startGame() Dispatcher (stores/game.ts)
  ├── engine_type='corvus' → POST /game/session/create → 选角 → POST /game/session/select-player → SSE 对话
  └── engine_type='legacy' → POST /game/start → 节点式对话 (保留不激活)

Frontend submitChoice/submitCustomInput Dispatcher (stores/game.ts)
  ├── engine_type='corvus' → SSE 流式分支 (text/done/gm_update/error)
  └── engine_type='legacy' → POST /game/choice 或 POST /game/custom-input (保留不激活)
```

#### Legacy 代码保留策略

CR-038 采用**条件分支保留**策略：
- `submitChoice()` 和 `submitCustomInput()` 中的 `if (isCorvus) { SSE 分支 } else { legacy 分支 }` 原样保留
- Legacy 分支代码不被删除、不被注释、不被标记
- C3 约束下所有剧本 `engine_type = 'corvus'`，legacy 分支自然不被执行
- 未来如需恢复 legacy 引擎，只需将 `engine_type` 改回 `'legacy'`

#### Data Flow: Corvus 前端全链路

```
用户选择剧本 → startGame()
  1. loadScripts(): GET /api/v1/scripts → 解析 engine_type='corvus'
  2. startGame(scriptId): POST /api/v1/game/session/create → 返回 game_session_id
  3. 选角 Modal 弹出: GET /api/v1/game/player/candidates → 展示候选列表
  4. 用户选择/创建角色 → POST /api/v1/game/session/select-player
  5. 页面进入游戏对话界面 → SSE 流式对话
  6. 用户输入文字 → submitCustomInput() → Corvus SSE 分支
  7. SSE 事件: text(逐字渲染) → gm_update(好感度/道具) → done(结束) → stream_end(关闭连接)
  8. resumeSession(): 恢复会话 → 写入 engine_type → 走对应分支
```

---

## CR-042 Additions: Legacy SSE 流式改造

### Legacy SSE 架构

CR-042 将 Legacy 引擎的三条非流式路径改为 SSE 流式输出，复用 Corvus SSE 基础设施。

#### 新增端点层 SSE 组装函数

| 函数 | 位置 | 用途 |
|------|------|------|
| `_stream_legacy_turn()` | `game.py` | Legacy `submit_choice` 推进到 transition/ai_dialog 节点时返回 SSE 流式输出 |
| `_stream_legacy_custom_input()` | `game.py` | Legacy `submit_custom_input` 改为 SSE 流式输出 |
| `_run_legacy_deferred()` | `game.py` | Legacy SSE 流后异步 DB 写入（对话历史、好感度、成就、收敛检查） |
| `_run_legacy_custom_input_deferred()` | `game.py` | Legacy custom_input SSE 流后异步 DB 写入 |

#### 设计决策：端点层组装（ADR-042-01）

SSE 流式逻辑在 `game.py` 端点层组装，不修改 `narrative_engine` 内部方法。与 Corvus 路径的 `_stream_corvus_turn()` 保持架构一致。

#### Legacy submit_choice 条件 SSE 分支

```
submit_choice()
  ├── Corvus 分支 → _stream_corvus_turn() (不变)
  └── Legacy 分支
       1. process_choice() 推进节点、扣 quota、存对话历史
       2. 检查 next_node.node_type:
          ├── preset/choice → 保持 JSON 响应 (AC-002)
          └── transition/ai_dialog → _stream_legacy_turn() 返回 SSE (AC-001)
```

#### Legacy submit_custom_input SSE 分支

```
submit_custom_input()
  ├── Corvus 分支 → _stream_corvus_turn() (不变)
  └── Legacy 分支 → _stream_legacy_custom_input() 返回 SSE (使用 llm_gateway.stream_dialogue())
```

#### model_router stream_with_fallback() 降级策略

```
stream_with_fallback(scenario, messages, **kwargs) → AsyncGenerator[str, None]
  1. 主模型 stream_complete() → 逐 token yield
  2. 主模型失败 → 切换 fallback 链下一个模型
  3. 所有模型失败 → 一次性 yield 场景特定友好提示文本
```

#### 前端 useSSEStream() composable 复用模式

```
useSSEStream(options, callbacks) → { start, abort, isStreaming }
  ├── submitChoice() Legacy 分支 → 检测 Content-Type: text/event-stream → useSSEStream
  ├── submitChoice() Corvus 分支 → useSSEStream (with onGmUpdate callback)
  ├── submitCustomInput() Legacy 分支 → useSSEStream
  ├── submitCustomInput() Corvus 分支 → useSSEStream (with onGmUpdate callback)
  └── FreeChatView.vue → useSSEStream (/free-chat/stream 端点)
```

#### Legacy done 事件一次性推送元数据（ADR-042-02）

Legacy 路径不使用 `gm_update` 事件。所有元数据（好感度变化、下一节点选项）通过 `done` 事件一次性推送。前端在 `onDone` callback 中直接更新 `currentSession.current_node_id` 和 `pendingChoices`，不需要 `fetchDialogue()` 二次请求。

---

## CR-043 Additions: 订阅权益区分与 CG 画廊权限控制

### 权限检查模块依赖

CR-043 在现有 API 端点层增加订阅权益强制检查逻辑，不新增模块或服务。

```
GalleryAPI (gallery.py)
  └── SubscriptionService.get_user_tier() → 计算 is_accessible

GameAPI (game.py)
  └── SubscriptionService.get_user_tier() → 检查 script_access
  └── _compute_script_accessible(tier, script) → 运行时判定

ScriptsAPI (scripts.py)
  └── SubscriptionService.get_user_tier() → 计算 is_accessible
  └── _compute_script_accessible(tier, script) → 运行时判定

SettingsAPI (settings.py)
  └── SubscriptionService.get_user_tier() → 统一 tier 数据源
  └── SubscriptionService.get_user_subscription() → status/expires_at
```

### 权限检查设计

- 权限检查放在 API 端点层（ADR-043-01），不新增中间件
- `is_accessible` 字段由后端基于 `SubscriptionService.get_user_tier()` 计算，前端不可篡改
- `script_access` 三档映射采用运行时虚拟判定（ADR-043-02），不修改数据库表结构
- 403 权限拒绝记录审计日志（user_id, script_id, tier, timestamp）
- 前端以后端 API 返回的 `is_accessible` 为权威值，不硬编码 tier→permissions 映射
