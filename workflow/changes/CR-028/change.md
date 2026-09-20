# CR-028: 剧本角色选择与多故事线系统

- 目标：玩家在剧本详情页选择扮演角色，不同角色对应不同故事线，生成独立存档
- 成功标准：可选角色进入不同 Route；存档按角色区分；存档管理页可按角色筛选；已有剧本原主角自动可扮演
- 功能清单：
  1. Character 表加 playable/playable_route_id/play_description/unlock_type/unlock_price 字段
  2. GameSession 表加 character_id/character_name 字段
  3. 剧本详情接口返回 playable_characters 列表
  4. 开始游戏接口接受 character_id，自动匹配 route
  5. 存档列表接口返回角色信息
  6. 剧本详情页复用现有角色展示区域，增加可扮演标识和选中状态
  7. 存档管理页增加角色筛选标签栏
  8. 个人中心展示角色信息
  9. NarrativeEngine 角色身份注入
  10. 数据迁移：已有 is_main 角色自动 playable
- 风险：
  - 已有 GameSession 无 character_id → 允许 NULL，显示「默认角色」
  - NarrativeEngine 改造影响现有对话 → 未配置角色时走原逻辑
  - 已有剧本无 playable 角色 → 数据迁移脚本默认设置
- 不做范围：管理后台配置界面、游戏页内切换角色、付费支付流程
- 变更类型：功能增强（Feature Enhancement）
- 主责角色：BE（接口+NarrativeEngine）、FE（剧本详情+存档+个人中心）、QA（测试）
