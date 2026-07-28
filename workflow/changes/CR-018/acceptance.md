# CR-018 用户复测问题 - 验收追踪

**Change ID**: user-retest-issues  
**创建时间**: 2026-07-27  
**状态**: 已完成（QA 验证通过）

---

## 验收追踪表

| REQ-ID | AC-ID | 描述 | 优先级 | 覆盖状态 | 验证结果 |
|--------|-------|------|--------|----------|----------|
| REQ-GIFT-001 | AC-GIFT-001 | 送礼接口修复：接口返回 200，碎片扣减正确，好感度增加正确 | P0 | covered | ✅ 通过 |
| REQ-CHAT-001 | AC-CHAT-001 | 剧本内自由对话修复：从剧本页面发起自由对话正常返回 AI 回复，无 401 错误 | P0 | covered | ✅ 通过 |
| REQ-AVATAR-001 | AC-AVATAR-001 | 头像上传修复：用户可成功上传新头像，页面立即显示新头像 | P0 | covered | ✅ 通过 |
| REQ-AFFECTION-001 | AC-AFFECTION-001 | 好感度实时更新：用户做出选择后，好感度立即更新，无需刷新页面 | P1 | covered | ✅ 通过 |
| REQ-FREECHAT-001 | AC-FREECHAT-001 | 自由对话历史持久化：同一剧本会话内的自由对话历史在重新进入时仍然展示 | P1 | covered | ✅ 通过 |
| REQ-SCRIPT-001 | AC-SCRIPT-001 | 剧本流程长度：剧本至少支持 5-8 轮对话才到达结局分支 | P1 | covered | ✅ 通过 |
| REQ-PROGRESS-001 | AC-PROGRESS-001 | 剧本进度记录与展示：每次选择后进度更新，进度条可视化变化 | P1 | covered | ✅ 通过 |
| REQ-UUID-001 | AC-UUID-001 | UUID v4 数据迁移：所有角色、剧本 ID 符合 UUID v4 格式，外键关联正确 | P1 | covered | ✅ 通过 |
| REQ-STATS-001 | AC-STATS-001 | 完成剧本统计修正："完成剧本" = 至少有 1 个结局被解锁的剧本数量 | P1 | covered | ✅ 通过 |
| REQ-SHARD-001 | AC-SHARD-001 | 累计获得碎片修复：累计获得 = 所有签到/奖励碎片之和，与实际获取一致 | P1 | covered | ✅ 通过 |
| REQ-QUOTA-001 | AC-QUOTA-001 | 对话额度重置确认：额度显示正确，重置时间符合预期，剧本对话和自由对话共享额度 | P1 | covered | ✅ 通过 |
| REQ-UI-001 | AC-UI-001 | AI 叙事 loading 状态：AI 叙事时显示 loading 动画 | P2 | covered | ✅ 通过 |
| REQ-I18N-001 | AC-I18N-001 | 性格特质中文映射：所有性格特质显示中文，不显示裸英文 key | P2 | covered | ✅ 通过 |
| REQ-CHAR-001 | AC-CHAR-001 | 性格特点数据补全：角色详情页展示 personality 字段内容 | P2 | covered | ✅ 通过 |
| REQ-VOICE-001 | AC-VOICE-001 | 语音试听功能：角色详情页有语音试听按钮，未解锁显示锁定状态 | P2 | covered | ✅ 通过 |
| REQ-ACH-001 | AC-ACH-001 | 成就卡片格式化：成就卡片显示格式化中文描述，不显示原始 JSON | P2 | covered | ✅ 通过 |
| REQ-SHOP-001 | AC-SHOP-001 | 碎片商城 Tab 样式：碎片商城 Tab 在页面顶部，样式与社区 Tab 一致 | P2 | covered | ✅ 通过 |
| REQ-SHARD-002 | AC-SHARD-002 | 碎片收支明细：展示签到获取、送礼支出等交易流水，显示中文 | P2 | covered | ✅ 通过 |
| REQ-PROFILE-001 | AC-PROFILE-001 | 个人中心对话次数展示：个人中心显示今日对话次数 / 总额度 | P2 | covered | ✅ 通过 |
| REQ-MEMORY-001 | AC-MEMORY-001 | AI 记忆日期修复：日期正确显示或显示"未知时间"，无 Invalid Date 错误 | P2 | covered | ✅ 通过 |
| REQ-AFFECTION-002 | AC-AFFECTION-002 | 角色羁绊中文翻译：所有好感度等级显示中文，不显示英文 | P2 | covered | ✅ 通过 |
| REQ-BILL-001 | AC-BILL-001 | 账单中文映射：账单类型显示中文，显示所有类型的交易记录 | P2 | covered | ✅ 通过 |
| REQ-COMM-001 | AC-COMM-001 | 社区浏览量记录：进入帖子详情页后浏览量 +1，刷新页面浏览量保持 | P2 | covered | ✅ 通过 |
| REQ-SCRIPT-002 | AC-SCRIPT-002 | 封面图/头像尺寸优化：不同屏幕下封面图/头像自适应，不拉伸不变形 | P2 | covered | ✅ 通过 |
| REQ-SHARD-003 | AC-SHARD-003 | 成就奖励跳转：点击"成就奖励"条目后路由跳转到成就页面 | P2 | covered | ✅ 通过 |
| REQ-I18N-002 | AC-I18N-002 | 碎片商城收支明细中文化：所有碎片收支明细显示中文 | P1 | covered | ✅ 通过 |
| REQ-COMM-002 | AC-COMM-002 | 帖子浏览量统计修复：浏览量正确记录，同一用户短时间内不重复计数 | P1 | covered | ✅ 通过 |
| REQ-BILL-002 | AC-BILL-002 | 会员账单显示所有交易：账单列表显示所有类型的交易记录（充值、碎片兑换、送礼、签到等） | P1 | covered | ✅ 通过 |

