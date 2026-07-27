# PRD — CR-002 Isekai Wanderer P1 功能补齐 + P0 测试补齐

## 变更概述

CR-001 MVP 已通过全流程 13 阶段并部署上线。CR-002 补齐 CR-001 中 deferred 的 P1 功能（8 项）和 P0 测试（10 项），使产品从 MVP 提升到完整可用状态。

## 变更目标

1. **P1 功能开发**：补齐 8 项 deferred P1 功能模块
2. **P0 测试补齐**：补齐 10 项 deferred P0 测试用例，验证已有功能
3. **邮件相关 mock 实现**：不接入真实邮件服务，使用 mock 实现

## 范围

### Phase 1：P1 功能开发（8 项）

按优先级排序，全部完成后再进入 Phase 2。

| AC | 功能 | 优先级 | 说明 | 类型 |
|---|---|---|---|---|
| AC-045 | 路线图探索 | P1 | 剧本完成后查看已探索/未探索分支，高亮已探索，灰色未探索 | FE 新功能 |
| AC-047 | 密码重置 | P1 | 忘记密码→生成重置链接→mock 邮件发送→重置密码 | BE 新 API + FE 页面 |
| AC-048 | 情绪节奏 | P1 | 情绪标签驱动打字速度（紧张→快/温馨→慢）+ BGM 音量联动 | FE 增强 |
| AC-052 | 国际化 i18n | P1 | vue-i18n 接入，中英文切换，设置页语言选项 | FE 新功能 |
| AC-054 | SEO | P1 | 页面 meta 标签（title/description/og:image）+ sitemap.xml + robots.txt | FE 配置 |
| AC-055 | Discord 集成 | P1 | Discord Bot webhook，结局解锁时发送通知到指定频道 | BE 新服务 |
| AC-056 | PWA 通知 | P1 | Service Worker Notification API 权限提示 + 推送通知 | FE 新功能 |
| AC-057 | 召回邮件 | P1 | 7 天未登录自动触发召回邮件（mock 实现），含游戏链接和进度摘要 | BE cron + mock 邮件 |
| AC-058 | 自由对话模式 | P1 | 剧本外 5 个预设话题 + LLM 角色约束生成对话 | BE 新 API + FE 页面 |

### Phase 2：P0 测试补齐（10 项）

功能已在 CR-001 中实现，只需补测试用例和验证。

| AC | 内容 | 测试类型 | 说明 |
|---|---|---|---|
| AC-008 | 坏结局重新开始流程 | Browser E2E | Playwright 触发坏结局→点击重新开始→验证进度重置 |
| AC-015 | 角色立绘表情切换性能（≤200ms） | Performance | 测量 CSS transition 时间 |
| AC-016 | 背景图淡入切换性能（≤500ms） | Performance | 测量 CSS transition 时间 |
| AC-017 | 场景切换 BGM 跟随 | Browser E2E | 验证 BGM 淡入淡出跟随场景切换 |
| AC-018 | 打字效果帧率（≥30fps） | Performance | rAF 帧率测量 |
| AC-019 | Lighthouse CI 首屏性能（3G Fast <3s） | Performance | Lighthouse CI 自动化 |
| AC-028 | 签到阶梯奖励种子数据 | Unit + Delivery | 种子数据驱动 Day 3/7/14/30 奖励测试 |
| AC-029 | 签到月历 UI | Browser E2E | 月历展示 + 已签到标记 |
| AC-034 | 首玩 AI 失败兜底 | Unit | MockProvider 失败率统计 <5% |
| AC-041 | 订阅到期降级 + 取消 | Unit + Delivery | 时间模拟到期/取消后权益降级 |

### 排除项（暂不测试）

| AC | 内容 | 排除原因 |
|---|---|---|
| AC-022 | 邮箱验证链接 | 未接入真实邮件服务，CR-001 已标记 auto-verify enabled |

## 成功标准

1. Phase 1 全部 8 项 P1 功能开发完成，通过 QA 验证
2. Phase 2 全部 10 项 P0 测试补齐，测试通过
3. CI/CD 全绿：pytest + vitest + build + E2E
4. Delivery E2E Mock API=no
5. Browser E2E Mock API=no
6. 无 P0/P1 阻塞缺陷
7. 部署后冒烟测试通过

## 技术约束

- **邮件服务**：AC-047 和 AC-057 使用 mock 实现，不接入真实 SMTP
- **LLM**：AC-058 自由对话使用现有 LLM Gateway（当前 mock provider）
- **Discord**：AC-055 使用 mock webhook，不配置真实 Bot token
- **i18n**：AC-052 仅中英文，不扩展其他语言
- **性能测试**：AC-015~AC-019 使用 Playwright performance API + Lighthouse CI
- **架构不变**：不改变 CR-001 的全栈架构（FastAPI + Vue3 + PostgreSQL + Redis）

## 影响范围

- 前端：Vue3 + vue-i18n + Service Worker + meta 标签
- 后端：FastAPI 新 API（password-reset, free-chat, discord, recall-email）
- 数据库：新增/修改表（password_resets, free_chat_sessions, discord_configs, recall_emails）
- 部署：无新增基础设施依赖（mock 实现）

## 风险

1. **P1 功能范围蔓延**：8 项 P1 功能可能引入额外复杂度 → 严格按 AC 验收标准执行
2. **性能测试环境差异**：开发机性能与生产环境不同 → 记录测试环境配置
3. **i18n 覆盖不完整**：硬编码文本可能遗漏 → 全量扫描 + 逐页面验证
4. **mock 邮件服务**：mock 实现与真实行为可能有差异 → 明确标记 [Mock]

## 验收项映射

| CR-001 AC | CR-002 阶段 | 处理方式 |
|---|---|---|
| AC-045 | Phase 1 | 新功能开发 |
| AC-047 | Phase 1 | 新功能开发（mock 邮件） |
| AC-048 | Phase 1 | 新功能开发 |
| AC-052 | Phase 1 | 新功能开发 |
| AC-054 | Phase 1 | 新功能开发 |
| AC-055 | Phase 1 | 新功能开发（mock webhook） |
| AC-056 | Phase 1 | 新功能开发 |
| AC-057 | Phase 1 | 新功能开发（mock 邮件） |
| AC-058 | Phase 1 | 新功能开发 |
| AC-008 | Phase 2 | 补测试 |
| AC-015~AC-019 | Phase 2 | 补性能测试 |
| AC-028 | Phase 2 | 补测试 |
| AC-029 | Phase 2 | 补 E2E |
| AC-034 | Phase 2 | 补单元测试 |
| AC-041 | Phase 2 | 补测试 |
