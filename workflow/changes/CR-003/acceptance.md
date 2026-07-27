# CR-003 Acceptance Criteria Matrix

> PM 交付物：P0/P1 验收矩阵（REQ/AC 编号 + 优先级 + 可测试验收标准 + 覆盖状态）
> 验收动作标注：Browser E2E = 需 Playwright 浏览器交互验证；API/DB = 需真实后端状态验证；PWA = 需 Service Worker 推送验证

| 验收编号 | 需求编号 | 优先级 | 来源规格 | 验收标准 | 设计落点 | OpenSpec Task | 测试用例 / 验证命令 | 状态 | 覆盖状态 | 未覆盖原因 | PL 处理 |
|---------|---------|-------|---------|---------|---------|-------------|---------|------|---------|---------|-------|
| AC-DISC-001.1 | REQ-DISC-001 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/剧本发现与推荐/spec.md | 未登录用户访问 `/discover`，页面正常加载剧本列表；点击"开始游戏"跳转登录页 | D-001 DiscoverView + script_tags 表 | CR3-003, CR3-005 | test_discover_api.py, discover.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-DISC-001.2 | REQ-DISC-001 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/剧本发现与推荐/spec.md | 已登录用户访问 `/discover`，显示推荐区+分类筛选区+热度排行区三个逻辑区域 | D-001 DiscoverView + script_tags 表 | CR3-003, CR3-005 | test_discover_api.py, discover.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-DISC-001.3 | REQ-DISC-001 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/剧本发现与推荐/spec.md | 无剧本数据时，发现页显示空状态提示 | D-001 DiscoverView + script_tags 表 | CR3-003, CR3-005 | test_discover_api.py, discover.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-DISC-002.1 | REQ-DISC-002 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/剧本发现与推荐/spec.md | 有行为数据用户在推荐区看到"因为你玩了《XX》"等可解释推荐理由的剧本卡片 | D-001 recommendation_service 规则引擎 | CR3-004 | test_recommendation.py | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-DISC-002.2 | REQ-DISC-002 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/剧本发现与推荐/spec.md | 新用户（无游玩记录）在推荐区看到热度最高的剧本（fallback 策略） | D-001 recommendation_service 规则引擎 | CR3-004 | test_recommendation.py | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-DISC-002.3 | REQ-DISC-002 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/剧本发现与推荐/spec.md | 无可推荐剧本时，推荐区显示"暂无推荐，快去探索剧本库" | D-001 recommendation_service 规则引擎 | CR3-004 | test_recommendation.py | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-DISC-003.1 | REQ-DISC-003 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/剧本发现与推荐/spec.md | 用户选择"恋爱"类型筛选后，列表只显示 `script_tags` 含 `genre=romance` 的剧本 | D-001 FilterBar + SortDropdown 组件 | CR3-003, CR3-005 | test_discover_api.py, discover.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-DISC-003.2 | REQ-DISC-003 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/剧本发现与推荐/spec.md | 用户选择"多结局"标签筛选后，列表只显示 `script_tags` 含 `theme=multiple_endings... | D-001 FilterBar + SortDropdown 组件 | CR3-003, CR3-005 | test_discover_api.py, discover.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-DISC-003.3 | REQ-DISC-003 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/剧本发现与推荐/spec.md | 用户选择"新手"难度筛选后，列表只显示 `scripts.difficulty='beginner'` 的剧本 | D-001 FilterBar + SortDropdown 组件 | CR3-003, CR3-005 | test_discover_api.py, discover.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-DISC-003.4 | REQ-DISC-003 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/剧本发现与推荐/spec.md | 用户同时选择"恋爱"+"HE"，列表显示同时满足两个条件的剧本（组合筛选） | D-001 FilterBar + SortDropdown 组件 | CR3-003, CR3-005 | test_discover_api.py, discover.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-DISC-003.5 | REQ-DISC-003 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/剧本发现与推荐/spec.md | 筛选无结果时，显示"无匹配剧本，试试其他筛选条件" | D-001 FilterBar + SortDropdown 组件 | CR3-003, CR3-005 | test_discover_api.py, discover.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-DISC-004.1 | REQ-DISC-004 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/剧本发现与推荐/spec.md | 用户点击"最多人玩"后，排行列表按 `script_stats.play_count` 降序显示 Top 10 | D-001 RankingList + script_stats 表 | CR3-003, CR3-005 | test_discover_api.py, discover.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-DISC-004.2 | REQ-DISC-004 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/剧本发现与推荐/spec.md | 用户点击"最高评分"后，排行列表按 `script_stats.rating` 降序显示 Top 10 | D-001 RankingList + script_stats 表 | CR3-003, CR3-005 | test_discover_api.py, discover.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-DISC-004.3 | REQ-DISC-004 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/剧本发现与推荐/spec.md | 用户点击"最多收藏"后，排行列表按 `script_stats.favorite_count` 降序显示 Top 10 | D-001 RankingList + script_stats 表 | CR3-003, CR3-005 | test_discover_api.py, discover.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-DISC-004.4 | REQ-DISC-004 | P2 | openspec/changes/CR-003-platform-expansion-20260723/specs/剧本发现与推荐/spec.md | 排行数据为空时，显示"暂无排行数据" | D-001 RankingList + script_stats 表 | CR3-003, CR3-005 | test_discover_api.py, discover.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-DISC-005.1 | REQ-DISC-005 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/剧本发现与推荐/spec.md | 有未完成 session 的用户访问首页，顶部显示大卡片：剧本封面+剧本名+最后节点名+"继续游戏"按钮 | D-001 ContinueCard + game_sessions 查询 | CR3-006 | continue_card.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-DISC-005.2 | REQ-DISC-005 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/剧本发现与推荐/spec.md | 用户有多个未完成 session 时，继续玩卡片显示 `updated_at` 最大的那条 session | D-001 ContinueCard + game_sessions 查询 | CR3-006 | continue_card.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-DISC-005.3 | REQ-DISC-005 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/剧本发现与推荐/spec.md | 用户所有 session 已完成时，首页不显示继续玩卡片，显示"重新开始"入口 | D-001 ContinueCard + game_sessions 查询 | CR3-006 | continue_card.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-DISC-005.4 | REQ-DISC-005 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/剧本发现与推荐/spec.md | 用户从未开始游戏时，首页显示"开始你的第一次冒险"引导 | D-001 ContinueCard + game_sessions 查询 | CR3-006 | continue_card.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-DISC-005.5 | REQ-DISC-005 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/剧本发现与推荐/spec.md | 用户点击"继续游戏"后，跳转到 `/game/:sessionId`，从上次节点继续 | D-001 ContinueCard + game_sessions 查询 | CR3-006 | continue_card.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-CHAR-001.1 | REQ-CHAR-001 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/角色卡片系统/spec.md | 用户访问 `/characters`，页面展示角色卡片网格，每张含立绘缩略图+角色名+所属剧本名 | D-002 CharactersView + character_profiles 表 | CR3-007, CR3-009 | test_character_api.py, characters.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-CHAR-001.2 | REQ-CHAR-001 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/角色卡片系统/spec.md | 已解锁角色显示彩色立绘；未解锁角色显示灰色剪影+"???" | D-002 CharactersView + character_profiles 表 | CR3-007, CR3-009 | test_character_api.py, characters.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-CHAR-001.3 | REQ-CHAR-001 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/角色卡片系统/spec.md | 用户点击已解锁角色进入详情页，显示：高清立绘+角色名+性格标签+背景故事+示例对话 | D-002 CharactersView + character_profiles 表 | CR3-007, CR3-009 | test_character_api.py, characters.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-CHAR-001.4 | REQ-CHAR-001 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/角色卡片系统/spec.md | 用户点击未解锁角色进入详情页，显示灰色立绘+"该角色尚未解锁"+所属剧本引导 | D-002 CharactersView + character_profiles 表 | CR3-007, CR3-009 | test_character_api.py, characters.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-CHAR-001.5 | REQ-CHAR-001 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/角色卡片系统/spec.md | 用户在搜索框输入关键词后，列表实时过滤显示匹配角色（按角色名/剧本名） | D-002 CharactersView + character_profiles 表 | CR3-007, CR3-009 | test_character_api.py, characters.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-CHAR-001.6 | REQ-CHAR-001 | P2 | openspec/changes/CR-003-platform-expansion-20260723/specs/角色卡片系统/spec.md | 数据库无角色数据时，显示"暂无角色数据"空状态 | D-002 CharactersView + character_profiles 表 | CR3-007, CR3-009 | test_character_api.py, characters.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-CHAR-002.1 | REQ-CHAR-002 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/角色卡片系统/spec.md | 用户在角色列表页点击"好感度排行"tab，显示角色列表按好感度降序，每行含角色名+好感度数值+等级标签 | D-002 AffectionRank + affection 聚合 | CR3-007, CR3-009 | test_character_api.py, characters.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-CHAR-002.2 | REQ-CHAR-002 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/角色卡片系统/spec.md | 用户无好感度记录时，排行显示"还没有与任何角色互动"引导 | D-002 AffectionRank + affection 聚合 | CR3-007, CR3-009 | test_character_api.py, characters.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-CHAR-002.3 | REQ-CHAR-002 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/角色卡片系统/spec.md | 用户与某角色好感度 ≥80 时，排行显示"羁绊"等级标签 | D-002 AffectionRank + affection 聚合 | CR3-007, CR3-009 | test_character_api.py, characters.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-CHAR-003.1 | REQ-CHAR-003 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/角色卡片系统/spec.md | 用户在角色详情页滑动到对话预览区域，显示 3-5 条示例对话（聊天气泡样式） | D-002 DialoguePreview 聊天气泡组件 | CR3-007, CR3-010 | test_character_api.py, dialogue_preview.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-CHAR-003.2 | REQ-CHAR-003 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/角色卡片系统/spec.md | 角色 `example_dialogue` 为空时，显示"暂无对话预览" | D-002 DialoguePreview 聊天气泡组件 | CR3-007, CR3-010 | test_character_api.py, dialogue_preview.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-CHAR-003.3 | REQ-CHAR-003 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/角色卡片系统/spec.md | 每条对话气泡含角色头像+角色名+对话文本（支持换行） | D-002 DialoguePreview 聊天气泡组件 | CR3-007, CR3-010 | test_character_api.py, dialogue_preview.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-CHAR-004.1 | REQ-CHAR-004 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/角色卡片系统/spec.md | 用户在角色详情页点击"关注"按钮，按钮变为"已关注"状态，`user_follows` 表新增记录 | D-002 FollowButton + user_follows 表 + PWA | CR3-008, CR3-011 | test_follows_api.py, follow_button.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-CHAR-004.2 | REQ-CHAR-004 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/角色卡片系统/spec.md | 用户点击"已关注"按钮后，按钮恢复"关注"状态，`user_follows` 表删除记录 | D-002 FollowButton + user_follows 表 + PWA | CR3-008, CR3-011 | test_follows_api.py, follow_button.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-CHAR-004.3 | REQ-CHAR-004 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/角色卡片系统/spec.md | 用户关注角色后，新剧本上线且包含该角色时，PWA 推送通知"你关注的角色 A 出现在新剧本《XX》中" | D-002 FollowButton + user_follows 表 + PWA | CR3-008, CR3-011 | test_follows_api.py, follow_button.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-CHAR-004.4 | REQ-CHAR-004 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/角色卡片系统/spec.md | 用户在"我的"页面查看关注列表，显示所有关注角色的卡片列表 | D-002 FollowButton + user_follows 表 + PWA | CR3-008, CR3-011 | test_follows_api.py, follow_button.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-CHAR-004.5 | REQ-CHAR-004 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/角色卡片系统/spec.md | 未登录用户点击关注按钮，跳转登录页 | D-002 FollowButton + user_follows 表 + PWA | CR3-008, CR3-011 | test_follows_api.py, follow_button.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SAVE-001.1 | REQ-SAVE-001 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/存档与多线路管理/spec.md | 用户访问 `/saves`，显示存档卡片列表，每张含剧本封面+剧本名+路线名+当前节点名+进度百分比+最后游玩时间 | D-003 SaveManagerView + save_snapshots 表 | CR3-012, CR3-015 | test_saves_api.py, save_manager.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SAVE-001.2 | REQ-SAVE-001 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/存档与多线路管理/spec.md | 存档列表默认按 `game_sessions.updated_at DESC` 排序 | D-003 SaveManagerView + save_snapshots 表 | CR3-012, CR3-015 | test_saves_api.py, save_manager.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SAVE-001.3 | REQ-SAVE-001 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/存档与多线路管理/spec.md | 用户点击重命名图标→输入新名称→确认后，存档名称更新，列表实时刷新 | D-003 SaveManagerView + save_snapshots 表 | CR3-012, CR3-015 | test_saves_api.py, save_manager.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SAVE-001.4 | REQ-SAVE-001 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/存档与多线路管理/spec.md | 重命名时清空名称→确认，显示"名称不能为空"错误提示，保存失败 | D-003 SaveManagerView + save_snapshots 表 | CR3-012, CR3-015 | test_saves_api.py, save_manager.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SAVE-001.5 | REQ-SAVE-001 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/存档与多线路管理/spec.md | 用户点击删除图标→确认删除后，存档从列表消失，后端记录删除 | D-003 SaveManagerView + save_snapshots 表 | CR3-012, CR3-015 | test_saves_api.py, save_manager.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SAVE-001.6 | REQ-SAVE-001 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/存档与多线路管理/spec.md | 点击删除后弹出确认弹窗"确定要删除？此操作不可恢复"，确认后才执行 | D-003 SaveManagerView + save_snapshots 表 | CR3-012, CR3-015 | test_saves_api.py, save_manager.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SAVE-001.7 | REQ-SAVE-001 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/存档与多线路管理/spec.md | 用户点击"继续游戏"后，跳转到 `/game/:sessionId`，从当前节点继续 | D-003 SaveManagerView + save_snapshots 表 | CR3-012, CR3-015 | test_saves_api.py, save_manager.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SAVE-001.8 | REQ-SAVE-001 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/存档与多线路管理/spec.md | 已完成存档（`status=completed`）显示"已通关"标签+"重新开始"按钮（替代"继续游戏"） | D-003 SaveManagerView + save_snapshots 表 | CR3-012, CR3-015 | test_saves_api.py, save_manager.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SAVE-001.9 | REQ-SAVE-001 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/存档与多线路管理/spec.md | 用户无存档时，显示"还没有存档，快去开始你的冒险吧"空状态 | D-003 SaveManagerView + save_snapshots 表 | CR3-012, CR3-015 | test_saves_api.py, save_manager.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SAVE-002.1 | REQ-SAVE-002 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/存档与多线路管理/spec.md | 用户对同一剧本有 2 个存档时，存档管理器按剧本分组显示，各含不同路线名和进度 | D-003 多线路限制 5 并发 + game_sessions 扩展 | CR3-012, CR3-015 | test_saves_api.py, save_manager.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SAVE-002.2 | REQ-SAVE-002 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/存档与多线路管理/spec.md | 用户在剧本详情页点击"开始新线路"，创建新 `game_session` 并进入路线选择 | D-003 多线路限制 5 并发 + game_sessions 扩展 | CR3-012, CR3-015 | test_saves_api.py, save_manager.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SAVE-002.3 | REQ-SAVE-002 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/存档与多线路管理/spec.md | 同一剧本已有 5 个存档时，尝试创建第 6 个，显示"最多 5 个存档"提示 | D-003 多线路限制 5 并发 + game_sessions 扩展 | CR3-012, CR3-015 | test_saves_api.py, save_manager.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SAVE-003.1 | REQ-SAVE-003 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/存档与多线路管理/spec.md | 用户在游戏中遇到 `node_type=choice` 节点并做出选择后，后端自动创建 `save_snapshots`... | D-003 SnapshotTimeline + ForkButton + snapshot_cleanup cron | CR3-013, CR3-016 | test_snapshot_api.py, test_snapshot_cleanup.py, snapshot_timeline.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SAVE-003.2 | REQ-SAVE-003 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/存档与多线路管理/spec.md | 用户在游戏中点击"创建快照"按钮，创建快照记录（`is_auto=false`），弹窗提示"快照创建成功" | D-003 SnapshotTimeline + ForkButton + snapshot_cleanup cron | CR3-013, CR3-016 | test_snapshot_api.py, test_snapshot_cleanup.py, snapshot_timeline.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SAVE-003.3 | REQ-SAVE-003 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/存档与多线路管理/spec.md | 用户在存档管理器展开快照时间线，显示按时间排序的快照列表，每个含节点名+创建时间+自动/手动标签 | D-003 SnapshotTimeline + ForkButton + snapshot_cleanup cron | CR3-013, CR3-016 | test_snapshot_api.py, test_snapshot_cleanup.py, snapshot_timeline.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SAVE-003.4 | REQ-SAVE-003 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/存档与多线路管理/spec.md | 用户点击快照的"从这里重新开始"，创建新 session（fork），复制 choice_history 到快照点，进入... | D-003 SnapshotTimeline + ForkButton + snapshot_cleanup cron | CR3-013, CR3-016 | test_snapshot_api.py, test_snapshot_cleanup.py, snapshot_timeline.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SAVE-003.5 | REQ-SAVE-003 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/存档与多线路管理/spec.md | 用户点击"固定"图标，快照标记为 `is_pinned=true`，不受自动清理影响 | D-003 SnapshotTimeline + ForkButton + snapshot_cleanup cron | CR3-013, CR3-016 | test_snapshot_api.py, test_snapshot_cleanup.py, snapshot_timeline.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SAVE-003.6 | REQ-SAVE-003 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/存档与多线路管理/spec.md | 30 天前的非 pinned 自动快照被定时任务删除；pinned 快照保留 | D-003 SnapshotTimeline + ForkButton + snapshot_cleanup cron | CR3-013, CR3-016 | test_snapshot_api.py, test_snapshot_cleanup.py, snapshot_timeline.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SAVE-003.7 | REQ-SAVE-003 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/存档与多线路管理/spec.md | 7 天内过期的快照显示"将在 X 天后自动清理"警告+"固定"快捷按钮 | D-003 SnapshotTimeline + ForkButton + snapshot_cleanup cron | CR3-013, CR3-016 | test_snapshot_api.py, test_snapshot_cleanup.py, snapshot_timeline.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SAVE-004.1 | REQ-SAVE-004 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/存档与多线路管理/spec.md | 用户在存档管理器或剧本详情页查看结局进度，显示"已解锁结局 X/Y"进度条+已解锁结局名称列表 | D-003 EndingProgress + ending_progress 表 | CR3-014, CR3-017 | test_ending_progress_api.py, ending_progress.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SAVE-004.2 | REQ-SAVE-004 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/存档与多线路管理/spec.md | 用户在游戏中到达结局节点时，`ending_progress` 表更新，新结局加入 `unlocked_endings` | D-003 EndingProgress + ending_progress 表 | CR3-014, CR3-017 | test_ending_progress_api.py, ending_progress.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SAVE-004.3 | REQ-SAVE-004 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/存档与多线路管理/spec.md | 用户解锁某剧本所有结局后，显示"🎉 全部结局已收集！"+特殊徽章或动画 | D-003 EndingProgress + ending_progress 表 | CR3-014, CR3-017 | test_ending_progress_api.py, ending_progress.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SAVE-004.4 | REQ-SAVE-004 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/存档与多线路管理/spec.md | 用户在结局进度页查看未解锁结局，显示灰色占位卡片+解锁条件提示 | D-003 EndingProgress + ending_progress 表 | CR3-014, CR3-017 | test_ending_progress_api.py, ending_progress.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SAVE-004.5 | REQ-SAVE-004 | P2 | openspec/changes/CR-003-platform-expansion-20260723/specs/存档与多线路管理/spec.md | 剧本未定义结局时，显示"该剧本暂无结局收集" | D-003 EndingProgress + ending_progress 表 | CR3-014, CR3-017 | test_ending_progress_api.py, ending_progress.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SHARD-001.1 | REQ-SHARD-001 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/碎片经济可视化/spec.md | 用户访问 `/shards`，页面顶部显示当前碎片余额（大字体数字）+碎片图标 | D-004 ShardCenterView + fragments 复用 | CR3-018, CR3-019 | test_shard_api.py, shard_center.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SHARD-001.2 | REQ-SHARD-001 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/碎片经济可视化/spec.md | 碎片中心显示 4 种用途卡片：解锁章节/购买装扮/抽卡/赠送礼物，每张含图标+名称+说明 | D-004 ShardCenterView + fragments 复用 | CR3-018, CR3-019 | test_shard_api.py, shard_center.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SHARD-001.3 | REQ-SHARD-001 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/碎片经济可视化/spec.md | 用户点击用途卡片（如"解锁章节"）后，跳转到 `/discover` | D-004 ShardCenterView + fragments 复用 | CR3-018, CR3-019 | test_shard_api.py, shard_center.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SHARD-001.4 | REQ-SHARD-001 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/碎片经济可视化/spec.md | 未登录用户访问 `/shards`，跳转登录页 | D-004 ShardCenterView + fragments 复用 | CR3-018, CR3-019 | test_shard_api.py, shard_center.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SHARD-002.1 | REQ-SHARD-002 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/碎片经济可视化/spec.md | 用户在消费记录 tab 看到交易列表，每行含：时间+类型（获得/消费）+数量（+N/-N）+来源说明 | D-004 TransactionList + fragment_transactions 复用 | CR3-018, CR3-019 | test_shard_api.py, shard_center.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SHARD-002.2 | REQ-SHARD-002 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/碎片经济可视化/spec.md | 用户选择"最近 7 天"筛选后，列表只显示 7 天内的交易记录 | D-004 TransactionList + fragment_transactions 复用 | CR3-018, CR3-019 | test_shard_api.py, shard_center.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SHARD-002.3 | REQ-SHARD-002 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/碎片经济可视化/spec.md | 用户选择"仅消费"筛选后，列表只显示消费类型（数量为负）的交易 | D-004 TransactionList + fragment_transactions 复用 | CR3-018, CR3-019 | test_shard_api.py, shard_center.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SHARD-002.4 | REQ-SHARD-002 | P2 | openspec/changes/CR-003-platform-expansion-20260723/specs/碎片经济可视化/spec.md | 用户无交易记录时，显示"暂无交易记录" | D-004 TransactionList + fragment_transactions 复用 | CR3-018, CR3-019 | test_shard_api.py, shard_center.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SHARD-002.5 | REQ-SHARD-002 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/碎片经济可视化/spec.md | 交易记录超过 20 条时，滚动到底部加载更多（分页 20/page） | D-004 TransactionList + fragment_transactions 复用 | CR3-018, CR3-019 | test_shard_api.py, shard_center.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SHARD-003.1 | REQ-SHARD-003 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/碎片经济可视化/spec.md | 获取途径区域显示 4 种途径卡片：每日签到/每日任务/邀请好友/充值，每张含图标+名称+说明+CTA 按钮 | D-004 AcquisitionGuide + 用途跳转路由 | CR3-018, CR3-019 | test_shard_api.py, shard_center.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SHARD-003.2 | REQ-SHARD-003 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/碎片经济可视化/spec.md | 用户点击"每日签到"CTA 后，跳转到签到页面 | D-004 AcquisitionGuide + 用途跳转路由 | CR3-018, CR3-019 | test_shard_api.py, shard_center.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SHARD-003.3 | REQ-SHARD-003 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/碎片经济可视化/spec.md | 用户点击"每日任务"CTA 后，滚动到首页任务面板 | D-004 AcquisitionGuide + 用途跳转路由 | CR3-018, CR3-019 | test_shard_api.py, shard_center.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SHARD-003.4 | REQ-SHARD-003 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/碎片经济可视化/spec.md | 用户点击"邀请好友"CTA 后，触发 PWA share（复用 Web Share API） | D-004 AcquisitionGuide + 用途跳转路由 | CR3-018, CR3-019 | test_shard_api.py, shard_center.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-SHARD-003.5 | REQ-SHARD-003 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/碎片经济可视化/spec.md | 用户点击"充值"CTA 后，跳转到 `/shop`（mock 支付页） | D-004 AcquisitionGuide + 用途跳转路由 | CR3-018, CR3-019 | test_shard_api.py, shard_center.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-ACH-001.1 | REQ-ACH-001 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/成就系统/spec.md | 系统启动后，`achievement_definitions` 表至少有 20 条成就定义，覆盖剧情/活跃/收集/隐藏四... | D-005 achievement_definitions 种子数据 + user_achievements 初始化 | CR3-020, CR3-022 | test_achievement_api.py, achievement.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-ACH-001.2 | REQ-ACH-001 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/成就系统/spec.md | 新用户注册后，`user_achievements` 自动创建所有成就的进度记录（`progress=0`） | D-005 achievement_definitions 种子数据 + user_achievements 初始化 | CR3-020, CR3-022 | test_achievement_api.py, achievement.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-ACH-001.3 | REQ-ACH-001 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/成就系统/spec.md | 按分类查询 `achievement_definitions`，四类（剧情/活跃/收集/隐藏）均可查到 | D-005 achievement_definitions 种子数据 + user_achievements 初始化 | CR3-020, CR3-022 | test_achievement_api.py, achievement.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-ACH-002.1 | REQ-ACH-002 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/成就系统/spec.md | 用户访问 `/achievements`，显示成就分类 tab（剧情/活跃/收集/隐藏）+成就卡片网格 | D-005 AchievementView + AchievementWall 组件 | CR3-020, CR3-022 | test_achievement_api.py, test_achievement_triggers.py, achievement.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-ACH-002.2 | REQ-ACH-002 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/成就系统/spec.md | 用户点击"剧情"tab，显示剧情类成就列表，已解锁显示金色+解锁时间，未解锁显示灰色+进度条 | D-005 AchievementView + AchievementWall 组件 | CR3-020, CR3-022 | test_achievement_api.py, test_achievement_triggers.py, achievement.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-ACH-002.3 | REQ-ACH-002 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/成就系统/spec.md | 未解锁的隐藏成就显示"???" +锁图标，不显示名称和条件；已解锁显示完整信息 | D-005 AchievementView + AchievementWall 组件 | CR3-020, CR3-022 | test_achievement_api.py, test_achievement_triggers.py, achievement.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-ACH-002.4 | REQ-ACH-002 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/成就系统/spec.md | 成就目标为"通关 3 个剧本"且用户已通关 1 个时，显示进度条 1/3 (33%) | D-005 AchievementView + AchievementWall 组件 | CR3-020, CR3-022 | test_achievement_api.py, test_achievement_triggers.py, achievement.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-ACH-002.5 | REQ-ACH-002 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/成就系统/spec.md | 成就墙顶部显示"已解锁 X/Y 个成就 (Z%)"总进度 | D-005 AchievementView + AchievementWall 组件 | CR3-020, CR3-022 | test_achievement_api.py, test_achievement_triggers.py, achievement.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-ACH-002.6 | REQ-ACH-002 | P2 | openspec/changes/CR-003-platform-expansion-20260723/specs/成就系统/spec.md | 新用户首次访问成就墙，所有成就显示为灰色待解锁，进度 0% | D-005 AchievementView + AchievementWall 组件 | CR3-020, CR3-022 | test_achievement_api.py, test_achievement_triggers.py, achievement.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-ACH-003.1 | REQ-ACH-003 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/成就系统/spec.md | 用户完成一个剧本后，`user_achievements` 中剧情类进度 +1；达到 `target_count` 则标... | D-005 achievement_service 事件触发 + Redis 缓存 | CR3-020, CR3-021, CR3-022 | test_achievement_api.py, test_achievement_triggers.py, achievement.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-ACH-003.2 | REQ-ACH-003 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/成就系统/spec.md | 用户连续签到 7 天后，`user_achievements` 中 `ACTIVE_STREAK_7` 标记解锁 | D-005 achievement_service 事件触发 + Redis 缓存 | CR3-020, CR3-021, CR3-022 | test_achievement_api.py, test_achievement_triggers.py, achievement.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-ACH-003.3 | REQ-ACH-003 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/成就系统/spec.md | 用户解锁一张 CG 后，`user_achievements` 中收集类进度 +1 | D-005 achievement_service 事件触发 + Redis 缓存 | CR3-020, CR3-021, CR3-022 | test_achievement_api.py, test_achievement_triggers.py, achievement.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-ACH-003.4 | REQ-ACH-003 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/成就系统/spec.md | 用户连续选择"沉默"3 次后，隐藏成就 `HIDDEN_SILENT_3` 解锁 | D-005 achievement_service 事件触发 + Redis 缓存 | CR3-020, CR3-021, CR3-022 | test_achievement_api.py, test_achievement_triggers.py, achievement.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-ACH-003.5 | REQ-ACH-003 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/成就系统/spec.md | 成就解锁时，FE 显示全局 toast/popup："🎉 成就解锁：XXX！奖励 N 碎片" | D-005 achievement_service 事件触发 + Redis 缓存 | CR3-020, CR3-021, CR3-022 | test_achievement_api.py, test_achievement_triggers.py, achievement.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-ACH-003.6 | REQ-ACH-003 | P0 | openspec/changes/CR-003-platform-expansion-20260723/specs/成就系统/spec.md | 成就已解锁后再次触发同一事件，`user_achievements.unlocked_at` 不变，不重复发放奖励 | D-005 achievement_service 事件触发 + Redis 缓存 | CR3-020, CR3-021, CR3-022 | test_achievement_api.py, test_achievement_triggers.py, achievement.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-ACH-004.1 | REQ-ACH-004 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/成就系统/spec.md | 用户在成就墙点击"领取"按钮后，碎片余额增加 `reward_amount`，`fragment_transaction... | D-005 claim API + fragments 余额增加 + fragment_transactions | CR3-021, CR3-022 | test_achievement_claim.py, achievement.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-ACH-004.2 | REQ-ACH-004 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/成就系统/spec.md | 成就奖励类型为 `title` 时，点击"领取"后用户 titles 列表新增该称号 | D-005 claim API + fragments 余额增加 + fragment_transactions | CR3-021, CR3-022 | test_achievement_claim.py, achievement.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-ACH-004.3 | REQ-ACH-004 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/成就系统/spec.md | 成就奖励已领取后，卡片显示"已领取"标签，按钮禁用 | D-005 claim API + fragments 余额增加 + fragment_transactions | CR3-021, CR3-022 | test_achievement_claim.py, achievement.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-ACH-004.4 | REQ-ACH-004 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/成就系统/spec.md | 用户有多个未领取成就时，点击"一键领取"后所有奖励一次性发放，余额累加 | D-005 claim API + fragments 余额增加 + fragment_transactions | CR3-021, CR3-022 | test_achievement_claim.py, achievement.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-ACH-004.5 | REQ-ACH-004 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/成就系统/spec.md | 网络异常时点击领取，显示"领取失败，请重试"，不扣减奖励 | D-005 claim API + fragments 余额增加 + fragment_transactions | CR3-021, CR3-022 | test_achievement_claim.py, achievement.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-TASK-001.1 | REQ-TASK-001 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/每日任务增强/spec.md | 用户访问首页，任务面板列出当日 3-5 个任务，每行含任务图标+描述+进度 (X/Y)+奖励碎片数 | D-006 TaskPanel + daily_tasks 扩展 | CR3-023, CR3-025 | test_daily_task_api.py, task_panel.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-TASK-001.2 | REQ-TASK-001 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/每日任务增强/spec.md | 任务类型包括：玩章节/签到/送礼物/观看对话预览/完成存档操作 | D-006 TaskPanel + daily_tasks 扩展 | CR3-023, CR3-025 | test_daily_task_api.py, task_panel.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-TASK-001.3 | REQ-TASK-001 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/每日任务增强/spec.md | 用户完成"玩一个章节"后，任务进度从 0/1 变为 1/1，状态变为"可领取" | D-006 TaskPanel + daily_tasks 扩展 | CR3-023, CR3-025 | test_daily_task_api.py, task_panel.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-TASK-001.4 | REQ-TASK-001 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/每日任务增强/spec.md | 任务状态"可领取"时点击"领取"按钮，碎片余额增加，`fragment_transactions` 新增记录 | D-006 TaskPanel + daily_tasks 扩展 | CR3-023, CR3-025 | test_daily_task_api.py, task_panel.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-TASK-001.5 | REQ-TASK-001 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/每日任务增强/spec.md | UTC 00:00 过后访问首页，任务列表重置为新任务，昨日未完成进度清零 | D-006 TaskPanel + daily_tasks 扩展 | CR3-023, CR3-025 | test_daily_task_api.py, task_panel.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-TASK-001.6 | REQ-TASK-001 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/每日任务增强/spec.md | 用户完成当日所有任务后，显示"🎉 今日任务全部完成！额外奖励 +25 碎片" | D-006 TaskPanel + daily_tasks 扩展 | CR3-023, CR3-025 | test_daily_task_api.py, task_panel.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-TASK-002.1 | REQ-TASK-002 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/每日任务增强/spec.md | 任务面板顶部显示进度条"已完成 X/Y 个任务"+百分比 | D-006 活跃度进度条 + activity_points | CR3-023, CR3-025 | test_daily_task_api.py, task_panel.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-TASK-002.2 | REQ-TASK-002 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/每日任务增强/spec.md | 用户完成一个任务并领取后，进度条实时更新（如从 2/5 变为 3/5） | D-006 活跃度进度条 + activity_points | CR3-023, CR3-025 | test_daily_task_api.py, task_panel.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-TASK-002.3 | REQ-TASK-002 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/每日任务增强/spec.md | 用户完成所有任务后，进度条满格（5/5 100%）+显示"全部完成！+25 碎片已发放" | D-006 活跃度进度条 + activity_points | CR3-023, CR3-025 | test_daily_task_api.py, task_panel.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-TASK-002.4 | REQ-TASK-002 | P2 | openspec/changes/CR-003-platform-expansion-20260723/specs/每日任务增强/spec.md | 当日未做任何任务时，进度条显示 0/5 (0%) | D-006 活跃度进度条 + activity_points | CR3-023, CR3-025 | test_daily_task_api.py, task_panel.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-TASK-002.5 | REQ-TASK-002 | P2 | openspec/changes/CR-003-platform-expansion-20260723/specs/每日任务增强/spec.md | 进度更新时平滑过渡动画（300ms ease-in-out） | D-006 活跃度进度条 + activity_points | CR3-023, CR3-025 | test_daily_task_api.py, task_panel.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-TASK-003.1 | REQ-TASK-003 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/每日任务增强/spec.md | 任务面板活跃度区域显示活跃度进度条+宝箱图标（50/100/150 三个阈值） | D-006 ActivityChest + activity_chests 表 + UTC 日切割 | CR3-024, CR3-026 | test_activity_api.py, activity_chest.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-TASK-003.2 | REQ-TASK-003 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/每日任务增强/spec.md | 用户完成任务获得活跃度后，活跃度进度条增加 | D-006 ActivityChest + activity_chests 表 + UTC 日切割 | CR3-024, CR3-026 | test_activity_api.py, activity_chest.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-TASK-003.3 | REQ-TASK-003 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/每日任务增强/spec.md | 活跃度达到 50 时，第一个宝箱图标亮起+"可领取"标签+全局 toast"🎁 活跃度宝箱已解锁！" | D-006 ActivityChest + activity_chests 表 + UTC 日切割 | CR3-024, CR3-026 | test_activity_api.py, activity_chest.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-TASK-003.4 | REQ-TASK-003 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/每日任务增强/spec.md | 用户点击可领取宝箱后，弹出开箱动画（2 秒）+显示奖励内容（如"+15 碎片"）+`activity_chests.cl... | D-006 ActivityChest + activity_chests 表 + UTC 日切割 | CR3-024, CR3-026 | test_activity_api.py, activity_chest.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-TASK-003.5 | REQ-TASK-003 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/每日任务增强/spec.md | 宝箱领取成功后，`fragments.balance` 增加，`fragment_transactions` 新增 `t... | D-006 ActivityChest + activity_chests 表 + UTC 日切割 | CR3-024, CR3-026 | test_activity_api.py, activity_chest.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-TASK-003.6 | REQ-TASK-003 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/每日任务增强/spec.md | 宝箱已领取后，图标变灰色+"已领取"标签 | D-006 ActivityChest + activity_chests 表 + UTC 日切割 | CR3-024, CR3-026 | test_activity_api.py, activity_chest.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-TASK-003.7 | REQ-TASK-003 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/每日任务增强/spec.md | UTC 00:00 过后，活跃度归零，宝箱状态重置为未解锁 | D-006 ActivityChest + activity_chests 表 + UTC 日切割 | CR3-024, CR3-026 | test_activity_api.py, activity_chest.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-TASK-003.8 | REQ-TASK-003 | P2 | openspec/changes/CR-003-platform-expansion-20260723/specs/每日任务增强/spec.md | 活跃度 < 50 时，宝箱图标灰色+"还需 X 活跃度"提示 | D-006 ActivityChest + activity_chests 表 + UTC 日切割 | CR3-024, CR3-026 | test_activity_api.py, activity_chest.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-TASK-004.1 | REQ-TASK-004 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/每日任务增强/spec.md | 用户访问首页，任务面板默认收起，显示"每日任务 (X/Y)"标题+进度条摘要 | D-006 动画资源 + TaskItem 交互动效 | CR3-027 | animations.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-TASK-004.2 | REQ-TASK-004 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/每日任务增强/spec.md | 用户点击面板标题后，面板展开，显示完整任务列表+活跃度进度+宝箱 | D-006 动画资源 + TaskItem 交互动效 | CR3-027 | animations.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-TASK-004.3 | REQ-TASK-004 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/每日任务增强/spec.md | 面板已展开时点击标题或空白区，面板收起 | D-006 动画资源 + TaskItem 交互动效 | CR3-027 | animations.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-TASK-004.4 | REQ-TASK-004 | P2 | openspec/changes/CR-003-platform-expansion-20260723/specs/每日任务增强/spec.md | 任务完成时，任务行播放"✓"打勾动画（500ms）+碎片飞入动效 | D-006 动画资源 + TaskItem 交互动效 | CR3-027 | animations.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-TASK-004.5 | REQ-TASK-004 | P2 | openspec/changes/CR-003-platform-expansion-20260723/specs/每日任务增强/spec.md | 用户点击可领取宝箱后，宝箱摇晃（500ms）→打开（1s）→金光特效（500ms）→显示奖励 | D-006 动画资源 + TaskItem 交互动效 | CR3-027 | animations.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |
| AC-TASK-004.6 | REQ-TASK-004 | P1 | openspec/changes/CR-003-platform-expansion-20260723/specs/每日任务增强/spec.md | 移动端查看任务面板，面板全屏展示，任务列表垂直排列，宝箱图标横向排列 | D-006 动画资源 + TaskItem 交互动效 | CR3-027 | animations.spec.ts | Designed | not_covered | REQ_GATE 后覆盖 | 待 DEVELOPMENT |

