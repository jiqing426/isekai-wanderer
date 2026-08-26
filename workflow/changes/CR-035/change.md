# CR-035: 剧本游戏体验优化

## 变更类型
Bug 修复 + 体验优化

## 问题清单

### BUG-035-001: dialogue 接口响应过慢 (P0)
**现象**: GET /dialogue 接口耗时 40-55 秒
**根因**: preset 节点调用 AI 生成补充内容，LLM 响应慢
**影响**: 用户体验差，页面长时间 loading
**修复方案**: 
- 方案A: preset 节点不调用 AI，直接返回预设文本
- 方案B: AI 生成改为异步，先返回预设文本，再异步补充
- 方案C: 优化 LLM 调用，使用更快的模型或减少 token

### BUG-035-002: 角色切换后名称不更新 (P1)
**现象**: StoryPanel 的 character-tag 显示的角色名称没有随角色切换更新
**根因**: characterName prop 没有正确响应式更新
**修复方案**: 检查 GameView.vue 中 characterName 的计算逻辑

### BUG-035-003: 选择项在 dialogue 加载时被清空 (P1)
**现象**: choice 接口成功后，dialogue 接口还在加载，此时选择项为空
**根因**: handleChoice 中清空了 pendingChoices
**修复方案**: 保留上一次的选择项，loading 加到选择上面，dialogue 返回后再更新选择

### BUG-035-004: 章节结束后跳转回剧本大厅 (P0)
**现象**: 第一章节结束点击"继续下一章节"，跳转到 /discover
**根因**: handleNextChapter 中 nextChapterId 为空
**修复方案**: 检查后端是否正确返回 next_chapter 字段

### BUG-035-005: AI 回复内容不相关 (P1)
**现象**: AI 回复全是地球月球相关内容，与当前剧情不符
**根因**: AI 生成时缺少当前剧情上下文
**修复方案**: 优化 prompt，传入当前节点内容、角色信息、剧情背景

## 优先级
- P0: BUG-035-001, BUG-035-004
- P1: BUG-035-002, BUG-035-003, BUG-035-005

## 任务分配
- BE: BUG-035-001, BUG-035-004, BUG-035-005
- FE: BUG-035-002, BUG-035-003

## 验收标准
1. dialogue 接口响应时间 < 5 秒
2. 角色切换后 character-tag 立即更新
3. 选择项在 dialogue 加载时保留，loading 显示在选择上方
4. 章节结束后正确进入下一章节
5. AI 回复内容与当前剧情相关
