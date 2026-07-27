# S-CR2-005 SEO 基础配置（CR-002 补充）

**MAS（最小可用标准）**：meta 标签 + sitemap.xml + robots.txt。

## REQ-CR2-005: SEO

### Requirement: 页面 meta 标签

**ID**: REQ-CR2-005-R01
**优先级**: P1

游戏首页和各剧本页面的 HTML 包含基础 meta 标签（title/description/og:image）。

#### Scenario: 首页 meta 标签

- **Given** 用户访问游戏首页
- **When** 搜索引擎爬取页面
- **Then** HTML head 包含 title、description、og:image

#### Scenario: 剧本详情页 meta 标签

- **Given** 用户访问某剧本详情页
- **When** 搜索引擎爬取页面
- **Then** HTML head 包含该剧本专属 title、description

### Requirement: sitemap 和 robots

**ID**: REQ-CR2-005-R02
**优先级**: P1

网站根目录有 sitemap.xml 和 robots.txt。

#### Scenario: 搜索引擎访问 sitemap

- **Given** 搜索引擎请求 /sitemap.xml
- **When** 服务器响应
- **Then** 返回有效的 XML sitemap

### R/C/U/D 完整性

| 动作 | 是否包含 | 说明 |
| --- | --- | --- |
| Create | 是 | 生成 sitemap |
| Read | 是 | 读取 meta 标签 |
| Update | 否 | — |
| Delete | 否 | — |

### 下游约束

- 依赖：Vite 构建系统（已存在）
- FE：@vueuse/head + sitemap.xml + robots.txt
