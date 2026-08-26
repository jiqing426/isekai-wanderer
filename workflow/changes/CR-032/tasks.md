# CR-032 Tasks

## 任务分配

### FE 任务

#### T-032-FE-001: 修复个人中心继续游戏角色错误
**优先级**：P1  
**负责人**：FE  
**问题描述**：从个人中心点击"继续游戏"跳转后，角色不是当前存档的角色  
**根因**：`continueGame()` 函数只传递了 `session_id`，没有传递 `character_id`  
**修复方案**：
1. 修改 `frontend/src/views/PersonalCenterView.vue` 的 `continueGame()` 函数
2. 从 `latestSave` 中获取 `character_id` 并添加到路由参数
3. 确保 `LatestSave` 类型定义包含 `character_id` 字段

**验收标准**：
- 继续游戏跳转后，游戏页面显示的角色与存档时一致
- URL 参数包含 `session_id` 和 `character_id`

**允许写入范围**：
- `frontend/src/views/PersonalCenterView.vue`
- `frontend/src/types/personal-center.ts`（如需更新类型定义）

**验证方式**：
1. 在个人中心查看"继续游玩"卡片显示的角色
2. 点击"继续游戏"跳转
3. 验证游戏页面左侧角色信息与存档一致

**回滚方案**：git revert

---

#### T-032-FE-002: 修复剧本游戏左侧头像显示异常
**优先级**：P2  
**负责人**：FE  
**问题描述**：新角色没有头像时，显示的是图片占位符而不是角色名首字母  
**期望行为**：无头像时显示默认头像（角色名称首字母）  
**根因**：`playerCharacterAvatar` 计算属性的 fallback 逻辑有问题  
**修复方案**：
1. 检查 `frontend/src/views/GameView.vue` 的 `playerCharacterAvatar` 计算属性
2. 确保优先使用 `characterDetail.avatar_url`
3. 如果 `avatar_url` 为空，返回空字符串让 `CharacterInfo.vue` 显示首字母
4. 检查 `CharacterInfo.vue` 的头像显示逻辑，确保无 `avatarUrl` 时显示首字母

**验收标准**：
- 有头像的角色显示头像图片
- 无头像的角色显示角色名首字母占位符

**允许写入范围**：
- `frontend/src/views/GameView.vue`
- `frontend/src/components/CharacterInfo.vue`

**验证方式**：
1. 选择一个没有头像的角色开始游戏
2. 检查左侧角色信息区域的头像显示
3. 验证显示的是角色名首字母而非图片占位符

**回滚方案**：git revert

---

#### T-032-FE-003: 修复自由对话角色错误
**优先级**：P1  
**负责人**：FE  
**问题描述**：剧本游戏中点击"自由对话"跳转后，对话对象是主角而非当前 NPC 角色  
**根因**：`goToFreeChat()` 传递的 `characterId` 可能不正确  
**修复方案**：
1. 检查 `frontend/src/views/GameView.vue` 的 `goToFreeChat()` 函数
2. 确保传递的是当前对话的 NPC 角色 ID（`game.currentDialogue.character_id`）
3. 检查 `FreeChatView.vue` 是否正确接收和使用 `characterId` 参数
4. 验证自由对话 API 调用时使用的是正确的角色 ID

**验收标准**：
- 自由对话跳转后，对话对象是当前剧本中的 NPC 角色
- 不是玩家扮演的主角

**允许写入范围**：
- `frontend/src/views/GameView.vue`
- `frontend/src/views/FreeChatView.vue`（如需修复）

**验证方式**：
1. 在剧本游戏中与 NPC 对话
2. 点击"自由对话"按钮
3. 验证自由对话页面的对话对象是刚才的 NPC

**回滚方案**：git revert

---

#### T-032-FE-004: 修复赠送礼物弹框信息缺失
**优先级**：P2  
**负责人**：FE  
**问题描述**：
1. 赠送成功后弹框中没有显示当前好感度、剩余碎片、好感度变化
2. 角色详情页的"送礼记录"点击时查询所有角色的记录，而非当前角色
3. 送礼记录在游戏页面加载时就查询，而非点击时才查询

**修复方案**：

