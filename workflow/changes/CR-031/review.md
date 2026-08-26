# CR-031 Review

## 开发覆盖声明: BE 修复

### 任务信息

| 字段 | 值 |
|------|-----|
| 任务编号 | T-031-01a, T-031-02a |
| 任务名称 | BE: 修复 session 状态返回 + latest-save 角色 |
| 负责人 | be (isekai-wanderer-be) |
| 关联 AC | AC-031-001, AC-031-002 |
| 实际工时 | 0.5h |
| 完成时间 | 2026-08-05T09:35:00+08:00 |

### 已实现 AC

| AC | 描述 | 实现状态 | 测试状态 | 证据 |
|----|------|----------|----------|------|
| AC-031-001 | 继续游戏恢复正确角色 | ✅ 已修复 | ✅ 代码验证 | `backend/app/api/v1/game.py`, `backend/app/api/v1/users.py` |
| AC-031-002 | 好感度持久化 | ✅ 已验证 | ✅ 代码验证 | `affection_service.py` flush + `get_db()` commit |

### 已测试 AC

| 测试项 | 结果 |
|--------|------|
| `GET /game/{session_id}` 返回 character_id, script_id, route_id | ✅ 已添加 |
| `GET /users/me/latest-save` 使用 session.character_id | ✅ 已修复 |
| 好感度通过 SQLAlchemy session 自动持久化 | ✅ 已验证 |

### 未实现 AC

无

### 未测试 AC

| AC | 原因 |
|----|------|
| AC-031-003 | FE 任务，由 FE 修复 playerCharacterAvatar |

### 已运行命令

- 代码分析: grep/搜索确认数据流
- 无实际运行测试（需真实 DB + token）

### 失败命令

无

### 需要人工验收

- 实际运行中验证"继续游戏"跳转到正确角色
- 刷新页面后进度不丢失
- 新角色头像显示首字母

### 已知风险

1. `GET /game/{session_id}` 新增字段可能影响已有 FE 代码（但 FE 已通知）
2. `latest-save` 修复依赖 `session.character_id` 不为空（CR-028 已保证）

---

## 代码变更清单

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `backend/app/api/v1/game.py` | Modified | `get_game_session()` 添加 script_id, character_id, character_name, route_id 返回字段 |
| `backend/app/api/v1/users.py` | Modified | `get_latest_save()` 优先使用 session.character_id 获取角色信息 |

---

## 变更详情

### 1. `backend/app/api/v1/game.py`

**修改前**:
```python
return {
    "session_id": str(session.id),
    "status": session.status,
    "current_node_id": str(node.id) if node else None,
    "current_node": current_node_data,
    "is_ended": state["is_ended"],
    "ending_type": session.ending_type,
}
```

**修改后**:
```python
return {
    "session_id": str(session.id),
    "script_id": str(session.script_id) if session.script_id else None,
    "character_id": str(session.character_id) if session.character_id else None,
    "character_name": session.character_name,
    "route_id": str(session.route_id) if hasattr(session, 'route_id') and session.route_id else None,
    "status": session.status,
    "current_node_id": str(node.id) if node else None,
    "current_node": current_node_data,
    "is_ended": state["is_ended"],
    "ending_type": session.ending_type,
}
```

### 2. `backend/app/api/v1/users.py`

**修改前**:
```python
# Get first character from script
char_stmt = select(Character).where(Character.script_id == session.script_id).limit(1)
```

**修改后**:
```python
# BUG-031-001 fix: Use session.character_id (the player's chosen character)
character = None
if session.character_id:
    char_stmt = select(Character).where(Character.id == session.character_id)
    char_result = await db.execute(char_stmt)
    character = char_result.scalar_one_or_none()
if not character:
    char_stmt = select(Character).where(
        Character.script_id == session.script_id,
        Character.is_main == True
    ).limit(1)
    char_result = await db.execute(char_stmt)
    character = char_result.scalar_one_or_none()
if not character:
    char_stmt = select(Character).where(Character.script_id == session.script_id).limit(1)
    char_result = await db.execute(char_stmt)
    character = char_result.scalar_one_or_none()
```

---

## 开发覆盖声明: FE 修复

### 任务信息

| 字段 | 值 |
|------|-----|
| 任务编号 | T-031-01b, T-031-02b, T-031-03, T-031-04 |
| 任务名称 | FE: 修复游戏进度与角色显示 + 结局收集展示 |
| 负责人 | fe (isekai-wanderer-fe) |
| 关联 AC | AC-031-001, AC-031-002, AC-031-003, AC-031-004 |
| 实际工时 | 0.5h |
| 完成时间 | 2026-08-05T09:45:00+08:00 |

### 已实现 AC