---

## 模块 1：剧本发现与推荐系统（P0）

| REQ | AC | 优先级 | 验收标准 | 验收动作 | 覆盖状态 |
|-----|----|----|----------|---------|---------|
| REQ-DISC-001 | AC-DISC-001.1 | P0 | 未登录用户访问 `/discover`，页面正常加载剧本列表；点击"开始游戏"跳转登录页 | Browser E2E | not_covered |
| REQ-DISC-001 | AC-DISC-001.2 | P0 | 已登录用户访问 `/discover`，显示推荐区+分类筛选区+热度排行区三个逻辑区域 | Browser E2E | not_covered |
| REQ-DISC-001 | AC-DISC-001.3 | P1 | 无剧本数据时，发现页显示空状态提示 | Browser E2E | not_covered |
| REQ-DISC-002 | AC-DISC-002.1 | P0 | 有行为数据用户在推荐区看到"因为你玩了《XX》"等可解释推荐理由的剧本卡片 | Browser E2E + API/DB | not_covered |
| REQ-DISC-002 | AC-DISC-002.2 | P0 | 新用户（无游玩记录）在推荐区看到热度最高的剧本（fallback 策略） | Browser E2E + API/DB | not_covered |
| REQ-DISC-002 | AC-DISC-002.3 | P1 | 无可推荐剧本时，推荐区显示"暂无推荐，快去探索剧本库" | Browser E2E | not_covered |
| REQ-DISC-003 | AC-DISC-003.1 | P0 | 用户选择"恋爱"类型筛选后，列表只显示 `script_tags` 含 `genre=romance` 的剧本 | Browser E2E + API/DB | not_covered |
| REQ-DISC-003 | AC-DISC-003.2 | P0 | 用户选择"多结局"标签筛选后，列表只显示 `script_tags` 含 `theme=multiple_endings` 的剧本 | Browser E2E + API/DB | not_covered |
| REQ-DISC-003 | AC-DISC-003.3 | P0 | 用户选择"新手"难度筛选后，列表只显示 `scripts.difficulty='beginner'` 的剧本 | Browser E2E + API/DB | not_covered |
| REQ-DISC-003 | AC-DISC-003.4 | P0 | 用户同时选择"恋爱"+"HE"，列表显示同时满足两个条件的剧本（组合筛选） | Browser E2E + API/DB | not_covered |
| REQ-DISC-003 | AC-DISC-003.5 | P1 | 筛选无结果时，显示"无匹配剧本，试试其他筛选条件" | Browser E2E | not_covered |
| REQ-DISC-004 | AC-DISC-004.1 | P1 | 用户点击"最多人玩"后，排行列表按 `script_stats.play_count` 降序显示 Top 10 | Browser E2E + API/DB | not_covered |
| REQ-DISC-004 | AC-DISC-004.2 | P1 | 用户点击"最高评分"后，排行列表按 `script_stats.rating` 降序显示 Top 10 | Browser E2E + API/DB | not_covered |
| REQ-DISC-004 | AC-DISC-004.3 | P1 | 用户点击"最多收藏"后，排行列表按 `script_stats.favorite_count` 降序显示 Top 10 | Browser E2E + API/DB | not_covered |
| REQ-DISC-004 | AC-DISC-004.4 | P2 | 排行数据为空时，显示"暂无排行数据" | Browser E2E | not_covered |
| REQ-DISC-005 | AC-DISC-005.1 | P0 | 有未完成 session 的用户访问首页，顶部显示大卡片：剧本封面+剧本名+最后节点名+"继续游戏"按钮 | Browser E2E + API/DB | not_covered |
| REQ-DISC-005 | AC-DISC-005.2 | P0 | 用户有多个未完成 session 时，继续玩卡片显示 `updated_at` 最大的那条 session | Browser E2E + API/DB | not_covered |
| REQ-DISC-005 | AC-DISC-005.3 | P0 | 用户所有 session 已完成时，首页不显示继续玩卡片，显示"重新开始"入口 | Browser E2E | not_covered |
| REQ-DISC-005 | AC-DISC-005.4 | P1 | 用户从未开始游戏时，首页显示"开始你的第一次冒险"引导 | Browser E2E | not_covered |
| REQ-DISC-005 | AC-DISC-005.5 | P0 | 用户点击"继续游戏"后，跳转到 `/game/:sessionId`，从上次节点继续 | Browser E2E + API/DB | not_covered |

