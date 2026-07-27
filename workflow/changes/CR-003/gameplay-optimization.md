# CR-003 游戏体验优化需求（Wave 4）

> CEO 2026-07-23 新增指令。在当前 Wave 1-3 完成后立即执行。

## 一、五大游戏体验优化（P0）

| # | 优化项 | 具体内容 | 负责 | AC 编号 |
|---|--------|---------|------|---------|
| 1 | 角色立绘替换 emoji | 每个角色准备 3-5 张表情差分图（normal/happy/sad/angry），根据 emotion 状态自动切换。当前 GameView.vue 的 `<div class="character-sprite">🧑</div>` 需替换为图片组件。 | FE | AC-GAME-001 |
| 2 | 场景背景图 | 每个 scene 配一张背景图（可 AI 生成），替换当前纯渐变背景色。GameView.vue 的 `.scene-bg` 从 `background: var(--bg-deep)` 改为 `background-image` + overlay。 | FE | AC-GAME-002 |
| 3 | BGM 实装 | 接入免版权 BGM 资源（平静/紧张/温馨/战斗 4 类），scene 切换时自动切歌。需准备音频资源 + 前端 AudioManager + fade 转场。 | FE | AC-GAME-003 |
| 4 | 打字音效 | 打字机效果播放时加轻微"哒哒"打字声，可开关。DialogueBox.vue 已有 typewriter 逻辑，需叠加 audio context。 | FE | AC-GAME-004 |
| 5 | 选择后果提示 | 选项卡片增加"⚠️ 影响剧情走向"标签提示。ChoicePanel.vue 选项目前只显示文字+好感度变化，缺少影响提示。 | FE | AC-GAME-005 |

## 二、API 接口报错排查（P0）

| # | 排查项 | 具体内容 | 负责 | AC 编号 |
|---|--------|---------|------|---------|
| 1 | 路由注册检查 | 检查 backend/app/api/v1/ 下所有 router 是否正确注册到 main app | BE | AC-API-001 |
| 2 | 404 接口排查 | 前端调用了哪些后端不存在的接口，补齐缺失路由 | BE | AC-API-002 |
| 3 | 500 接口排查 | 检查接口内部报错（数据库模型不匹配、import 错误等） | BE | AC-API-003 |
| 4 | 前端错误拦截器优化 | api/http.ts 拦截器显示有用中文错误信息，不用 raw error | FE | AC-API-004 |
| 5 | 页面 catch 块优化 | 所有页面 catch 块显示有意义的错误信息 | FE | AC-API-005 |

## 三、Free Chat 输入框验证（P1）

| # | 验证项 | 具体内容 | 负责 | AC 编号 |
|---|--------|---------|------|---------|
| 1 | FreeChatView.vue 修复验证 | CEO 已修复前端输入框问题，需验证功能完整性 | QA | AC-FC-001 |
| 2 | /free-chat/topics 接口验证 | 新增接口功能验证 | QA | AC-FC-002 |
| 3 | /free-chat/history 接口验证 | 新增接口功能验证 | QA | AC-FC-003 |

## 优先级与执行顺序

- **P0**：五大体验优化 + API 排查（Wave 4，当前 Wave 1-3 完成后立即执行）
- **P1**：Free Chat 验证（Wave 4 尾部或 INTEGRATION 阶段验证）

## 四、API 报错排查详细报告（小智 2026-07-18 补充）

### 后端问题：错误格式不统一

| 错误方式 | 文件 | 返回格式 | 影响 |
|---------|------|---------|------|
| ✅ `AppException` | auth.py, game.py, memories.py | `{"error_code": "xxx", "message": "xxx"}` | 前端能正确解析 |
| ❌ `HTTPException` | daily.py, gallery.py, oauth.py, payment.py, scripts.py, share.py, ugc.py, user.py, moderation.py, dependencies.py | `{"detail": "xxx"}` | 前端拿到的是 `HTTP 422` 或 `detail` 字段，无法匹配 |
| ❌ 无异常处理 | affection.py, health.py | 直接 500 或空响应 | 前端只能显示 `HTTP 500` |

### 前端问题

1. **部分 catch 块是空的** — FreeChatView.vue 的 topics/history 加载失败时 `catch {}` 直接吞掉错误
2. **错误信息不友好** — 多数页面显示 `err.message`，但后端返回的 message 是英文或 Python 堆栈信息
3. **缺少全局错误兜底** — api/http.ts 的 request 函数在非 ok 响应时 throw Error，但没有统一的用户提示机制

