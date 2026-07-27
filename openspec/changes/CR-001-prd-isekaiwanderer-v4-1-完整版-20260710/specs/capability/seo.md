# S014 SEO（P1）

**MAS（最小可用标准）**：基础 meta 标签 + sitemap.xml，不做高级 SEO 优化。

## Capability: SEO

### Requirement: 基础 Meta 标签

系统所有页面包含 SEO 基础 meta 标签（title/description/og:image/og:url）。

#### Scenario: 页面 meta 标签完整

**Given** 用户访问游戏首页
**When** 搜索引擎爬虫抓取页面
**Then** 页面包含 title、description、og:title、og:description、og:image meta 标签
**And** 标签内容非空且与页面内容相关

### Requirement: Sitemap 生成

系统提供 sitemap.xml 文件，包含所有公开页面 URL。

#### Scenario: sitemap.xml 可访问

**Given** 系统已部署
**When** 访问 /sitemap.xml
**Then** 返回有效的 XML sitemap，包含首页、剧本列表、分享页面等公开 URL