**模块 1 统计**：P0=10，P1=7，P2=1 | 覆盖状态：全部 not_covered

---

## 模块 2：角色卡片系统（P0）

| REQ | AC | 优先级 | 验收标准 | 验收动作 | 覆盖状态 |
|-----|----|----|----------|---------|---------|
| REQ-CHAR-001 | AC-CHAR-001.1 | P0 | 用户访问 `/characters`，页面展示角色卡片网格，每张含立绘缩略图+角色名+所属剧本名 | Browser E2E | not_covered |
| REQ-CHAR-001 | AC-CHAR-001.2 | P0 | 已解锁角色显示彩色立绘；未解锁角色显示灰色剪影+"???" | Browser E2E + API/DB | not_covered |
| REQ-CHAR-001 | AC-CHAR-001.3 | P0 | 用户点击已解锁角色进入详情页，显示：高清立绘+角色名+性格标签+背景故事+示例对话 | Browser E2E + API/DB | not_covered |
| REQ-CHAR-001 | AC-CHAR-001.4 | P1 | 用户点击未解锁角色进入详情页，显示灰色立绘+"该角色尚未解锁"+所属剧本引导 | Browser E2E | not_covered |
| REQ-CHAR-001 | AC-CHAR-001.5 | P0 | 用户在搜索框输入关键词后，列表实时过滤显示匹配角色（按角色名/剧本名） | Browser E2E | not_covered |
| REQ-CHAR-001 | AC-CHAR-001.6 | P2 | 数据库无角色数据时，显示"暂无角色数据"空状态 | Browser E2E | not_covered |
| REQ-CHAR-002 | AC-CHAR-002.1 | P0 | 用户在角色列表页点击"好感度排行"tab，显示角色列表按好感度降序，每行含角色名+好感度数值+等级标签 | Browser E2E + API/DB | not_covered |
| REQ-CHAR-002 | AC-CHAR-002.2 | P1 | 用户无好感度记录时，排行显示"还没有与任何角色互动"引导 | Browser E2E | not_covered |
| REQ-CHAR-002 | AC-CHAR-002.3 | P0 | 用户与某角色好感度 ≥80 时，排行显示"羁绊"等级标签 | Browser E2E + API/DB | not_covered |
| REQ-CHAR-003 | AC-CHAR-003.1 | P0 | 用户在角色详情页滑动到对话预览区域，显示 3-5 条示例对话（聊天气泡样式） | Browser E2E + API/DB | not_covered |
| REQ-CHAR-003 | AC-CHAR-003.2 | P1 | 角色 `example_dialogue` 为空时，显示"暂无对话预览" | Browser E2E | not_covered |
| REQ-CHAR-003 | AC-CHAR-003.3 | P0 | 每条对话气泡含角色头像+角色名+对话文本（支持换行） | Browser E2E | not_covered |
| REQ-CHAR-004 | AC-CHAR-004.1 | P0 | 用户在角色详情页点击"关注"按钮，按钮变为"已关注"状态，`user_follows` 表新增记录 | Browser E2E + API/DB | not_covered |
| REQ-CHAR-004 | AC-CHAR-004.2 | P0 | 用户点击"已关注"按钮后，按钮恢复"关注"状态，`user_follows` 表删除记录 | Browser E2E + API/DB | not_covered |
| REQ-CHAR-004 | AC-CHAR-004.3 | P0 | 用户关注角色后，新剧本上线且包含该角色时，PWA 推送通知"你关注的角色 A 出现在新剧本《XX》中" | PWA + API/DB | not_covered |
| REQ-CHAR-004 | AC-CHAR-004.4 | P1 | 用户在"我的"页面查看关注列表，显示所有关注角色的卡片列表 | Browser E2E | not_covered |
| REQ-CHAR-004 | AC-CHAR-004.5 | P0 | 未登录用户点击关注按钮，跳转登录页 | Browser E2E | not_covered |

