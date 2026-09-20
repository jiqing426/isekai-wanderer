# CR-005 验收追踪

## 验收项

| REQ | AC | 优先级 | 验收标准 | 覆盖状态 | 备注 |
|-----|-----|--------|----------|----------|------|
| REQ-TTS-001 | AC-TTS-001 | P0 | 新建角色 gender 默认为 "female"，可设置为 male/female/neutral | not_covered | 需后端单元测试 |
| REQ-TTS-002 | AC-TTS-002 | P0 | 角色创建后异步生成 4 个情绪语音 mp3，存储在 /app/static/voices/{prefix}/ | not_covered | 需后端集成测试 + 文件验证 |
| REQ-TTS-002 | AC-TTS-003 | P0 | 语音生成失败不阻塞角色创建，前端降级到 Web Speech API | not_covered | 需后端异常测试 + 前端降级测试 |
| REQ-TTS-002 | AC-TTS-004 | P1 | 文案模板 {character_name} 动态替换为角色名 | not_covered | 需后端单元测试 |
| REQ-TTS-003 | AC-TTS-005 | P0 | female 角色使用 longxiaochun/longxiaoxia/longshu，male 角色使用 longshuo/longshu | not_covered | 需后端单元测试验证 voice 选择逻辑 |
| REQ-TTS-004 | AC-TTS-006 | P0 | 用户点击播放按钮，有 audio_url 时使用 HTML5 Audio 播放 mp3 | covered | 前端实现完成，待联调验证 |
| REQ-TTS-004 | AC-TTS-007 | P0 | audio_url 为空或加载失败时自动降级到 Web Speech API | covered | 前端实现完成，待联调验证 |
| REQ-TTS-004 | AC-TTS-008 | P0 | free 用户看到锁标识和升级提示，standard/premium 用户可播放 | covered | 前端实现完成，待联调验证 |
| REQ-TTS-004 | AC-TTS-009 | P1 | 播放中再次点击停止；跨情绪播放互斥 | covered | 前端实现完成，待联调验证 |
| REQ-TTS-005 | AC-TTS-010 | P1 | 管理端 POST /characters/{id}/regenerate-voices 重新生成并覆盖音频 | not_covered | 需后端 API 测试 |
| REQ-TTS-006 | AC-TTS-011 | P1 | 已有角色可批量补生成语音 | not_covered | 需脚本 + 手动验证 |

## 下游测试标注

| 类型 | 涉及 AC | 后续动作 |
|------|---------|----------|
| Browser Interaction E2E | AC-TTS-006, AC-TTS-007, AC-TTS-008, AC-TTS-009 | QA 编写 Playwright/Cypress 测试 |
| API/DB/Runtime 契约 | AC-TTS-002, AC-TTS-003, AC-TTS-005, AC-TTS-010 | Architect 同步 api.md / database.md |
