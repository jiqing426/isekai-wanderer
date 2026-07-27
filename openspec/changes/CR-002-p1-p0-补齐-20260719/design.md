# Design — CR-002 P1-P0 补齐

## Overview

- CR-002 Phase 1 补齐 9 项 P1 功能（AC-045, AC-047, AC-048, AC-052, AC-054, AC-055, AC-056, AC-057, AC-058）
- 架构沿用 CR-001 FastAPI + Vue 3 + PostgreSQL + Redis 栈，增量开发
- 不引入新基础设施、不引入新 ADR
- 邮件（MockEmailService）、Discord（MockDiscordService）、LLM（MockProvider）全部 mock 实现
- Phase 1 完成后才进入 Phase 2（P0 测试补齐）
- 排除 AC-022（邮箱验证）

## Technical Approach

- 沿用 CR-001 已接受的架构（FastAPI + Vue 3 + PostgreSQL + pgvector + Redis），增量开发 9 项 P1 功能
- 不引入新基础设施、不引入新 ADR
- 全部外部依赖（邮件、Discord、LLM）使用 mock 实现
- 新增 4 个 API endpoint（route-map, forgot-password, reset-password, free-chat）
- 新增 4 个数据库表（password_resets, discord_configs, recall_emails, free_chat_sessions）
- 新增 5 个 FE View（RouteMap, FreeChat, ForgotPassword, ResetPassword, NotificationPrompt）
- 新增 2 个 composable（useNotification）和常量表（emotions.ts）
- 引入 vue-i18n@9 和 @vueuse/head 两个前端库（无需独立 ADR，Vue 3 生态标准选择）

## Technology Decisions

CR-002 无新技术选型决策。全部沿用 CR-001 已接受的 ADR：

| Decision | Selected | Status | Evidence |
| --- | --- | --- | --- |
| 后端框架 | Python FastAPI | Accepted | ADR-0001 (CR-001) |
| 向量数据库 | PostgreSQL + pgvector | Accepted | ADR-0002 (CR-001) |
| 剧本数据格式 | JSON | Accepted | ADR-0003 (CR-001) |
| 认证方式 | JWT | Accepted | ADR-0004 (CR-001) |
| 实时协议 | SSE | Accepted | ADR-0005 (CR-001) |
| 前端 UI 框架 | Naive UI | Accepted | ADR-0006 (CR-001) |
| 缓存层 | Redis | Accepted | ADR-0007 (CR-001) |
| LLM 调用 | GPT-4o-mini + Unified Gateway | Accepted | ADR-0008 (CR-001) |
| i18n 库 | vue-i18n@9 | Not Required | 沿用 Vue 3 生态标准选择，无需独立 ADR |
| SEO 库 | @vueuse/head | Not Required | 沿用 Vue 3 生态标准选择，无需独立 ADR |

## Change Scope

| AC | 功能 | 模块影响 | 新 API | 新表 | 新 FE 页面/组件 |
|---|---|---|---|---|---|
| AC-045 | 路线图探索 | BE + FE | GET /game/{id}/route-map | — | RouteMap.vue |
| AC-047 | 密码重置 | BE + FE | POST /auth/forgot-password, POST /auth/reset-password | password_resets | ForgotPasswordView.vue, ResetPasswordView.vue |
| AC-048 | 情绪节奏 | FE | — | — | TypewriterSpeed + BGMVolume 增强 |
| AC-052 | 国际化 i18n | FE | — | — | vue-i18n 集成, SettingsView 增强 |
| AC-054 | SEO | FE | — | — | @vueuse/head meta, sitemap.xml, robots.txt |
| AC-055 | Discord 集成 | BE | — | discord_configs | SettingsView Discord 链接 |
| AC-057 | 召回邮件 | BE | — | recall_emails | — |
| AC-056 | PWA 通知 | FE | — | — | Service Worker, NotificationPrompt.vue |
| AC-058 | 自由对话 | BE + FE | POST /game/{sessionId}/free-chat | free_chat_sessions | FreeChatView.vue |

---

## D-001: 路线图探索 (AC-045)

### 设计思路

复用已有 `game_sessions` + `game_progress` 数据，聚合查询用户在某 script 下所有 route 的完成状态。前端在剧本详情页新增"路线探索"入口，展示树状路线图。

### BE: GET /api/v1/game/{scriptId}/route-map

**Request**:
```
GET /api/v1/game/{scriptId}/route-map
Authorization: Bearer <token>
```

