# CR-008 重构后页面优化 - 设计文档

## 变更概述

本次变更包含三个主要部分：
1. 重构后页面优化（18 个后端接口 + 前端对接）
2. 设置页面优化（8 个后端接口 + 前端重构）
3. 碎片中心（3 个后端接口 + 前端开发）

## 架构设计

### 后端架构

#### API 路由设计
- `/api/v1/users/me/*` - 用户中心相关接口
- `/api/v1/sign/info` - 签到信息接口
- `/api/v1/fragment/*` - 碎片中心接口

#### 数据库设计
新增表：
- `posts` - UGC 帖子表
- `collections` - 用户收藏表
- `login_devices` - 登录设备表
- `shop_goods` - 商品表
- `user_goods` - 用户持有表

扩展表：
- `users` - 新增 signature 字段
- `user_settings` - 新增播放偏好、通知设置字段

### 前端架构

#### 页面结构
- PersonalCenterView - 个人中心页面（9 个模块卡片）
- SettingsView - 设置页面（左右分栏，5 个模块）
- FragmentMallView - 碎片中心页面（3 个 Tab）

#### 组件设计
- 类型定义：`types/user.ts`, `types/personal-center.ts`
- API 层：`api/user.ts`, `api/ugc.ts`, `api/gallery.ts`

## 接口设计

### 用户中心接口（18 个）
详见：`docs/api/api-contract-post-refactor.md`

### 设置页面接口（8 个）
详见：`docs/api/api-contract-settings-v42.md`

### 碎片中心接口（3 个）
详见：`docs/api/api-contract-fragment-mall.md`

## 安全设计

- 所有 `/users/me/*` 接口需要 Bearer Token 认证
- 密码修改需要验证旧密码
- 会员功能（memory/full）需要检查 subscription_tier
- 输入校验使用 Pydantic schema

## 测试策略

- 后端接口测试：curl 验证所有 29 个接口
- 前端构建测试：TypeScript 编译 + Vite 构建
- E2E 测试：Browser E2E + Delivery E2E

## 部署策略

- 数据库迁移：手动创建新表
- 后端部署：重启 backend 服务
- 前端部署：构建静态资源

## 回滚方案

- 数据库：保留旧表结构，可手动删除新表
- 后端：回滚代码到上一版本
- 前端：回滚静态资源到上一版本
