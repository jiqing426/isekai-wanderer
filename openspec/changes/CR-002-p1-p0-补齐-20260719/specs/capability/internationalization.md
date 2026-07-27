# S-CR2-004 国际化 i18n（CR-002 补充）

**MAS（最小可用标准）**：vue-i18n + 中英文切换。

## REQ-CR2-004: 国际化

### Requirement: 中英文语言切换

**ID**: REQ-CR2-004-R01
**优先级**: P1

游戏 UI 文本支持英文翻译；用户在设置页可切换语言（中文/英文），切换后文本即时更新。

#### Scenario: 用户切换到英文

- **Given** 用户当前语言为中文
- **When** 用户在设置页选择英文
- **Then** 所有 UI 文本切换为英文，无需刷新

#### Scenario: 用户切换回中文

- **Given** 用户当前语言为英文
- **When** 用户在设置页选择中文
- **Then** 所有 UI 文本切换为中文

### R/C/U/D 完整性

| 动作 | 是否包含 | 说明 |
| --- | --- | --- |
| Create | 是 | 创建翻译文件 |
| Read | 是 | 读取当前语言 |
| Update | 是 | 切换语言 |
| Delete | 否 | — |

### 下游约束

- 依赖：Vue3 框架
- FE：vue-i18n + zh.json + en.json + SettingsView
