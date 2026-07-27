# S-CR2-002 密码重置（CR-002 补充）

**MAS（最小可用标准）**：忘记密码→mock 邮件发链接→重置密码。

## REQ-CR2-002: 密码重置

### Requirement: 密码重置流程

**ID**: REQ-CR2-002-R01
**优先级**: P1

用户在登录页点击忘记密码并输入邮箱后，收到密码重置链接（有效期 1 小时，mock 邮件）。

#### Scenario: 用户请求密码重置

- **Given** 用户已注册，邮箱存在
- **When** 用户在登录页点击"忘记密码"并输入邮箱
- **Then** 系统生成重置链接（有效期 1 小时），通过 MockEmailService 发送

#### Scenario: 用户通过重置链接修改密码

- **Given** 用户收到重置邮件
- **When** 用户点击链接并输入新密码
- **Then** 密码更新成功，旧密码失效

#### Scenario: 重置链接过期

- **Given** 重置链接已生成超过 1 小时
- **When** 用户点击链接
- **Then** 系统提示链接已过期，需重新请求

### R/C/U/D 完整性

| 动作 | 是否包含 | 说明 |
| --- | --- | --- |
| Create | 是 | 创建重置令牌 |
| Read | 是 | 验证令牌有效性 |
| Update | 是 | 更新密码 |
| Delete | 是 | 令牌过期后清理 |

### 下游约束

- 依赖：现有 auth 模块
- BE：POST /auth/forgot-password + POST /auth/reset-password
- FE：ForgotPasswordView.vue + ResetPasswordView.vue
- 新增：password_resets 表 + MockEmailService