**模块 2 统计**：P0=10，P1=4，P2=1 | 覆盖状态：全部 not_covered

---

## 模块 3：存档与多线路管理（P0）

| REQ | AC | 优先级 | 验收标准 | 验收动作 | 覆盖状态 |
|-----|----|----|----------|---------|---------|
| REQ-SAVE-001 | AC-SAVE-001.1 | P0 | 用户访问 `/saves`，显示存档卡片列表，每张含剧本封面+剧本名+路线名+当前节点名+进度百分比+最后游玩时间 | Browser E2E + API/DB | not_covered |
| REQ-SAVE-001 | AC-SAVE-001.2 | P0 | 存档列表默认按 `game_sessions.updated_at DESC` 排序 | Browser E2E + API/DB | not_covered |
| REQ-SAVE-001 | AC-SAVE-001.3 | P0 | 用户点击重命名图标→输入新名称→确认后，存档名称更新，列表实时刷新 | Browser E2E + API/DB | not_covered |
| REQ-SAVE-001 | AC-SAVE-001.4 | P1 | 重命名时清空名称→确认，显示"名称不能为空"错误提示，保存失败 | Browser E2E | not_covered |
| REQ-SAVE-001 | AC-SAVE-001.5 | P0 | 用户点击删除图标→确认删除后，存档从列表消失，后端记录删除 | Browser E2E + API/DB | not_covered |
| REQ-SAVE-001 | AC-SAVE-001.6 | P0 | 点击删除后弹出确认弹窗"确定要删除？此操作不可恢复"，确认后才执行 | Browser E2E | not_covered |
| REQ-SAVE-001 | AC-SAVE-001.7 | P0 | 用户点击"继续游戏"后，跳转到 `/game/:sessionId`，从当前节点继续 | Browser E2E + API/DB | not_covered |
| REQ-SAVE-001 | AC-SAVE-001.8 | P0 | 已完成存档（`status=completed`）显示"已通关"标签+"重新开始"按钮（替代"继续游戏"） | Browser E2E | not_covered |
| REQ-SAVE-001 | AC-SAVE-001.9 | P1 | 用户无存档时，显示"还没有存档，快去开始你的冒险吧"空状态 | Browser E2E | not_covered |
| REQ-SAVE-002 | AC-SAVE-002.1 | P0 | 用户对同一剧本有 2 个存档时，存档管理器按剧本分组显示，各含不同路线名和进度 | Browser E2E + API/DB | not_covered |
| REQ-SAVE-002 | AC-SAVE-002.2 | P0 | 用户在剧本详情页点击"开始新线路"，创建新 `game_session` 并进入路线选择 | Browser E2E + API/DB | not_covered |
| REQ-SAVE-002 | AC-SAVE-002.3 | P1 | 同一剧本已有 5 个存档时，尝试创建第 6 个，显示"最多 5 个存档"提示 | Browser E2E | not_covered |
| REQ-SAVE-003 | AC-SAVE-003.1 | P0 | 用户在游戏中遇到 `node_type=choice` 节点并做出选择后，后端自动创建 `save_snapshots` 记录（`is_auto=true`） | API/DB | not_covered |
| REQ-SAVE-003 | AC-SAVE-003.2 | P0 | 用户在游戏中点击"创建快照"按钮，创建快照记录（`is_auto=false`），弹窗提示"快照创建成功" | Browser E2E + API/DB | not_covered |
| REQ-SAVE-003 | AC-SAVE-003.3 | P0 | 用户在存档管理器展开快照时间线，显示按时间排序的快照列表，每个含节点名+创建时间+自动/手动标签 | Browser E2E + API/DB | not_covered |
| REQ-SAVE-003 | AC-SAVE-003.4 | P0 | 用户点击快照的"从这里重新开始"，创建新 session（fork），复制 choice_history 到快照点，进入该节点 | Browser E2E + API/DB | not_covered |
| REQ-SAVE-003 | AC-SAVE-003.5 | P0 | 用户点击"固定"图标，快照标记为 `is_pinned=true`，不受自动清理影响 | Browser E2E + API/DB | not_covered |
| REQ-SAVE-003 | AC-SAVE-003.6 | P0 | 30 天前的非 pinned 自动快照被定时任务删除；pinned 快照保留 | API/DB + 定时任务 | not_covered |
| REQ-SAVE-003 | AC-SAVE-003.7 | P1 | 7 天内过期的快照显示"将在 X 天后自动清理"警告+"固定"快捷按钮 | Browser E2E | not_covered |
| REQ-SAVE-004 | AC-SAVE-004.1 | P0 | 用户在存档管理器或剧本详情页查看结局进度，显示"已解锁结局 X/Y"进度条+已解锁结局名称列表 | Browser E2E + API/DB | not_covered |
| REQ-SAVE-004 | AC-SAVE-004.2 | P0 | 用户在游戏中到达结局节点时，`ending_progress` 表更新，新结局加入 `unlocked_endings` | API/DB | not_covered |
| REQ-SAVE-004 | AC-SAVE-004.3 | P1 | 用户解锁某剧本所有结局后，显示"🎉 全部结局已收集！"+特殊徽章或动画 | Browser E2E | not_covered |
| REQ-SAVE-004 | AC-SAVE-004.4 | P1 | 用户在结局进度页查看未解锁结局，显示灰色占位卡片+解锁条件提示 | Browser E2E | not_covered |
| REQ-SAVE-004 | AC-SAVE-004.5 | P2 | 剧本未定义结局时，显示"该剧本暂无结局收集" | Browser E2E | not_covered |

