# CR-005 验收追踪

## 验收项

| REQ | AC | 优先级 | 验收标准 | 覆盖状态 | 备注 |
|-----|-----|--------|----------|----------|------|
| REQ-TTS-001 | AC-TTS-001 | P0 | 新建角色 gender 默认为 "female"，可设置为 male/female/neutral | covered | BE-01 已实现，Character.gender 字段已添加 |
| REQ-TTS-002 | AC-TTS-002 | P0 | 角色创建后异步生成 4 个情绪语音 mp3，存储在 /app/static/voices/{prefix}/ | covered | BE-02 已实现，TTSService.generate_character_voices() 生成 4 个情绪语音 |
| REQ-TTS-002 | AC-TTS-003 | P0 | 语音生成失败不阻塞角色创建，前端降级到 Web Speech API | covered | BE-02 异常处理已实现，audio_url 为 None 时前端可降级 |
| REQ-TTS-002 | AC-TTS-004 | P1 | 文案模板 {character_name} 动态替换为角色名 | covered | BE-02 TEXT_TEMPLATES 已实现动态替换 |
| REQ-TTS-003 | AC-TTS-005 | P0 | female 角色使用 longxiaochun/longxiaoxia/longshu，male 角色使用 longshuo/longshu | covered | BE-02 VOICE_CONFIG 已按性别配置声音 |
| REQ-TTS-004 | AC-TTS-006 | P0 | 用户点击播放按钮，有 audio_url 时使用 HTML5 Audio 播放 mp3 | fe_covered | FE-02/FE-03 已实现前端播放逻辑 |
| REQ-TTS-004 | AC-TTS-007 | P0 | audio_url 为空或加载失败时自动降级到 Web Speech API | fe_covered | FE-02 useCharacterVoice.ts 已实现降级逻辑 |
| REQ-TTS-004 | AC-TTS-008 | P0 | free 用户看到锁标识和升级提示，standard/premium 用户可播放 | not_covered | 需前端 E2E 测试验证订阅状态逻辑 |
| REQ-TTS-004 | AC-TTS-009 | P1 | 播放中再次点击停止；跨情绪播放互斥 | fe_covered | FE-03 已实现播放控制逻辑 |
| REQ-TTS-005 | AC-TTS-010 | P1 | 管理端 POST /characters/{id}/regenerate-voices 重新生成并覆盖音频 | covered | BE-04 已实现 regenerate-voices 接口 |
| REQ-TTS-006 | AC-TTS-011 | P1 | 已有角色可批量补生成语音 | not_covered | 需编写批量生成脚本 |

## 下游测试标注

| 类型 | 涉及 AC | 后续动作 |
|------|---------|----------|
| Browser Interaction E2E | AC-TTS-006, AC-TTS-007, AC-TTS-008, AC-TTS-009 | QA 编写 Playwright/Cypress 测试 |
| API/DB/Runtime 契约 | AC-TTS-002, AC-TTS-003, AC-TTS-005, AC-TTS-010 | Architect 同步 api.md / database.md |
