# CR-005 Spec: 角色语音试听 TTS 集成

## Requirement: Character 模型扩展

#### Scenario: 新建角色时自动设置默认 gender
- **Given** 管理员创建新角色，未指定 gender
- **Then** 角色 gender 默认为 "female"

#### Scenario: 角色 gender 可设置为 male/female/neutral
- **Given** 管理员编辑角色
- **When** 设置 gender 为 "male" / "female" / "neutral"
- **Then** 数据库正确存储，API 返回正确值

## Requirement: TTS 语音自动生成

#### Scenario: 角色创建后自动生成 4 个情绪语音
- **Given** 新角色创建成功，gender = "female"
- **Then** 系统异步调用阿里云 CosyVoice API 生成 4 个 mp3 文件
- **And** 文件存储在 `/app/static/voices/{character_id_prefix}/`
- **And** tts_config JSON 记录每个情绪的 voice/speed/text/audio_url

#### Scenario: 语音生成失败时不阻塞角色创建
- **Given** 阿里云 API 不可用或返回错误
- **Then** 角色创建仍然成功
- **And** tts_config 中对应情绪的 audio_url 为空
- **And** 前端播放时降级到 Web Speech API

#### Scenario: 文案模板动态替换角色名
- **Given** 角色名为 "樱"
- **When** 生成打招呼语音
- **Then** 实际合成文本为 "你好呀，我是樱，很高兴认识你！今天想聊点什么呢？"

## Requirement: 声音配置按性别区分

#### Scenario: 女性角色使用女性声音
- **Given** 角色 gender = "female"
- **When** 生成打招呼语音
- **Then** 使用 voice = "longxiaochun", speed = 1.1

#### Scenario: 男性角色使用男性声音
- **Given** 角色 gender = "male"
- **When** 生成打招呼语音
- **Then** 使用 voice = "longshuo", speed = 1.1

#### Scenario: neutral 性别角色
- **Given** 角色 gender = "neutral"
- **Then** 使用与 female 相同的声音配置（建议默认值，待确认）

## Requirement: 前端语音播放

#### Scenario: 播放预生成音频
- **Given** 用户点击某情绪的播放按钮
- **And** 该情绪有有效的 audio_url
- **Then** 前端使用 HTML5 Audio 播放预生成 mp3
- **And** 播放中显示暂停图标，播放结束恢复播放图标

#### Scenario: 降级到 Web Speech API
- **Given** 用户点击某情绪的播放按钮
- **And** 该情绪 audio_url 为空或加载失败
- **Then** 前端自动降级使用 Web Speech API 播放
- **And** 用户无感知（无错误提示）

#### Scenario: 订阅墙保持
- **Given** 用户为 free 订阅
- **When** 访问语音试听区域
- **Then** 播放按钮显示为锁标识（与现有行为一致）
- **And** 提示 "💎 升级到 Standard 或 Premium 即可解锁全部语音"

#### Scenario: 播放中再次点击停止
- **Given** 某情绪语音正在播放
- **When** 用户再次点击该情绪的播放按钮
- **Then** 播放停止，按钮恢复为播放图标

#### Scenario: 跨情绪播放互斥
- **Given** 情绪 A 的语音正在播放
- **When** 用户点击情绪 B 的播放按钮
- **Then** 情绪 A 的播放自动停止
- **And** 情绪 B 开始播放，显示暂停图标
- **And** 情绪 A 恢复播放图标

#### Scenario: 音频加载状态反馈
- **Given** 用户点击某情绪的播放按钮
- **And** 该情绪 audio_url 有效但正在加载
- **Then** 按钮显示加载指示器（如旋转图标）
- **And** 加载完成后开始播放

#### Scenario: 音频文件 404 或损坏
- **Given** 用户点击某情绪的播放按钮
- **And** audio_url 返回 404 或文件损坏
- **Then** 前端自动降级使用 Web Speech API 播放
- **And** 控制台记录错误日志（用户无感知）

#### Scenario: 移动端 iOS Safari 播放
- **Given** 用户使用 iOS Safari
- **When** 点击播放按钮
- **Then** 音频正常播放（iOS Safari 需要用户交互才能播放音频，已通过点击事件满足）

## Requirement: 管理端重新生成语音

#### Scenario: 管理端调用重新生成接口
- **Given** 管理员调用 `POST /characters/{id}/regenerate-voices`
- **Then** 系统重新调用阿里云 API 生成 4 个语音
- **And** 覆盖原有音频文件
- **And** 更新 tts_config 中的 audio_url

## Requirement: 数据迁移

#### Scenario: 已有角色补生成语音
- **Given** 数据库中存在创建时未生成语音的角色（tts_config 为空）
- **When** 执行批量生成脚本
- **Then** 为所有 tts_config 为空的角色补生成语音
- **And** 根据 gender 字段选择声音（gender 为空默认 female）