**模块 3 统计**：P0=17，P1=5，P2=1 | 覆盖状态：全部 not_covered

---

## 模块 4：碎片经济体系可视化（P1）

| REQ | AC | 优先级 | 验收标准 | 验收动作 | 覆盖状态 |
|-----|----|----|----------|---------|---------|
| REQ-SHARD-001 | AC-SHARD-001.1 | P1 | 用户访问 `/shards`，页面顶部显示当前碎片余额（大字体数字）+碎片图标 | Browser E2E + API/DB | not_covered |
| REQ-SHARD-001 | AC-SHARD-001.2 | P1 | 碎片中心显示 4 种用途卡片：解锁章节/购买装扮/抽卡/赠送礼物，每张含图标+名称+说明 | Browser E2E | not_covered |
| REQ-SHARD-001 | AC-SHARD-001.3 | P1 | 用户点击用途卡片（如"解锁章节"）后，跳转到 `/discover` | Browser E2E | not_covered |
| REQ-SHARD-001 | AC-SHARD-001.4 | P0 | 未登录用户访问 `/shards`，跳转登录页 | Browser E2E | not_covered |
| REQ-SHARD-002 | AC-SHARD-002.1 | P1 | 用户在消费记录 tab 看到交易列表，每行含：时间+类型（获得/消费）+数量（+N/-N）+来源说明 | Browser E2E + API/DB | not_covered |
| REQ-SHARD-002 | AC-SHARD-002.2 | P1 | 用户选择"最近 7 天"筛选后，列表只显示 7 天内的交易记录 | Browser E2E + API/DB | not_covered |
| REQ-SHARD-002 | AC-SHARD-002.3 | P1 | 用户选择"仅消费"筛选后，列表只显示消费类型（数量为负）的交易 | Browser E2E + API/DB | not_covered |
| REQ-SHARD-002 | AC-SHARD-002.4 | P2 | 用户无交易记录时，显示"暂无交易记录" | Browser E2E | not_covered |
| REQ-SHARD-002 | AC-SHARD-002.5 | P1 | 交易记录超过 20 条时，滚动到底部加载更多（分页 20/page） | Browser E2E | not_covered |
| REQ-SHARD-003 | AC-SHARD-003.1 | P1 | 获取途径区域显示 4 种途径卡片：每日签到/每日任务/邀请好友/充值，每张含图标+名称+说明+CTA 按钮 | Browser E2E | not_covered |
| REQ-SHARD-003 | AC-SHARD-003.2 | P1 | 用户点击"每日签到"CTA 后，跳转到签到页面 | Browser E2E | not_covered |
| REQ-SHARD-003 | AC-SHARD-003.3 | P1 | 用户点击"每日任务"CTA 后，滚动到首页任务面板 | Browser E2E | not_covered |
| REQ-SHARD-003 | AC-SHARD-003.4 | P1 | 用户点击"邀请好友"CTA 后，触发 PWA share（复用 Web Share API） | Browser E2E + PWA | not_covered |
| REQ-SHARD-003 | AC-SHARD-003.5 | P1 | 用户点击"充值"CTA 后，跳转到 `/shop`（mock 支付页） | Browser E2E | not_covered |

