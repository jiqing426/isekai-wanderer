# CR-044 Proposal: 数据库清理 + Vben Admin 替换 + 个人中心/设置重构

## Why

当前项目存在以下问题：

- 数据库有 3 张冗余表（email_verifications、user_preferences、subscription_plans），其中 2 张 0 行数据
- 订阅表重复定义（subscription_plans 和 subscriptions），容易混淆
- 管理后台用裸 Vue 3 + Naive UI 手搭，缺少权限、布局、组件库支撑
- 系统配置（SMTP、APP_URL）只能改 .env，不能从后台管理
- 前端个人中心缺少设置入口，会员管理放在设置 tab 里逻辑不通

## What Changes

- S1: 数据库清理 — 删除冗余表、合并订阅表、补约束
- S2: system_configs 表 — 后台可动态配置 SMTP/APP_URL/JWT 等
- S3: Vben Admin v2 替换 — 替换 admin/，端口 8082
- S4: 后端配置动态加载 — 从 DB 加载配置覆盖 .env
- S5: 前端个人中心重构 — 头像下拉 + 会员卡内联
- S6: 前端设置页精简 — 删除 member tab
- S7: 前台移动端适配 — 14 个缺适配页面补 @media 响应式样式
- S8: 前端 i18n 全覆盖 — 4295 行硬编码中文提取为 i18n key，zh-CN/en-US 双语完整覆盖

## Non-Goals

- 真实支付/订阅对接
- OAuth 对接
- Push 通知
- 剧本编辑器

## Impact

### 后端

- 删除 3 个模型类（UserPreference、EmailVerification、subscription_plans Subscription）
- 新增 system_configs 表和 admin_system API
- config.py 和 email.py 支持从 DB 动态加载配置
- Alembic 迁移脚本 cr044_db_cleanup

### 前端

- PersonalCenterView 重构（头像下拉 + 会员卡内联）
- SettingsView 精简（删除 member tab）
- 14 个页面补移动端 @media 适配（AchievementView、CommunityView、GalleryView、SubscriptionView、SaveManagerView、EndingView、RecapView、RouteMap、ForgotPasswordView、ResetPasswordView、GiftView、OAuthCallbackView、NotFoundView、ShareView）
- 4295 行硬编码中文提取为 i18n key，补全 zh-CN.ts 和 en-US.ts

### 管理后台

- admin/ 整个目录用 Vben Admin v2 替换
- 端口从 3100 改为 8082
- 迁移现有 7 个页面 + 新增系统配置、用户管理

### 部署

- docker-compose.yml admin 端口变更
- .env / .env.example ADMIN_PORT 变更

## Success Criteria

- email_verifications、user_preferences、subscription_plans 表已删除
- post_likes 有唯一约束 (user_id, post_id)
- system_configs 表存在且有 CRUD API
- 后台管理可通过 UI 修改 SMTP 配置并热生效
- Vben Admin v2 在端口 8082 运行，现有页面已迁移
- 前端个人中心头像可下拉（设置/退出），会员卡内联展示
- 前端设置页只有 4 个 tab（无 member）
- 前台 14 个缺适配页面在移动端（≤767px）下布局正常、无横向滚动、触摸目标≥44px
- 前端所有硬编码中文文本提取为 i18n key，zh-CN.ts 和 en-US.ts 双语完整覆盖，无遗漏

## Open Questions

无阻塞问题。用户已确认全部方案。