**Response** (200):
```json
{
  "script_id": "uuid",
  "routes": [
    {
      "route_id": "uuid",
      "route_name": "Route A",
      "status": "completed",
      "ending_type": "good",
      "nodes_explored": 12,
      "nodes_total": 15,
      "completed_at": "2026-07-20T10:00:00Z"
    },
    {
      "route_id": "uuid",
      "route_name": "Route B",
      "status": "partial",
      "ending_type": null,
      "nodes_explored": 5,
      "nodes_total": 18,
      "completed_at": null
    }
  ]
}
```

**Error Codes**:
| Code | HTTP | Condition |
|---|---|---|
| SCRIPT_NOT_FOUND | 404 | script_id 不存在 |
| AUTH_TOKEN_EXPIRED | 401 | Token 过期 |

**实现层**:
- Route: `backend/app/api/v1/game.py` 新增 `get_route_map` endpoint
- Service: `backend/app/services/script_service.py` 新增 `get_route_map(user_id, script_id)` 方法
- Query: 聚合 `game_sessions` JOIN `game_progress` GROUP BY `route_id`

### FE: RouteMap.vue

- 位置: `frontend/src/views/RouteMap.vue`
- 路由: `/scripts/:scriptId/route-map`
- 入口: `ScriptDetailView.vue` 新增"路线探索"按钮
- 展示:
  - 已完成路线: 高亮色 + 结局类型标签 (good/normal/bad)
  - 部分探索: 进度条 + 百分比
  - 未探索: 灰色 + "完成剧本后解锁" 提示
- 数据来源: 调用 `api/game.ts` 新增 `getRouteMap(scriptId)` 方法
- 状态管理: 复用 `script` store

---

## D-002: 密码重置 (AC-047)

### 设计思路

复用现有 `auth` 模块，新增密码重置令牌流程。`password_resets` 表已在 CR-001 schema 中定义但未实现。MockEmailService 发送重置链接到控制台。

### DB: password_resets 表

```sql
CREATE TABLE password_resets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_password_resets_token ON password_resets(token);
CREATE INDEX idx_password_resets_user_id ON password_resets(user_id);
```

- Token 生成: `secrets.token_urlsafe(32)`
- 有效期: 1 小时
- 单次使用: `used = TRUE` 后不可再用

### BE: POST /api/v1/auth/forgot-password

**Request**:
```json
{
  "email": "user@example.com"
}
```

**Response** (200):
```json
{
  "message": "If the email exists, a reset link has been sent.",
  "reset_token": "mock-only-xxxxx"
}
```

- 邮箱不存在时返回相同的 200 响应（防枚举）
- MockEmailService 打印重置链接到控制台/日志
- Rate limit: 3 次/小时/邮箱 (Redis counter)

**实现层**:
- Route: `backend/app/api/v1/auth.py` 新增 `forgot_password` endpoint
- Service: `backend/app/services/auth_service.py` 新增 `request_password_reset(email)`
- Email: `backend/app/core/email.py` MockEmailService 新增 `send_password_reset(email, token)`

### BE: POST /api/v1/auth/reset-password

**Request**:
```json
{
  "token": "reset-token-xxx",
  "new_password": "NewSecurePass123"
}
```

**Response** (200):
```json
{
  "message": "Password has been reset successfully."
}
```

**Error Codes**:
| Code | HTTP | Condition |
|---|---|---|
| AUTH_RESET_TOKEN_INVALID | 400 | Token 不存在或已使用 |
| AUTH_RESET_TOKEN_EXPIRED | 400 | Token 已过期 |
| VALIDATION_ERROR | 422 | 密码强度不满足 |

**实现层**:
- Route: `backend/app/api/v1/auth.py` 新增 `reset_password` endpoint
- Service: `backend/app/services/auth_service.py` 新增 `reset_password(token, new_password)`
- Password: bcrypt hash (cost 12)，复用 `core/security.py`

### FE: ForgotPasswordView.vue + ResetPasswordView.vue

- `frontend/src/views/ForgotPasswordView.vue`:
  - 路由: `/forgot-password`
  - 入口: LoginView 新增"忘记密码？"链接
  - 表单: email 输入 + 提交按钮
  - 提交后展示"如果邮箱存在，重置链接已发送"
- `frontend/src/views/ResetPasswordView.vue`:
  - 路由: `/reset-password?token=xxx`
  - 表单: 新密码 + 确认密码 + 提交按钮
  - 成功后跳转登录页

### MockEmailService

```python
class MockEmailService:
    """Shared between AC-047 and AC-057."""
    async def send_password_reset(self, email: str, token: str) -> None:
        logger.info(f"[MockEmail] Password reset for {email}: token={token}")
    
    async def send_recall_email(self, email: str, game_link: str, summary: str) -> None:
        logger.info(f"[MockEmail] Recall email for {email}: link={game_link}")
```