**模块 4 统计**：P0=1，P1=12，P2=1 | 覆盖状态：全部 not_covered

---

## 模块 5：成就系统（P1）

| REQ | AC | 优先级 | 验收标准 | 验收动作 | 覆盖状态 |
|-----|----|----|----------|---------|---------|
| REQ-ACH-001 | AC-ACH-001.1 | P1 | 系统启动后，`achievement_definitions` 表至少有 20 条成就定义，覆盖剧情/活跃/收集/隐藏四类 | API/DB | not_covered |
| REQ-ACH-001 | AC-ACH-001.2 | P1 | 新用户注册后，`user_achievements` 自动创建所有成就的进度记录（`progress=0`） | API/DB | not_covered |
| REQ-ACH-001 | AC-ACH-001.3 | P1 | 按分类查询 `achievement_definitions`，四类（剧情/活跃/收集/隐藏）均可查到 | API/DB | not_covered |
| REQ-ACH-002 | AC-ACH-002.1 | P1 | 用户访问 `/achievements`，显示成就分类 tab（剧情/活跃/收集/隐藏）+成就卡片网格 | Browser E2E | not_covered |
| REQ-ACH-002 | AC-ACH-002.2 | P1 | 用户点击"剧情"tab，显示剧情类成就列表，已解锁显示金色+解锁时间，未解锁显示灰色+进度条 | Browser E2E + API/DB | not_covered |
| REQ-ACH-002 | AC-ACH-002.3 | P1 | 未解锁的隐藏成就显示"???" +锁图标，不显示名称和条件；已解锁显示完整信息 | Browser E2E | not_covered |
| REQ-ACH-002 | AC-ACH-002.4 | P1 | 成就目标为"通关 3 个剧本"且用户已通关 1 个时，显示进度条 1/3 (33%) | Browser E2E + API/DB | not_covered |
| REQ-ACH-002 | AC-ACH-002.5 | P1 | 成就墙顶部显示"已解锁 X/Y 个成就 (Z%)"总进度 | Browser E2E + API/DB | not_covered |
| REQ-ACH-002 | AC-ACH-002.6 | P2 | 新用户首次访问成就墙，所有成就显示为灰色待解锁，进度 0% | Browser E2E | not_covered |
| REQ-ACH-003 | AC-ACH-003.1 | P1 | 用户完成一个剧本后，`user_achievements` 中剧情类进度 +1；达到 `target_count` 则标记 `unlocked_at` | API/DB | not_covered |
| REQ-ACH-003 | AC-ACH-003.2 | P1 | 用户连续签到 7 天后，`user_achievements` 中 `ACTIVE_STREAK_7` 标记解锁 | API/DB | not_covered |
| REQ-ACH-003 | AC-ACH-003.3 | P1 | 用户解锁一张 CG 后，`user_achievements` 中收集类进度 +1 | API/DB | not_covered |
| REQ-ACH-003 | AC-ACH-003.4 | P1 | 用户连续选择"沉默"3 次后，隐藏成就 `HIDDEN_SILENT_3` 解锁 | API/DB | not_covered |
| REQ-ACH-003 | AC-ACH-003.5 | P1 | 成就解锁时，FE 显示全局 toast/popup："🎉 成就解锁：XXX！奖励 N 碎片" | Browser E2E | not_covered |
| REQ-ACH-003 | AC-ACH-003.6 | P0 | 成就已解锁后再次触发同一事件，`user_achievements.unlocked_at` 不变，不重复发放奖励 | API/DB + 幂等性 | not_covered |
| REQ-ACH-004 | AC-ACH-004.1 | P1 | 用户在成就墙点击"领取"按钮后，碎片余额增加 `reward_amount`，`fragment_transactions` 新增 `type=achievement_reward` 记录 | Browser E2E + API/DB | not_covered |
| REQ-ACH-004 | AC-ACH-004.2 | P1 | 成就奖励类型为 `title` 时，点击"领取"后用户 titles 列表新增该称号 | Browser E2E + API/DB | not_covered |
| REQ-ACH-004 | AC-ACH-004.3 | P1 | 成就奖励已领取后，卡片显示"已领取"标签，按钮禁用 | Browser E2E | not_covered |
| REQ-ACH-004 | AC-ACH-004.4 | P1 | 用户有多个未领取成就时，点击"一键领取"后所有奖励一次性发放，余额累加 | Browser E2E + API/DB | not_covered |
| REQ-ACH-004 | AC-ACH-004.5 | P1 | 网络异常时点击领取，显示"领取失败，请重试"，不扣减奖励 | Browser E2E | not_covered |

