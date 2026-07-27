# Test Plan: CR-001 — Isekai Wanderer MVP

## 测试策略

### 测试金字塔

```txt
        ╱╲
       ╱ E2E ╲          Browser Interaction + Delivery E2E
      ╱────────╲        (Playwright + 真实后端)
     ╱ 集成测试  ╲       API 端到端 + DB 事务
    ╱──────────────╲    (pytest + httpx + PostgreSQL)
   ╱    单元测试     ╲   Service 逻辑 + 工具函数
  ╱──────────────────╲ (pytest + Vitest)
```

### 测试类型与覆盖率目标

| 测试类型 | 工具 | 覆盖率目标 | 执行频率 | 负责人 |
|---------|------|-----------|---------|--------|
| 单元测试 | pytest (BE) + Vitest (FE) | 核心模块 ≥80% | 每次 commit | be, fe, ai |
| 集成测试 | pytest + httpx AsyncClient | API 100% 端点 | 每次 PR | be |
| E2E 测试 | Playwright | P0 AC 100% 覆盖 | 每次 PR + 发布前 | qa |
| 性能测试 | Lighthouse + k6 | 首屏 <3s + 流式 ≥30fps | 发布前 | qa |
| AI 输出验证 | pytest + LLM mock | 叙事/记忆/风格 场景覆盖 | 每次 LLM prompt 变更 | ai |
| 安全测试 | OWASP ZAP + 手动 | 认证/授权/注入 | 发布前 | qa |

### Mock 使用策略

| 场景 | 允许 Mock | 必须真实 | 说明 |
|------|----------|---------|------|
| **单元测试** | ✅ LLM Provider / DB / Redis / Email | ❌ 业务逻辑 | Service 层逻辑必须真实 |
| **集成测试** | ❌ 全部真实 | ✅ PostgreSQL + Redis + LLM (test key) | API 端到端必须真实后端 |
| **E2E 测试** | ❌ 禁止 mock API | ✅ 真实前端 + Nginx + 后端 + DB | Delivery E2E 和 Browser E2E 必须全链路 |
| **性能测试** | ❌ 禁止 mock | ✅ 真实环境 | Lighthouse + 真实网络条件 |
| **AI 输出验证** | ✅ LLM mock (确定性输出) | ❌ 生成逻辑 | 验证 prompt 注入和规则校验 |
| **支付/订阅/OAuth** | ✅ IPaymentProvider / ISubscriptionProvider / IOAuthProvider mock 实现 | ❌ 抽象接口 | mock 和真实共用同一接口 |

**关键原则**：Delivery E2E / Release evidence 禁止 mock API。mock 只允许用于支付/订阅/OAuth 的 Provider 实现层。

## Test-First Scope

- 叙事引擎 (DEV-007~009)：Red → Green，先写 pytest 用例（预设节点/拦截/兜底/状态机），再实现 Service
- 记忆系统 (DEV-017)：Red → Green，先写 pgvector 存储/召回/误召回用例，再实现 MemoryService
- 好感度系统 (DEV-010)：Red → Green，先写数值更新/等级升级/持久化用例，再实现 AffectionService
- 用户认证 (DEV-020~022)：Red → Green，先写 JWT/限流/重置用例，再实现 Auth API
- 签到/任务 (DEV-031~032)：Red → Green，先写 UTC 重置/Streak 计算用例，再实现 DailyService
- 支付/订阅 (DEV-034~035)：Red → Green，先写接口契约用例，再实现 mock Provider
- E2E (DEV-053~054)：先写 Playwright spec，再联调验证

## 高风险模块测试计划

### 1. 叙事引擎 (DEV-007, DEV-008)

**风险**：AI 生成违反规则、兜底失败、状态机死锁

#### 单元测试

| 用例 ID | 场景 | 输入 | 预期输出 | 负责人 |
|---------|------|------|---------|--------|
| UT-NE-001 | 预设节点不被修改 | 节点 type=preset | 返回预设内容，不调用 LLM | be |
| UT-NE-002 | 规则引擎拦截违规对话 | AI 输出违反性格约束 | 拦截 + 重试(最多2次) | be |
| UT-NE-003 | 兜底触发 | AI 连续2次失败 | 返回预设兜底对话 | be |
| UT-NE-004 | 状态机跳转 | 当前节点 + 选择 | 正确跳转到下一节点 | be |
| UT-NE-005 | 好感度变化计算 | 选择 +3 | affection.value += 3 | be |

