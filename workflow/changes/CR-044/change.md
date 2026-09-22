# CR-044: 数据库清理 + Vben Admin 替换 + 个人中心/设置重构

## 变更入口

- 提出者: 用户
- 提出时间: 2026-09-20
- 项目: isekai-wanderer
- 优先级: P0
- 目标: 数据库清理 + Vben Admin 替换 + 后台系统配置 + 前端个人中心/设置重构 + 前台移动端适配 + i18n 全覆盖
- 成功标准: 冗余表删除、system_configs CRUD、Vben 8082 运行、个人中心头像下拉、设置页 4 tab、14 个页面移动端适配、前端无硬编码中文

## 变更目标

1. 数据库清理：删除冗余表（email_verifications、user_preferences、subscription_plans），合并订阅表，补约束
2. 后台管理系统配置：新增 system_configs 表，支持从管理后台动态配置 SMTP/APP_URL 等
3. Vben Admin v2 替换现有 admin/，端口改为 8082
4. 前端个人中心重构：头像下拉（设置/退出）+ 内联会员卡
5. 前端设置页精简：删除 member tab

## 影响范围

### 后端
- `backend/app/models/asset.py` — 删除 UserPreference、EmailVerification
- `backend/app/models/subscription.py` — 改为引用 payment.py 的 Subscription
- `backend/app/models/system_config.py` — 新增 system_configs 表模型
- `backend/app/api/v1/admin_system.py` — 新增管理配置 API
- `backend/app/core/config.py` — 启动时从 DB 加载配置
- `backend/app/core/email.py` — SMTP 配置支持动态加载
- `backend/alembic/versions/cr044_db_cleanup.py` — DB 迁移

### 前端
- `frontend/src/views/PersonalCenterView.vue` — 头像下拉 + 会员卡内联
- `frontend/src/views/SettingsView.vue` — 删除 member tab

### 管理后台
- `admin/` — 用 Vben Admin v2 替换，端口 8082
- 迁移现有 7 个页面 + 新增系统配置、用户管理

### 部署
- `docker-compose.yml` — admin 端口 3100→8082
- `.env` / `.env.example` — ADMIN_PORT=8082

## 成功标准

- email_verifications、user_preferences、subscription_plans 表已删除
- post_likes 有唯一约束 (user_id, post_id)
- system_configs 表存在且有 CRUD API
- 后台管理可通过 UI 修改 SMTP 配置并热生效
- Vben Admin v2 在端口 8082 运行，现有页面已迁移
- 前端个人中心头像可下拉（设置/退出），会员卡内联展示
- 前端设置页只有 4 个 tab（无 member）

## 风险

- Vben Admin 替换可能导致管理后台短暂不可用
- 数据库迁移需先备份
- 配置从 DB 加载需确保启动顺序正确

## 确认

- [x] 用户已确认方案（2026-09-20）