- 位置: `backend/app/core/email.py`
- 日志输出到 `logs/mock-email.log`
- 后续 CR-003 可替换为真实 SMTP/Resend 实现

---

## D-003: 情绪节奏 (AC-048)

### 设计思路

纯 FE 增强。SSE 流已有 `emotion` 事件类型，前端在 `useTypewriter` composable 和 `AudioPlayer` 组件中增加情绪映射表，根据 emotion tag 动态调整打字速度和 BGM 音量。

### 情绪映射表

| Emotion Tag | Typewriter Speed Multiplier | BGM Volume Multiplier |
|---|---|---|
| `normal` | 1.0x | 1.0x |
| `tense` | 2.0x | 1.2x |
| `warm` | 0.7x | 0.8x |
| `sad` | 0.5x | 0.6x |
| `excited` | 1.8x | 1.1x |
| `angry` | 1.5x | 1.3x |

### FE 改动

- `frontend/src/composables/useTypewriter.ts`:
  - 新增 `setEmotionMultiplier(emotion: string)` 方法
  - 内部 `charsPerFrame` 乘以 `emotionMultiplier`
  - 监听 SSE `emotion` 事件自动调用
- `frontend/src/components/AudioPlayer.vue`:
  - 新增 `emotionVolumeMultiplier` prop 或 composable
  - `effectiveVolume = baseVolume * emotionVolumeMultiplier`
  - 使用 CSS transition `volume 0.5s ease` 平滑过渡
- `frontend/src/views/GameView.vue`:
  - 在 SSE `emotion` 事件回调中同时调用 `typewriter.setEmotionMultiplier()` 和 `audioPlayer.setEmotionMultiplier()`

### 无需 BE 改动

情绪标签已在 CR-001 的 node JSON 和 SSE `emotion` 事件中定义。本 AC 仅前端消费。

---

## D-004: 国际化 i18n (AC-052)

### 设计思路

引入 vue-i18n，将 UI 文本抽取到 `zh.json` 和 `en.json`。语言偏好存储在 `user_preferences.locale` 字段（已有）和 `localStorage`。SettingsView 增加语言切换控件。

### FE: vue-i18n 集成

**安装**: `npm install vue-i18n@9`

**初始化** (`frontend/src/i18n/index.ts`):
```typescript
import { createI18n } from 'vue-i18n';
import zh from './zh.json';
import en from './en.json';

export const i18n = createI18n({
  legacy: false,
  locale: localStorage.getItem('locale') || 'zh',
  fallbackLocale: 'zh',
  messages: { zh, en }
});
```

**翻译文件结构** (`frontend/src/i18n/zh.json`):
```json
{
  "nav": { "home": "首页", "profile": "个人中心", "settings": "设置" },
  "auth": { "login": "登录", "register": "注册", "forgotPassword": "忘记密码" },
  "game": { "start": "开始游戏", "routeMap": "路线探索", "freeChat": "自由对话" },
  "common": { "save": "保存", "cancel": "取消", "confirm": "确认" }
}
```

**翻译文件结构** (`frontend/src/i18n/en.json`):
```json
{
  "nav": { "home": "Home", "profile": "Profile", "settings": "Settings" },
  "auth": { "login": "Login", "register": "Register", "forgotPassword": "Forgot Password" },
  "game": { "start": "Start Game", "routeMap": "Route Map", "freeChat": "Free Chat" },
  "common": { "save": "Save", "cancel": "Cancel", "confirm": "Confirm" }
}
```

**SettingsView 增强**:
- 位置: `frontend/src/views/SettingsView.vue` (新建或增强现有)
- 语言切换: `NSelect` 组件，选项 `[{label: '中文', value: 'zh'}, {label: 'English', value: 'en'}]`
- 切换时: `i18n.global.locale.value = newLocale` + `localStorage.setItem('locale', newLocale)` + `PUT /api/v1/user/preferences { locale: newLocale }`

### 改动范围

- 所有 View 和 Component 中的硬编码中文替换为 `$t('key')` 或 `useI18n().t('key')`
- `main.ts` 注册 i18n 插件
- `router/index.ts` 中的页面 title 使用 i18n

---

## D-005: SEO 基础配置 (AC-054)

### 设计思路

使用 `@vueuse/head` 管理 meta 标签。每个 View 组件通过 `useHead()` 设置页面级 meta。静态文件 `sitemap.xml` 和 `robots.txt` 放在 `public/` 目录。

### FE: @vueuse/head

**安装**: `npm install @vueuse/head`

**初始化** (`frontend/src/main.ts`):
```typescript
import { createHead } from '@vueuse/head';
const head = createHead();
app.use(head);
```

