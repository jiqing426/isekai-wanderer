# Frontend

## 模块职责

`frontend/` 负责面向最终用户的客户端应用，包括页面路由、组件、状态管理、表单交互、可访问性、国际化和公开 API 调用。

前端不得直接连接数据库，不得实现最终业务裁决，不得包含管理端专属功能或内部运营权限逻辑。

## 启动方式

```sh
npm run dev        # Vite dev server on :3000
npm run build      # TypeScript check + production build
npm run preview    # Preview production build
```

## 目录约定

- `src/views/`：页面级组件 (LoginView, RegisterView, OnboardingView, HomeView)
- `src/components/`：可复用组件
- `src/stores/`：Pinia 状态管理
- `src/api/`：API 调用封装
- `src/router/`：Vue Router 路由配置
- `src/types/`：TypeScript 类型定义
- `src/composables/`：组合式函数
- `src/__tests__/`：单元测试
- `tests/e2e/`：Playwright E2E 测试
- `public/`：静态资源 (manifest.json, sw.js, icons)

## 技术栈

| 项目 | 选型 |
|------|------|
| 框架 | Vue 3.5 + TypeScript |
| UI 库 | Naive UI |
| 状态管理 | Pinia |
| 路由 | Vue Router 4 |
| 构建工具 | Vite 6 |
| 测试 | Vitest (unit) + Playwright (E2E) |
| PWA | manifest.json + service worker |

## 开发规范

- 用户可见流程变化同步 `../docs/status/feature-status.md`。
- API 调用变化以 `../docs/api/api.md` 和后端契约为准。
- 前端校验只作为交互保护，不能替代服务端校验。
- 组件应保持可复用但不提前抽象；先沿用项目既有设计系统。
- 不把 token、密钥或私有环境变量打包进客户端。

## 代理配置

Vite dev server 将 `/api` 请求代理到 `http://localhost:8000`（后端）。
生产环境由 Nginx 反向代理处理。

## 测试方式

```sh
npm run test       # Vitest 单元测试
npm run test:e2e   # Playwright E2E (需要后端)
```
