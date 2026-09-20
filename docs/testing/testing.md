# Testing

本文记录测试分层、命令、覆盖要求和验证责任。

## 测试分层

| 层级 | 位置 | 目的 | 触发条件 |
| --- | --- | --- | --- |
| 单元测试 | 各模块内 | 验证纯逻辑、组件和小函数 | 默认随相关代码修改 |
| 集成测试 | 各模块内或 `tests/` | 验证数据库、API、外部适配器 | API、数据访问、任务修改 |
| 契约测试 | `tests/` | 验证前后端、管理端和 API 契约 | API 字段、错误码、权限变化 |
| 端到端测试 | `tests/` | 验证关键用户路径 | 关键流程变化或发布前 |
| Delivery E2E / Runtime Smoke | `tests/e2e/`、CI/CD 或部署脚本 | 从真实前端入口穿过代理访问真实后端 | 发布关口前必跑 |
| Browser Interaction E2E | `tests/e2e/`、Playwright/Puppeteer/浏览器插件 | 用真实浏览器执行用户动作并验证 UI/API 状态 | 存在前端验收项时必跑 |
| 冒烟测试 | `tests/` 或部署平台 | 验证环境可用 | 每次部署 |

## CR-043 测试要求

### 验证类型映射

| AC 编号 | 验证类型 | 说明 |
| --- | --- | --- |
| AC-001, AC-004, AC-005, AC-006, AC-007, AC-008, AC-009, AC-018, AC-019 | API/DB 契约验证 | 后端权限检查逻辑、is_accessible 字段返回、GameSession 创建/拒绝、member-info 数据源修复 |
| AC-002, AC-003, AC-010, AC-011, AC-012, AC-013, AC-016, AC-017, AC-020 | Browser Interaction E2E | 前端锁/升级提示展示、订阅状态同步、登录后自动加载、用户交互行为验证 |
| AC-015 | API 安全测试 | API 层面绕过风险验证（Security 阶段） |
| AC-014, AC-021 | 代码审查 + Browser E2E | 前端复用 useSubscriptionStore 验证、TypeScript 类型修复验证 |

### 测试数据准备

- 需要 4 个不同订阅等级的测试用户账号：free、basic、standard、premium
- 需要至少 2 个剧本：1 个试用剧本（对 free 可用）、1 个非试用剧本
- 需要至少 1 个独家剧本（对 basic/standard 不可用，对 premium 可用）
- 需要至少 1 个已通过剧情解锁的 CG 和 1 个未解锁的 CG

### 测试约束

- **不得使用 mock 作为发布证据**：权限检查必须在真实后端验证，不可用 mock API 替代
- **Security 阶段必审**：AC-015 API 安全测试由 Security Agent 在 SECURITY 阶段执行
- **Browser E2E 必跑**：AC-002/003/010/011/012/013 涉及前端用户交互，必须用真实浏览器验证

## 证据等级

| 等级 | 名称 | 说明 | 典型示例 |
| --- | --- | --- | --- |
| L1 | 本地通过 | localhost 或本机环境下通过 | 本地登录、列表展示、本机 API 联调 |
| L2 | 联调通过 | 真实前后端、真实 proxy、非 mock 链路通过 | 测试机部署地址访问、真实后端返回 |
| L3 | 交付通过 | 目标交付环境和访问方式下通过 | 内网入口、公网 IP、域名、真实代理/CORS 场景 |

发布关口引用的 Delivery E2E、Browser Interaction E2E、Runtime Smoke 必须明确自己的证据等级；未达到目标环境要求时，不得写成 release-ready。

## 环境测试矩阵

每个关键功能、关键入口或环境敏感改动至少要声明覆盖到哪个环境层级。

| 环境编号 | 环境名称 | 访问方式 | 典型风险 |
| --- | --- | --- | --- |
| ENV-L1 | DEV_LOCAL | localhost / 本机端口 | 基础功能、页面渲染、本机 API 联调 |
| ENV-L2 | DEPLOY_PRIVATE | 测试机 / 内网入口 / 服务器本地访问 | 真实部署、端口监听、代理配置、服务编排 |
| ENV-L3 | DEPLOY_PUBLIC | 公网 IP / 域名 / 外网入口 | CORS、反向代理、端口暴露、证书、外网可访问性 |