#### 集成测试

| 用例 ID | 场景 | 验证点 |
|---------|------|--------|
| IT-NE-001 | 全流程对话 | POST /game/start → GET /dialogue (SSE) → POST /choice → 验证节点跳转 |
| IT-NE-002 | 剧本数据加载 | GET /scripts/:id 返回完整节点图 |
| IT-NE-003 | 进度持久化 | 选择后 game_progress 表写入 + 刷新后可恢复 |

#### AI 输出验证

| 用例 ID | 场景 | 验证方法 |
|---------|------|---------|
| AI-NE-001 | 角色性格一致性 | 输入角色性格约束 + 对话上下文，检查输出是否包含违规词汇/行为 |
| AI-NE-002 | 记忆注入 | 注入记忆后，检查 LLM prompt 是否包含记忆文本 |
| AI-NE-003 | 情绪标注 | 检查 SSE 输出是否包含 emotion_tag |

### 2. 记忆系统 (DEV-017, DEV-018, DEV-019)

**风险**：向量检索不准、记忆误召回、压缩丢失关键信息

#### 单元测试

| 用例 ID | 场景 | 输入 | 预期输出 |
|---------|------|------|---------|
| UT-MEM-001 | 记忆提取 | 对话文本 "我喜欢向日葵" | 提取出记忆条目 + embedding |
| UT-MEM-002 | 向量存储 | 记忆条目 | pgvector INSERT 成功 |
| UT-MEM-003 | 相似度召回 | 查询 "你喜欢什么花" + 已存 "喜欢向日葵" | 相似度 >0.8，召回 |
| UT-MEM-004 | 不误召回 | 查询 "今天天气" + 已存 "喜欢向日葵" | 相似度 <0.8，不召回 |
| UT-MEM-005 | 记忆压缩 | 10 条相似记忆 | LLM 合并为摘要 + 标记 is_compressed=true |

#### 集成测试

| 用例 ID | 场景 | 验证点 |
|---------|------|--------|
| IT-MEM-001 | 跨会话记忆 | Session A 存储 → Session B 召回 → 验证对话引用 |
| IT-MEM-002 | 多角色隔离 | User A + Char X 的记忆不影响 User A + Char Y |

### 3. 好感度系统 (DEV-010, DEV-015)

**风险**：数值溢出、等级阈值错误、持久化失败

#### 单元测试

| 用例 ID | 场景 | 输入 | 预期输出 |
|---------|------|------|---------|
| UT-AFF-001 | 数值更新 | 当前 35，选择 +3 | 38 |
| UT-AFF-002 | 等级升级 | 19 → 20 | level: acquaintance → ambiguous |
| UT-AFF-003 | 数值上限 | 当前 98，选择 +5 | 100 (不超过) |
| UT-AFF-004 | 持久化 | 更新后刷新 | 数值保留 |

### 4. 用户认证 (DEV-020, DEV-021, DEV-022, DEV-023)

**风险**：JWT 伪造、密码泄露、暴力破解、OAuth mock 绕过

#### 单元测试

| 用例 ID | 场景 | 验证点 |
|---------|------|--------|
| UT-AUTH-001 | 密码哈希 | bcrypt cost=12 + 不可逆 |
| UT-AUTH-002 | JWT 颁发 | Access 15min + Refresh 7d |
| UT-AUTH-003 | JWT 验证 | 过期/伪造/篡改 → 401 |
| UT-AUTH-004 | 登录限流 | 5次失败 → 锁定15min (Redis) |
| UT-AUTH-005 | OAuth mock | Google/Discord mock → 创建账户 + JWT |
| UT-AUTH-006 | IOAuthProvider 接口 | mock 和真实实现可替换 |

#### 集成测试

| 用例 ID | 场景 | 验证点 |
|---------|------|--------|
| IT-AUTH-001 | 注册 → 验证 → 登录 | 全流程 + 邮箱验证链接 |
| IT-AUTH-002 | Token 刷新 | Access 过期 → Refresh → 新 Access |
| IT-AUTH-003 | 密码重置 | 请求 → 邮件 → 重置 → 登录 |

### 5. 签到/任务系统 (DEV-031, DEV-032, DEV-033)

**风险**：UTC 时区错误、Streak 计算错误、奖励重复发放

#### 单元测试

