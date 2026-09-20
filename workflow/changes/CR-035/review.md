# CR-035 Review

## 开发覆盖声明: FE 修复（二次修复）

### 任务信息

| 字段 | 值 |
|------|-----|
| 任务编号 | T-035-FE-001, T-035-FE-002 |
| 任务名称 | FE: 角色切换名称响应 + 选择项保留（二次修复） |
| 负责人 | fe (isekai-wanderer-fe) |
| 关联 AC | AC-035-001, AC-035-002 |
| 实际工时 | 0.5h（含二次修复） |
| 完成时间 | 2026-08-05T16:50:00+08:00 |

### 已实现 AC

| AC | 描述 | 实现状态 | 测试状态 | 证据 |
|----|------|----------|----------|------|
| AC-035-001 | 角色切换后 character-tag 立即更新 | ✅ 已修复 | ✅ 构建通过 | `GameView.vue` characterDisplayName 优先使用 gameStatus.character_name |
| AC-035-002 | 选择项在 dialogue 加载时保留 | ✅ 已修复 | ✅ 构建通过 | `ChoicePanel.vue` v-if 改为 hasChoices||loading，loading 在上方显示，选项列表保留 |

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
| AC-035-001~002 | 需要真实浏览器 + 后端环境进行 E2E 验证 |

### 已运行命令

| 命令 | 结果 |
|------|------|
| `npm run build` | ✅ PASSED |
| `vue-tsc --noEmit` | ✅ PASSED |

### 失败命令

无

### 需要人工验收

- 角色切换后 character-tag 立即更新
- 选择项在 dialogue 加载时保留，loading 显示在上方
- 新对话返回后选择项更新

### 已知风险

1. `gameStatus` 依赖 `/game/{session_id}/status` API 返回的 `character_name`，需确保后端返回正确
2. ChoicePanel loading 时选项列表保留，旧选项 disabled 防止重复点击

---

## 代码变更清单 (FE)

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `frontend/src/stores/game.ts` | Modified | characterNameMap 改为 reactive Record + 移除 pendingChoices 清空 |
| `frontend/src/views/GameView.vue` | Modified | characterDisplayName 优先使用 gameStatus + ChoicePanel v-if 改为 hasChoices\|\|loading |
| `frontend/src/components/ChoicePanel.vue` | Modified | loading 和选项列表同时显示，loading 时选项 disabled |

---

## 变更详情 (FE)

### 1. `frontend/src/views/GameView.vue` - characterDisplayName

**修改前**:
```typescript
const characterDisplayName = computed(() => {
  if (!game.currentDialogue?.character_id) return t('gameView.narrator');
  const cid = game.currentDialogue.character_id;
  const gameName = game.characterNameMap.get(cid);
  if (gameName) return gameName;
  const aff = affectionStore.getAffection(cid);
  if (aff?.character_name) return aff.character_name;
  return t('gameView.character');
});
```

**修改后**:
```typescript
const characterDisplayName = computed(() => {
  // CR-035: 优先使用 gameStatus 中的角色名
  if (gameStatus.value?.character_name) {
    return gameStatus.value.character_name;
  }
  if (game.currentDialogue?.character_id) {
    const cid = game.currentDialogue.character_id;
    const gameName = game.characterNameMap[cid];
    if (gameName) return gameName;
    const aff = affectionStore.getAffection(cid);
    if (aff?.character_name) return aff.character_name;
  }
  return t('gameView.narrator');
});
```

### 2. `frontend/src/views/GameView.vue` - ChoicePanel v-if

**修改前**:
```html
<ChoicePanel v-if="game.hasChoices" ... />
```

**修改后**:
```html
<ChoicePanel v-if="game.hasChoices || game.loading" ... />
```

### 3. `frontend/src/components/ChoicePanel.vue` - loading 结构

**修改前**:
```html
<div v-if="loading" class="choice-loading">...</div>
<div v-else class="choice-list">...</div>
```

**修改后**:
```html
<div v-if="loading" class="choice-loading">...</div>
<div class="choice-list">
  <!-- 选项始终渲染，loading 时 disabled -->
  <div :class="{ disabled: loading }" @click="handleSelect">...</div>
</div>
```

### 4. `frontend/src/components/ChoicePanel.vue` - handleSelect

**修改前**:
```typescript
function handleSelect(choice: Choice) {
  if (submitting.value || choice.locked) return;
```