**模块 5 统计**：P0=1，P1=18，P2=1 | 覆盖状态：全部 not_covered

---

## 模块 6：每日任务系统增强（P1）

| REQ | AC | 优先级 | 验收标准 | 验收动作 | 覆盖状态 |
|-----|----|----|----------|---------|---------|
| REQ-TASK-001 | AC-TASK-001.1 | P1 | 用户访问首页，任务面板列出当日 3-5 个任务，每行含任务图标+描述+进度 (X/Y)+奖励碎片数 | Browser E2E + API/DB | not_covered |
| REQ-TASK-001 | AC-TASK-001.2 | P1 | 任务类型包括：玩章节/签到/送礼物/观看对话预览/完成存档操作 | Browser E2E + API/DB | not_covered |
| REQ-TASK-001 | AC-TASK-001.3 | P1 | 用户完成"玩一个章节"后，任务进度从 0/1 变为 1/1，状态变为"可领取" | Browser E2E + API/DB | not_covered |
| REQ-TASK-001 | AC-TASK-001.4 | P1 | 任务状态"可领取"时点击"领取"按钮，碎片余额增加，`fragment_transactions` 新增记录 | Browser E2E + API/DB | not_covered |
| REQ-TASK-001 | AC-TASK-001.5 | P1 | UTC 00:00 过后访问首页，任务列表重置为新任务，昨日未完成进度清零 | API/DB + 定时任务 | not_covered |
| REQ-TASK-001 | AC-TASK-001.6 | P1 | 用户完成当日所有任务后，显示"🎉 今日任务全部完成！额外奖励 +25 碎片" | Browser E2E + API/DB | not_covered |
| REQ-TASK-002 | AC-TASK-002.1 | P1 | 任务面板顶部显示进度条"已完成 X/Y 个任务"+百分比 | Browser E2E | not_covered |
| REQ-TASK-002 | AC-TASK-002.2 | P1 | 用户完成一个任务并领取后，进度条实时更新（如从 2/5 变为 3/5） | Browser E2E + API/DB | not_covered |
| REQ-TASK-002 | AC-TASK-002.3 | P1 | 用户完成所有任务后，进度条满格（5/5 100%）+显示"全部完成！+25 碎片已发放" | Browser E2E + API/DB | not_covered |
| REQ-TASK-002 | AC-TASK-002.4 | P2 | 当日未做任何任务时，进度条显示 0/5 (0%) | Browser E2E | not_covered |
| REQ-TASK-002 | AC-TASK-002.5 | P2 | 进度更新时平滑过渡动画（300ms ease-in-out） | Browser E2E | not_covered |
| REQ-TASK-003 | AC-TASK-003.1 | P1 | 任务面板活跃度区域显示活跃度进度条+宝箱图标（50/100/150 三个阈值） | Browser E2E | not_covered |
| REQ-TASK-003 | AC-TASK-003.2 | P1 | 用户完成任务获得活跃度后，活跃度进度条增加 | Browser E2E + API/DB | not_covered |
| REQ-TASK-003 | AC-TASK-003.3 | P1 | 活跃度达到 50 时，第一个宝箱图标亮起+"可领取"标签+全局 toast"🎁 活跃度宝箱已解锁！" | Browser E2E + API/DB | not_covered |
| REQ-TASK-003 | AC-TASK-003.4 | P1 | 用户点击可领取宝箱后，弹出开箱动画（2 秒）+显示奖励内容（如"+15 碎片"）+`activity_chests.claimed=true` | Browser E2E + API/DB | not_covered |
| REQ-TASK-003 | AC-TASK-003.5 | P1 | 宝箱领取成功后，`fragments.balance` 增加，`fragment_transactions` 新增 `type=activity_chest` 记录 | API/DB | not_covered |
| REQ-TASK-003 | AC-TASK-003.6 | P1 | 宝箱已领取后，图标变灰色+"已领取"标签 | Browser E2E | not_covered |
| REQ-TASK-003 | AC-TASK-003.7 | P1 | UTC 00:00 过后，活跃度归零，宝箱状态重置为未解锁 | API/DB + 定时任务 | not_covered |
| REQ-TASK-003 | AC-TASK-003.8 | P2 | 活跃度 < 50 时，宝箱图标灰色+"还需 X 活跃度"提示 | Browser E2E | not_covered |
| REQ-TASK-004 | AC-TASK-004.1 | P1 | 用户访问首页，任务面板默认收起，显示"每日任务 (X/Y)"标题+进度条摘要 | Browser E2E | not_covered |
| REQ-TASK-004 | AC-TASK-004.2 | P1 | 用户点击面板标题后，面板展开，显示完整任务列表+活跃度进度+宝箱 | Browser E2E | not_covered |
| REQ-TASK-004 | AC-TASK-004.3 | P1 | 面板已展开时点击标题或空白区，面板收起 | Browser E2E | not_covered |
| REQ-TASK-004 | AC-TASK-004.4 | P2 | 任务完成时，任务行播放"✓"打勾动画（500ms）+碎片飞入动效 | Browser E2E | not_covered |
| REQ-TASK-004 | AC-TASK-004.5 | P2 | 用户点击可领取宝箱后，宝箱摇晃（500ms）→打开（1s）→金光特效（500ms）→显示奖励 | Browser E2E | not_covered |
| REQ-TASK-004 | AC-TASK-004.6 | P1 | 移动端查看任务面板，面板全屏展示，任务列表垂直排列，宝箱图标横向排列 | Browser E2E + 响应式 | not_covered |