规则：

- `localhost` 通过不能替代 `DEPLOY_PUBLIC` 通过。
- 涉及登录、跨域、上传下载、回调、Webhook、支付、媒体资源访问时，默认视为环境敏感，必须声明是否覆盖 `DEPLOY_PUBLIC`。
- `test-plan.md` 和 `test-report.md` 中的交付级证据必须能回到本矩阵中的某个环境编号。

## 通用命令

```sh
./scripts/test.sh backend
./scripts/test.sh frontend
./scripts/test.sh admin
./scripts/test.sh system
./scripts/test.sh all
```

具体项目应在模块 README 中记录实际命令和测试框架。

## 最低验证要求

- 文档修改：检查标题层级、链接、路径和 diff。
- 后端逻辑修改：运行相关单元测试；涉及 API 或数据库时运行集成或契约测试。
- 前端修改：运行相关组件或页面测试；涉及关键路径时运行端到端测试。
- 管理端修改：验证权限展示、拒绝路径、危险操作确认和审计入口。
- 部署修改：运行配置检查、容器启动或冒烟测试。

## 测试数据

- 不提交真实生产数据。
- 敏感样本必须脱敏并标注来源和用途。
- 测试数据应可重复创建和清理。

## E2E 测试编写规范

### 位置和命名

- E2E 测试文件统一放在 `tests/e2e/` 目录。
- 文件名格式：`<测试场景>.test.ts` 或 `<测试场景>.spec.ts`。
- 不得将 E2E 文件放入 `backend/__tests__/e2e/` 或任何模块内测试目录；E2E 是跨模块测试。

### 端口和地址配置

- **禁止硬编码端口**。前端地址必须通过环境变量 `APP_BASE` 或 `E2E_BASE_URL` 配置。
- 默认值：`APP_BASE=http://localhost:3000`（Vite dev server）或 `http://localhost:80`（Nginx 代理）。
- 后端地址通过 `API_BASE` 环境变量配置，默认 `http://localhost:8080`。
- 示例：
  ```typescript
  const APP_BASE = process.env.APP_BASE || 'http://localhost:3000';
  const API_BASE = process.env.API_BASE || 'http://localhost:8080/api/v1';
  ```

### E2E 测试内容要求

E2E 测试**必须覆盖真实用户交互**，不仅仅是 API 调用：

| 类别 | 要求 | 示例 |
| --- | --- | --- |
| 页面加载 | 验证页面 title、关键元素 | `expect(page.title()).toContain('智能项目看板')` |
| 导航流程 | **测试完整路由链**：点击→跳转→验证新页面 | 打开首页→进入关键业务页面→返回或切换视图 |
| 表单交互 | 填写表单→提交→验证结果 | 新建/编辑/删除业务对象并验证页面变化 |
| API 集成 | 通过浏览器发请求验证前端→后端通路 | `page.evaluate(fetch('/api/v1/<resource>'))` |
| 拖拽/手势 | 真实浏览器拖拽操作 | Puppeteer `page.mouse.move` + `page.mouse.down` + `page.mouse.up` |

### Delivery E2E / Runtime Smoke

发布关口使用的交付级 E2E 必须满足：

- 从真实前端入口开始，例如 `APP_BASE=http://localhost:<frontend_port>`。
- 请求必须经真实前端代理或运行时配置访问真实后端，例如 `<APP_BASE>/api/v1/health`。
- 使用 `docs/runtime/runtime-contract.md` 中的 frontend/backend/API/proxy/health 配置。
- 禁止 mock API、fixture server、MSW、组件级替身或静态假数据作为发布证据。
- 必须记录 `APP_BASE`、`API_BASE` 或 proxy path、命令、日志/trace/screenshot 位置和是否 mock。
- 必须记录环境编号（`ENV-L1` / `ENV-L2` / `ENV-L3`）和证据等级（`L1` / `L2` / `L3`）。
- 如果测试使用 mock，只能归类为组件测试、功能预演或开发阶段测试，不能写入 `Delivery E2E / Runtime Smoke Results`。

