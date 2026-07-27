# Spec: 剧本发现与推荐系统（P0）

### Requirement: REQ-DISC-001 发现页入口

#### 需求描述
用户可访问 `/discover` 路由，进入剧本发现页面。页面包含推荐区、分类筛选区、热度排行区三个逻辑区域。

#### Scenario: 发现页入口场景

| ID | Scenario | Given | When | Then |
|----|---------|-------|------|------|
| AC-DISC-001.1 | 未登录用户访问发现页 | 用户未登录 | 访问 `/discover` | 页面正常加载，剧本列表可浏览；点击"开始游戏"或"继续玩"时跳转登录页 |
| AC-DISC-001.2 | 已登录用户访问发现页 | 用户已登录 | 访问 `/discover` | 页面加载，显示个性化推荐、分类筛选、热度排行三个区域 |
| AC-DISC-001.3 | 发现页空状态 | 无剧本数据 | 访问 `/discover` | 显示空状态提示，引导用户等待内容更新 |

## REQ-DISC-002: 智能推荐

### 需求描述
根据用户已玩剧本类型和角色好感度偏好，推荐相似剧本。推荐结果按匹配度排序，fallback 为热度排序。

### Scenarios

| ID | Scenario | Given | When | Then |
|----|---------|-------|------|------|
| AC-DISC-002.1 | 有行为数据用户看推荐 | 用户已玩过至少 1 个剧本 | 访问 `/discover` | 推荐区显示"因为你玩了《XX》"等可解释推荐理由的剧本卡片 |
| AC-DISC-002.2 | 新用户看推荐（冷启动） | 用户无游玩记录 | 访问 `/discover` | 推荐区显示热度最高的剧本（fallback 策略） |
| AC-DISC-002.3 | 推荐数据为空 | 无剧本可推荐 | 访问 `/discover` | 推荐区显示"暂无推荐，快去探索剧本库" |

### 推荐规则约束（需求层）
- 优先匹配：用户 `preferred_genre` + 高好感度角色的 `script_tags`
- Fallback：`script_stats.play_count` 降序
- 推荐理由必须可解释（"因为你玩了《XX》"或"热门剧本"）
- 已玩剧本不重复推荐

## REQ-DISC-003: 分类筛选

### 需求描述
用户可按类型（恋爱/奇幻/悬疑/科幻）、标签（HE/BE/多结局）、难度（新手/进阶/硬核）筛选剧本列表。

### Scenarios

| ID | Scenario | Given | When | Then |
|----|---------|-------|------|------|
| AC-DISC-003.1 | 按类型筛选 | 用户在发现页 | 选择"恋爱"类型 | 列表只显示 `script_tags` 含 `genre=romance` 的剧本 |
| AC-DISC-003.2 | 按标签筛选 | 用户在发现页 | 选择"多结局"标签 | 列表只显示 `script_tags` 含 `theme=multiple_endings` 的剧本 |
| AC-DISC-003.3 | 按难度筛选 | 用户在发现页 | 选择"新手"难度 | 列表只显示 `scripts.difficulty='beginner'` 的剧本 |
| AC-DISC-003.4 | 组合筛选 | 用户在发现页 | 同时选择"恋爱"+"HE" | 列表显示同时满足两个条件的剧本 |
| AC-DISC-003.5 | 筛选无结果 | 用户在发现页 | 选择不存在的组合 | 显示"无匹配剧本，试试其他筛选条件" |

### 筛选交互约束
- 筛选条件变更时列表实时更新（无需"提交"按钮）
- 支持多选标签（最多 3 个）
- 提供"清除筛选"一键重置

## REQ-DISC-004: 热度排行

### 需求描述
展示剧本热度 Top 10 列表，支持按游玩人数、评分、收藏数排序。

### Scenarios

| ID | Scenario | Given | When | Then |
|----|---------|-------|------|------|
| AC-DISC-004.1 | 按游玩人数排序 | 用户在发现页排行区 | 点击"最多人玩" | 列表按 `script_stats.play_count` 降序显示 Top 10 |
| AC-DISC-004.2 | 按评分排序 | 用户在发现页排行区 | 点击"最高评分" | 列表按 `script_stats.rating` 降序显示 Top 10 |
| AC-DISC-004.3 | 按收藏数排序 | 用户在发现页排行区 | 点击"最多收藏" | 列表按 `script_stats.favorite_count` 降序显示 Top 10 |
| AC-DISC-004.4 | 排行数据为空 | 新平台无数据 | 访问排行区 | 显示"暂无排行数据" |

## REQ-DISC-005: "继续玩"模块（首页）

### 需求描述
首页顶部显示大卡片，展示用户最近一次未完成的剧本，一键继续游戏。

### Scenarios

| ID | Scenario | Given | When | Then |
|----|---------|-------|------|------|
| AC-DISC-005.1 | 有未完成 session | 用户有 `status=in_progress` 的 session | 访问首页 | 顶部显示大卡片：剧本封面 + 剧本名 + 最后游玩节点名 + "继续游戏"按钮 |
| AC-DISC-005.2 | 多个未完成 session | 用户有多个未完成 session | 访问首页 | 显示 `updated_at` 最大的那条 session |
| AC-DISC-005.3 | 所有 session 已完成 | 用户所有 session `status=completed` | 访问首页 | 不显示继续玩卡片；显示"重新开始"入口（跳转剧本列表） |
| AC-DISC-005.4 | 无 session | 用户从未开始游戏 | 访问首页 | 不显示继续玩卡片；显示"开始你的第一次冒险"引导 |
| AC-DISC-005.5 | 点击继续游戏 | 继续玩卡片显示 | 点击"继续游戏"按钮 | 跳转到 `/game/:sessionId`，从上次节点继续 |

### "继续玩"展示策略（Q2 确认）
- 选择规则：`game_sessions.updated_at DESC`，`status='in_progress'`
- `status='completed'` 的 session 不显示继续玩
- 卡片内容：剧本封面图 + 剧本标题 + 当前节点名 + 游玩进度百分比

## 数据模型需求

| 表 | 用途 | 关键字段 |
|----|------|---------|
| `scripts`（扩展） | 剧本元数据 | +`difficulty`, +`cover_image_url`, +`description`, +`estimated_duration` |
| `script_tags`（新建） | 剧本标签 | `script_id FK`, `tag`, `tag_type ENUM('genre','theme','difficulty')` |
| `script_stats`（新建） | 剧本统计 | `script_id FK UNIQUE`, `play_count`, `rating`, `favorite_count` |

## 路由需求

| 路由 | 用途 | Auth |
|------|------|------|
| `/discover` | 发现页 | Optional（未登录可浏览，操作需登录） |

## 验收动作标注

- **Browser Interaction E2E**：所有 AC 涉及页面跳转、筛选交互、按钮点击，需 Playwright E2E 验证
- **API/DB 验证**：筛选结果需真实后端返回数据，不得用 mock 静态数据