| 用例 ID | 场景 | 验证点 |
|---------|------|--------|
| UT-DAILY-001 | 首次签到 | streak=1 + daily_checkins 写入 |
| UT-DAILY-002 | 连续签到 | 昨日签到 → 今日签到 → streak+1 |
| UT-DAILY-003 | 断签重置 | 昨日未签 → 今日签到 → streak=1 |
| UT-DAILY-004 | 阶梯奖励 | streak=3/7/14/30 → 发放碎片 |
| UT-DAILY-005 | UTC 重置 | UTC 0:00 后任务自动重置 |
| UT-DAILY-006 | 任务进度 | 对话/选择/查看角色 → 进度+1 |
| UT-DAILY-007 | 全完成奖励 | 3/3 任务 → 额外 25 碎片 + Streak 延续 |

### 6. 支付/订阅系统 (DEV-034, DEV-035, DEV-036)

**风险**：mock 实现与真实接口不一致、余额错误、重复扣款

#### 单元测试

| 用例 ID | 场景 | 验证点 |
|---------|------|--------|
| UT-PAY-001 | IPaymentProvider 接口 | mock 实现符合接口定义 |
| UT-PAY-002 | mock 购买 | 余额更新 + 交易流水写入 |
| UT-PAY-003 | 购买历史 | 按时间倒序查询 |
| UT-PAY-004 | ISubscriptionProvider 接口 | mock 实现符合接口定义 |
| UT-PAY-005 | 订阅激活 | 状态=active + 权益生效 |
| UT-PAY-006 | 订阅到期 | 状态=expired + 权益降级 |
| UT-PAY-007 | 取消订阅 | 当前周期结束前权益不变 |
| UT-PAY-008 | 多货币 | USD/EUR/CNY/JPY 价格转换 |

### 7. 视觉呈现 (DEV-024, DEV-025, DEV-026, DEV-027, DEV-028)

**风险**：动画卡顿、表情切换延迟、首屏加载慢

#### E2E 测试 (Playwright)

| 用例 ID | 场景 | 验证点 |
|---------|------|--------|
| E2E-VIS-001 | 表情切换 | SSE emotion_tag → CharacterSprite 切换 ≤200ms |
| E2E-VIS-002 | 背景切换 | 节点 scene 变化 → SceneBackground 淡入 ≤500ms |
| E2E-VIS-003 | BGM 切换 | 场景切换 → AudioPlayer 淡入淡出 |
| E2E-VIS-004 | 流式文字 | SSE text → DialogueBox 打字效果 ≥30fps |
| E2E-VIS-005 | 点击跳过 | 点击对话区域 → 全部文本立即显示 |
| E2E-VIS-006 | 首屏性能 | 3G Fast → Lighthouse Performance ≥70 |

## Delivery E2E / Runtime Smoke Plan

| 任务编号 | 命令 / 步骤 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
|---------|------------|---------|---------|-----------------|---------|-----------|-------------|------|
| DEL-001 | `docker compose up -d && sleep 5 && curl -f http://localhost/api/v1/health` | `http://localhost:3000` | `http://localhost:8000` | `/api/v1/health` | no | AC-004 | `tests/e2e/screenshots/del-001.png` | Planned |
| DEL-002 | `APP_BASE=http://localhost npx playwright test tests/e2e/delivery-smoke.spec.ts -g "register and login"` | `http://localhost:3000` | `http://localhost:8000` | `/api/v1/auth/*` | no | AC-020, AC-023 | `tests/e2e/screenshots/del-002.png` | Planned |
| DEL-003 | `APP_BASE=http://localhost npx playwright test tests/e2e/delivery-smoke.spec.ts -g "start game and play"` | `http://localhost:3000` | `http://localhost:8000` | `/api/v1/game/*` | no | AC-004, AC-005 | `tests/e2e/screenshots/del-003.png` | Planned |
| DEL-004 | `APP_BASE=http://localhost npx playwright test tests/e2e/delivery-smoke.spec.ts -g "choice and affection"` | `http://localhost:3000` | `http://localhost:8000` | `/api/v1/game/*/choice` | no | AC-005, AC-012 | `tests/e2e/screenshots/del-004.png` | Planned |
| DEL-005 | `APP_BASE=http://localhost npx playwright test tests/e2e/delivery-smoke.spec.ts -g "checkin and tasks"` | `http://localhost:3000` | `http://localhost:8000` | `/api/v1/daily/*` | no | AC-026, AC-030 | `tests/e2e/screenshots/del-005.png` | Planned |
| DEL-006 | `APP_BASE=http://localhost npx playwright test tests/e2e/delivery-smoke.spec.ts -g "shop and subscribe"` | `http://localhost:3000` | `http://localhost:8000` | `/api/v1/shop/*` | no | AC-035, AC-039 | `tests/e2e/screenshots/del-006.png` | Planned |

