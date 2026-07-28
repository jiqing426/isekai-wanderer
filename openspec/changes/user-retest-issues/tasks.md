# OpenSpec Tasks: CR-018 用户复测问题修复

> 创建时间：2026-07-26 | 状态：已完成 | 关联 proposal: `openspec/changes/user-retest-issues/proposal.md`

---

## 任务总览

本 change 的任务详情定义在 `workflow/changes/CR-018/tasks.md`，包含 27 个主任务 + 5 个补充任务 + 5 个 QA 验证项。以下为 OpenSpec 格式的任务元数据补充。

---

## P0 任务（阻塞发布）

### T-001: 修复送礼接口 400 错误
| 元数据 | 值 |
|--------|-----|
| 负责人 | BE |
| 允许写入范围 | `backend/app/api/v1/gift.py`, `backend/app/services/` |
| 验证方式 | 端到端送礼流程：选择角色→送礼→碎片扣减→好感度增加 |
| 回滚方案 | 回退 gift.py 到上一版本，接口恢复原有行为 |

### T-002: 修复剧本内自由对话 401 错误
| 元数据 | 值 |
|--------|-----|
| 负责人 | BE |
| 允许写入范围 | `backend/app/api/v1/chat.py`, `backend/app/services/free_chat_service.py` |
| 验证方式 | 从剧本页面发起自由对话，验证返回 AI 回复 |
| 回滚方案 | 回退 chat.py 鉴权逻辑 |

### T-003 / T-029: 修复头像上传失败
| 元数据 | 值 |
|--------|-----|
| 负责人 | BE |
| 允许写入范围 | `backend/app/api/v1/users.py`, nginx 配置 |
| 验证方式 | 设置页面上传新头像，页面立即显示 |
| 回滚方案 | 回退 users.py + nginx 配置 |

---

## P1 任务（功能逻辑）

### T-004: 好感度实时更新
| 元数据 | 值 |
|--------|-----|
| 负责人 | BE + FE |
| 允许写入范围 | BE: `narrative_engine.py`; FE: `GameView.vue`, `affection-display.vue` |
| 验证方式 | 做出选择后好感度立即更新，无需刷新 |
| 回滚方案 | 回退 process_choice 响应结构和前端更新逻辑 |

### T-005: 自由对话历史持久化
| 元数据 | 值 |
|--------|-----|
| 负责人 | BE + FE |
| 允许写入范围 | BE: `free_chat_service.py`; FE: `GameView.vue` |
| 验证方式 | 重新进入自由对话，历史记录仍在 |
| 回滚方案 | 回退 session 复用逻辑 |

### T-006: 剧本流程过短修复
| 元数据 | 值 |
|--------|-----|
| 负责人 | BE |
| 允许写入范围 | `backend/app/services/narrative_engine.py`, mock 剧本数据 |
| 验证方式 | 完整游戏流程至少 5-8 轮对话 |
| 回滚方案 | 回退节点流转逻辑和 mock 数据 |

### T-007: 剧本进度记录 & 展示
| 元数据 | 值 |
|--------|-----|
| 负责人 | BE + FE |
| 允许写入范围 | BE: `ending_progress.py`; FE: `progress-row.vue` |
| 验证方式 | 每次选择后进度条变化 |
| 回滚方案 | 回退进度写入和展示逻辑 |

### T-008: UUID v4 数据迁移
| 元数据 | 值 |
|--------|-----|
| 负责人 | DBA / BE |
| 允许写入范围 | `migrations/uuid_v4_migration.sql`, 种子数据文件 |
| 验证方式 | 所有角色/剧本 ID 为 UUID v4 格式；外键引用完整 |
| 回滚方案 | 从备份恢复迁移前数据 |

### T-009: 完成剧本统计修正
| 元数据 | 值 |
|--------|-----|
| 负责人 | BE |
| 允许写入范围 | `backend/app/api/v1/users.py` |
| 验证方式 | 完成剧本数 = COUNT DISTINCT script_id |
| 回滚方案 | 回退统计查询逻辑 |

### T-010: 累计获得碎片为 0 修复
| 元数据 | 值 |
|--------|-----|
| 负责人 | BE |
| 允许写入范围 | `backend/app/api/v1/shards.py`, `backend/app/services/sign.py` |
| 验证方式 | 累计获得 = 所有签到/奖励碎片之和 |
| 回滚方案 | 回退查询和创建逻辑 |

### T-011: 对话额度重置确认
| 元数据 | 值 |
|--------|-----|
| 负责人 | BE |
| 允许写入范围 | `backend/app/services/subscription.py` |
| 验证方式 | 额度显示正确，08:00 重置生效 |
| 回滚方案 | 回退额度配置 |

