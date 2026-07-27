# Feature Status

本文记录当前功能状态、缺口、TODO 和已知限制。AI 和团队判断"当前系统是否支持某能力"时，以本文和当前代码共同为准。

## 状态定义

| 状态 | 含义 |
| --- | --- |
| Planned | 已规划，尚未实现 |
| In Progress | 正在实现，不能视为稳定能力 |
| Available | 已实现并通过必要验证 |
| Deprecated | 已废弃，不建议新增依赖 |
| Blocked | 被外部条件阻塞 |
| Unknown | 尚未确认，不能当成事实 |

## 功能清单

| 功能 | 状态 | REQ | 关联 AC | 入口 | 验证方式 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 叙事一致性引擎 | Planned | REQ-001 | AC-001~AC-003 | 游戏对话界面 | AI 输出 + 后端验证 | MVP 核心 |
| 结构化剧本系统 | Planned | REQ-002 | AC-004~AC-008 | 剧本首页/游戏界面 | 浏览器交互 + 后端验证 | MVP 核心，1-2 个剧本 |
| 跨会话角色记忆 | Planned | REQ-003 | AC-009~AC-011 | 游戏对话界面（透明） | AI 输出 + 向量数据库验证 | MVP 核心差异化 |
| 好感度系统 | Planned | REQ-004 | AC-012~AC-014 | 游戏界面/角色信息页 | 浏览器交互 + 后端验证 | MVP 核心循环 |
| 基础视觉呈现 | Planned | REQ-005 | AC-015~AC-019 | 游戏界面 | 浏览器交互 + 性能测试 | MVP 体验底线 |
| 用户账户系统（邮箱） | Planned | REQ-006 | AC-020~AC-025 | 注册/登录/引导页面 | 浏览器交互 + 后端验证 + 邮件 | MVP 仅邮箱 |
| 每日签到 Streak | Planned | REQ-007 | AC-026~AC-029 | 签到页面/日历 | 浏览器交互 + 后端验证 | 留存机制 |
| 每日任务系统 | Planned | REQ-008 | AC-030~AC-032 | 任务面板 | 浏览器交互 + 后端验证 | 留存机制 |
| 路线探索展示 | Planned（P1） | REQ-002-R04 | AC-033 | 剧本详情页 | 浏览器交互 | P1 延后 |
| 记忆摘要压缩 | Planned（P1） | REQ-003-R03 | AC-034 | 后台透明 | 后端验证 | P1 延后 |
| 密码找回 | Planned（P1） | REQ-006-R05 | AC-035 | 登录页 | 浏览器交互 + 后端验证 | P1 延后 |
| 剧本发现与推荐系统 | Planned（CR-003 P0） | REQ-DISC-001~005 | AC-DISC-001~005 | `/discover` + 首页继续玩 | Browser E2E + API/DB | CR-003 需求已细化 |
| 角色卡片系统 | Planned（CR-003 P0） | REQ-CHAR-001~004 | AC-CHAR-001~004 | `/characters` | Browser E2E + API/DB + PWA | CR-003 需求已细化 |
| 存档与多线路管理 | Planned（CR-003 P0） | REQ-SAVE-001~004 | AC-SAVE-001~004 | `/saves` | Browser E2E + API/DB + 定时任务 | CR-003 需求已细化 |
| 碎片经济可视化 | Planned（CR-003 P1） | REQ-SHARD-001~003 | AC-SHARD-001~003 | `/shards` | Browser E2E + API/DB | 纯展示层，复用现有表 |
| 成就系统 | Planned（CR-003 P1） | REQ-ACH-001~004 | AC-ACH-001~004 | `/achievements` | Browser E2E + API/DB + 幂等性 | 新建两表，20+成就种子 |
| 每日任务增强 | Planned（CR-003 P1） | REQ-TASK-001~004 | AC-TASK-001~004 | HomeView 任务面板 | Browser E2E + API/DB + 定时任务 | 活跃度宝箱+动效 |
| 订阅/内购系统 | Planned（延后） | — | — | — | — | CEO 裁剪：不在 MVP |
| OAuth 登录 | Planned（延后） | — | — | — | — | CEO 裁剪：不在 MVP |
| 管理后台 | Planned（延后） | — | — | — | — | CEO 裁剪：不在 MVP |
| 社区与 UGC | Planned（CR-004） | — | — | — | — | CEO 澄清：CR-003 不含，留待 CR-004 |

## CR-003 功能汇总

| 模块 | 优先级 | REQ 数 | AC 数 | 新表 | 新 API | 新页面 |
|------|--------|--------|-------|------|--------|--------|
| 剧本发现与推荐 | P0 | 5 | 18 | 2 (script_tags, script_stats) | 4 | DiscoverView |
| 角色卡片系统 | P0 | 4 | 15 | 2 (character_profiles, user_follows) | 3 | CharactersView + CharacterDetailView |
| 存档与多线路管理 | P0 | 4 | 23 | 2 (save_snapshots, ending_progress) | 5 | SaveManagerView |
| 碎片经济可视化 | P1 | 3 | 14 | 0（复用 fragments 表） | 2 | ShardCenterView |
| 成就系统 | P1 | 4 | 20 | 2 (achievement_definitions, user_achievements) | 3 | AchievementView |
| 每日任务增强 | P1 | 4 | 24 | 1 (activity_chests) | 2 | HomeView 内嵌 |
| 共享层 | — | — | — | — | 2 (迁移+导航) | — |
| **合计** | — | **24** | **114** | **9** | **21** | **6** |

## 已知限制

| 限制 | 影响范围 | 临时方案 | 计划处理 |
| --- | --- | --- | --- |
| 账户删除功能缺失 | 用户数据合规 | MVP 不做，上线前补齐 | 后续 CR 补齐 |
| mock 碎片无消费场景 | 留存验证深度有限 | 仅累积展示 + 签到阶梯奖励 | MVP+1 加入消费场景 |
| 无离线能力 | 弱网体验 | 仅 installable PWA | 后续 CR 评估 |
| 碎片中心仅展示层 | 碎片经济闭环 | 复用现有 fragments 表，不新增支付流程 | CR-004 评估真实支付 |
| 成就称号池未定义 | 金箱奖励 | BE 先用 placeholder title code | 内容策划确认后补齐 |

## TODO

| 事项 | 优先级 | 负责人 | 截止或触发条件 |
| --- | --- | --- | --- |
| LLM API 选型确认（PRE-01） | P0 | Architect + AI Engineer | REQUIREMENT 阶段并行 |
| 向量数据库选型确认（PRE-02） | P0 | Architect | REQUIREMENT 阶段并行 |
| 美术资源获取方式确认（PRE-03） | P0 | PL | REQUIREMENT 阶段并行 |
| 首发剧本大纲确认（PRE-04） | P0 | PM + 内容策划 | REQUIREMENT 阶段并行 |
| 账户删除/数据删除合规补齐 | P0 | PM | 上线前必须完成 |

## 维护规则

- 新增、删除、上线、下线或改变用户可见功能时必须更新本文。
- 不把未实现能力写成 Available。
- 需求想法不直接写成事实；未确认内容使用 Unknown 或 Planned。