### 需要 BE 修复

- [ ] `daily.py` — HTTPException → AppException
- [ ] `gallery.py` — HTTPException → AppException  
- [ ] `oauth.py` — HTTPException → AppException
- [ ] `payment.py` — HTTPException → AppException
- [ ] `scripts.py` — HTTPException → AppException
- [ ] `share.py` — HTTPException → AppException
- [ ] `ugc.py` — HTTPException → AppException
- [ ] `user.py` — HTTPException → AppException
- [ ] `moderation.py` — HTTPException → AppException
- [ ] `dependencies.py` — HTTPException → AppException
- [ ] `affection.py` — 添加异常处理

### 需要 FE 修复

- [ ] api/http.ts — 全局错误拦截器增加中文错误映射
- [ ] FreeChatView.vue — 空 catch 块补充 `message.error()`
- [ ] 所有页面 catch 块 — 统一使用 `message.error()` + i18n 错误文案

## 五、剩余优化项（纳入 Wave 1）

### 选择系统优化（中难度）

| # | 优化项 | 具体内容 | 负责 | AC 编号 |
|---|--------|---------|------|--------|
| 1 | 隐藏选项 | 好感度达标时才出现的特殊选项（金色高亮）。ChoicePanel.vue 加 `locked`/`required_affection` 字段，不达标时灰显+锁图标 | FE+BE | AC-GAME-006 |
| 2 | 选择后果预览 | 选前提示影响方向（如"这可能让她更信任你"）。ChoicePanel.vue 加 `hint` 字段，hover 显示 | FE+BE | AC-GAME-007 |
| 3 | 累积选择效果 | 连续选对触发特殊剧情（streak 计数器）。BE 记录选择链，触发特殊事件 | BE | AC-GAME-008 |

### 剧本结构优化

| # | 优化项 | 具体内容 | 负责 | AC 编号 |
|---|--------|---------|------|--------|
| 4 | 多结局扩展 | 从 good/bad 扩展到 5 种：good/bad/normal/perfect/regret。EndingView.vue 加对应 UI + cg-emoji | FE+BE | AC-GAME-009 |
| 5 | 多分支路线 | Route 系统真正支持 A/B 分支。BE NarrativeEngine 支持分支跳转逻辑 | BE | AC-GAME-010 |
| 6 | LLM 过渡内容增强 | 增加 LLM 生成的场景间过渡文本，减少纯预设文本 | BE | AC-GAME-011 |

### 记忆系统可见化

| # | 优化项 | 具体内容 | 负责 | AC 编号 |
|---|--------|---------|------|--------|
| 7 | 回忆录系统 | 通关后生成"冒险回顾"页面，展示关键选择 + AI 总结。新增 RecapView.vue | FE+BE | AC-GAME-012 |
| 8 | 记忆可见化 | GalleryView 展示角色的记忆列表，玩家能看到角色记住了什么 | FE+BE | AC-GAME-013 |
| 9 | 对话历史回看 | GameView 支持上滑查看之前的对话记录 | FE | AC-GAME-014 |

### 沉浸感增强

| # | 优化项 | 具体内容 | 负责 | AC 编号 |
|---|--------|---------|------|--------|
| 10 | 场景切换转场动画 | 主场景切换加 fade/slide/闪白效果。GameView.vue 加 `<transition>` 包裹 | FE | AC-GAME-015 |
| 11 | 环境音效 | 下雨/风声/战斗等环境音效，根据 scene 类型自动播放。扩展 useAudioManager.ts | FE | AC-GAME-016 |
| 12 | 角色语音 TTS | 用 Web Speech API 或外部 TTS 给角色配音，不同角色不同声线 | FE | AC-GAME-017 |

## 约束

- 角色立绘和场景背景图可使用 AI 生成或免版权素材
- BGM 必须免版权（推荐 freesound.org / incompetech.com）
- 打字音效默认关闭，用户可在设置中开启
- API 排查需在真实后端环境执行，不使用 mock
- TTS 优先用 Web Speech API（免费），备选外部 API
- 多分支路线需与现有 Route 系统兼容
- 累积选择效果需持久化到 game_sessions 表
