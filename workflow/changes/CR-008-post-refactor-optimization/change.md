# CR-008: 重构后页面优化

## 变更目标

修复重构后遗留的后端接口问题，新增用户中心 API，优化前端页面体验。

## 影响范围

- 后端：用户模块、UGC 模块、角色模块、成就模块
- 前端：设置页面、收藏馆、剧本大厅、登录注册

## 成功标准

1. 所有 P0 后端接口修复/新增完成
2. 前端 10 项功能优化完成
3. Header 结构调整完成（移动端 + PC 端）

## 功能清单

### P0 - 后端接口修复（4 项）
1. `/api/v1/ugc/posts` 500 错误修复
2. `/api/v1/characters` 404 路由新增（列表接口）
3. `/api/v1/gallery/collections` 认证处理确认
4. 后端 ImportError `get_free_chat_service` 修复

### P0 - 新增用户 API（6 项）
5. `GET /api/v1/users/me` 获取用户信息
6. `PATCH /api/v1/users/me` 修改用户信息
7. `POST /api/v1/users/me/change-password` 修改密码
8. `DELETE /api/v1/users/me` 注销账号
9. `GET /api/v1/users/me/subscription` 获取订阅状态
10. `GET /api/v1/users/me/achievements` 获取成就列表

### P1 - 前端功能优化（10 项）
1. 登录/注册：密码框加"小眼睛"
2. 引导页面：尺寸改一屏展示
3. 引导页面：准备就绪对话框 i18n 适配
4. 剧本大厅：PC 端标题+搜索框一行左右分布
5. 剧本大厅：评分改星级显示
6. 剧本大厅：列表左上角显示剧本类型标签
7. 设置页面：渲染后端 API 数据
8. 设置页面：i18n 适配
9. 收藏馆：新增入口页面，整合成就系统
10. 成就页面：改卡片式展示，移到收藏馆内

### P2 - Header 结构调整
- 移动端：`下拉菜单 | Logo | 头像`
- PC 端：`logo | 导航tab | 语言切换 | 登录/注册`

## 风险

1. Mock 中间件可能拦截真实路由，需确认 DISABLE_MOCK 环境变量行为
2. 数据库 migration 需确认已执行（posts 表、achievements 表）
3. 前端 http interceptor 需确认自动注入 Bearer token

## API Contract

详见：`docs/api/api-contract-post-refactor.md`

## 执行顺序

1. **第一阶段**：BE 完成所有 P0 后端任务
2. **第二阶段**：FE 完成所有 P1 前端任务
3. **第三阶段**：FE 完成 P2 Header 调整
