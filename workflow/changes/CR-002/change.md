# Change

## 变更单

| 项 | 内容 |
| --- | --- |
| CR 编号 | CR-002 |
| 来源 | CEO 指令 |
| 类型 | feature + test |
| 优先级 | P1（功能开发）+ P0（测试补齐） |
| 当前状态 | gate-review |
| 负责人 | pl |
| 关联 PRD | `docs/prd/cr-002-prd.md` |
| 关联 OpenSpec Change | `openspec/changes/CR-002-p1-p0-补齐-20260719/` |

## 问题和目标

- 现状：CR-001 MVP 已通过全流程并部署上线，但 59 项验收项中 16 项 deferred_with_approval，其中 9 项 P1 功能未开发、10 项 P0 测试未运行。
- 目标：补齐 CR-001 deferred 的 P1 功能（9 项）和 P0 测试（10 项），使产品从 MVP 提升到完整可用状态。
- 成功标准：Phase 1 全部 9 项 P1 功能开发完成通过 QA，Phase 2 全部 10 项 P0 测试补齐通过，CI/CD 全绿，Delivery E2E 和 Browser E2E Mock API=no，无 P0/P1 阻塞缺陷，部署后冒烟测试通过。
- 本次不做：AC-022 邮箱验证链接、真实支付网关、真实 OAuth、管理后台。

## 原始 PRD

CEO 指令（2026-07-19）：

Phase 1（P1 功能开发，8 项，全部完成后再进 Phase 2）：
- AC-045 路线图探索
- AC-047 密码重置（mock 邮件）
- AC-048 情绪节奏（打字速度+BGM）
- AC-052 国际化 i18n
- AC-054 SEO（meta + sitemap）
- AC-055 Discord 集成（mock webhook）
- AC-056 PWA 通知
- AC-057 召回邮件（mock）
- AC-058 自由对话模式

Phase 2（P0 测试补齐，10 项）：
- AC-008 坏结局重新开始
- AC-015 立绘表情切换 ≤200ms
- AC-016 背景图淡入 ≤500ms
- AC-017 BGM 跟随切换
- AC-018 打字效果 ≥30fps
- AC-019 Lighthouse CI 3G Fast <3s
- AC-028 签到阶梯奖励
- AC-029 签到月历 UI
- AC-034 首玩 AI 失败兜底
- AC-041 订阅到期降级

## OpenSpec Change 生成

- PM 根据本文件创建或更新对应 OpenSpec change：`proposal.md`、`specs/**/spec.md`；同时维护 `docs/prd/cr-002-prd.md` 摘要和 `acceptance.md`。
- 未确认内容必须以 Q 编号登记；非阻塞问题可以记录为暂缓，不得伪装为已确认事实。
- OpenSpec change 或 workflow 追踪文件不完整时，不能直接让关口 `passed`。

## 影响范围

| 领域 | 是否影响 | 说明 |
| --- | --- | --- |
| 架构 / 模块边界 | 否 | 架构不变，增量开发 |
| API / 契约 | 是 | 4 新 API + 1 cron |
| 数据库 / 迁移 | 是 | 3 新表（password_resets, free_chat_sessions, recall_emails） |
| 权限 / 安全 / 隐私 | 是 | SECURITY 阶段审查；mock 服务无真实外部依赖，风险低 |
| 前端 / 管理端体验 | 是 | 8 项 FE 新功能 |
| 测试 / 验收 | 是 | 19 项验收 + 10 项测试补齐 |
| 部署 / 生产 / 回滚 | 是 | DEPLOY 阶段处理；CR-001 已有部署环境，增量部署无风险 |

## 人工确认

| 项 | 是 / 否 | 说明 |
| --- | --- | --- |
| 生产环境变更 | 否 | mock 实现，无真实服务接入 |
| 数据删除或不可逆迁移 | 否 | 仅新增表，无不可逆迁移 |
| 认证、授权或权限边界变更 | 否 | AC-047 密码重置为增量功能 |
| 支付、账务或合规承诺 | 否 | MVP mock 模式 |
| 公共 API 破坏性变更 | 否 | 增量 API，不改变已有 API |
| 大范围跨模块重构 | 否 | 增量开发 |

## 自动入口记录

- 创建时间：2026-07-19T10:00:00Z
- 执行方式：CEO 指令，手动创建 CR 结构
- 初始授权：仅授权创建 CR、记录 PRD、生成初始 workflow / OpenSpec 骨架；不授权自动通过阶段、关口或部署。
- 放行要求：每个推进型流转仍必须由 PL 展示交付物清单、关键结论、缺口和风险，并取得用户明确同意后，才能运行 readiness 并推进。