### Browser Interaction E2E

存在前端页面、管理端页面或用户验收项时，发布关口还必须满足：

- 使用真实浏览器打开 `docs/runtime/runtime-contract.md` 中的 `frontend_origin`。
- 执行至少一个与 AC 绑定的真实用户动作，例如点击、输入、提交、筛选、拖拽、导航或错误恢复。
- 通过 UI 文本、DOM 状态、浏览器请求、截图/trace 或后端 API 状态证明动作生效。
- 通过真实 API / Proxy 访问后端，`Mock API=no`。
- 记录 `Browser / Tool`、用户动作、前端入口、后端地址、API/Proxy Path、证据链接和覆盖 AC。
- 记录环境编号（`ENV-L1` / `ENV-L2` / `ENV-L3`）和证据等级（`L1` / `L2` / `L3`）。
- 只用 API/fetch/curl/Runtime Smoke 不能替代本节；确实没有前端时，必须写 `Not Required: <原因>` 并由 PL 在 `review.md` 批准。

### E2E 报告分类

E2E 测试报告必须按以下分类统计，不得混在一起：

| 分类 | 说明 | 示例 |
| --- | --- | --- |
| API 集成测试 | 纯 API 调用，不打开浏览器 | 创建业务对象、更新状态、筛选列表 |
| 前端渲染测试 | 通过浏览器验证页面加载和渲染 | 页面可访问、#root 存在 |
| 前端交互测试 | 通过浏览器验证真实用户操作 | 点击按钮、拖拽卡片、表单提交 |
| Delivery E2E / Runtime Smoke | 从真实前端入口访问真实后端 | `curl <frontend_origin>/api/v1/health`、Playwright 打开真实首页 |
| Browser Interaction E2E | 真实浏览器执行用户动作并访问真实后端 | Playwright/Puppeteer/browser 插件点击、填写、提交、拖拽 |

报告格式示例：
```
E2E 总计: 10 用例
  - API 集成: 4/4 通过
  - 前端渲染: 3/3 通过
  - 前端交互: 3/3 通过
```

**禁止仅写"E2E 7/7 通过"，必须注明各分类结果。**
**禁止把 mock E2E 写成交付级 E2E 通过。**

### E2E 最小覆盖

每个有前端的项目至少包含一个冒烟级 E2E 文件，覆盖以下路径：
1. 打开真实前端入口并确认关键首屏元素。
2. 通过真实 API / Proxy 访问后端健康检查或关键资源。
3. 执行一个与 AC 绑定的用户动作。
4. 验证动作后的 UI 状态和后端/API 状态一致。
5. 记录 no-mock 证据、命令、环境变量和日志/trace/screenshot 位置。

### 标准 E2E 样例模板

龙虾执行 E2E 时可直接按以下口径创建或改写 `tests/e2e/smoke.test.ts`，并把执行结果写入当前 CR 的 `test-report.md`。如果项目使用 Playwright，也可以等价改成 `smoke.spec.ts`，但字段、证明口径和 no-mock 要求不能变化。

#### 必填环境变量

| 变量 | 示例 | 用途 |
| --- | --- | --- |
| `APP_BASE` | `http://localhost:<frontend_port>` | 真实前端入口。必须来自运行时契约，不得写死。 |
| `API_BASE` | `http://localhost:<backend_port>/api/v1` | 真实后端 API base。 |
| `CHROME_PATH` | `/usr/bin/google-chrome` | 浏览器可执行文件。 |
| `E2E_PROXY_HEALTH_PATH` | `/api/v1/health` | 通过前端代理访问后端的 health path。 |
| `E2E_BACKEND_HEALTH_PATH` | `/health` | 直接后端 health path，拼接在 `API_BASE` 后。 |
| `E2E_HOME_READY_SELECTOR` | `#root, [data-testid="app-root"], main` | 首页关键首屏元素。 |
| `E2E_ACTION_SELECTOR` | `[data-testid="submit"]` | 可选；绑定 AC 的真实用户动作入口。 |
| `E2E_EXPECT_TEXT` | `保存成功` | 可选；动作后的 UI 可观察结果。 |
| `E2E_EVIDENCE_DIR` | `logs/e2e` | E2E 截图、trace、失败上下文等证据保存目录。 |

