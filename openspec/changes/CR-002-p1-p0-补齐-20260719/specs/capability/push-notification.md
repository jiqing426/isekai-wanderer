# S-CR2-007 PWA 通知（CR-002 补充）

**MAS（最小可用标准）**：Service Worker + 通知权限提示。

## REQ-CR2-007: PWA 通知

### Requirement: 通知权限请求

**ID**: REQ-CR2-007-R01
**优先级**: P1

用户首次进入游戏时，浏览器弹出通知权限提示；用户授权后系统可发送通知。

#### Scenario: 首次进入游戏请求通知权限

- **Given** 用户首次进入游戏
- **When** 页面加载完成
- **Then** 浏览器弹出 Notification API 权限请求

#### Scenario: 用户授权后发送通知

- **Given** 用户已授权通知权限
- **When** 系统触发通知事件
- **Then** 通过 Service Worker 发送浏览器通知

### R/C/U/D 完整性

| 动作 | 是否包含 | 说明 |
| --- | --- | --- |
| Create | 是 | 注册 Service Worker |
| Read | 是 | 检查权限状态 |
| Update | 是 | 更新权限 |
| Delete | 否 | — |

### 下游约束

- 依赖：Vite 构建系统（已存在）
- FE：Service Worker + Notification API
