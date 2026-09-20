# CR-005: 角色详情语音试听 TTS 集成

## 变更类型
功能增强（Feature Enhancement）

## 变更描述
将角色详情页的语音试听功能从 Web Speech API 升级为阿里云 CosyVoice TTS，预生成音频存储到数据库和文件系统。

## 变更原因
- 当前 Web Speech API 音质差，不同浏览器/OS 表现不一致
- 无法差异化角色声音（所有角色用同一系统语音）
- 无法根据角色性别选择不同音色
- 用户体验低端，与产品"乙女向高品质"定位不符

## 影响范围
- 数据库：Character 表新增 2 字段（tts_config, gender）
- 文件系统：新增 `/app/static/voices/` 目录
- API：`GET /characters/{id}/voices` 返回结构变更
- 前端：`useCharacterVoice.ts` 重写、`CharacterDetailView.vue` 修改
- 后端：新增 TTS 服务、修改角色创建流程

## 主责角色
- PM: 需求分析
- Architect: 架构设计
- Backend: TTS 服务实现、API 修改
- Frontend: 播放逻辑重写
- QA: 测试验证

## 前置条件
- 阿里云 CosyVoice API Key 已配置
- 数据库迁移工具可用
- 静态文件服务已配置

## 风险
- TTS API 调用成本（每角色 4 次调用）
- 阿里云 API 可用性风险（需降级方案）
- 音频文件存储和 CDN 缓存策略

## 不做范围
- 不集成 TTS 到游戏对话流程（仅试听场景）
- 不支持用户/运营自定义文案
- 不支持用户自选声音角色
- 不支持多语言语音
- 不新增语音试听统计/埋点
- 不新增"重新生成语音"的用户入口（仅管理端接口）