## Browser Interaction E2E Plan

| 任务编号 | 命令 / 步骤 | Browser / Tool | 用户动作 | 前端入口 | 后端地址 | API / Proxy Path | Mock API | 覆盖验收项 | 证据记录位置 | 状态 |
|---------|------------|---------------|---------|---------|---------|-----------------|---------|-----------|-------------|------|
| BR-001 | `APP_BASE=http://localhost:3000 npx playwright test tests/e2e/user-journey.spec.ts --headed --trace on -g "register"` | Chromium (Playwright) | 访问注册页 → 输入邮箱+密码 → 提交 | `http://localhost:3000` | `http://localhost:8000` | `/api/v1/auth/register` | no | AC-020, AC-021 | `tests/e2e/traces/br-001.zip` | Planned |
| BR-002 | `APP_BASE=http://localhost:3000 npx playwright test tests/e2e/user-journey.spec.ts --headed --trace on -g "login"` | Chromium (Playwright) | 登录 → 验证邮箱 → 完成引导 | `http://localhost:3000` | `http://localhost:8000` | `/api/v1/auth/login` | no | AC-022, AC-023, AC-025 | `tests/e2e/traces/br-002.zip` | Planned |
| BR-003 | `APP_BASE=http://localhost:3000 npx playwright test tests/e2e/user-journey.spec.ts --headed --trace on -g "game"` | Chromium (Playwright) | 选择剧本 → 选择路线 → 开始游戏 → 阅读对话 → 做出选择 | `http://localhost:3000` | `http://localhost:8000` | `/api/v1/game/*` | no | AC-004, AC-005, AC-015, AC-018 | `tests/e2e/traces/br-003.zip` | Planned |
| BR-004 | `APP_BASE=http://localhost:3000 npx playwright test tests/e2e/user-journey.spec.ts --headed --trace on -g "affection"` | Chromium (Playwright) | 查看好感度进度条 → 点击展开精确数值 → 验证升级动画 | `http://localhost:3000` | `http://localhost:8000` | `/api/v1/affection/*` | no | AC-012, AC-013, AC-014 | `tests/e2e/traces/br-004.zip` | Planned |
| BR-005 | `APP_BASE=http://localhost:3000 npx playwright test tests/e2e/user-journey.spec.ts --headed --trace on -g "ending"` | Chromium (Playwright) | 继续对话 → 达成结局 → 重新开始 | `http://localhost:3000` | `http://localhost:8000` | `/api/v1/game/*/ending` | no | AC-007, AC-008 | `tests/e2e/traces/br-005.zip` | Planned |
| BR-006 | `APP_BASE=http://localhost:3000 npx playwright test tests/e2e/user-journey.spec.ts --headed --trace on -g "daily"` | Chromium (Playwright) | 签到 → 查看任务面板 → 完成任务 | `http://localhost:3000` | `http://localhost:8000` | `/api/v1/daily/*` | no | AC-026, AC-027, AC-028, AC-030, AC-031 | `tests/e2e/traces/br-006.zip` | Planned |
| BR-007 | `APP_BASE=http://localhost:3000 npx playwright test tests/e2e/user-journey.spec.ts --headed --trace on -g "shop"` | Chromium (Playwright) | 进入商店 → mock购买 → 进入订阅页 → 切换货币 | `http://localhost:3000` | `http://localhost:8000` | `/api/v1/shop/*`, `/api/v1/subscription/*` | no | AC-035, AC-036, AC-039 | `tests/e2e/traces/br-007.zip` | Planned |

## 性能测试计划

### 指标与阈值

| 指标 | 阈值 | 测试工具 | 测试条件 |
|------|------|---------|---------|
| 首屏加载 (FCP) | <3s | Lighthouse | 3G Fast (1.6Mbps) |
| 可交互时间 (TTI) | <5s | Lighthouse | 3G Fast |
| 流式文字帧率 | ≥30fps | Playwright + requestAnimationFrame | 正常网络 |
| 表情切换延迟 | ≤200ms | Playwright + performance.now() | 正常网络 |
| 背景切换延迟 | ≤500ms | Playwright + CSS transition 监听 | 正常网络 |
| API 响应时间 (P95) | <500ms | k6 | 100 并发 |
| LLM 流式首字延迟 | <2s | 真实 GPT-4o-mini 调用 | 正常网络 |

