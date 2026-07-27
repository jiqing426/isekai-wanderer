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