| AC | 描述 | 实现状态 | 测试状态 | 证据 |
|----|------|----------|----------|------|
| AC-031-001 | 继续游戏恢复正确角色 | ✅ 已确认 | ✅ 代码验证 | `game.ts` resumeSession() 已调用 GET /game/:sessionId |
| AC-031-002 | 好感度持久化 | ✅ 已修复 | ✅ 代码验证 | `game.ts` submitChoice() 后调用 POST /game/auto-save |
| AC-031-003 | 无头像角色显示首字母 | ✅ 已修复 | ✅ 代码验证 | `GameView.vue` playerCharacterAvatar 移除 sprites fallback |
| AC-031-004 | 结局收集显示所有章节结局 | ✅ 已修复 | ✅ 代码验证 | `ScriptDetailView.vue` + `EndingList.vue` 改为传递 endings 数组 |

### 已测试 AC

| 测试项 | 结果 |
|--------|------|
| npm run build | ✅ 通过 (exit code 0) |
| TypeScript 类型检查 | ✅ 通过 |

### 未实现 AC

无

### 未测试 AC

| AC | 原因 |
|----|------|
| AC-031-001~004 | 需要真实浏览器 + 后端环境进行 E2E 验证 |

### 已运行命令

- `npm run build` - 通过
- `vue-tsc --noEmit` - 通过

### 失败命令

无

### 需要人工验收

- "继续游戏"跳转到正确角色
- 刷新页面后进度不丢失
- 新角色头像显示首字母
- 结局收集显示章节内所有结局

### 已知风险

1. auto-save 失败不阻塞游戏流程（fire-and-forget）
2. 结局展示改为显示所有章节结局，UI 布局可能需要视觉调整

---

## 代码变更清单 (FE)

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `frontend/src/stores/game.ts` | Modified | submitChoice() 后调用 POST /game/auto-save |
| `frontend/src/views/GameView.vue` | Modified | playerCharacterAvatar 移除 sprites fallback |
| `frontend/src/views/ScriptDetailView.vue` | Modified | chapterEndings 改为传递 endings 数组 |
| `frontend/src/components/EndingList.vue` | Modified | 适配新数据结构，显示章节内所有结局 |

---

## 变更详情 (FE)

### 1. `frontend/src/stores/game.ts`

**修改**: submitChoice() 成功后调用 auto-save

```typescript
// CR-031 BUG-031-002: 调用 auto-save API 持久化游戏进度
try {
  await api.post('/game/auto-save', {
    session_id: currentSession.value.id,
    node_id: currentSession.value.current_node_id,
    choice_id: choiceId,
  });
} catch (saveErr) {
  // auto-save 失败不应阻塞游戏流程，只记录警告
  console.warn('CR-031: auto-save failed:', saveErr);
}
```

### 2. `frontend/src/views/GameView.vue`

**修改前**:
```typescript
const playerCharacterAvatar = computed(() => {
  if (characterDetail.value?.avatar_url) {
    return characterDetail.value.avatar_url;
  }
  // Fallback to first sprite image if available
  const sprites = characterDetail.value?.sprites;
  if (sprites && sprites.length > 0 && sprites[0].image_url) {
    return sprites[0].image_url;
  }
  return '';
});
```

**修改后**:
```typescript
// CR-031 BUG-031-003: 只使用 avatar_url，不走 sprites fallback
const playerCharacterAvatar = computed(() => {
  return characterDetail.value?.avatar_url || '';
});
```

### 3. `frontend/src/views/ScriptDetailView.vue`

**修改前**:
```typescript
chapterEndings.value = Array.from(chapterMap.values())
  .sort((a, b) => a.chapterIndex - b.chapterIndex)
  .map(ch => {
    const displayEnding = ch.hasUnlocked 
      ? ch.endings.find(e => e.unlocked) || ch.endings[0]
      : ch.endings[0] || null;
    return {
      chapter: ch.chapter,
      chapterIndex: ch.chapterIndex,
      ending: displayEnding,
      unlocked: ch.hasUnlocked
    };
  });
```

**修改后**:
```typescript
// CR-031 T-031-04: 传递所有章节结局
chapterEndings.value = Array.from(chapterMap.values())
  .sort((a, b) => a.chapterIndex - b.chapterIndex)
  .map(ch => ({
    chapter: ch.chapter,
    chapterIndex: ch.chapterIndex,
    endings: ch.endings,
    unlockedCount: ch.endings.filter((e: any) => e.unlocked).length
  }));
```

### 4. `frontend/src/components/EndingList.vue`

**修改**: 适配新数据结构，显示章节内所有结局

```vue
<div v-for="(chapterData, index) in chapterEndings" :key="..." class="chapter-group">
  <div class="chapter-header">
    <span class="chapter-label">{{ chapterData.chapter }}</span>
    <span class="chapter-progress">{{ chapterData.unlockedCount }}/{{ chapterData.endings.length }} 结局</span>
  </div>
  <div class="endings-grid">
    <div v-for="ending in chapterData.endings" :key="ending.id" class="ending-item" ...>
      <!-- 每个结局独立显示 -->
    </div>
  </div>
</div>
```
