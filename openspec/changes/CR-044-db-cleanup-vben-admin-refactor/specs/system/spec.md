# System Spec: CR-044

### Requirement: REQ-001 数据库清理

删除冗余表、合并订阅表、补充约束。

#### Scenario: 删除冗余表

- GIVEN 数据库有 email_verifications 表
- WHEN 执行迁移 cr044_db_cleanup
- THEN email_verifications 表被删除
- AND user_preferences 表被删除
- AND subscription_plans 表被删除，数据迁移到 subscriptions

#### Scenario: 补充约束

- GIVEN post_likes 表无唯一约束
- WHEN 执行迁移 cr044_db_cleanup
- THEN post_likes 表有唯一约束 (user_id, post_id)
- AND affection 表外键有 ondelete=CASCADE

### Requirement: REQ-002 system_configs 表 + 管理配置 API

新增 system_configs 表存储运行时配置，提供管理员 CRUD API。

#### Scenario: 管理员查看系统配置

- GIVEN 管理员登录后台
- WHEN GET /api/v1/admin/system-config
- THEN 返回所有配置项（key、value、category、description）
- AND 敏感字段（is_secret=*** 的）返回 ***，不泄露明文

#### Scenario: 管理员修改 SMTP 配置

- GIVEN 管理员在系统配置页面
- WHEN PUT /api/v1/admin/system-config {key: "smtp_host", value: "smtp.163.com"}
- THEN 配置更新成功
- AND 后端 email service 使用新配置发送邮件，无需重启

#### Scenario: 配置优先级

- GIVEN .env 有 SMTP_HOST=localhost
- AND system_configs 有 smtp_host=smtp.163.com
- WHEN 后端启动或读取配置
- THEN 使用 system_configs 的值（DB 优先于 .env）

### Requirement: REQ-003 Vben Admin v2 替换

用 Vben Admin v2 替换现有 admin/，端口改为 8082。

#### Scenario: Vben Admin 启动

- GIVEN admin/ 目录用 Vben Admin v2 替换
- WHEN 访问 http://localhost:8082
- THEN 显示 Vben Admin 布局（侧边栏 + 顶栏 + 内容区）
- AND 端口为 8082（不是 3100）

#### Scenario: 页面迁移

- GIVEN Vben Admin 已替换
- WHEN 访问管理后台各页面
- THEN 现有 7 个页面可正常访问（Dashboard、Login、CharacterList、CharacterEdit、LorebookManage、SceneConfig、NotFound）
- AND 新增系统配置页面可访问
- AND 新增用户管理页面可访问

### Requirement: REQ-004 前端个人中心重构

头像下拉菜单 + 会员卡内联展示。

#### Scenario: 头像下拉菜单

- GIVEN 用户登录后进入个人中心
- WHEN 点击头像
- THEN 下拉显示「设置」「退出登录」选项
- AND 点击「设置」跳转到 /settings
- AND 点击「退出登录」清除 token 并跳转到 /login

#### Scenario: 会员卡内联展示

- GIVEN 用户在个人中心
- WHEN 查看用户信息卡片下方
- THEN 内联展示会员信息（等级、到期时间、碎片余额、升级按钮）
- AND 不跳转到单独的会员管理页

### Requirement: REQ-005 前端设置页精简

删除 member tab，只保留配置类 tab。

#### Scenario: 设置页只有配置 tab

- GIVEN 用户进入设置页
- WHEN 查看 tab 列表
- THEN 只有 4 个 tab（个人资料、播放偏好、通知、隐私安全）
- AND 没有 member tab

### Requirement: REQ-006 前台移动端适配

14 个缺适配页面补 @media 响应式样式，确保移动端（≤767px）布局正常。

#### Scenario: 移动端布局正常

- GIVEN 用户在手机上访问前台页面
- WHEN 浏览 AchievementView、CommunityView、GalleryView、SubscriptionView、SaveManagerView、EndingView、RecapView、RouteMap、ForgotPasswordView、ResetPasswordView、GiftView、OAuthCallbackView、NotFoundView、ShareView
- THEN 页面布局为单列
- AND 无横向滚动
- AND 按钮和输入框触摸目标≥44px
- AND 弹窗转底部抽屉

#### Scenario: 桌面端不受影响

- GIVEN 用户在桌面端（≥1024px）访问
- WHEN 浏览上述页面
- THEN 布局与现有桌面端一致
- AND 移动端样式不影响桌面端

### Requirement: REQ-007 前端 i18n 全覆盖

将所有硬编码中文文本提取为 i18n key，补全 zh-CN.ts 和 en-US.ts。

#### Scenario: 无硬编码中文

- GIVEN 前端代码中存在约 4295 行硬编码中文
- WHEN 完成 i18n 提取
- THEN 所有用户可见的中文文本通过 $t() 或 t() 调用
- AND zh-CN.ts 包含所有 key 的中文值
- AND en-US.ts 包含所有 key 的英文值
- AND 切换语言时所有文本正确切换

#### Scenario: 语言切换

- GIVEN 用户在前端页面
- WHEN 切换语言为 en-US
- THEN 所有界面文本显示为英文
- WHEN 切换语言为 zh-CN
- THEN 所有界面文本显示为中文
