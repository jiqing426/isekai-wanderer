# Backend Spec — CR-008

## 接口清单

### 第一批 18 个接口
详见：`docs/api/api-contract-post-refactor.md`

### 第二批 8 个接口
详见：`docs/api/api-contract-settings-v42.md`

### 第三批 3 个接口
详见：`docs/api/api-contract-fragment-mall.md`

## 数据库变更

### 新增表
- `posts` - UGC 帖子表
- `collections` - 用户收藏表
- `login_devices` - 登录设备表
- `shop_goods` - 商品表
- `user_goods` - 用户持有表

### 扩展表
- `users` - 新增 signature 字段
- `user_settings` - 新增播放偏好、通知设置字段

## 安全要求

- 所有 `/users/me/*` 接口需要 Bearer Token 认证
- 密码修改需要验证旧密码
- 会员功能需要检查 subscription_tier
- 输入校验使用 Pydantic schema
