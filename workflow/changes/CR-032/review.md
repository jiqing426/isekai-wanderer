# CR-032 Review

## 开发覆盖声明: T-032-BE-004

### 任务信息

| 字段 | 值 |
|------|-----|
| 任务编号 | T-032-BE-004 |
| 任务名称 | 修复碎片兑换对话次数被错误重置 |
| 负责人 | be (isekai-wanderer-be) |
| 关联 AC | AC-032-004 |
| 实际工时 | 0.5h |
| 完成时间 | 2026-08-05T10:20:00+08:00 |

### 已实现 AC

| AC | 描述 | 实现状态 | 测试状态 | 证据 |
|----|------|----------|----------|------|
| AC-032-004 | 碎片兑换对话次数次日保留 | ✅ 已实现 | ✅ 逻辑验证 | `backend/app/services/quota_service.py` |

### 已测试 AC

| 测试项 | 结果 |
|--------|------|
| 部分使用场景：extra=5, consumed=2 → carry_over=3 | ✅ PASSED |
| 全部使用场景：extra=5, consumed=5 → carry_over=0 | ✅ PASSED |
| 未购买场景：extra=0, consumed=0 → carry_over=0 | ✅ PASSED |

### 未实现 AC

无

### 未测试 AC

无

### 已运行命令

- 逻辑验证脚本: Python 单元测试通过

### 失败命令

无

### 需要人工验收

- 实际环境中用碎片兑换对话次数
- 等待次日重置（或手动触发）
- 验证 fragment_extra 保留

### 已知风险

1. 如果用户昨天没有 quota 记录（新用户），carry_over=0，行为正常
2. 如果昨天 quota 记录被删除，carry_over=0，行为正常

---

## 代码变更清单

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `backend/app/services/quota_service.py` | Modified | `_get_or_create_quota()` 添加 carry-over 逻辑 |
| `backend/app/services/quota_service.py` | Modified | `reset_all_daily_quotas()` 更新注释 |

---

## 变更详情

### `backend/app/services/quota_service.py`

**修改前**:
```python
if not quota:
    base_quota = await self.get_daily_base_quota(user_id)
    quota = DialogueQuota(
        user_id=user_id,
        date=today,
        base_quota=base_quota if base_quota != -1 else -1,
        consumed=0,
        fragment_extra=0,  # ❌ 每天重置为 0
        fragment_consumed=0,
    )
```

**修改后**:
```python
if not quota:
    base_quota = await self.get_daily_base_quota(user_id)
    
    # CR-032: Carry over unused fragment_extra from yesterday
    yesterday = today - timedelta(days=1)
    carry_over = 0
    y_stmt = select(DialogueQuota).where(
        and_(
            DialogueQuota.user_id == user_id,
            DialogueQuota.date == yesterday,
        )
    )
    y_result = await self.db.execute(y_stmt)
    y_quota = y_result.scalar_one_or_none()
    if y_quota:
        unused = y_quota.fragment_extra - y_quota.fragment_consumed
        carry_over = max(0, unused)
    
    quota = DialogueQuota(
        user_id=user_id,
        date=today,
        base_quota=base_quota if base_quota != -1 else -1,
        consumed=0,
        fragment_extra=carry_over,  # ✅ 保留未使用的碎片兑换次数
        fragment_consumed=0,
    )
```

---

## 开发覆盖声明: FE 修复

### 任务信息

| 字段 | 值 |
|------|-----|
| 任务编号 | T-032-FE-001, T-032-FE-002, T-032-FE-003, T-032-FE-004 |
| 任务名称 | FE: 修复继续游戏/自由对话/头像显示/送礼弹框 |
| 负责人 | fe (isekai-wanderer-fe) |
| 关联 AC | AC-032-001, AC-032-002, AC-032-003, AC-032-005 |
| 实际工时 | 0.5h |
| 完成时间 | 2026-08-05T10:36:00+08:00 |

### 已实现 AC

| AC | 描述 | 实现状态 | 测试状态 | 证据 |
|----|------|----------|----------|------|
| AC-032-001 | 继续游戏跳转后角色与存档一致 | ✅ 已修复 | ✅ 构建通过 | `PersonalCenterView.vue` continueGame() 传递 character_id |
| AC-032-002 | 无头像角色显示首字母占位符 | ✅ 已修复 | ✅ 构建通过 | CR-031 已修复，`GameView.vue` playerCharacterAvatar 不走 sprites fallback |
| AC-032-003 | 自由对话对象为当前 NPC 角色 | ✅ 已修复 | ✅ 构建通过 | `GameView.vue` goToFreeChat() 移除 player character fallback |
| AC-032-005 | 送礼弹框显示完整信息 + 记录按角色查询 | ✅ 已修复 | ✅ 构建通过 | `GiftModal.vue` 字段映射 + `GameView.vue` 按角色查询送礼记录 |