---

## 验收统计

**总需求数**: 28  
**优先级分布**:
- P0: 3 个（REQ-GIFT-001, REQ-CHAT-001, REQ-AVATAR-001）
- P1: 11 个（REQ-AFFECTION-001, REQ-FREECHAT-001, REQ-SCRIPT-001, REQ-PROGRESS-001, REQ-UUID-001, REQ-STATS-001, REQ-SHARD-001, REQ-QUOTA-001, REQ-I18N-002, REQ-COMM-002, REQ-BILL-002）
- P2: 14 个（REQ-UI-001, REQ-I18N-001, REQ-CHAR-001, REQ-VOICE-001, REQ-ACH-001, REQ-SHOP-001, REQ-SHARD-002, REQ-PROFILE-001, REQ-MEMORY-001, REQ-AFFECTION-002, REQ-BILL-001, REQ-COMM-001, REQ-SCRIPT-002, REQ-SHARD-003）

**验收状态**: 全部 covered，已 QA 验证通过

**验证时间**: 2026-07-27

---

## 任务映射

| 任务 ID | REQ-ID | 描述 | 优先级 |
|---------|--------|------|--------|
| T-001 | REQ-GIFT-001 | 送礼接口修复 | P0 |
| T-002 | REQ-CHAT-001 | 剧本内自由对话修复 | P0 |
| T-003, T-029 | REQ-AVATAR-001 | 头像上传修复 | P0 |
| T-004 | REQ-AFFECTION-001 | 好感度实时更新 | P1 |
| T-005 | REQ-FREECHAT-001 | 自由对话历史持久化 | P1 |
| T-006 | REQ-SCRIPT-001 | 剧本流程长度 | P1 |
| T-007 | REQ-PROGRESS-001 | 剧本进度记录与展示 | P1 |
| T-008 | REQ-UUID-001 | UUID v4 数据迁移 | P1 |
| T-009 | REQ-STATS-001 | 完成剧本统计修正 | P1 |
| T-010 | REQ-SHARD-001 | 累计获得碎片修复 | P1 |
| T-011 | REQ-QUOTA-001 | 对话额度重置确认 | P1 |
| T-012 | REQ-UI-001 | AI 叙事 loading 状态 | P2 |
| T-013, T-025 | REQ-I18N-001 | 性格特质中文映射 | P2 |
| T-014 | REQ-CHAR-001 | 性格特点数据补全 | P2 |
| T-015 | REQ-VOICE-001 | 语音试听功能 | P2 |
| T-016 | REQ-ACH-001 | 成就卡片格式化 | P2 |
| T-017 | REQ-SHOP-001 | 碎片商城 Tab 样式 | P2 |
| T-018, T-026 | REQ-SHARD-002 | 碎片收支明细 | P2 |
| T-019 | REQ-PROFILE-001 | 个人中心对话次数展示 | P2 |
| T-020 | REQ-MEMORY-001 | AI 记忆日期修复 | P2 |
| T-021 | REQ-AFFECTION-002 | 角色羁绊中文翻译 | P2 |
| T-022, T-030 | REQ-BILL-001 | 账单中文映射 | P2 |
| T-023, T-028 | REQ-COMM-001 | 社区浏览量记录 | P2 |
| T-024 | REQ-SCRIPT-002 | 封面图/头像尺寸优化 | P2 |
| T-027 | REQ-SHARD-003 | 成就奖励跳转 | P2 |
| T-026 | REQ-I18N-002 | 碎片商城收支明细中文化 | P1 |
| T-028 | REQ-COMM-002 | 帖子浏览量统计修复 | P1 |
| T-030 | REQ-BILL-002 | 会员账单显示所有交易 | P1 |

---

## 验证说明

所有验收标准均已通过 QA 验证，验证方式包括：
- API 接口测试
- 浏览器端到端测试
- 数据库数据验证
- UI 渲染检查

验证时间：2026-07-27  
验证人：QA Agent
