# CR-044 Design

## Overview

- CR-044 涉及 4 个模块的改动：数据库清理、后端动态配置、Vben Admin 替换、前端 UI 重构 + 移动端适配 + i18n 全覆盖
- 设计遵循最小侵入原则，后端改动集中在 core 和 models 层，前端改动集中在 views 和 i18n 层

## Technical Approach

### 1. 数据库清理 (REQ-001)

- 迁移脚本 cr044_db_cleanup.py：DROP email_verifications/user_preferences/subscription_plans，subscription_plans 数据迁移到 subscriptions，post_likes 加唯一约束，affection 外键加 CASCADE
- 模型清理：asset.py 删除 UserPreference/EmailVerification，subscription.py 改为 re-export from payment.py

### 2. system_configs + 动态配置 (REQ-002)

- 新表 system_configs (key/value/category/description/is_secret)
- 后端 admin_system.py 提供 GET/PUT API，管理员权限
- config.py 启动时从 DB 加载覆盖 .env
- email.py 新增 reload_email_service() 支持热更新

### 3. Vben Admin v2 替换 (REQ-003)

- 克隆 Vben Admin v2 到 admin/，清空 demo，保留框架骨架
- 端口 8082
- 迁移现有 7 个页面 + 新增系统配置和用户管理页面

### 4. 前端个人中心重构 (REQ-004)

- PersonalCenterView 头像加下拉菜单（设置/退出），内联会员卡区域

### 5. 前端设置页精简 (REQ-005)

- SettingsView 删除 member tab，保留 4 个配置 tab

### 6. 前台移动端适配 (REQ-006)

- 14 个缺适配页面补 @media (max-width: 767px) 响应式样式，单列布局、触摸目标 44px、弹窗转底部抽屉

### 7. i18n 全覆盖 (REQ-007)

- 4295 行硬编码中文提取为 i18n key，zh-CN.ts 和 en-US.ts 同步补全

## Technology Decisions

| 选型项 | 选择 | 状态 | 确认依据 |
|--------|------|------|----------|
| 后台管理框架 | Vben Admin v2 | Accepted | 用户确认 |
| 配置存储 | PostgreSQL system_configs 表 | Accepted | 用户确认，项目已用 PG |
| 配置缓存 | 无（启动时加载） | Accepted | 用户确认，配置量小 |
| 邮件热更新 | 重建 email_service 单例 | Accepted | 用户确认，reload_email_service() |
| 移动端断点 | 768px | Accepted | 用户确认，与 mobile.css 一致 |
| i18n 方案 | vue-i18n（已有） | Accepted | 用户确认，项目已集成 |

## Document Sync

| 目标文档 | 状态 | 同步说明 |
|----------|------|----------|
| docs/database/database.md | Not Required | 数据库迁移脚本自带说明，DEV-001 完成后同步 |
| docs/api/api.md | Not Required | admin API 在 DEV-002 完成后同步 |
| docs/architecture/architecture.md | Not Required | 配置优先级在 DEV-003 完成后同步 |
| docs/security/security.md | Not Required | 无安全边界变更，CR-044 不新增攻击面 |
| docs/decisions/decisions.md | Not Required | 技术选型已在此 design.md 记录 |
| docs/runtime/runtime-contract.md | Not Required | 端口和代理配置已在现有 runtime-contract.md 中定义，CR-044 仅新增 8082 admin 端口 |
