# CR-035 Tasks

## 任务分配

### FE 任务

#### T-035-FE-001: 角色切换后名称不更新
**优先级**：P1  
**负责人**：FE  
**状态**：✅ 已完成（二次修复）  
**问题描述**：StoryPanel 的 character-tag 显示的角色名称没有随角色切换更新  
**根因**：`characterDisplayName` 没有优先从 `gameStatus` 获取角色名  
**修复方案**：
1. `characterNameMap` 从 `ref<Map>` 改为 `reactive<Record>`（第一次修复）
2. `characterDisplayName` 优先使用 `gameStatus.value?.character_name`（第二次修复）

**修改文件**：
- `frontend/src/stores/game.ts`
- `frontend/src/views/GameView.vue`

**验收标准**：
- 角色切换后 character-tag 立即更新

---

#### T-035-FE-002: 选择项在 dialogue 加载时被清空
**优先级**：P1  
**负责人**：FE  
**状态**：✅ 已完成（二次修复）  
**问题描述**：choice 接口成功后，dialogue 接口还在加载，此时选择项为空  
**根因**：`submitChoice()` 清空了 `pendingChoices` + `ChoicePanel` 的 `v-if` 和 `v-else` 结构导致 loading 时选项列表隐藏  
**修复方案**：
1. `submitChoice()` 不清空 `pendingChoices`（第一次修复）
2. `ChoicePanel` 的 `v-if` 改为 `game.hasChoices || game.loading`（第二次修复）
3. `ChoicePanel` 内部 loading 从 `v-else` 改为同时显示，loading 在上方，选项列表保留
4. loading 时选项 disabled，防止重复点击

**修改文件**：
- `frontend/src/stores/game.ts`
- `frontend/src/views/GameView.vue`
- `frontend/src/components/ChoicePanel.vue`

**验收标准**：
- 选择项在 dialogue 加载时保留
- loading 显示在选择上方
- dialogue 返回后选择项更新

---

## 开发进度跟踪

| 任务 ID | 状态 | 开始时间 | 完成时间 | 备注 |
|---------|------|----------|----------|------|
| T-035-FE-001 | ✅ 完成 | 2026-08-05 10:42 | 2026-08-05 16:50 | 二次修复：characterDisplayName 优先使用 gameStatus |
| T-035-FE-002 | ✅ 完成 | 2026-08-05 10:42 | 2026-08-05 16:50 | 二次修复：ChoicePanel v-if + loading 结构 |