### 负载测试

```bash
# k6 负载测试脚本
k6 run tests/perf/api-load.js --vus 100 --duration 5m
```

**场景**：
- 100 并发用户同时查询剧本列表
- 50 并发用户同时进行游戏对话
- 验证 P95 <500ms + 无 5xx

## 安全测试计划

### 测试项

| 测试项 | 工具 | 验证点 |
|--------|------|--------|
| SQL 注入 | OWASP ZAP + 手动 | 所有 API 参数化查询 |
| XSS | OWASP ZAP | Vue 默认转义 + CSP header |
| CSRF | 手动 | JWT 模式无 cookie → 不需要 CSRF token |
| 认证绕过 | 手动 | 无 token / 过期 token / 伪造 token → 401 |
| 授权绕过 | 手动 | User A 访问 User B 数据 → 403 |
| 暴力破解 | 手动 | 5次失败 → 锁定15min |
| 敏感数据泄露 | 手动 | 日志不记录密码/JWT/邮箱明文 |

## 测试环境

### 本地开发

```bash
# 后端
cd backend && pytest tests/unit tests/integration

# 前端
cd frontend && npm run test:unit && npm run test:e2e
```

### CI/CD 证据计划

```yaml
# .github/workflows/test.yml
jobs:
  test:
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: isekai_test
      redis:
        image: redis:7
    steps:
      - run: cd backend && pytest --cov
      - run: cd frontend && npm run test:unit
      - run: docker compose up -d && npx playwright test
```

### 预发布环境

- 真实 VPS + Docker Compose
- 真实 PostgreSQL + Redis + Nginx
- LLM test key (GPT-4o-mini)
- 完整 E2E + 性能测试

## 测试产物

| 产物 | 路径 | 生成时机 |
|------|------|---------|
| 单元测试报告 | `backend/coverage/` + `frontend/coverage/` | 每次 CI |
| E2E 截图 | `tests/e2e/screenshots/` | 每次 E2E |
| E2E trace | `tests/e2e/traces/` | 每次 E2E |
| Lighthouse 报告 | `tests/perf/lighthouse/` | 发布前 |
| k6 报告 | `tests/perf/k6/` | 发布前 |
| 安全扫描报告 | `tests/security/` | 发布前 |

## 测试负责人

| 角色 | 职责 |
|------|------|
| **be** | 后端单元测试 + 集成测试 |
| **fe** | 前端单元测试 + 组件测试 |
| **ai** | LLM prompt 测试 + 记忆系统测试 |
| **qa** | E2E 测试 + 性能测试 + 安全测试 + 测试报告汇总 |

## 测试进度追踪

| 阶段 | 计划开始 | 计划完成 | 状态 |
|------|---------|---------|------|
| Phase 1-2 单元测试 | Week 2 | Week 5 | Pending |
| Phase 3-4 集成测试 | Week 4 | Week 8 | Pending |
| Phase 5 E2E 测试 | Week 8 | Week 10 | Pending |
| Phase 6 性能+安全测试 | Week 10 | Week 11 | Pending |
| Phase 7 全量回归 | Week 11 | Week 12 | Pending |

## Test Case Artifacts