**各页面 meta**:
- `HomeView.vue`:
  ```typescript
  useHead({
    title: 'Isekai Wanderer - 异世界漫游者',
    meta: [
      { name: 'description', content: '沉浸式 AI 驱动的异世界冒险叙事游戏' },
      { property: 'og:title', content: 'Isekai Wanderer' },
      { property: 'og:description', content: '沉浸式 AI 驱动的异世界冒险叙事游戏' },
      { property: 'og:image', content: '/og-image.png' }
    ]
  });
  ```
- `ScriptDetailView.vue` (动态 meta):
  ```typescript
  useHead({
    title: computed(() => `${script.value?.name} - Isekai Wanderer`),
    meta: computed(() => [
      { name: 'description', content: script.value?.description },
      { property: 'og:title', content: script.value?.name }
    ])
  });
  ```

### 静态文件

- `frontend/public/sitemap.xml`: 包含首页和各剧本 URL
- `frontend/public/robots.txt`: `User-agent: *`, `Allow: /`, `Sitemap: https://isekai-wanderer.example.com/sitemap.xml`

### Vite 构建

- `index.html` 添加默认 meta fallback
- sitemap.xml 由构建脚本从 API 数据生成（开发阶段手写静态版）

---

## D-006: Discord 集成 (AC-055)

### 设计思路

后端新增 `DiscordService`（mock webhook），在结局解锁事件时发送通知。前端 SettingsView 展示 Discord 邀请链接。

### DB: discord_configs 表

```sql
CREATE TABLE discord_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    webhook_url VARCHAR(500) NOT NULL,
    channel_name VARCHAR(100),
    enabled BOOLEAN DEFAULT TRUE,
    events JSONB DEFAULT '["ending_unlocked"]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### BE: DiscordService

```python
class DiscordService:
    """Mock Discord webhook integration."""
    
    async def send_notification(self, event_type: str, payload: dict) -> None:
        """Send mock webhook notification."""
        config = await self._get_config(event_type)
        if not config or not config.enabled:
            return
        # Mock: log instead of actual HTTP POST
        logger.info(
            f"[MockDiscord] Event: {event_type}, "
            f"Webhook: {config.webhook_url}, "
            f"Payload: {json.dumps(payload)}"
        )
```

- 位置: `backend/app/services/discord_service.py`
- 触发: 在 `game_service.py` 结局解锁时调用 `discord_service.send_notification('ending_unlocked', {...})`
- Mock webhook 日志输出到 `logs/mock-discord.log`

### FE: SettingsView Discord 链接

- 位置: `frontend/src/views/SettingsView.vue` 新增 Discord 区块
- 展示: Discord logo + "加入官方 Discord" 链接
- 链接: 硬编码 `https://discord.gg/isekai-wanderer` (mock)

---

## D-007: PWA 通知 (AC-056)

### 设计思路

纯 FE 实现。增强现有 Service Worker 注册逻辑，首次进入游戏时请求 Notification API 权限。授权后可通过 Service Worker 发送本地通知。

### FE: Service Worker 增强

**通知权限请求** (`frontend/src/composables/useNotification.ts`):
```typescript
export function useNotification() {
  const permission = ref(Notification.permission);
  
  async function requestPermission() {
    if (permission.value === 'default') {
      const result = await Notification.requestPermission();
      permission.value = result;
    }
    return permission.value;
  }
  
  function sendNotification(title: string, options?: NotificationOptions) {
    if (permission.value === 'granted') {
      new Notification(title, options);
    }
  }
  
  return { permission, requestPermission, sendNotification };
}
```

**NotificationPrompt.vue** (`frontend/src/components/NotificationPrompt.vue`):
- 首次进入游戏时在 GameView 底部弹出 toast/snackbar
- 文案: "启用通知以获取游戏更新提醒" + "启用" / "稍后" 按钮
- 点击"启用"调用 `requestPermission()`
- 权限状态持久化到 `localStorage`

**Service Worker** (`frontend/public/sw.js`):
- 已有基础 SW (PWA manifest)
- 新增 `push` 事件监听（预留，本期不接 Push API）
- 新增 `notificationclick` 事件：点击通知跳转到游戏页面

### 触发逻辑

- `GameView.vue` `onMounted` 时检查 `localStorage.getItem('notification_prompted')`
- 未提示过 → 显示 NotificationPrompt
- 已提示过 → 跳过

---

## D-008: 召回邮件 (AC-057)

### 设计思路

后端新增 `RecallService` cron 任务，每日扫描 `users.last_login` 超过 7 天的用户，通过共享的 `MockEmailService` 发送召回邮件。

### DB: recall_emails 表

