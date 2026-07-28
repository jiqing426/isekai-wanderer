# CR-018 用户复测问题修复

## 为什么做 / Why

用户在 CR-001~CR-017 迭代完成后进行复测，发现 27 个问题涉及剧本游戏、角色系统、收藏馆、碎片商城、个人中心、设置、社区等核心模块。其中 3 个 P0 问题（送礼接口 400、自由对话 401、头像上传失败）直接阻塞核心功能使用，10 个 P1 问题影响功能逻辑正确性，14 个 P2 问题影响用户体验。

## 变更内容 / What Changes

### P0 修复（3项）
- T-001: 送礼接口 400 错误修复（gift.py 查询逻辑）
- T-002: 剧本内自由对话 401 修复（前端鉴权）
- T-003: 更换头像 AUTH_TOKEN_EXPIRED 修复（multipart token 传递）

### P1 修复（10项）
- T-004: 好感度实时更新（process_choice 返回 affection_change）
- T-005: 自由对话历史持久化（session 复用逻辑）
- T-006: 剧本流程过短修复（节点流转逻辑）
- T-007: 剧本进度记录（choice_history JSON 持久化）
- T-008: UUID v4 数据迁移（3+3+12 条记录 + JSON 字段 + 外键）
- T-009: 完成剧本统计修正（COUNT DISTINCT script_id）
- T-010: 累计获得碎片为 0 修复（FragmentTransaction 创建逻辑）
- T-011: 对话额度重置确认（honeymoon base_quota=10）

### P2 修复（14项）
- T-012~T-025: 前端 UI/展示/i18n 修复
- T-026~T-030: 二次复测新增问题修复

### 额外修复
- UUID v4 迁移导致 6 个空 route 修复（36 nodes + 36 choices）
- 林辰 UUID 迁移修复（新 UUID: 26917e16-...）
- 头像图片 404 修复（nginx 兼容配置）
- 碎片交易明细中文映射修复（shards.py 前缀匹配逻辑）
- 送礼弹框碎片余额显示

## 非目标 / Non-Goals

- 不涉及新功能开发（仅修复已有功能缺陷）
- 不涉及架构变更
- 不涉及数据库 schema 变更（仅数据迁移）
- Mock 数据文件中的硬编码 UUID 不修复（DISABLE_MOCK=1 已禁用）

## 成功标准 / Success Criteria

1. 所有 P0 问题修复并通过 QA 端到端验证
2. 所有 P1 问题修复并通过 QA 验证
3. P2 问题修复或标记为不阻塞发布
4. UUID v4 迁移完成，7 张表无硬编码残留
5. 无回归问题
6. 完整游戏流程（开始→选择→结局）验证通过

## 影响 / Impact

- **后端**: gift.py, chat.py, users.py, shards.py, narrative_engine.py, ending_progress.py, sign.py, subscription.py, characters.py, community.py 等文件修改
- **前端**: GameView.vue, CharacterDetailView.vue, PersonalCenterView.vue, FragmentMallView.vue, AchievementView.vue, zh-CN.ts 等文件修改
- **数据库**: UUID v4 迁移（scripts/routes/characters/nodes/choices/user_scripts/fragment_transactions）
- **配置**: nginx 兼容路由（/static/avatars/ + /avatars/）

## 状态

✅ 全部完成（27/27 + 额外修复 5 项）