**修改后**:
```typescript
function handleSelect(choice: Choice) {
  if (submitting.value || choice.locked || props.loading) return;
```

---

## QA 覆盖复核

| AC / BUG ID | 描述 | 开发覆盖 | QA 复核 | 测试证据 | 状态 |
|-------------|------|----------|---------|----------|------|
| AC-036-001 / BUG-036-001 | 社区帖子详情显示头像 | ✅ FE 已修复 | ✅ PASSED | Browser E2E + 代码审查: img + fallback 到首字母 | ✅ Verified |
| BUG-036-002 | 自由对话角色过滤 | ✅ BE 已修复 | ✅ PASSED | API: character_name=林辰; Browser: 自由对话显示林辰; 代码审查: get_free_chat_history 使用 game_session.character_id | ✅ Verified |
| BUG-036-003 | AI 对话异步接口 | ✅ BE 已修复 | ✅ PASSED | API: 22ms, 返回 {"text":"","emotion":"neutral"}; preset 节点不受影响 | ✅ Verified |

### QA 复核详情

**复核时间**: 2026-08-05 17:30 CST  
**复核人**: isekai-wanderer-qa

**复核方法**:
1. ✅ Delivery E2E / Runtime Smoke: 健康检查通过 + 前端 HTTP 200
2. ✅ API 集成测试: 3 个 BUG 修复均通过 API 验证
3. ✅ Browser Interaction E2E: 全部 4 个用例通过（含 CR-035 回归）

**测试证据**:
- 截图: test-results/cr036-001-01-community.png, cr036-002-01-free-chat.png, cr036-regression-01-game-page.png
- API: ai-dialogue 22ms, character_name=林辰, dialogue 26ms
- 代码审查: CommunityView img+fallback, get_free_chat_history character_id, ai-dialogue endpoint

**CR-035 回归**: ✅ dialogue 26ms, 角色名称显示, 选择面板正常

**测试结论**: ✅ ALL PASSED - 全部通过

---

## QA 覆盖复核

| AC / BUG ID | 描述 | 开发覆盖 | QA 复核 | 测试证据 | 状态 |
|-------------|------|----------|---------|----------|------|
| AC-035-001 / BUG-035-002 | 角色切换后名称立即更新 | ✅ FE 已修复 | ✅ PASSED | API: character_name=林辰; Browser: 角色标签显示"林辰"; 代码审查: characterDisplayName 优先 gameStatus | ✅ Verified |
| AC-035-002 / BUG-035-003 | 选择项在加载时保留 | ✅ FE 已修复 | ✅ PASSED | Browser: 2 个选择项可见; 代码审查: ChoicePanel v-if=hasChoices\|\|loading, 选项 disabled | ✅ Verified |
| BUG-035-001 | dialogue 接口响应速度 | ✅ BE 已修复 | ✅ PASSED | API: 32ms 响应时间 << 1 秒目标 | ✅ Verified |
| BUG-035-004 | 章节结束后跳转 | ✅ BE 已修复 | ✅ PASSED | API: chapter_number=1, chapter_type=encounter; 代码审查: 跳转逻辑已修复 | ✅ Verified |
| BUG-035-005 | AI 回复内容不相关 | ✅ BE 已修复 | ✅ PASSED | API: 对话内容含角色设定和场景描述; character_name=林辰, script_name=星辰之约 | ✅ Verified |

### QA 复核详情

**复核时间**: 2026-08-05 12:10 CST  
**复核人**: isekai-wanderer-qa

**复核方法**:
1. ✅ Delivery E2E / Runtime Smoke: 健康检查通过 + 前端 HTTP 200
2. ✅ API 集成测试: 5 个 BUG 修复均通过 API 验证
3. ✅ Browser Interaction E2E: 全部 5 个用例通过，含截图证据

**测试证据**:
- 截图: test-results/cr035-001-01-game-page.png ~ cr035-004-01-game-page.png
- API 响应: dialogue 32ms, character_name=林辰, chapter_number=1
- 代码审查: characterDisplayName 优先 gameStatus, ChoicePanel 保留选项

**额外发现**: CR-033 的 P0 缺陷（DEFECT-033-001: 剧本详情 API 500 错误）已修复并验证通过

**测试结论**: ✅ ALL PASSED - 全部通过