```sql
CREATE TABLE recall_emails (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    email VARCHAR(255) NOT NULL,
    email_type VARCHAR(50) DEFAULT 'recall_7day',
    game_link TEXT,
    progress_summary JSONB DEFAULT '{}',
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    opened BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_recall_emails_user_id ON recall_emails(user_id);
CREATE INDEX idx_recall_emails_sent_at ON recall_emails(sent_at);
```

### BE: RecallService

```python
class RecallService:
    """Cron job: send recall emails to inactive users."""
    
    async def run_daily(self) -> int:
        """Scan users with last_login > 7 days ago and send recall emails."""
        cutoff = datetime.utcnow() - timedelta(days=7)
        inactive_users = await self.db.execute(
            select(User).where(
                User.last_login < cutoff,
                User.email_verified == True
            )
        )
        sent_count = 0
        for user in inactive_users:
            # Check if already sent recently
            recent = await self._check_recent_recall(user.id)
            if recent:
                continue
            summary = await self._build_progress_summary(user.id)
            await self.email_service.send_recall_email(
                email=user.email,
                game_link=f"https://isekai-wanderer.example.com/?recall={user.id}",
                summary=summary
            )
            await self._record_recall_email(user, summary)
            sent_count += 1
        return sent_count
    
    async def _build_progress_summary(self, user_id: UUID) -> dict:
        """Build recent play progress summary."""
        sessions = await self.db.execute(
            select(GameSession)
            .where(GameSession.user_id == user_id)
            .order_by(GameSession.started_at.desc())
            .limit(3)
        )
        return {
            "recent_scripts": [s.script_name for s in sessions],
            "total_sessions": len(sessions)
        }
```

- 位置: `backend/app/services/recall_service.py`
- Cron 调度: `backend/app/main.py` 中使用 `APScheduler` 或 `asyncio` 定时任务
  - 每日 UTC 09:00 执行
  - 开发阶段可手动触发: `POST /api/v1/admin/trigger-recall` (内部测试用)
- 复用 AC-047 的 `MockEmailService`

### users 表补充

- 确认 `users.last_login` 字段存在（CR-001 已有 `updated_at`，补充 `last_login TIMESTAMPTZ`）
- 登录成功时更新 `last_login = NOW()`

---

## D-009: 自由对话模式 (AC-058)

### 设计思路

新增自由对话 API，复用 LLM Gateway + MemoryService。5 个预设话题通过 prompt 模板注入角色约束。前端新增 FreeChatView 提供角色选择 → 话题选择 → 对话界面。

### DB: free_chat_sessions 表

```sql
CREATE TABLE free_chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    character_id UUID NOT NULL REFERENCES characters(id),
    topic VARCHAR(50) NOT NULL,
    messages JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_free_chat_user_id ON free_chat_sessions(user_id);
CREATE INDEX idx_free_chat_character_id ON free_chat_sessions(character_id);
```

`messages` JSONB 结构:
```json
[
  {"role": "user", "content": "你好", "timestamp": "..."},
  {"role": "assistant", "content": "欢迎回来...", "timestamp": "..."}
]
```

### BE: POST /api/v1/game/{sessionId}/free-chat

**Request**:
```json
{
  "character_id": "uuid",
  "topic": "daily_chat",
  "message": "你好，今天过得怎么样？",
  "session_id": "uuid (optional, empty = new session)"
}
```

**Response** (200):
```json
{
  "chat_session_id": "uuid",
  "character_id": "uuid",
  "topic": "daily_chat",
  "reply": {
    "content": "啊，是你啊...今天的风很大呢。",
    "emotion": "warm"
  }
}
```

**Error Codes**:
| Code | HTTP | Condition |
|---|---|---|
| CHARACTER_NOT_FOUND | 404 | character_id 不存在 |
| LLM_GENERATION_FAILED | 503 | AI 生成失败，fallback 预设回复 |
| VALIDATION_ERROR | 422 | topic 不在 5 个预设中 |

**5 个预设话题**:
| Topic Key | 中文名 | 英文名 |
|---|---|---|
| `daily_chat` | 日常闲聊 | Daily Chat |
| `character_story` | 角色故事 | Character Story |
| `world_discussion` | 世界观探讨 | World Discussion |
| `emotional_support` | 情感倾诉 | Emotional Support |
| `adventure_advice` | 冒险建议 | Adventure Advice |

**实现层**:
- Route: `backend/app/api/v1/game.py` 新增 `free_chat` endpoint
- Service: `backend/app/services/free_chat_service.py`
  - `create_or_resume_session(user_id, character_id, topic)`
  - `generate_reply(user_message, character, topic, memories)`