**问题 1：送礼成功弹框信息缺失**
1. 检查 `frontend/src/components/GiftModal.vue` 的送礼成功回调
2. 从 API 返回数据中提取 `new_affection_value`、`remaining_shards`、`affection_gained`
3. 在成功弹框中显示这些信息

**问题 2：送礼记录查询逻辑错误**
1. 检查角色详情页的送礼记录查询逻辑
2. 修改为只查询当前角色的送礼记录（传递 `character_id` 参数）
3. 修改 API 调用，使用 `gameApi.getCharacterGiftHistory(characterId)` 而非 `gameApi.getGiftHistory(sessionId)`

**问题 3：送礼记录查询时机错误**
1. 将送礼记录查询从页面加载时改为点击"送礼记录"按钮时
2. 使用懒加载方式，点击时才发起查询

**验收标准**：
- 送礼成功弹框显示：当前好感度、剩余碎片、好感度变化
- 角色详情页的送礼记录只显示当前角色的记录
- 送礼记录在点击按钮时才查询

**允许写入范围**：
- `frontend/src/components/GiftModal.vue`
- `frontend/src/views/CharacterDetailView.vue`（或角色详情相关组件）
- `frontend/src/views/GameView.vue`（送礼记录按钮逻辑）

**验证方式**：
1. 赠送礼物，检查成功弹框是否显示完整信息
2. 在角色详情页点击"送礼记录"，验证只显示该角色的记录
3. 检查网络请求，确认点击时才发起查询

**回滚方案**：git revert

---

### BE 任务

#### T-032-BE-001: 修复碎片兑换对话次数被错误重置
**优先级**：P0  
**负责人**：BE  
**问题描述**：每天 8 点重置时，用碎片兑换的额外对话次数也被清零  
**期望行为**：只重置每日免费对话次数（base_quota），碎片兑换的额外次数（fragment_extra）不应重置  
**根因**：`reset_all_daily_quotas()` 方法可能错误地重置了 `fragment_extra` 字段  
**修复方案**：
1. 检查 `backend/app/services/quota_service.py` 的 `reset_all_daily_quotas()` 方法
2. 确保只重置 `consumed` 字段（或创建新记录时 `consumed=0`）
3. 保留 `fragment_extra` 字段的值（不重置为 0）
4. 检查 `DialogueQuota` 模型，确认字段定义正确

**验收标准**：
- 每日重置后，用户的免费对话额度恢复（consumed 清零）
- 碎片兑换的额外对话次数保留（fragment_extra 不变）
- 用户的总可用对话次数 = base_quota - consumed + fragment_extra

**允许写入范围**：
- `backend/app/services/quota_service.py`
- `backend/app/models/dialogue_quota.py`（如需确认字段定义）

**验证方式**：
1. 用户用碎片兑换额外对话次数
2. 等待每日重置（或手动触发重置）
3. 检查用户的对话额度，验证 fragment_extra 保留

**回滚方案**：
1. git revert
2. 如有数据问题，执行数据修复脚本

---

## 任务依赖关系

```
T-032-FE-001 (继续游戏角色) ──┐
T-032-FE-002 (头像显示)    ──┤
T-032-FE-003 (自由对话)    ──┼──> QA 回归测试
T-032-FE-004 (送礼弹框)    ──┤
T-032-BE-001 (对话额度)    ──┘
```

所有任务可并行开发，无依赖关系。

---

## 开发进度跟踪

| 任务 ID | 状态 | 开始时间 | 完成时间 | 备注 |
|---------|------|----------|----------|------|
| T-032-FE-001 | ✅ 完成 | 2026-08-05 10:00 | 2026-08-05 10:30 | continueGame() 传递 character_id |
| T-032-FE-002 | ✅ 完成 | 2026-08-05 10:00 | 2026-08-05 10:25 | CR-031 已修复，playerCharacterAvatar 不走 sprites fallback |
| T-032-FE-003 | ✅ 完成 | 2026-08-05 10:00 | 2026-08-05 10:30 | goToFreeChat() 移除玩家角色 fallback |
| T-032-FE-004 | ✅ 完成 | 2026-08-05 10:00 | 2026-08-05 10:35 | GiftModal 字段映射 + 送礼记录按角色查询 |
| T-032-BE-001 | ✅ done | 2026-08-05 10:10 | 2026-08-05 10:20 | P0 已修复，carry_over 逻辑 |