#### 推荐命令

```sh
APP_BASE=http://localhost:<frontend_port> \
API_BASE=http://localhost:<backend_port>/api/v1 \
CHROME_PATH=/usr/bin/google-chrome \
E2E_PROXY_HEALTH_PATH=/api/v1/health \
E2E_BACKEND_HEALTH_PATH=/health \
E2E_HOME_READY_SELECTOR='[data-testid="app-root"]' \
E2E_ACTION_SELECTOR='[data-testid="<ac-action>"]' \
E2E_EXPECT_TEXT='<expected-visible-result>' \
E2E_EVIDENCE_DIR=logs/e2e \
npx jest tests/e2e/smoke.test.ts --runInBand
```

使用 Playwright 时命令可等价替换为：

```sh
APP_BASE=http://localhost:<frontend_port> \
API_BASE=http://localhost:<backend_port>/api/v1 \
CHROME_PATH=/usr/bin/google-chrome \
npx playwright test tests/e2e/smoke.spec.ts --reporter=list
```

#### 必须证明的步骤

1. 打开 `APP_BASE`，断言 title 或关键首屏元素存在，证明首页不是白屏或 404。
2. 在浏览器页面内执行 `fetch(E2E_PROXY_HEALTH_PATH)`，证明前端 runtime/proxy 能访问真实后端。
3. 直接访问 `API_BASE + E2E_BACKEND_HEALTH_PATH`，证明后端服务本身可达。
4. 至少执行一个与 `AC-*` 绑定的真实用户动作，例如点击、填写、提交、筛选、导航或错误恢复。
5. 用 UI 文本、DOM 状态、浏览器请求、后端状态、trace、screenshot 或日志证明动作生效。
6. 在 `test-report.md` 写明：`Mock API=no`、`APP_BASE`、`API_BASE`、proxy path、命令、浏览器、覆盖 AC、证据路径和失败截图/trace。

#### 截图保留凭证

E2E 发布证据必须保留截图或 trace，不能只在聊天中描述“页面正常”。截图和 trace 必须写入当前项目目录下的稳定证据目录，例如 `logs/e2e/` 或 `test-results/<case>/`，并在 `test-report.md` 中引用相对路径。

最低截图要求：

1. `home-ready.png`：打开 `APP_BASE` 后的首页或关键首屏元素截图。
2. `ac-action-result.png`：完成至少一个 `AC-*` 绑定用户动作后的结果截图。
3. `failure-context.png` 或 Playwright trace：任一 E2E 失败时保留失败页面、错误态或上下文截图。

缺少截图或 trace 时，Browser Interaction E2E 不能作为 RELEASE_GATE 发布证据；只能记录为待补证据。

#### 报告模板

```md
### Browser Interaction E2E Results

| Case | AC | APP_BASE | API/Proxy Path | User Action | Expected Result | Mock API | Screenshot / Trace | Log | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| smoke-home | AC-001 | http://localhost:<frontend_port> | /api/v1/health | 打开首页 | 首屏元素存在 | no | logs/e2e/home-ready.png | logs/e2e/smoke.log | passed |
| smoke-action | AC-002 | http://localhost:<frontend_port> | /api/v1/<resource> | 点击/填写/提交 | 页面出现预期结果 | no | logs/e2e/ac-action-result.png | logs/e2e/smoke.log | passed |

### Delivery E2E / Runtime Smoke Results

| Case | Frontend URL | Backend URL | Command | Mock API | Screenshot / Trace | Log | Result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| proxy-health | http://localhost:<frontend_port>/api/v1/health | http://localhost:<backend_port>/api/v1/health | npx jest tests/e2e/smoke.test.ts --runInBand | no | logs/e2e/home-ready.png | logs/e2e/smoke.log | passed |
```