### 已测试 AC

| 测试项 | 结果 |
|--------|------|
| `npm run build` | ✅ PASSED (exit code 0) |
| TypeScript 类型检查 | ✅ PASSED |

### 未实现 AC

无

### 未测试 AC

| AC | 原因 |
|----|------|
| AC-032-001~003, AC-032-005 | 需要真实浏览器 + 后端环境进行 E2E 验证 |

### 已运行命令

| 命令 | 结果 |
|------|------|
| `npm run build` | ✅ PASSED |
| `vue-tsc --noEmit` | ✅ PASSED |

### 失败命令

无

### 需要人工验收

- 个人中心"继续游戏"跳转后角色正确
- 无头像角色显示首字母
- 自由对话对象为当前 NPC
- 送礼成功弹框显示好感度/碎片/变化
- 送礼记录只显示当前角色

### 已知风险

1. `goToFreeChat()` 当无 NPC 角色时提示用户而非跳转
2. `getCharacterGiftHistory()` 后端返回 `history` 字段，前端已映射为 `gifts`

---

## 代码变更清单 (FE)

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `frontend/src/types/personal-center.ts` | Modified | `LatestSave` 添加 `character_id` 字段 |
| `frontend/src/views/PersonalCenterView.vue` | Modified | `continueGame()` 传递 `character_id` |
| `frontend/src/views/GameView.vue` | Modified | `goToFreeChat()` 修复 NPC 角色 + `viewGiftHistory()` 按角色查询 |
| `frontend/src/components/GiftModal.vue` | Modified | 送礼成功结果字段映射 |
| `frontend/src/api/game.ts` | Modified | `getCharacterGiftHistory()` 字段映射 |

---

## 变更详情 (FE)

### 1. `frontend/src/types/personal-center.ts`
```typescript
// CR-032: LatestSave 添加 character_id
export interface LatestSave {
  // ...
  character_id: string;  // 新增
  // ...
}
```

### 2. `frontend/src/views/PersonalCenterView.vue`
```typescript
function continueGame() {
  if (latestSave.value) {
    const sessionId = latestSave.value.session_id;
    const characterId = latestSave.value.character_id;
    // CR-032: 传递 character_id 确保继续游戏时角色正确
    router.push(`/game?session=${sessionId}${characterId ? `&character_id=${characterId}` : ''}`);
  }
}
```

### 3. `frontend/src/views/GameView.vue` - goToFreeChat()
```typescript
function goToFreeChat() {
  // CR-032: 确保传递 NPC 角色 ID，不传递玩家角色 ID
  const npcCharacterId = game.currentDialogue?.character_id;
  if (!npcCharacterId) {
    message.warning('当前没有对话角色，无法开启自由对话');
    return;
  }
  router.push({
    path: `/game/${game.currentSession.id}/free-chat`,
    query: {
      character: characterDisplayName.value,
      characterId: npcCharacterId,  // 不再 fallback 到玩家角色
      scriptId: game.currentScript?.id,
    },
  });
}
```

### 4. `frontend/src/views/GameView.vue` - viewGiftHistory()
```typescript
async function viewGiftHistory() {
  // CR-032: 获取当前 NPC 角色的送礼记录
  const npcCharacterId = game.currentDialogue?.character_id || gameStatus.value?.character_id;
  // 使用角色专属 API
  const historyData = await gameApi.getCharacterGiftHistory(npcCharacterId);
}
```

### 5. `frontend/src/components/GiftModal.vue`
```typescript
// CR-032: 统一字段名映射
sendResult.value = {
  affection_gained: (result as any).affection_delta ?? (result as any).affection_gained ?? 0,
  new_affection_value: (result as any).new_affection ?? (result as any).new_affection_value ?? 0,
  remaining_shards: (result as any).remaining_fragments ?? (result as any).remaining_shards ?? ...,
};
```

### 6. `frontend/src/api/game.ts`
```typescript
// CR-032: 后端返回 history 字段，前端映射为 gifts
getCharacterGiftHistory(characterId: string) {
  return api.get<any>(`/characters/${characterId}/gift-history`).then((resp: any) => ({
    gifts: resp.history || resp.gifts || [],
    total: (resp.history || resp.gifts || []).length,
  }));
}
```