| Task ID | Test Case Artifact | Acceptance IDs | Status |
|---------|-------------------|----------------|--------|
| DEV-007 | `backend/tests/unit/test_narrative_engine.py` | AC-001, AC-002, AC-003 | Ready |
| DEV-007 | `backend/tests/unit/test_rule_engine.py` | AC-002 | Ready |
| DEV-009 | `backend/tests/unit/test_fallback.py` | AC-006 | Ready |
| DEV-017 | `backend/tests/unit/test_memory_extract.py` | AC-009, AC-010, AC-011 | Ready |
| DEV-017 | `backend/tests/unit/test_memory_recall.py` | AC-010, AC-011 | Ready |
| DEV-010 | `backend/tests/unit/test_affection_update.py` | AC-012, AC-013 | Ready |
| DEV-010 | `backend/tests/unit/test_affection_level.py` | AC-013 | Ready |
| DEV-020 | `backend/tests/unit/test_security.py` | AC-020, AC-021 | Ready |
| DEV-021 | `backend/tests/unit/test_jwt.py` | AC-023 | Ready |
| DEV-008 | `backend/tests/integration/test_game_flow.py` | AC-004, AC-005 | Ready |
| DEV-020 | `backend/tests/integration/test_auth_flow.py` | AC-020, AC-022, AC-023 | Ready |
| DEV-024 | `tests/e2e/visual.spec.ts` | AC-015, AC-016, AC-017 | Ready |
| DEV-027 | `tests/e2e/typewriter.spec.ts` | AC-018 | Ready |
| DEV-053 | `tests/e2e/delivery-smoke.spec.ts` | AC-004, AC-005, AC-012, AC-020, AC-026, AC-035 | Ready |
| DEV-054 | `tests/e2e/user-journey.spec.ts` | AC-004, AC-005, AC-012, AC-015, AC-020, AC-023, AC-026, AC-030, AC-035, AC-039 | Ready |

## CI/CD Evidence Plan

| Stage | Trigger | Command / Pipeline | Acceptance IDs | Owner | Record Location | Status |
|-------|---------|-------------------|----------------|-------|-----------------|--------|
| Lint | push/PR | `pre-commit run --all-files` | AC-001, AC-002 | be | `.pre-commit-config.yaml` | Planned |
| Unit Test | push/PR | `cd backend && pytest tests/unit/ -v --tb=short` | AC-001, AC-002, AC-003, AC-006, AC-009, AC-010, AC-011, AC-012, AC-013, AC-020, AC-021, AC-023 | be | `backend/tests/unit/` | Planned |
| Integration Test | push/PR | `cd backend && pytest tests/integration/ -v --tb=short` | AC-004, AC-005, AC-020, AC-022, AC-023 | be | `backend/tests/integration/` | Planned |
| Frontend Lint | push/PR | `cd frontend && npm run lint` | AC-015, AC-016, AC-017, AC-018 | fe | `.eslintrc.cjs` | Planned |
| Frontend Unit Test | push/PR | `cd frontend && npm run test` | AC-015, AC-018 | fe | `frontend/src/__tests__/` | Planned |
| Build Check | push/PR | `cd frontend && npm run build && cd ../backend && docker build -f Dockerfile -t backend .` | AC-001, AC-015 | ops | `docker-compose.yml` | Planned |
| Delivery E2E | push/PR | `docker compose up -d && sleep 5 && curl -f http://localhost/api/v1/health && APP_BASE=http://localhost npx playwright test tests/e2e/delivery-smoke.spec.ts` | AC-004, AC-005, AC-012, AC-020, AC-026, AC-035 | qa | `tests/e2e/screenshots/` | Planned |
| Browser E2E | push/PR | `APP_BASE=http://localhost:3000 npx playwright test tests/e2e/user-journey.spec.ts --headed --trace on` | AC-004, AC-005, AC-012, AC-015, AC-020, AC-023, AC-026, AC-030, AC-035, AC-039 | qa | `tests/e2e/traces/` | Planned |

## Red 失败记录

> Red 失败记录属于 DEVELOPMENT 阶段写业务代码前的 code readiness，不属于 DESIGN 关口必须完成项。
> 以下表格在 DEVELOPMENT 阶段、写业务代码前由开发补齐。

| 模块 | Red 用例 | 预期失败 | 实际结果 | 记录人 | 日期 |
|------|---------|---------|---------|--------|------|
| （DEVELOPMENT 阶段补齐） | — | — | — | — | — |

## 状态规则

- 测试用例产物状态：`Draft`、`Ready`、`Approved`、`Recorded`。
- 测试证据状态：`pending`、`pass`、`fail`、`manual_pending`。
- P0/P1 验收项必须有测试证据；只有 `manual_pending` 或 `out_of_scope_with_reason` 可例外。
- 每个 P0/P1 AC 必须记录至少一条用户动作或验证命令。

## 维护规则

- QA 在 Architect 和 PL 确认验收矩阵、运行契约和测试要求后，补齐测试用例和执行证据。
- QA 必须独立复核测试证据和覆盖结论，不直接采纳开发自测结论。
- 测试用例和证据必须可在仓库或制品中追溯。
- 发布关口前，所有测试证据应达到 `pass` 或 `manual_pending`。
