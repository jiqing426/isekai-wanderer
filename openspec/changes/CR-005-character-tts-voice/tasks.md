# CR-005: 角色详情语音试听 TTS 集成

## 概述
将角色详情页的语音试听功能从 Web Speech API 升级为阿里云 CosyVoice TTS，预生成音频存储到数据库和文件系统。

## 任务清单

### 后端任务（BE）

#### BE-01: 数据库模型变更 ✅
- [x] Character 模型新增 `tts_config` JSON 字段
- [x] Character 模型新增 `gender` 字段（male/female/neutral，默认 female）
- [x] 创建数据库迁移脚本 `002_add_character_tts_config.py`
- 完成时间：2026-07-31 16:40
- 交付物：backend/app/models/script.py, backend/migrations/002_add_character_tts_config.py

#### BE-02: TTS 服务实现 ✅
- [x] 创建 `backend/app/services/tts/service.py`
- [x] 实现 `TTSService.synthesize()` 方法（调用阿里云 API）
- [x] 实现 `TTSService.generate_character_voices()` 方法（生成 4 个情绪的语音）
- [x] 音频文件存储到 `/app/static/voices/{character_id_prefix}/`
- 完成时间：2026-07-31 16:40
- 交付物：backend/app/services/tts/service.py, backend/app/services/tts/__init__.py

#### BE-03: 配置变更 ✅
- [x] `backend/app/core/config.py` 添加 TTS 配置项
- [x] `.env` 添加 TTS 环境变量
- 完成时间：2026-07-31 16:40
- 交付物：backend/app/core/config.py, backend/.env

#### BE-04: API 接口修改 ✅
- [x] 修改 `GET /characters/{id}/voices` 返回 `audio_url`、`text`、`voice`、`speed`
- [x] 修改角色创建接口，自动生成 TTS 语音
- [x] 新增 `POST /characters/{id}/regenerate-voices` 重新生成语音接口
- 完成时间：2026-07-31 16:40
- 交付物：backend/app/api/v1/characters.py

#### BE-05: 静态文件服务 ✅
- [x] 确保 FastAPI 挂载 `/static` 目录包含 `voices/` 子目录
- 完成时间：2026-07-31 16:40
- 交付物：backend/app/main.py (已存在), /app/static/voices/ 目录已创建

### 前端任务（FE）

#### FE-01: API 层 ✅
- [x] 修改 `src/api/character.ts` 或 `game.ts`，更新 voices 接口返回类型
- 完成时间：2026-07-31 15:55
- 交付物：src/api/game.ts 新增 VoiceSample 接口

#### FE-02: Composable 重写 ✅
- [x] 重写 `src/composables/useCharacterVoice.ts`
- [x] 实现 `playAudioUrl()` 播放预生成音频
- [x] 实现降级到 Web Speech API 的逻辑
- 完成时间：2026-07-31 15:55
- 交付物：src/composables/useCharacterVoice.ts 重写完成

#### FE-03: 页面修改 ✅
- [x] 修改 `src/views/CharacterDetailView.vue` 的 `playVoice()` 函数
- [x] 传递 `audio_url` 和降级配置给 `speakVoice()`
- 完成时间：2026-07-31 15:55
- 交付物：src/views/CharacterDetailView.vue 修改完成

#### FE-04: 编译验证 ✅
- [x] vue-tsc --noEmit 通过
- 完成时间：2026-07-31 15:55
- 交付物：零新增类型错误

## 依赖关系
- BE-01 → BE-02 → BE-04
- BE-03 可与 BE-01 并行
- FE-01 依赖 BE-04
- FE-02 可与 BE 并行开发
- FE-03 依赖 FE-01 + FE-02

## 验收标准
- [x] 角色创建时自动生成 4 个情绪的语音文件
- [x] 语音试听页面可播放预生成的音频
- [x] 阿里云 API 失败时降级到 Web Speech API
- [x] 音频文件可通过 URL 直接访问