**模块 6 统计**：P0=0，P1=20，P2=4 | 覆盖状态：全部 not_covered

---

## 汇总统计

| 模块 | P0 | P1 | P2 | 合计 |
|------|----|----|----|-----|
| 1. 剧本发现与推荐 | 10 | 7 | 1 | 18 |
| 2. 角色卡片系统 | 10 | 4 | 1 | 15 |
| 3. 存档与多线路管理 | 17 | 5 | 1 | 23 |
| 4. 碎片经济可视化 | 1 | 12 | 1 | 14 |
| 5. 成就系统 | 1 | 18 | 1 | 20 |
| 6. 每日任务增强 | 0 | 20 | 4 | 24 |
| **合计** | **39** | **66** | **9** | **114** |

**全部覆盖状态**：not_covered（待 REQ_GATE 后进入 DESIGN → DEVELOPMENT → QA 覆盖）

## 验收约束汇总

| 验收类型 | 数量 | 说明 |
|---------|------|------|
| Browser E2E | 98 | 需 Playwright 浏览器交互验证（页面跳转/筛选/按钮/动效） |
| API/DB | 72 | 需真实后端状态验证（数据创建/查询/更新/删除） |
| PWA | 2 | 需 Service Worker 推送验证（角色关注通知/分享） |
| 定时任务 | 4 | 需 BE 定时任务日志验证（快照清理/任务刷新/宝箱重置） |
| 幂等性 | 2 | 需 BE 单元测试覆盖（重复事件不重复解锁/不重复发放） |

> **注**：部分 AC 同时需要 Browser E2E + API/DB 验证，上表为分类统计，不去重。

## 待 PL 处理项

| # | 事项 | 原因 | 建议 |
|---|------|------|------|
| 1 | 全部 114 条 AC 覆盖状态为 `not_covered` | CR-003 刚完成需求细化，未进入开发 | REQ_GATE 通过后进入 DESIGN → DEVELOPMENT 逐步覆盖 |
| 2 | P2 验收项（9 条）是否纳入 MVP | P2 为体验优化（空状态/动画/响应式），可延后 | 建议纳入但不阻塞 REQ_GATE |
| 3 | 活跃度金箱"稀有称号"奖励具体内容 | 需内容策划确认称号池 | 非阻塞，BE 先用