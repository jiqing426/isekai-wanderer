# CR-028 Design: 剧本角色选择与多故事线系统

## Overview

- 玩家在剧本详情页选择扮演角色，不同角色对应不同故事线（Route），生成独立存档
- 扩展 Character 表（+5 字段）、GameSession 表（+2 字段）、新建 user_character_unlocks 表
- 扩展 GET /scripts/{id}、POST /game/start、GET /saves 接口，新增 POST /characters/{id}/unlock
- NarrativeEngine PromptBuilder 新增 L3 Player Identity 层（100 tok），向后兼容
- 前端改造：剧本详情页角色选择、游戏页角色展示、存档筛选、个人中心角色信息
- 数据迁移：已有 is_main 角色自动 playable，已有 GameSession 向后兼容

## Technical Approach

- 数据层：Alembic 迁移脚本，Character 加 playable/playable_route_id/play_description/unlock_type/unlock_price；GameSession 加 character_id/character_name；新建 user_character_unlocks（UNIQUE user_id+character_id）
- API 层：GET /scripts/{id} 返回 playable_characters 数组（含 is_unlocked 计算）；POST /game/start 接受可选 character_id，自动匹配 playable_route_id；GET /saves 返回 character_name 并支持 ?character_id= 筛选；POST /characters/{id}/unlock 直接写入解锁记录（本期不扣费）
- NarrativeEngine：PromptBuilder 新增 L3 Player Identity 层，character_id 不为 NULL 时注入角色身份到 Prompt，为 NULL 时 L3 为空（向后兼容）
- 前端：Script Store 新增 selectedCharacterId 状态；剧本详情页复用角色区域增加可扮演标识和选中态；锁定角色显示遮罩+🔒+价格；游戏页顶部展示角色信息（无切换按钮）；存档管理页标签栏筛选；个人中心展示最近扮演角色
- 数据迁移：is_main=true 角色自动 playable=true，playable_route_id 取剧本第一条 Route，unlock_type='free'；迁移幂等（WHERE playable=false 条件）

## Technology Decisions

| Decision | Selected | Status | Evidence |
|----------|----------|--------|----------|
| 数据模型扩展方式 | 扩展 Character/GameSession 表 + 新建 user_character_unlocks | Accepted | ADR-0009 `docs/decisions/decisions.md`，用户确认 |
| 角色名存储方式 | GameSession 快照 character_name | Accepted | ADR-0010 `docs/decisions/decisions.md`，用户确认 |
| 解锁类型枚举 | VARCHAR(20) free/paid/subscription | Accepted | ADR-0011 `docs/decisions/decisions.md`，用户确认 |
| PromptBuilder 角色注入 | 新增 L3 Player Identity 层（100 tok） | Accepted | 设计决策 D-001 `design.md`，PL 确认，向后兼容验证通过 |
| 前端状态管理 | Pinia Store 新增 selectedCharacterId | Not Required | 纯前端实现细节，无长期架构影响 |

## Document Sync

| Target Doc | Status | Summary / Evidence |
|------------|--------|-------------------|
| `docs/architecture/architecture.md` | Synced | 新增 CR-028 模块依赖关系、PromptBuilder L3 层、新组件 |
| `docs/api/api.md` | Synced | 扩展 3 端点 + 新增 1 端点 + 新增错误码，总计 61 端点 |
| `docs/database/database.md` | Synced | 新增 user_character_unlocks 表 + 扩展 characters/game_sessions + 迁移策略，总计 32 表 |
| `docs/security/security.md` | Synced | 新增 CR-028 安全表：解锁接口鉴权、数据校验、SQL 注入防护 |
| `docs/decisions/decisions.md` | Synced | 新增 ADR-0009/0010/0011：多角色架构、快照模式、解锁枚举 |
| `docs/runtime/runtime-contract.md` | Synced | 新增 CR-028 端点 + Browser E2E 命令/用户动作 + 端点总数更新 |