### T-026: 碎片商城收支明细中文化
| 元数据 | 值 |
|--------|-----|
| 负责人 | FE |
| 允许写入范围 | `frontend/src/locales/zh-CN.ts`, `FragmentMallView.vue` |
| 验证方式 | 所有收支明细显示中文 |
| 回滚方案 | 回退 i18n 映射 |

### T-028: 帖子详情页浏览量统计
| 元数据 | 值 |
|--------|-----|
| 负责人 | BE |
| 允许写入范围 | `backend/app/api/v1/community.py` |
| 验证方式 | 进入帖子详情浏览量 +1，刷新保持，防刷 |
| 回滚方案 | 回退浏览量逻辑 |

### T-030: 会员账单显示所有交易
| 元数据 | 值 |
|--------|-----|
| 负责人 | BE + FE |
| 允许写入范围 | BE: `subscription.py`; FE: `SettingsView.vue` |
| 验证方式 | 账单列表显示充值/兑换/送礼/签到等所有类型 |
| 回滚方案 | 回退查询过滤和前端渲染 |

---

## P2 任务（UI/展示）

### T-012: AI 叙事 loading 状态
| 负责人 | FE | 允许写入范围 | `GameView.vue` | 验证方式 | AI 叙事时显示 loading 动画 |

### T-013: 性格 loyal 映射中文
| 负责人 | FE | 允许写入范围 | `zh-CN.ts`, `CharacterDetailView.vue` | 验证方式 | 性格特质显示中文 |

### T-014: 性格特点数据补全
| 负责人 | BE + FE | 允许写入范围 | BE: `characters.py`; FE: `CharacterDetailView.vue` | 验证方式 | 角色详情页展示 personality |

### T-015: 语音试听功能
| 负责人 | FE | 允许写入范围 | `CharacterDetailView.vue` | 验证方式 | 有试听按钮，未解锁显示锁定 |

### T-016: 成就卡片 JSON 展示
| 负责人 | FE | 允许写入范围 | `AchievementView.vue` | 验证方式 | 成就卡片显示格式化中文描述 |

### T-017: 碎片商城 Tab 样式
| 负责人 | FE | 允许写入范围 | `FragmentMallView.vue` | 验证方式 | Tab 在顶部，样式与社区一致 |

### T-018: 碎片收支明细
| 负责人 | BE + FE | 允许写入范围 | BE: `shards.py`; FE: `FragmentMallView.vue` | 验证方式 | 展示签到/送礼等交易流水 |

### T-019: 个人中心对话次数展示
| 负责人 | FE | 允许写入范围 | `PersonalCenterView.vue` | 验证方式 | 显示今日对话次数/总额度 |

### T-020: AI 记忆 Invalid Date 修复
| 负责人 | FE | 允许写入范围 | `PersonalCenterView.vue` | 验证方式 | 日期正确显示或"未知时间"；列表可滚动 |

### T-021: 角色羁绊英文翻译
| 负责人 | FE | 允许写入范围 | `zh-CN.ts`, `CharacterDetailView.vue` | 验证方式 | 好感度等级显示中文 |

### T-022: 账单中文映射
| 负责人 | FE | 允许写入范围 | `zh-CN.ts`, `SettingsView.vue` | 验证方式 | 账单类型显示中文 |

### T-023: 社区浏览量记录
| 负责人 | BE | 允许写入范围 | `community.py` | 验证方式 | 同 T-028 |

### T-024: 封面图/头像尺寸优化
| 负责人 | FE | 允许写入范围 | 相关 view 组件 | 验证方式 | 不同屏幕自适应 |

### T-025: 前端中文 i18n 补全
| 负责人 | FE | 允许写入范围 | `zh-CN.ts` | 验证方式 | 页面无裸英文 key |

### T-027: 碎片获取"成就奖励"跳转成就页
| 负责人 | FE | 允许写入范围 | `FragmentMallView.vue` | 验证方式 | 点击跳转到成就页 |

---

## QA 验证项

| ID | 功能 | 测试要求 | 优先级 |
|----|------|----------|--------|
| V-001 | 剧本对话限制 | 额度扣减 + 用完阻止 | P0 |
| V-002 | 成就系统 | 解锁/显示/领取 | P1 |
| V-003 | CG 获取动效 | 动效展示 | P2 |
| V-004 | 对话扣费 | 游玩时扣费正常 | P0 |
| V-005 | 完整游戏流程 | 开始→对话→选择→结局→统计 | P0 |

---

## 回滚总方案

- 所有修改通过 git 管理，可按 commit 粒度回退
- UUID 迁移有完整备份，可恢复迁移前状态
- 前端构建产物可按版本号回退
- 无数据库 schema 变更，回滚风险低