- LLM: 复用 `llm/gateway.py`，prompt 模板:
  ```python
  FREE_CHAT_SYSTEM_PROMPT = """
  你正在扮演角色 {character_name}。
  性格特征: {personality_traits}
  对话风格: {dialogue_style}
  当前话题: {topic_name}
  
  规则:
  1. 始终保持角色性格一致性
  2. 回复不超过 200 字
  3. 适当引用与话题相关的记忆（如果有）
  4. 回复必须包含情绪标签 [emotion: xxx]
  """
  ```
- Memory: 调用 `memory_service.recall(user_id, character_id, user_message)` 获取相关记忆注入 prompt
- 对话历史: 保存到 `free_chat_sessions.messages` JSONB

### FE: FreeChatView.vue

- 位置: `frontend/src/views/FreeChatView.vue`
- 路由: `/free-chat`
- 入口: HomeView 新增"自由对话"按钮

**三阶段 UI**:
1. **角色选择**: 展示已解锁角色卡片网格，点击选择
2. **话题选择**: 展示 5 个话题卡片，点击选择
3. **对话界面**: 复用 `DialogueBox` 组件风格，顶部显示角色立绘和话题标签

**API 调用**: `frontend/src/api/game.ts` 新增 `sendFreeChat(data)` 方法

---

## Runtime Contract — CR-002 Additions

### CR-002 新增/更新 Runtime 配置

| Key | Value | Status |
|---|---|---|
| frontend_origin | `http://localhost:3000` (dev) | Defined (unchanged) |
| backend_origin | `http://localhost:8000` (dev) | Defined (unchanged) |
| api_base_path | `/api/v1` | Defined (unchanged) |
| vite_proxy_target | `http://localhost:8000` | Defined (unchanged) |
| health_endpoint | `/api/v1/health` | Defined (unchanged) |
| delivery_e2e_command | `docker compose up -d && sleep 5 && curl -f http://localhost/api/v1/health` | Defined (unchanged) |
| browser_e2e_command | `APP_BASE=http://localhost:3000 npx playwright test tests/e2e/cr002-features.spec.ts --headed --trace on` | **New** |
| browser_e2e_user_actions | 路线图查看 + 密码重置流程 + 语言切换 + SEO meta 检查 + 自由对话 + 通知权限提示 | **New** |
| api_contract_doc | `docs/api/api.md` (44 endpoints: 41 existing + 3 new) | **Updated** |
| database_contract_doc | `docs/database/database.md` (29 tables: 26 existing + 3 new) | **Updated** |
| persistence_contract | PostgreSQL + pgvector + Redis (unchanged) | Defined (unchanged) |
| mock_policy | MockEmailService (AC-047/AC-057), MockDiscordService (AC-055), MockLLMProvider (AC-058); **no mock API for Delivery E2E or Release evidence** | **Updated** |

### New API Endpoints (CR-002)

| Method | Path | Auth | AC |
|---|---|---|---|
| GET | /api/v1/game/{scriptId}/route-map | Bearer | AC-045 |
| POST | /api/v1/auth/forgot-password | None | AC-047 |
| POST | /api/v1/auth/reset-password | None | AC-047 |
| POST | /api/v1/game/{sessionId}/free-chat | Bearer | AC-058 |

### New DB Tables (CR-002)

| Table | AC | Notes |
|---|---|---|
| `password_resets` | AC-047 | 已在 CR-001 schema 中定义，CR-002 实现 |
| `discord_configs` | AC-055 | Mock webhook config |
| `recall_emails` | AC-057 | 召回邮件记录 |
| `free_chat_sessions` | AC-058 | 自由对话历史 |

### Mock Policy (CR-002)

| Mock 对象 | Mock 实现 | 替换路径 |
|---|---|---|
| Email (SMTP) | MockEmailService → logger + log file | CR-003: Resend/SendGrid |
| Discord Webhook | MockDiscordService → logger + log file | CR-003: Real Discord Bot |
| LLM Provider | MockLLMProvider (已有) → 预设回复 | CR-003: Real OpenAI/Anthropic |

**禁止 mock 的场景**:
- Delivery E2E / Runtime Smoke: 必须使用真实前后端 + 真实 proxy
- Release 证据: Mock API=no
- Browser Interaction E2E: 必须使用真实后端 API

---

## Architecture Impact

### Module Changes

