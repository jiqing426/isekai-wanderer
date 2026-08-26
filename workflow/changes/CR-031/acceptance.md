# CR-031 验收追踪

| 验收编号 | 需求编号 | 优先级 | 验收标准 | 覆盖状态 | 设计落点 | OpenSpec Task | 状态 |
|----------|----------|--------|----------|----------|----------|---------------|------|
| AC-031-001 | BUG-031-001 | P0 | 个人中心"继续游戏"跳转到正确的角色和进度节点 | covered | game.ts resumeSession | T-031-01 | FE Done |
| AC-031-002 | BUG-031-002 | P0 | 刷新页面后游戏进度不丢失，好感度正确保存 | covered | game.ts auto-save | T-031-02 | FE Done |
| AC-031-003 | BUG-031-003 | P1 | 无头像角色显示默认首字母头像，与现有角色一致 | covered | GameView.vue playerCharacterAvatar | T-031-03 | FE Done |
| AC-031-004 | BUG-031-004 | P1 | 剧本详情页同一章节多个结局全部展示，不只显示一个 | covered | ScriptDetailView.vue + EndingList.vue | T-031-04 | FE Done |
