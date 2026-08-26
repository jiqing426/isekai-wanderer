# 异世界漫游者 - 后台管理系统详细功能规格文档

> 版本：v2.0 | 日期：2026-08-05 | 基于数据库模型自动生成

---

## 目录

1. [用户管理](#1-用户管理)
2. [剧本管理](#2-剧本管理)
3. [角色管理](#3-角色管理)
4. [订阅管理](#4-订阅管理)
5. [碎片与支付管理](#5-碎片与支付管理)
6. [礼物管理](#6-礼物管理)
7. [好感度管理](#7-好感度管理)
8. [游戏会话与对话记录](#8-游戏会话与对话记录)
9. [自由对话管理](#9-自由对话管理)
10. [存档管理](#10-存档管理)
11. [每日签到与任务](#11-每日签到与任务)
12. [对话额度管理](#12-对话额度管理)
13. [成就系统](#13-成就系统)
14. [CG 管理](#14-cg-管理)
15. [解锁记录管理](#15-解锁记录管理)
16. [记忆系统管理](#16-记忆系统管理)
17. [社区管理](#17-社区管理)
18. [商品商城管理](#18-商品商城管理)
19. [场景配置管理](#19-场景配置管理)
20. [知识库管理](#20-知识库管理)
21. [集合点管理](#21-集合点管理)
22. [用户画像](#22-用户画像)
23. [用户设置](#23-用户设置)
24. [登录设备管理](#24-登录设备管理)
25. [分享卡片管理](#25-分享卡片管理)
26. [付费墙事件](#26-付费墙事件)
27. [Discord 集成配置](#27-discord-集成配置)
28. [数据统计仪表盘](#28-数据统计仪表盘)

---

## 1. 用户管理

### 1.1 用户列表页

**数据表**: `users`

| 字段 | 类型 | 说明 | 可搜索 | 可排序 |
|------|------|------|--------|--------|
| id | UUID | 用户唯一ID | ✅ | ✅ |
| email | String(255) | 邮箱地址 | ✅ | ✅ |
| display_name | String(100) | 昵称 | ✅ | ✅ |
| avatar_url | Text | 头像URL | ❌ | ❌ |
| email_verified | Boolean | 邮箱是否验证 | ✅筛选 | ❌ |
| oauth_provider | String(50) | 第三方登录(Google/Discord) | ✅筛选 | ❌ |
| oauth_id | String(255) | 第三方平台用户ID | ✅ | ❌ |
| subscription_tier | String(20) | 订阅等级(free/basic/standard/premium) | ✅筛选 | ✅ |
| onboarding_completed | Boolean | 是否完成新手引导 | ✅筛选 | ❌ |
| preferred_genre | String(50) | 偏好类型 | ✅筛选 | ❌ |
| locale | String(10) | 语言偏好 | ✅筛选 | ❌ |
| signature | String(200) | 个性签名 | ❌ | ❌ |
| last_login | DateTime | 最后登录时间 | ✅范围 | ✅ |
| is_admin | Boolean | 是否管理员 | ✅筛选 | ❌ |
| created_at | DateTime | 注册时间 | ✅范围 | ✅ |
| updated_at | DateTime | 更新时间 | ❌ | ✅ |

**操作按钮**: 查看详情、编辑、禁用/启用、重置密码、删除、导出

**批量操作**: 批量禁用、批量导出、批量修改订阅等级

---

### 1.2 用户详情页

#### Tab 1: 基本信息

**可编辑字段**: display_name、avatar_url、signature、subscription_tier、preferred_genre、locale、is_admin

#### Tab 2: 账号安全

**数据表**: `password_resets`, `oauth_accounts`

| 字段 | 类型 | 说明 |
|------|------|------|
| password_resets.token | String(255) | 重置令牌 |
| password_resets.expires_at | DateTime | 过期时间 |
| password_resets.used | Boolean | 是否已使用 |
| password_resets.created_at | DateTime | 创建时间 |
| oauth_accounts.provider | String(50) | 绑定平台 |
| oauth_accounts.provider_user_id | String(255) | 平台用户ID |
| oauth_accounts.created_at | DateTime | 绑定时间 |

**操作**: 强制退出所有设备、解绑第三方账号、发送密码重置邮件

#### Tab 3: 游戏统计

| 统计项 | 计算方式 |
|--------|----------|
| 总游戏会话数 | COUNT(game_sessions WHERE user_id) |
| 已完成会话数 | COUNT(status='completed') |
| 总对话数 | COUNT(dialogue_history) |
| 总选择次数 | COUNT(game_progress) |
| 完成剧本数 | COUNT(DISTINCT script_id WHERE status='completed') |
| 解锁结局数 | COUNT(ending_type IS NOT NULL) |
| 碎片余额 | fragments.balance |
| 累计获得碎片 | SUM(amount WHERE amount > 0) |
| 累计消费碎片 | SUM(ABS(amount) WHERE amount < 0) |

#### Tab 4: 好感度记录

**数据表**: `affection`

| 字段 | 类型 | 说明 |
|------|------|------|
| character_id | UUID | 角色ID |
| character.name | - | 角色名称(关联) |
| value | Integer | 好感度值(0-100) |
| level | String(20) | 等级 |
| updated_at | DateTime | 最后更新 |

**操作**: 手动调整好感度值

#### Tab 5: 游戏存档

**数据表**: `save_snapshots`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 存档ID |
| session_id | UUID | 会话ID |
| label | String(100) | 存档标签 |
| current_node_id | UUID | 当前节点 |
| choice_history | JSON | 选择历史 |
| metadata | JSON | 元数据 |
| created_at | DateTime | 存档时间 |

**操作**: 查看详情、删除、恢复

#### Tab 6: 碎片交易记录

**数据表**: `fragments`, `fragment_transactions`

| 字段 | 类型 | 说明 |
|------|------|------|
| fragments.balance | Integer | 当前余额 |
| fragment_transactions.amount | Integer | 交易金额(正=收入,负=支出) |
| fragment_transactions.reason | String(100) | 交易原因 |
| fragment_transactions.created_at | DateTime | 交易时间 |

**操作**: 手动补发碎片、扣除碎片

#### Tab 7: 登录设备

**数据表**: `login_devices`

| 字段 | 类型 | 说明 |
|------|------|------|
| device_name | String(255) | 设备名称 |
| device_type | String(50) | 设备类型 |
| browser | String(100) | 浏览器 |
| os | String(100) | 操作系统 |
| ip_address | String(50) | IP地址 |
| location | String(255) | 登录地点 |
| last_active_at | DateTime | 最后活跃 |
| is_current | Boolean | 是否当前设备 |

**操作**: 强制下线

---

### 1.3 新增用户

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| email | String | ✅ | 邮箱(唯一) |
| password | String | ✅ | 初始密码 |
| display_name | String | ❌ | 昵称 |
| subscription_tier | Select | ✅ | 默认free |
| is_admin | Boolean | ❌ | 默认false |

---

## 2. 剧本管理

### 2.1 剧本列表页

**数据表**: `scripts`

| 字段 | 类型 | 说明 | 可搜索 | 可排序 |
|------|------|------|--------|--------|
| id | UUID | 剧本ID | ✅ | ✅ |
| slug | String(100) | URL标识 | ✅ | ✅ |
| title | String(255) | 标题 | ✅ | ✅ |
| description | Text | 描述 | ✅ | ❌ |
| genre | String(50) | 类型 | ✅筛选 | ✅ |
| cover_image_url | Text | 封面图 | ❌ | ❌ |
| author | String(255) | 作者 | ✅ | ❌ |
| hot_value | Integer | 热度值 | ❌ | ✅ |
| total_convergence_points | Integer | 集合点数量 | ❌ | ✅ |
| characters_per_script | Integer | 角色数量 | ❌ | ✅ |
| created_at | DateTime | 创建时间 | ✅范围 | ✅ |

**操作**: 新增、编辑、删除、上下架、封面上传

**统计列**: 章节数、节点数、结局数、游玩人数

---

### 2.2 剧本编辑页

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| slug | String | ✅ | URL标识(唯一) |
| title | String | ✅ | 标题 |
| description | Textarea | ❌ | 描述 |
| genre | Select | ✅ | romance/fantasy/mystery |
| cover_image_url | FileUpload | ❌ | 封面图 |
| author | String | ❌ | 作者名 |
| hot_value | Number | ❌ | 热度值 |
| total_convergence_points | Number | ❌ | 集合点数量 |
| characters_per_script | Number | ❌ | 角色数量 |

---

### 2.3 章节/路线管理

**数据表**: `routes`

| 字段 | 类型 | 说明 | 可编辑 |
|------|------|------|--------|
| id | UUID | 路线ID | ❌ |
| script_id | UUID | 所属剧本 | ❌ |
| title | String(255) | 章节标题 | ✅ |
| description | Text | 描述 | ✅ |
| chapter_number | Integer | 章节序号(1-4) | ✅ |
| chapter_type | String(50) | encounter/daily/conflict/convergence | ✅ |
| branch_type | String(50) | main/branch_a/branch_b/secret | ✅ |
| branch_label | String(100) | 分支标签 | ✅ |
| branch_condition | JSON | 进入条件 | ✅ |

**操作**: 新增、编辑、删除、拖拽排序

---

### 2.4 剧情节点管理

**数据表**: `nodes`

| 字段 | 类型 | 说明 | 可编辑 |
|------|------|------|--------|
| id | UUID | 节点ID | ❌ |
| route_id | UUID | 所属章节 | ✅ |
| parent_id | UUID | 父节点ID | ✅ |
| node_type | String(20) | 节点类型 | ✅ |
| content | JSON | 节点内容 | ✅ |
| background | Text | 背景图URL | ✅ |
| character_id | UUID | 绑定角色(NULL=公共) | ✅ |

**节点类型与 content 结构**:

| 类型 | 说明 | content字段 |
|------|------|-------------|
| preset | 预设节点 | text, emotion, scene, character_id |
| transition | AI过渡 | text, emotion, context |
| choice | 选择节点 | text |
| ending | 结局节点 | text, ending_type, ending_title, is_ending |
| ai_dialog | AI对话 | character, dialogue, emotion, dialogue_options |
| choice_point | 选择点 | text, title |
| fixed_scene | 固定场景 | text, background, narration |
| cg_trigger | CG触发 | title, description, image, rarity |
| converge_node | 收敛节点 | description |

**emotion 枚举**: neutral, happy, sad, angry, surprised, shy

**操作**: 新增、编辑、删除、复制、拖拽排序、可视化关系图

---

### 2.5 选择项管理

**数据表**: `node_choices`

| 字段 | 类型 | 说明 | 可编辑 |
|------|------|------|--------|
| id | UUID | 选择项ID | ❌ |
| node_id | UUID | 所属节点 | ❌ |
| text | Text | 选项文本 | ✅ |
| next_node_id | UUID | 下一节点ID | ✅ |
| affection_delta | Integer | 好感度变化(-5~+5) | ✅ |
| required_affection | Integer | 所需好感度阈值 | ✅ |
| is_hidden | Boolean | 是否隐藏 | ✅ |
| hint | Text | 提示文本 | ✅ |

**操作**: 新增、编辑、删除、拖拽排序

---

## 3. 角色管理

### 3.1 角色列表页

**数据表**: `characters`

| 字段 | 类型 | 说明 | 可搜索 | 可排序 |
|------|------|------|--------|--------|
| id | UUID | 角色ID | ✅ | ✅ |
| script_id | UUID | 所属剧本 | ✅筛选 | ❌ |
| name | String(255) | 名称 | ✅ | ✅ |
| description | Text | 描述 | ✅ | ❌ |
| age | Integer | 年龄 | ❌ | ✅ |
| height | Integer | 身高(cm) | ❌ | ✅ |
| birthday | String(20) | 生日 | ❌ | ❌ |
| personality | JSON | 性格特征 | ❌ | ❌ |
| avatar_url | Text | 头像URL | ❌ | ❌ |
| is_main | Boolean | 是否主角 | ✅筛选 | ❌ |
| playable | Boolean | 是否可扮演 | ✅筛选 | ❌ |
| unlock_type | String(20) | 解锁类型 | ✅筛选 | ❌ |
| unlock_price | Integer | 解锁价格 | ❌ | ✅ |
| likes | JSON | 喜好列表 | ❌ | ❌ |
| dialogue_style | Text | 对话风格 | ❌ | ❌ |

**操作**: 新增、编辑、删除、头像上传

---

### 3.2 角色编辑页

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| script_id | Select | ✅ | 所属剧本 |
| name | String | ✅ | 名称 |
| description | Textarea | ❌ | 描述 |
| age | Number | ❌ | 年龄 |
| height | Number | ❌ | 身高 |
| birthday | String | ❌ | 生日 |
| personality | JSON编辑器 | ❌ | 性格特征 |
| avatar_url | FileUpload | ❌ | 头像 |
| is_main | Boolean | ❌ | 主角 |
| playable | Boolean | ❌ | 可扮演 |
| unlock_type | Select | ❌ | free/paid/subscription |
| unlock_price | Number | ❌ | 碎片价格 |
| likes | TagInput | ❌ | 喜好标签 |
| dialogue_style | Textarea | ❌ | 对话风格 |

---

### 3.3 角色立绘管理

**数据表**: `character_sprites`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 立绘ID |
| character_id | UUID | 所属角色 |
| emotion | String(50) | 表情状态 |
| image_url | Text | 图片URL |

**操作**: 上传、编辑表情标签、删除

---

## 4. 订阅管理

### 4.1 订阅记录列表

**数据表**: `subscription_plans`

| 字段 | 类型 | 说明 | 可搜索 | 可排序 |
|------|------|------|--------|--------|
| id | UUID | 计划ID | ❌ | ✅ |
| user_id | UUID | 用户ID | ✅筛选 | ✅ |
| tier | String(20) | 等级 | ✅筛选 | ✅ |
| status | String(20) | 状态 | ✅筛选 | ✅ |
| started_at | DateTime | 开始时间 | ✅范围 | ✅ |
| expires_at | DateTime | 到期时间 | ✅范围 | ✅ |
| fragment_quota | Integer | 每月碎片配额 | ❌ | ✅ |
| last_fragment_grant_at | DateTime | 上次发放时间 | ❌ | ❌ |
| next_fragment_grant_at | DateTime | 下次发放时间 | ❌ | ❌ |

**tier 枚举**: free, basic, standard, premium

**status 枚举**: active, cancelled, expired

**操作**: 手动续期、取消、调整等级、补发碎片

---

## 5. 碎片与支付管理

### 5.1 碎片余额

**数据表**: `fragments`

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | UUID | 用户ID |
| balance | Integer | 当前余额 |
| updated_at | DateTime | 更新时间 |

**操作**: 手动调整(需填原因)

---

### 5.2 碎片交易记录

**数据表**: `fragment_transactions`

| 字段 | 类型 | 说明 | 可搜索 | 可排序 |
|------|------|------|--------|--------|
| id | UUID | 交易ID | ✅ | ✅ |
| user_id | UUID | 用户ID | ✅筛选 | ✅ |
| amount | Integer | 金额(正=收入,负=支出) | ❌ | ✅ |
| reason | String(100) | 原因 | ✅ | ✅ |
| created_at | DateTime | 时间 | ✅范围 | ✅ |

**reason 枚举**:
| 值 | 说明 |
|----|------|
| checkin | 签到 |
| task_claim:task_dialogue | 每日任务-对话达人 |
| task_claim:task_choice | 每日任务-选择大师 |
| task_claim:task_profile | 每日任务-角色探索 |
| task_claim:all_complete | 全完成奖励 |
| gift_send | 送礼支出 |
| fragment_purchase | 碎片购买 |
| achievement_claim | 成就奖励 |
| admin_adjust | 管理员调整 |

**操作**: 手动补发、扣除、导出

---

### 5.3 购买记录

**数据表**: `purchases`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 购买ID |
| user_id | UUID | 用户ID |
| item_id | String(100) | 商品ID |
| item_name | String(255) | 商品名称 |
| price | Numeric(10,2) | 价格 |
| currency | String(3) | 货币(USD/JPY/EUR/CNY) |
| is_mock | Boolean | 是否模拟支付 |
| created_at | DateTime | 时间 |

---

## 6. 礼物管理

### 6.1 礼物商城配置

**数据表**: `gifts`

| 字段 | 类型 | 说明 | 可编辑 |
|------|------|------|--------|
| id | String(100) | 礼物ID | ✅ |
| name | String(255) | 名称 | ✅ |
| description | Text | 描述 | ✅ |
| price | Integer | 价格(碎片) | ✅ |
| affection_bonus | Integer | 好感度加成 | ✅ |
| icon_url | String(500) | 图标URL | ✅ |
| is_active | Boolean | 上架状态 | ✅ |

**操作**: 新增、编辑、删除、上架/下架、排序

---

### 6.2 送礼记录

**数据表**: `gift_records`

| 字段 | 类型 | 说明 | 可搜索 | 可排序 |
|------|------|------|--------|--------|
| id | UUID | 记录ID | ❌ | ✅ |
| user_id | UUID | 送礼用户 | ✅筛选 | ✅ |
| character_id | UUID | 接收角色 | ✅筛选 | ❌ |
| gift_id | String | 礼物ID | ✅筛选 | ❌ |
| gift_name | String | 礼物名称 | ❌ | ❌ |
| quantity | Integer | 数量 | ❌ | ✅ |
| affection_delta | Integer | 好感度变化 | ❌ | ✅ |
| created_at | DateTime | 时间 | ✅范围 | ✅ |

**操作**: 查看详情、导出

---

## 7. 好感度管理

### 7.1 好感度列表

**数据表**: `affection`

| 字段 | 类型 | 说明 | 可搜索 | 可排序 |
|------|------|------|--------|--------|
| user_id | UUID | 用户ID | ✅筛选 | ✅ |
| character_id | UUID | 角色ID | ✅筛选 | ❌ |
| value | Integer | 好感度值(0-100) | ❌ | ✅ |
| level | String(20) | 等级 | ✅筛选 | ✅ |
| updated_at | DateTime | 更新时间 | ✅范围 | ✅ |

**等级映射**:
| 等级 | 范围 | 中文 |
|------|------|------|
| acquaintance | 0-19 | 相识 |
| ambiguous | 20-39 | 暧昧 |
| trust | 40-59 | 信赖 |
| bond | 60-79 | 羁绊 |
| love | 80-100 | 挚爱 |

**操作**: 查看详情、手动调整、重置

---

### 7.2 好感度变化历史

**数据表**: `affection_history`

| 字段 | 类型 | 说明 | 可搜索 |
|------|------|------|--------|
| user_id | UUID | 用户ID | ✅筛选 |
| character_id | UUID | 角色ID | ✅筛选 |
| delta | Integer | 变化量 | ❌ |
| old_value | Integer | 旧值 | ❌ |
| new_value | Integer | 新值 | ❌ |
| old_level | String(50) | 旧等级 | ❌ |
| new_level | String(50) | 新等级 | ❌ |
| reason | String(100) | 原因 | ✅筛选 |
| source_session_id | UUID | 来源会话 | ✅ |
| source_choice_id | UUID | 来源选择 | ✅ |
| created_at | DateTime | 时间 | ✅范围 |

**操作**: 查看详情、导出

---

## 8. 游戏会话与对话记录

### 8.1 游戏会话列表

**数据表**: `game_sessions`

| 字段 | 类型 | 说明 | 可搜索 | 可排序 |
|------|------|------|--------|--------|
| id | UUID | 会话ID | ✅ | ✅ |
| user_id | UUID | 用户ID | ✅筛选 | ✅ |
| script_id | UUID | 剧本ID | ✅筛选 | ❌ |
| route_id | UUID | 章节ID | ✅筛选 | ❌ |
| character_id | UUID | 扮演角色 | ✅筛选 | ❌ |
| character_name | String | 角色名 | ✅ | ❌ |
| current_node_id | UUID | 当前节点 | ❌ | ❌ |
| status | String(20) | 状态 | ✅筛选 | ✅ |
| ending_type | String(20) | 结局类型 | ✅筛选 | ❌ |
| started_at | DateTime | 开始时间 | ✅范围 | ✅ |
| completed_at | DateTime | 完成时间 | ✅范围 | ✅ |
| choice_history | JSON | 选择历史 | ❌ | ❌ |

**status 枚举**: active, completed, abandoned

**操作**: 查看详情、结束会话、删除

---

### 8.2 会话详情页

**对话历史数据表**: `dialogue_history`

| 字段 | 类型 | 说明 |
|------|------|------|
| session_id | UUID | 会话ID |
| user_id | UUID | 用户ID |
| role | String(20) | user/assistant |
| content | Text | 对话内容 |
| character_id | UUID | 角色ID |
| character_name | String | 角色名 |
| emotion | String(20) | 情感 |
| created_at | DateTime | 时间 |

**游戏进度数据表**: `game_progress`

| 字段 | 类型 | 说明 |
|------|------|------|
| session_id | UUID | 会话ID |
| node_id | UUID | 经过的节点 |
| choice_id | UUID | 做出的选择 |
| created_at | DateTime | 时间 |

---

## 9. 自由对话管理

**数据表**: `free_chat_sessions`

| 字段 | 类型 | 说明 | 可搜索 | 可排序 |
|------|------|------|--------|--------|
| id | UUID | 会话ID | ✅ | ✅ |
| user_id | UUID | 用户ID | ✅筛选 | ✅ |
| topic_id | String(50) | 话题ID | ✅筛选 | ❌ |
| character_id | UUID | 角色ID | ✅筛选 | ❌ |
| script_id | UUID | 剧本ID | ✅筛选 | ❌ |
| messages | JSON | 消息列表 | ❌ | ❌ |
| created_at | DateTime | 创建时间 | ✅范围 | ✅ |
| updated_at | DateTime | 更新时间 | ✅范围 | ✅ |

**操作**: 查看消息详情、删除会话

---

## 10. 存档管理

**数据表**: `save_snapshots`

| 字段 | 类型 | 说明 | 可搜索 | 可排序 |
|------|------|------|--------|--------|
| id | UUID | 存档ID | ✅ | ✅ |
| user_id | UUID | 用户ID | ✅筛选 | ✅ |
| session_id | UUID | 会话ID | ✅ | ✅ |
| label | String(100) | 标签 | ✅ | ✅ |
| current_node_id | UUID | 当前节点 | ❌ | ❌ |
| choice_history | JSON | 选择历史 | ❌ | ❌ |
| metadata | JSON | 元数据 | ❌ | ❌ |
| created_at | DateTime | 存档时间 | ✅范围 | ✅ |

**操作**: 查看详情、删除、导出

---

## 11. 每日签到与任务

### 11.1 签到记录

**数据表**: `daily_checkins`

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | UUID | 用户ID |
| date | Date | 签到日期 |
| created_at | DateTime | 签到时间 |

### 11.2 连续签到

**数据表**: `streak_records`

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | UUID | 用户ID |
| current_streak | Integer | 当前连续天数 |
| max_streak | Integer | 最大连续天数 |
| last_checkin_date | Date | 最后签到日期 |

### 11.3 每日任务

**数据表**: `daily_tasks`

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | UUID | 用户ID |
| date | Date | 任务日期 |
| task_type | String(50) | 任务类型 |
| progress | Integer | 当前进度 |
| target | Integer | 目标值 |
| completed | Boolean | 是否完成 |
| claimed | Boolean | 是否领取 |

**task_type 枚举**:
| 值 | 说明 | 目标 | 奖励 |
|----|------|------|------|
| task_dialogue | 对话达人 | 1次 | 3碎片 |
| task_choice | 选择大师 | 1次 | 3碎片 |
| task_profile | 角色探索 | 1次 | 2碎片 |
| all_complete | 全完成奖励 | 全部 | 5碎片 |

**操作**: 重置任务、手动发放奖励

---

## 12. 对话额度管理

**数据表**: `dialogue_quotas`

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | UUID | 用户ID |
| date | Date | 日期 |
| base_quota | Integer | 基础额度(默认3) |
| consumed | Integer | 已消耗 |
| fragment_extra | Integer | 碎片兑换额外额度 |
| fragment_consumed | Integer | 碎片额度已消耗 |

**计算字段**:
| 字段 | 公式 |
|------|------|
| 剩余免费额度 | base_quota - consumed |
| 剩余碎片额度 | fragment_extra - fragment_consumed |
| 总剩余 | (base_quota-consumed) + (fragment_extra-fragment_consumed) |

**操作**: 手动调整额度

---

## 13. 成就系统

### 13.1 用户成就

**数据表**: `achievements`

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | UUID | 用户ID |
| achievement_id | String(100) | 成就ID |
| title | String(255) | 成就标题 |
| description | Text | 描述 |
| icon_url | Text | 图标 |
| unlocked_at | DateTime | 解锁时间 |

### 13.2 成就领取

**数据表**: `user_achievement_claims`

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | UUID | 用户ID |
| achievement_id | String(100) | 成就ID |
| reward_type | String(50) | 奖励类型(fragments) |
| reward_amount | Integer | 奖励数量 |
| claimed_at | DateTime | 领取时间 |

### 13.3 活跃度宝箱

**数据表**: `activity_chest_claims`

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | UUID | 用户ID |
| chest_tier | Integer | 宝箱等级(1/2/3) |
| claimed_at | DateTime | 领取时间 |

**操作**: 手动解锁成就、发放奖励

---

## 14. CG 管理

### 14.1 CG 资源

**数据表**: `cg_assets`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | CG ID |
| script_id | UUID | 所属剧本 |
| route_id | UUID | 所属章节(可选) |
| name | String(255) | 名称 |
| image_url | Text | 图片URL |
| created_at | DateTime | 创建时间 |

**操作**: 上传、编辑、删除

### 14.2 用户CG解锁

**数据表**: `unlocked_cgs`

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | UUID | 用户ID |
| cg_id | UUID | CG ID |
| unlocked_at | DateTime | 解锁时间 |

**操作**: 手动解锁

---

## 15. 解锁记录管理

**数据表**: `unlock_records`

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | UUID | 用户ID |
| unlock_type | String | 类型(cg/ending/achievement) |
| content_id | String | 内容ID |
| title | String | 标题 |
| description | Text | 描述 |
| image_url | Text | 图片 |
| rarity | String | 稀有度(N/R/SR/SSR) |
| reward_data | JSON | 奖励数据 |
| unlocked_at | DateTime | 解锁时间 |
| viewed | Boolean | 是否已查看 |

**操作**: 查看详情、手动解锁

---

## 16. 记忆系统管理

**数据表**: `character_memories`

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | UUID | 用户ID |
| character_id | UUID | 角色ID |
| memory_text | Text | 记忆内容 |
| source | String(50) | 来源(game_event/dialogue/choice/system) |
| source_session_id | UUID | 来源会话 |
| confidence | Numeric(3,2) | 置信度(0-1) |
| importance | Numeric(3,2) | 重要度(0-1) |
| is_compressed | Boolean | 是否已压缩 |
| created_at | DateTime | 创建时间 |

**操作**: 查看、删除、手动添加记忆

---

## 17. 社区管理

### 17.1 帖子管理

**数据表**: `posts`

| 字段 | 类型 | 说明 | 可搜索 |
|------|------|------|--------|
| id | UUID | 帖子ID | ✅ |
| user_id | UUID | 作者 | ✅筛选 |
| title | String(255) | 标题 | ✅ |
| content | Text | 内容 | ✅ |
| image_urls | Text | 图片(JSON数组) | ❌ |
| like_count | Integer | 点赞数 | ❌ |
| comment_count | Integer | 评论数 | ❌ |
| views_count | Integer | 浏览数 | ❌ |
| is_deleted | Boolean | 是否删除 | ✅筛选 |
| created_at | DateTime | 发布时间 | ✅范围 |

**操作**: 查看、删除、置顶

### 17.2 评论管理

**数据表**: `comments`

| 字段 | 类型 | 说明 |
|------|------|------|
| post_id | UUID | 帖子ID |
| user_id | UUID | 评论者 |
| content | Text | 内容 |
| is_deleted | Boolean | 是否删除 |
| created_at | DateTime | 时间 |

**操作**: 删除评论

### 17.3 点赞记录

**数据表**: `post_likes`

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | UUID | 用户ID |
| post_id | UUID | 帖子ID |
| created_at | DateTime | 时间 |

---

## 18. 商品商城管理

### 18.1 商品配置

**数据表**: `shop_goods`

| 字段 | 类型 | 说明 | 可编辑 |
|------|------|------|--------|
| id | UUID | 商品ID | ❌ |
| name | String(255) | 名称 | ✅ |
| description | Text | 描述 | ✅ |
| category | String(50) | 分类 | ✅ |
| icon_url | Text | 图标URL | ✅ |
| price | Integer | 价格(碎片) | ✅ |
| stock | Integer | 库存(-1=无限) | ✅ |
| limit_per_user | Integer | 每人限购数 | ✅ |
| item_type | String(50) | 物品类型 | ✅ |
| item_id | String(255) | 关联物品ID | ✅ |
| is_active | Boolean | 上架状态 | ✅ |
| created_at | DateTime | 创建时间 | ❌ |

**操作**: 新增、编辑、删除、上架/下架

### 18.2 用户物品

**数据表**: `user_goods`

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | UUID | 用户ID |
| goods_id | UUID | 商品ID |
| quantity | Integer | 数量 |
| acquired_at | DateTime | 获取时间 |

**操作**: 查看详情、手动发放

---

## 19. 场景配置管理

**数据表**: `scene_configs`

| 字段 | 类型 | 说明 | 可编辑 |
|------|------|------|--------|
| id | UUID | 配置ID | ❌ |
| node_id | UUID | 关联节点 | ✅ |
| scene_name | String(200) | 场景名称 | ✅ |
| tags | JSON | 标签列表 | ✅ |
| description | Text | 描述 | ✅ |
| created_at | DateTime | 创建时间 | ❌ |
| updated_at | DateTime | 更新时间 | ❌ |

**操作**: 新增、编辑、删除

---

## 20. 知识库管理

**数据表**: `lorebook_entries`

| 字段 | 类型 | 说明 | 可搜索 | 可排序 |
|------|------|------|--------|--------|
| id | UUID | 条目ID | ✅ | ✅ |
| title | String(200) | 标题 | ✅ | ✅ |
| content | Text | 内容 | ✅ | ❌ |
| tags | JSON | 标签 | ✅筛选 | ❌ |
| priority | Integer | 优先级 | ❌ | ✅ |
| status | String | 状态(active/draft/archived) | ✅筛选 | ✅ |
| created_by | UUID | 创建者 | ✅筛选 | ❌ |
| created_at | DateTime | 创建时间 | ✅范围 | ✅ |
| updated_at | DateTime | 更新时间 | ❌ | ✅ |

**操作**: 新增、编辑、删除、启用/禁用

---

## 21. 集合点管理

**数据表**: `convergence_points`

| 字段 | 类型 | 说明 | 可编辑 |
|------|------|------|--------|
| id | UUID | 集合点ID | ❌ |
| script_id | UUID | 所属剧本 | ❌ |
| chapter | Integer | 章节号 | ✅ |
| title | String(255) | 标题 | ✅ |
| description | Text | 描述 | ✅ |
| required_rounds | JSON | 所需轮数配置 | ✅ |
| scene_id | UUID | 关联场景 | ✅ |
| content | JSON | 内容配置 | ✅ |
| is_final | Boolean | 是否最终集合点 | ✅ |
| created_at | DateTime | 创建时间 | ❌ |
| updated_at | DateTime | 更新时间 | ❌ |

**操作**: 新增、编辑、删除

---

## 22. 用户画像

**数据表**: `user_personas`

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | UUID | 用户ID |
| chat_style | Text | 聊天风格偏好 |
| preferences | JSON | 偏好设置 |
| fav_characters | JSON | 喜爱角色 |
| total_chats | Integer | 总对话数 |
| avg_session_duration | Integer | 平均会话时长(秒) |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

**操作**: 查看详情、手动调整

---

## 23. 用户设置

**数据表**: `user_settings`

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | UUID | 用户ID |
| typing_speed | String(20) | 打字速度(slow/normal/fast) |
| auto_play | Boolean | 自动播放 |
| auto_play_delay_ms | Integer | 自动播放延迟(ms) |
| bgm_volume | Integer | 背景音乐音量(0-100) |
| sfx_volume | Integer | 音效音量(0-100) |
| animation_enabled | Boolean | 动画开关 |
| animation_quality | String(20) | 动画质量(low/medium/high) |
| notification_cg_unlock | Boolean | CG解锁通知 |
| notification_affection | Boolean | 好感度通知 |
| notification_new_script | Boolean | 新剧本通知 |
| update_notify | Boolean | 更新通知 |
| activity_reminder | Boolean | 活动提醒 |
| checkin_push | Boolean | 签到推送 |

**操作**: 查看详情、重置为默认

---

## 24. 登录设备管理

**数据表**: `login_devices`

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | UUID | 用户ID |
| device_name | String(255) | 设备名称 |
| device_type | String(50) | 设备类型(mobile/desktop/tablet) |
| browser | String(100) | 浏览器 |
| os | String(100) | 操作系统 |
| ip_address | String(50) | IP地址 |
| location | String(255) | 位置 |
| refresh_token_hash | String(255) | Token哈希 |
| last_active_at | DateTime | 最后活跃 |
| is_current | Boolean | 当前设备 |
| created_at | DateTime | 首次登录 |

**操作**: 查看详情、强制下线

---

## 25. 分享卡片管理

**数据表**: `share_cards`

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | UUID | 用户ID |
| share_type | String(50) | 类型(game_result/affection/achievement) |
| title | String(255) | 标题 |
| description | Text | 描述 |
| image_url | Text | 图片URL |
| extra_data | JSON | 额外数据 |
| created_at | DateTime | 创建时间 |

**操作**: 查看详情、删除

---

## 26. 付费墙事件

**数据表**: `paywall_events`

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | UUID | 用户ID |
| scene | String(30) | 触发场景 |
| display_type | String(10) | 展示类型 |
| triggered_at | DateTime | 触发时间 |

**scene 枚举**: dialogue_quota, gift_limit, script_lock, chat_limit

**操作**: 查看统计、分析转化

---

## 27. Discord 集成配置

**数据表**: `discord_configs`

| 字段 | 类型 | 说明 | 可编辑 |
|------|------|------|--------|
| id | UUID | 配置ID | ❌ |
| webhook_url | String(512) | Webhook URL | ✅ |
| channel_name | String(100) | 频道名称 | ✅ |
| enabled | Boolean | 是否启用 | ✅ |
| events | JSON | 监听事件列表 | ✅ |
| created_at | DateTime | 创建时间 | ❌ |
| updated_at | DateTime | 更新时间 | ❌ |

**events 枚举**: ending_unlocked, achievement_unlocked, user_signup, subscription_change

**操作**: 新增、编辑、删除、测试发送

---

## 28. 数据统计仪表盘

### 28.1 概览面板

| 统计项 | 数据来源 | 展示方式 |
|--------|----------|----------|
| 注册用户总数 | users COUNT | 数字卡片 |
| 今日活跃用户 | users WHERE last_login = today | 数字卡片 |
| 今日新注册 | users WHERE created_at = today | 数字卡片 |
| 活跃游戏会话 | game_sessions WHERE status='active' | 数字卡片 |
| 今日对话数 | dialogue_history WHERE created_at = today | 数字卡片 |
| 今日碎片流通 | fragment_transactions SUM(ABS(amount)) | 数字卡片 |

### 28.2 用户增长趋势

| 指标 | 数据来源 | 图表类型 |
|------|----------|----------|
| 每日新注册用户 | users GROUP BY DATE(created_at) | 折线图 |
| 订阅等级分布 | users GROUP BY subscription_tier | 饼图 |
| 用户活跃度分布 | users GROUP BY last_login 区间 | 柱状图 |

### 28.3 剧本统计

| 指标 | 数据来源 | 图表类型 |
|------|----------|----------|
| 各剧本游玩人数 | game_sessions GROUP BY script_id | 柱状图 |
| 各剧本完成率 | completed/total GROUP BY script_id | 进度条 |
| 结局解锁分布 | game_sessions GROUP BY ending_type | 饼图 |
| 热度排行 | scripts ORDER BY hot_value | 排行榜 |

### 28.4 收入统计

| 指标 | 数据来源 | 图表类型 |
|------|----------|----------|
| 每日碎片发放 | fragment_transactions WHERE amount>0 | 折线图 |
| 每日碎片消费 | fragment_transactions WHERE amount<0 | 折线图 |
| 送礼消费排行 | gift_records GROUP BY user_id | 排行榜 |
| 订阅收入 | purchases GROUP BY month | 柱状图 |

### 28.5 角色统计

| 指标 | 数据来源 | 图表类型 |
|------|----------|----------|
| 角色好感度分布 | affection GROUP BY character_id | 箱线图 |
| 最受欢迎角色 | affection ORDER BY value DESC | 排行榜 |
| 角色对话次数 | dialogue_history GROUP BY character_id | 柱状图 |

---

## 附录A: 数据表总览

| 序号 | 数据表 | 所属模块 | 主要用途 |
|------|--------|----------|----------|
| 1 | users | 用户管理 | 用户账号信息 |
| 2 | password_resets | 用户管理 | 密码重置令牌 |
| 3 | oauth_accounts | 用户管理 | 第三方登录绑定 |
| 4 | scripts | 剧本管理 | 剧本基础信息 |
| 5 | routes | 剧本管理 | 章节/路线 |
| 6 | nodes | 剧本管理 | 剧情节点 |
| 7 | node_choices | 剧本管理 | 选择项 |
| 8 | characters | 角色管理 | 角色信息 |
| 9 | character_sprites | 角色管理 | 角色立绘 |
| 10 | subscription_plans | 订阅管理 | 订阅记录 |
| 11 | fragments | 碎片管理 | 碎片余额 |
| 12 | fragment_transactions | 碎片管理 | 碎片交易记录 |
| 13 | purchases | 支付管理 | 购买记录 |
| 14 | gifts | 礼物管理 | 礼物商城 |
| 15 | gift_records | 礼物管理 | 送礼记录 |
| 16 | affection | 好感度 | 当前好感度 |
| 17 | affection_history | 好感度 | 好感度变化历史 |
| 18 | game_sessions | 游戏会话 | 游戏会话 |
| 19 | game_progress | 游戏会话 | 游戏进度 |
| 20 | dialogue_history | 对话记录 | 对话历史 |
| 21 | free_chat_sessions | 自由对话 | 自由对话会话 |
| 22 | chat_messages | 社区聊天 | 聊天消息 |
| 23 | chat_topics | 社区聊天 | 聊天话题 |
| 24 | save_snapshots | 存档 | 游戏存档 |
| 25 | daily_checkins | 签到 | 每日签到 |
| 26 | streak_records | 签到 | 连续签到记录 |
| 27 | daily_tasks | 每日任务 | 任务进度 |
| 28 | dialogue_quotas | 对话额度 | 每日对话额度 |
| 29 | achievements | 成就 | 用户成就 |
| 30 | user_achievement_claims | 成就 | 成就奖励领取 |
| 31 | activity_chest_claims | 成就 | 活跃度宝箱 |
| 32 | cg_assets | CG管理 | CG资源 |
| 33 | unlocked_cgs | CG管理 | 用户CG解锁 |
| 34 | unlock_records | 解锁记录 | 通用解锁记录 |
| 35 | character_memories | 记忆系统 | 角色记忆 |
| 36 | posts | 社区 | 帖子 |
| 37 | comments | 社区 | 评论 |
| 38 | post_likes | 社区 | 点赞 |
| 39 | shop_goods | 商城 | 商品 |
| 40 | user_goods | 商城 | 用户物品 |
| 41 | scene_configs | 场景配置 | 场景配置 |
| 42 | lorebook_entries | 知识库 | 知识库条目 |
| 43 | convergence_points | 集合点 | 剧情集合点 |
| 44 | user_personas | 用户画像 | 用户画像 |
| 45 | user_settings | 用户设置 | 用户偏好设置 |
| 46 | login_devices | 登录设备 | 登录设备记录 |
| 47 | share_cards | 分享 | 分享卡片 |
| 48 | paywall_events | 付费墙 | 付费墙触发事件 |
| 49 | discord_configs | Discord | Discord集成配置 |
| 50 | user_character_unlocks | 角色管理 | 角色解锁记录 |
| 51 | user_preferences | 用户设置 | 用户偏好 |
| 52 | user_dialogue_counts | 对话统计 | 用户对话计数 |
| 53 | recall_emails | 召回 | 召回邮件记录 |

---

## 附录B: 技术栈建议

### 前端
- Vue 3 + TypeScript
- Element Plus / Ant Design Vue
- Vue Router
- Pinia
- Axios
- ECharts / D3.js (图表)

### 后端
- FastAPI (复用现有)
- SQLAlchemy ORM
- JWT认证 + RBAC权限
- Redis缓存

### 部署
- Docker容器化
- Nginx反向代理
- 独立域名 admin.example.com

---

## 文档信息

- 版本: v2.0
- 日期: 2026-08-05
- 数据表总数: 53
- 功能模块: 28
- 状态: 初稿完成