| Module | Change Type | Description |
|---|---|---|
| `backend/app/api/v1/auth.py` | Extend | +forgot_password, +reset_password |
| `backend/app/api/v1/game.py` | Extend | +get_route_map, +free_chat |
| `backend/app/services/auth_service.py` | Extend | +request_password_reset, +reset_password |
| `backend/app/services/script_service.py` | Extend | +get_route_map |
| `backend/app/services/free_chat_service.py` | **New** | Free chat business logic |
| `backend/app/services/discord_service.py` | **New** | Mock Discord webhook |
| `backend/app/services/recall_service.py` | **New** | Cron recall email job |
| `backend/app/core/email.py` | Extend | MockEmailService 实现 |
| `backend/app/llm/prompts/free_chat.py` | **New** | Free chat prompt templates |
| `backend/alembic/versions/cr002_*.py` | **New** | Migration for 3 new tables |
| `frontend/src/views/RouteMap.vue` | **New** | Route map view |
| `frontend/src/views/ForgotPasswordView.vue` | **New** | Forgot password view |
| `frontend/src/views/ResetPasswordView.vue` | **New** | Reset password view |
| `frontend/src/views/FreeChatView.vue` | **New** | Free chat view |
| `frontend/src/views/SettingsView.vue` | Extend | +language switch, +Discord link |
| `frontend/src/components/NotificationPrompt.vue` | **New** | PWA notification prompt |
| `frontend/src/composables/useTypewriter.ts` | Extend | +emotion speed multiplier |
| `frontend/src/composables/useNotification.ts` | **New** | Notification API wrapper |
| `frontend/src/components/AudioPlayer.vue` | Extend | +emotion volume multiplier |
| `frontend/src/i18n/` | **New** | i18n directory + zh.json + en.json + index.ts |
| `frontend/src/main.ts` | Extend | +i18n plugin, +head plugin |
| `frontend/public/sitemap.xml` | **New** | SEO sitemap |
| `frontend/public/robots.txt` | **New** | SEO robots |
| `frontend/public/sw.js` | Extend | +notification events |

### Dependency Direction (unchanged)

```
frontend ──(HTTP/SSE)──> backend ──> PostgreSQL/pgvector
                             ├──> Redis
                             └──> LLM API (mock or real)
```

No new cross-module dependencies introduced.

---

## Security Considerations

### AC-047 密码重置安全

| 风险 | 缓解措施 |
|---|---|
| 邮箱枚举 | forgot-password 对不存在邮箱也返回 200 |
| Token 暴力猜测 | Token 为 `secrets.token_urlsafe(32)` (256-bit entropy) |
| Token 重用 | 单次使用，used=TRUE 后立即失效 |
| Token 过期 | 1 小时 TTL，过期拒绝 |
| Rate limit | 3 次/小时/邮箱 (Redis counter) |
| 密码强度 | Pydantic 验证: 最少 8 字符 + 数字 + 字母 |

### AC-058 自由对话安全

| 风险 | 缓解措施 |
|---|---|
| Prompt injection | 用户输入转义，system prompt 与 user message 分离 |
| LLM 输出不可控 | RuleEngine 验证 + 最大长度限制 + 情绪标签格式校验 |
| 对话数据隐私 | 存储在数据库，仅用户本人可访问 |

### AC-055/AC-057 Mock 服务安全

- Mock 服务不发送真实 HTTP 请求，无外部攻击面
- Webhook URL 存储在数据库，不暴露到前端
- 日志文件不含敏感用户数据（邮箱脱敏）

---

## Document Sync

| Target Doc | Status | Summary / Evidence |
|-----------|--------|-------------------|
| `docs/architecture/architecture.md` | Synced | 新增 free_chat_service, discord_service, recall_service 模块 + 4 个新 View + 2 个新 composable |
| `docs/api/api.md` | Synced | 新增 4 个 API endpoint (45 total) + 3 个新错误码 + mock 边界更新 |
| `docs/database/database.md` | Synced | 新增 3 个表 (29 total) + users.last_login 字段 + CR-002 DB/API/Mock/Runtime 关系表 |
| `docs/security/security.md` | Synced | 新增密码重置安全策略 + 自由对话安全 + Mock 服务安全 |
| `docs/decisions/decisions.md` | Not Required | CR-002 无新技术选型决策，沿用 CR-001 ADR-0001~0008 |
| `docs/runtime/runtime-contract.md` | Synced | CR-002 新增 browser_e2e_command + browser_e2e_user_actions + mock services + CR-002 Additions 章节 |

---

## Rollback Strategy

CR-002 为增量开发，所有新功能可独立回滚：

| AC | Rollback 方案 |
|---|---|
| AC-045 | 删除 RouteMap.vue + 移除 route-map endpoint + 回滚 ScriptDetailView |
| AC-047 | 删除 ForgotPasswordView/ResetPasswordView + 移除 auth endpoints + 保留 password_resets 表（无数据风险） |
| AC-048 | 回滚 useTypewriter + AudioPlayer 到 CR-001 版本 |
| AC-052 | 删除 i18n/ 目录 + 回滚 main.ts + 移除 SettingsView 语言切换 |
| AC-054 | 删除 sitemap.xml/robots.txt + 移除 @vueuse/head |
| AC-055 | 删除 discord_service + discord_configs 表 + 移除 SettingsView Discord 链接 |
| AC-056 | 回滚 sw.js + 删除 NotificationPrompt + useNotification |
| AC-057 | 删除 recall_service + recall_emails 表 + 停止 cron |
| AC-058 | 删除 FreeChatView + free_chat_service + free_chat_sessions 表 |

---

## Task Split Suggestions (for PL)

### Phase 1 模块拆分

| 模块 | 任务 | Owner | 依赖 | 验证方式 |
|---|---|---|---|---|
| BE-Auth | AC-047 密码重置 | Cat01-be | 无 | pytest + httpx |
| BE-Game | AC-045 路线图 | Cat01-be | 无 | pytest + httpx |
| BE-Game | AC-058 自由对话 | Cat01-be | AC-045 (共享 game.py) | pytest + httpx |
| BE-Service | AC-055 Discord | Cat01-be | 无 | pytest mock |
| BE-Service | AC-057 召回邮件 | Cat01-be | AC-047 (共享 MockEmailService) | pytest + cron |
| FE-Auth | AC-047 密码重置页面 | Cat01-fe | BE-Auth | Playwright |
| FE-Game | AC-045 路线图页面 | Cat01-fe | BE-Game | Playwright |
| FE-Game | AC-058 自由对话页面 | Cat01-fe | BE-Game | Playwright |
| FE-Core | AC-048 情绪节奏 | Cat01-fe | 无 | Vitest + Playwright |
| FE-Core | AC-052 i18n | Cat01-fe | 无 | Vitest + Playwright |
| FE-Core | AC-054 SEO | Cat01-fe | 无 | Lighthouse / curl |
| FE-Core | AC-056 PWA 通知 | Cat01-fe | 无 | Playwright |
| FE-Settings | AC-052+AC-055 SettingsView | Cat01-fe | BE-Discord | Playwright |
| QA | Phase 1 E2E | Cat01-qa | 全部 P1 | Playwright + pytest |

### 并行策略

- **Wave 1** (无依赖): BE-Auth, BE-Game (AC-045), BE-Service (AC-055), FE-Core (AC-048/052/054/056)
- **Wave 2** (依赖 Wave 1): BE-Service (AC-057 依赖 AC-047 MockEmailService), BE-Game (AC-058), FE-Auth (依赖 BE-Auth), FE-Game (依赖 BE-Game)
- **Wave 3** (集成): FE-Settings (整合 AC-052+AC-055), QA E2E

---

## Phase 2 Preview (P0 测试补齐)

Phase 1 全部完成并通过 QA 后，进入 Phase 2。Phase 2 不新增代码，仅补齐 10 项 P0 测试：

| AC | 测试类型 | 工具 |
|---|---|---|
| AC-008 | Browser E2E | Playwright |
| AC-015 | Performance | Playwright + performance.now() |
| AC-016 | Performance | Playwright + CSS transition |
| AC-017 | Browser E2E | Playwright |
| AC-018 | Performance | Playwright + rAF |
| AC-019 | Performance | Lighthouse CI |
| AC-028 | Unit + Delivery | pytest |
| AC-029 | Browser E2E | Playwright |
| AC-034 | Unit | pytest + MockProvider |
| AC-041 | Unit + Delivery | pytest |

---

## Design Landing Points (AC → Design)

| AC | Design Section | Key Artifacts |
|---|---|---|
| AC-045 | D-001 | RouteMap.vue, GET /game/{scriptId}/route-map, script_service.get_route_map |
| AC-047 | D-002 | ForgotPasswordView, ResetPasswordView, POST /auth/forgot-password, POST /auth/reset-password, password_resets, MockEmailService |
| AC-048 | D-003 | useTypewriter emotion multiplier, AudioPlayer emotion volume, emotion mapping table |
| AC-052 | D-004 | vue-i18n, zh.json, en.json, SettingsView language switch, i18n/index.ts |
| AC-054 | D-005 | @vueuse/head, sitemap.xml, robots.txt, per-view meta |
| AC-055 | D-006 | DiscordService mock, discord_configs, SettingsView Discord link |
| AC-056 | D-007 | useNotification, NotificationPrompt.vue, sw.js notification events |
| AC-057 | D-008 | RecallService cron, recall_emails, MockEmailService (shared), users.last_login |
| AC-058 | D-009 | FreeChatView, POST /game/{sessionId}/free-chat, free_chat_sessions, free_chat_service, LLM prompt template |