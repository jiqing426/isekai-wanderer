# unknown

UI_IsekaiWanderer_v4.1_20260710
UI视觉执行规范：异世界漫游（Isekai Wanderer）
**产品名称**：异世界漫游（Isekai Wanderer）
**文档类型**：V9.2标准第三层文档 · UI视觉执行规范
**文档版本**：UI-v4.1
**生成日期**：2026-07-10
**文档状态**：✅ 开发就绪
**关联PRD**：PRD_IsekaiWanderer_v4.1_完整版_20260710.md
**关联DRD/UX**：产品3_UX开发交付文档_v4.1_完整版_20260710.md
**输出Agent**：Agent07 体验架构师（pd-m）
**制度依据**：V9.2编码标准 · 总法-03（圆角规范）· 总法-04（间距规范）· 总法-05（阴影层级）· 总法-06（深色模式）· 总法-37（双端一致）· 总法-38（双端台账）· 指法-UI-01~11（视觉执行层）
————————
一、文档信息
维度 | 内容
------ | ------
**产品名称** | 异世界漫游（Isekai Wanderer）
**产品代号** | AI二次元交互式叙事游戏（网页端）
**文档版本** | v4.1（付费+留存增量升级）
**基线版本** | v4.0（中英双语+原型图对齐版 · 2026-06-24）
**迭代日期** | 2026-07-10
**目标上线** | MVP 3个月内（2026 Q3）
**关联PRD** | PRD_IsekaiWanderer_v4.1_完整版_20260710.md
**关联UX文档** | 产品3_UX开发交付文档_v4.1_完整版_20260710.md
**适用对象** | 前端开发 / UI设计师 / 视觉设计师 / 测试
**V9.2合规** | 指法-UI-01~11 · 总法-03~06 · 总法-37/38
————————
二、设计哲学与品牌定义
2.1 产品视觉定位
维度 | 定义
------ | ------
**视觉关键词** | 异世界奇幻感 · 二次元沉浸 · 暗色优先 · 情感温度 · 精致细腻
**视觉调性** | 日系视觉小说×现代SaaS，暗色调为主营造沉浸感，辅以高饱和品牌色点缀
**目标用户审美** | 乙女玩家/冒险者/创作者 — 高二次元浓度，追求精致、有温度的视觉体验
**竞品视觉对标** | Character.AI（简洁）→ 我们更精致；NovelAI（暗黑）→ 我们更温暖
2.2 Slogan双语视觉呈现
语言 | Slogan | 字体 | 字号 | 字重 | 颜色
------ | -------- | ------ | ------ | ------ | ------
**英文（主）** | Your Story, Woven by AI | Playfair Display Italic | 48px/32px/24px(Hero/H1/H2) | 700 | `--primary-light`(#818CF8)
**中文（副）** | 每一个选择都改变故事，每一个角色都记得你 | Noto Sans SC | 18px/16px/14px | 400 | `--neutral-500`(#6B7280)
Slogan排版规则：
Hero区：英文48px在上，中文18px在下，行间距24px
H1区：英文32px在上，中文16px在下，行间距16px
页脚区：英文14px+中文12px，单行横排，用`·`分隔
2.3 视觉情绪板关键词
情绪维度 | 关键词 | 视觉映射
--------- | -------- | ---------
**沉浸感** | 深夜追番、烛光书房、星空下的篝火 | 深色背景 + 柔和光晕 + 暖色点缀
**情感温度** | 心跳加速、温柔触碰、樱花飘落 | 粉色渐变 + 柔焦效果 + 微粒子动画
**奇幻冒险** | 异世界传送门、魔法阵、古老卷轴 | 靛蓝渐变 + 发光效果 + 粒子特效
**精致品质** | 日式工笔、高级感、手工质感 | 精细线条 + 微妙阴影 + 考究排版
————————
三、色彩体系（指法-UI-05）
3.1 品牌主色体系
色名 | HEX | RGB | HSL | CSS变量 | 用途
------ | ----- | ----- | ----- | --------- | ------
**深靛蓝（主色）** | `#4F46E5` | rgb(79,70,229) | hsl(244,76%,59%) | `--primary` | CTA按钮/激活状态/Logo/链接
**薰衣草紫（浅色）** | `#818CF8` | rgb(129,140,248) | hsl(234,89%,74%) | `--primary-light` | 悬停背景/辅助元素/Slogan
**午夜蓝（深色）** | `#1E1B4B` | rgb(30,27,75) | hsl(244,47%,20%) | `--primary-dark` | 标题文字/深色图标/渐变终点
品牌色使用比例：
主色`--primary`：15%（CTA/关键交互）
浅色`--primary-light`：25%（辅助/悬停/装饰）
深色`--primary-dark`：10%（标题/强调）
中性色+辅助色：50%
3.2 辅助色体系
色名 | HEX | RGB | HSL | CSS变量 | 用途
------ | ----- | ----- | ----- | --------- | ------
**樱花粉** | `#F472B6` | rgb(244,114,182) | hsl(330,86%,70%) | `--accent-pink` | 好感度/恋爱相关/暧昧状态
**翡翠绿** | `#34D399` | rgb(52,211,153) | hsl(160,60%,52%) | `--accent-green` | 成功/完成/好感度提升/签到
**琥珀金** | `#FBBF24` | rgb(251,191,36) | hsl(43,96%,56%) | `--accent-gold` | CG解锁/成就/Streak/Standard推荐
3.3 中性色体系（9级灰阶）
色阶 | HEX | RGB | CSS变量 | 用途
------ | ----- | ----- | --------- | ------
**Neutral-50** | `#F9FAFB` | rgb(249,250,251) | `--neutral-50` | 页面背景(Light)
**Neutral-100** | `#F3F4F6` | rgb(243,244,246) | `--neutral-100` | 分组背景/卡片悬停
**Neutral-200** | `#E5E7EB` | rgb(229,231,235) | `--neutral-200` | 边框/分隔线
**Neutral-300** | `#D1D5DB` | rgb(209,213,219) | `--neutral-300` | 禁用状态边框
**Neutral-400** | `#9CA3AF` | rgb(156,163,175) | `--neutral-400` | 占位符文字/相识等级
**Neutral-500** | `#6B7280` | rgb(107,114,128) | `--neutral-500` | 辅助文字/正文
**Neutral-600** | `#4B5563` | rgb(75,85,99) | `--neutral-600` | 次要标题
**Neutral-700** | `#374151` | rgb(55,65,81) | `--neutral-700` | 正文（强调）
**Neutral-800** | `#1F2937` | rgb(31,41,55) | `--neutral-800` | 标题文字
**Neutral-900** | `#111827` | rgb(17,24,39) | `--neutral-900` | 最深文字/页面背景(Dark)
3.4 好感度等级色（5级）
等级 | 中文名 | 英文名 | HEX | CSS变量 | 分数段 | 使用场景
------ | -------- | -------- | ----- | --------- | -------- | ---------
**Lv.1** | 相识 | Acquaintance | `#9CA3AF` | `--bond-lv1` | 0-19 | 初次见面的冷淡感
**Lv.2** | 暧昧 | Flirt | `#F472B6` | `--bond-lv2` | 20-39 | 萌生好感的粉色
**Lv.3** | 信赖 | Trust | `#38BDF8` | `--bond-lv3` | 40-59 | 建立信任的清澈蓝
**Lv.4** | 羁绊 | Bond | `#A78BFA` | `--bond-lv4` | 60-79 | 深层连接的紫色
**Lv.5** | 挚爱 | Love | `#F43F5E` | `--bond-lv5` | 80-100 | 最高等级的炽热红
好感度进度条渐变定义：
  --bond-gradient: linear-gradient(90deg, #9CA3AF 0%, #F472B6 25%, #38BDF8 50%, #A78BFA 75%, #F43F5E 100%);
3.5 状态色
类型 | HEX | 浅色背景(10%) | CSS变量 | 用途
------ | ----- | -------------- | --------- | ------
**成功** | `#10B981` | `#D1FAE5` | `--success` / `--success-bg` | 完成/解锁/签到成功
**信息** | `#3B82F6` | `#DBEAFE` | `--info` / `--info-bg` | 提示/引导/新消息
**警告** | `#F59E0B` | `#FEF3C7` | `--warning` / `--warning-bg` | 注意/即将用完/提醒
**错误** | `#EF4444` | `#FEE2E2` | `--error` / `--error-bg` | 操作失败/支付错误/危险操作
3.6 深色模式色彩映射（指法-UI-09·总法-06）
**核心规则**：暗色模式为默认模式（视觉小说沉浸感），所有颜色降低饱和度15%。
浅色模式 | 深色模式 | 变量名(Dark) | 说明
--------- | --------- | ------------- | ------
`#4F46E5` | `#4338CA` | `--primary-dark-mode` | 主色降饱和
`#818CF8` | `#6366F1` | `--primary-light-dark-mode` | 浅色降饱和
`#1E1B4B` | `#312E81` | `--primary-dark-dark-mode` | 深色提亮
`#F472B6` | `#EC4899` | `--accent-pink-dark-mode` | 樱花粉降饱和
`#34D399` | `#10B981` | `--accent-green-dark-mode` | 翡翠绿降饱和
`#FBBF24` | `#F59E0B` | `--accent-gold-dark-mode` | 琥珀金降饱和
`#F9FAFB` | `#111827` | `--bg-page-dark` | 页面背景反转
`#FFFFFF` | `#1F2937` | `--bg-card-dark` | 卡片背景反转
`#1F2937` | `#F9FAFB` | `--text-primary-dark` | 标题文字反转
`#6B7280` | `#9CA3AF` | `--text-secondary-dark` | 辅助文字反转
`#E5E7EB` | `#374151` | `--border-dark` | 边框反转
`#10B981` | `#059669` | `--success-dark` | 成功色降饱和
`#3B82F6` | `#2563EB` | `--info-dark` | 信息色降饱和
`#F59E0B` | `#D97706` | `--warning-dark` | 警告色降饱和
`#EF4444` | `#DC2626` | `--error-dark` | 错误色降饱和
`#9CA3AF` | `#6B7280` | `--bond-lv1-dark` | 相识降饱和
`#F472B6` | `#EC4899` | `--bond-lv2-dark` | 暧昧降饱和
`#38BDF8` | `#0EA5E9` | `--bond-lv3-dark` | 信赖降饱和
`#A78BFA` | `#8B5CF6` | `--bond-lv4-dark` | 羁绊降饱和
`#F43F5E` | `#E11D48` | `--bond-lv5-dark` | 挚爱降饱和
深色模式CSS变量切换方案：
  :root {
  color-scheme: dark;
  --bg-page: #111827;
  --bg-card: #1F2937;
  --text-primary: #F9FAFB;
  --text-secondary: #9CA3AF;
  --border: #374151;
  --primary: #4338CA;
  --primary-light: #6366F1;
  }
  [data-theme="light"] {
  color-scheme: light;
  --bg-page: #F9FAFB;
  --bg-card: #FFFFFF;
  --text-primary: #1F2937;
  --text-secondary: #6B7280;
  --border: #E5E7EB;
  --primary: #4F46E5;
  --primary-light: #818CF8;
  }
3.7 渐变定义
渐变名 | CSS值 | 用途
-------- | ------- | ------
**品牌渐变** | `linear-gradient(135deg, #4F46E5 0%, #1E1B4B 100%)` | CTA大按钮/标准推荐按钮
**品牌渐变(Dark)** | `linear-gradient(135deg, #4338CA 0%, #312E81 100%)` | 深色模式CTA
**卡片渐变** | `linear-gradient(180deg, rgba(30,27,75,0.8) 0%, rgba(30,27,75,0.95) 100%)` | 剧本封面遮罩
**樱花渐变** | `linear-gradient(135deg, #F472B6 0%, #A78BFA 100%)` | 好感度升级动画/恋爱相关
**金粉渐变** | `linear-gradient(135deg, #FBBF24 0%, #F472B6 100%)` | 成就解锁/特殊奖励
**翡翠渐变** | `linear-gradient(135deg, #34D399 0%, #3B82F6 100%)` | 成功确认/完成动画
**按钮悬浮渐变** | `linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)` | 按钮Hover状态
**Standard推荐渐变** | `linear-gradient(135deg, #4F46E5 0%, #1E1B4B 100%)` | W11 Standard方案CTA
**Premium金色渐变** | `linear-gradient(135deg, #FBBF24 0%, #F59E0B 100%)` | Premium方案CTA
**结局-True End渐变** | `linear-gradient(135deg, #FBBF24 0%, #F472B6 50%, #4F46E5 100%)` | 分享卡片-True End
**结局-Normal渐变** | `linear-gradient(135deg, #3B82F6 0%, #A78BFA 100%)` | 分享卡片-Normal End
**结局-Bad渐变** | `linear-gradient(135deg, #991B1B 0%, #1F2937 100%)` | 分享卡片-Bad End
**结局-Secret渐变** | `linear-gradient(135deg, #7C3AED 0%, #4F46E5 100%)` | 分享卡片-Secret End
————————
四、字体体系（指法-UI-06）
4.1 字体选型
类型 | 拉丁/西文 | 中文简体 | 日文 | 韩文 | 备用
------ | ---------- | --------- | ------ | ------ | ------
**展示字体(Display)** | Playfair Display | Noto Serif SC | Noto Serif JP | Noto Serif KR | Georgia, serif
**主字体(Primary)** | Inter | Noto Sans SC | Noto Sans JP | Noto Sans KR | -apple-system, sans-serif
**对话字体(Dialogue)** | Georgia | Noto Serif SC | Noto Serif JP | Noto Serif KR | Times New Roman, serif
**等宽字体(Mono)** | JetBrains Mono | — | — | — | Fira Code, monospace
  --font-display: 'Playfair Display', 'Noto Serif SC', 'Noto Serif JP', 'Noto Serif KR', Georgia, serif;
  --font-primary: 'Inter', 'Noto Sans SC', 'Noto Sans JP', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-dialogue: 'Georgia', 'Noto Serif SC', 'Noto Serif JP', 'Noto Serif KR', 'Times New Roman', serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
4.2 字号层级
层级 | 字号(px/rem) | 字体 | 字重 | 用途 | 行高
------ | ------------- | ------ | ------ | ------ | ------
**H1** | 48px / 3rem | `--font-display` | 700 (Bold) | Hero主标题 | 1.2
**H2** | 32px / 2rem | `--font-display` | 600 (SemiBold) | 页面标题/区块标题 | 1.3
**H3** | 24px / 1.5rem | `--font-display` | 600 (SemiBold) | 子标题/卡片标题 | 1.4
**H4** | 18px / 1.125rem | `--font-primary` | 500 (Medium) | 小标题/面板标题 | 1.5
**H5** | 16px / 1rem | `--font-primary` | 500 (Medium) | 列表标题/按钮文字 | 1.5
**H6** | 14px / 0.875rem | `--font-primary` | 500 (Medium) | 标签/小标题 | 1.5
**Body** | 14px / 0.875rem | `--font-primary` | 400 (Regular) | 正文/描述 | 1.7
**Body-LG** | 16px / 1rem | `--font-primary` | 400 (Regular) | 大号正文/FAQ答案 | 1.7
**Caption** | 12px / 0.75rem | `--font-primary` | 400 (Regular) | 辅助文字/时间戳 | 1.5
**Overline** | 10px / 0.625rem | `--font-primary` | 600 (SemiBold) | 标签/角标/徽章 | 1.4
**Code** | 14px / 0.875rem | `--font-mono` | 400 (Regular) | 代码/错误码 | 1.6
**Dialogue** | 18px / 1.125rem | `--font-dialogue` | 400 (Regular) | 对话文字(特殊排版) | 1.9
**Dialogue-SM** | 16px / 1rem | `--font-dialogue` | 400 (Regular) | 移动端对话文字 | 1.9
**Stat-Number** | 36px / 2.25rem | `--font-display` | 700 (Bold) | 统计大数字 | 1.0
4.3 字重定义
字重值 | 名称 | 用途
-------- | ------ | ------
**100** | Thin | 极少使用，装饰性文字
**200** | ExtraLight | 不使用
**300** | Light | 水印/极淡装饰文字
**400** | Regular | 正文/对话/描述/辅助文字
**500** | Medium | 小标题/按钮/导航/标签
**600** | SemiBold | 标题/强调/徽章/Overline
**700** | Bold | H1/统计数字/品牌名/CTA
**800** | ExtraBold | 不使用
**900** | Black | 不使用
4.4 行高规范
类型 | 行高倍数 | CSS值 | 用途
------ | --------- | ------- | ------
**紧凑** | 1.0 | `line-height: 1` | 统计数字/单行标签
**标题** | 1.2-1.3 | `line-height: 1.2` | H1/H2大标题
**标准** | 1.5 | `line-height: 1.5` | H3-H6/按钮/导航
**正文** | 1.7 | `line-height: 1.7` | 正文/描述/列表
**对话** | 1.9 | `line-height: 1.9` | 对话文字（沉浸阅读）
**宽松** | 2.0 | `line-height: 2` | 辅助文字/Caption
4.5 多语言字体降级策略
  /* 英文优先场景 */
  html[lang="en"] {
  --font-display: 'Playfair Display', Georgia, serif;
  --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-dialogue: 'Georgia', 'Times New Roman', serif;
  }
  /* 日文优先场景 */
  html[lang="ja"] {
  --font-display: 'Noto Serif JP', 'Playfair Display', serif;
  --font-primary: 'Noto Sans JP', 'Inter', sans-serif;
  --font-dialogue: 'Noto Serif JP', serif;
  }
  /* 韩文优先场景 */
  html[lang="ko"] {
  --font-display: 'Noto Serif KR', 'Playfair Display', serif;
  --font-primary: 'Noto Sans KR', 'Inter', sans-serif;
  --font-dialogue: 'Noto Serif KR', serif;
  }
  /* 中文优先场景 */
  html[lang="zh"] {
  --font-display: 'Noto Serif SC', 'Playfair Display', serif;
  --font-primary: 'Noto Sans SC', 'Inter', sans-serif;
  --font-dialogue: 'Noto Serif SC', serif;
  }
4.6 对话文字特殊排版
参数 | 值 | 说明
------ | ----- | ------
**字体** | Georgia / Noto Serif SC/JP/KO | 衬线体营造文学感
**字号** | 1.125rem (18px) | 略大于正文，沉浸阅读
**行高** | 1.9 | 宽松行高，阅读舒适
**段间距** | 16px (`--space-4`) | 段落间留白
**首行缩进** | 2em | 中文/日文首行缩进
**字间距** | 0.02em | 微微增加字间距
**颜色(Dark)** | `#E5E7EB` (`--neutral-200`) | 深色模式下对话文字色
**颜色(Light)** | `#374151` (`--neutral-700`) | 浅色模式下对话文字色
**角色名** | 14px Medium `--accent-pink` | 角色名标识
**打字速度** | 1x=40ms/字, 1.5x=27ms/字, 2x=20ms/字 | 可调节打字速度
————————
五、间距体系（指法-UI-04·总法-04）
5.1 4px基础单位完整间距表
变量名 | 值 | rem | 倍数 | 具体用途定义
-------- | ----- | ----- | ------ | ------------
`--space-1` | **4px** | 0.25rem | 1× | 图标与文字间距/标签内边距/极小元素间距
`--space-2` | **8px** | 0.5rem | 2× | 组件内间距/选项间距/按钮内图标间距/列表项间距
`--space-3` | **12px** | 0.75rem | 3× | 任务卡片间距/输入框与标签间距/小卡片内边距
`--space-4` | **16px** | 1rem | 4× | 默认间距/卡片内边距/段落间距/按钮内边距(水平)
`--space-5` | **20px** | 1.25rem | 5× | 面板内边距/中等区块间距
`--space-6` | **24px** | 1.5rem | 6× | 组件间间距/卡片间距/Header高度基准
`--space-8` | **32px** | 2rem | 8× | 模块间距/页面边距(≥1440px)/大区块间距
`--space-10` | **40px** | 2.5rem | 10× | 页面侧边距(桌面端)/大面板间距
`--space-12` | **48px** | 3rem | 12× | 侧栏宽度基准/Header高度(xl断点)/大区块分隔
`--space-16` | **64px** | 4rem | 16× | 页面顶部留白/Hero区域上下间距
`--space-20` | **80px** | 5rem | 20× | 页面底部留白/Footer间距
`--space-24` | **96px** | 6rem | 24× | Hero区域高度/特大区块分隔
5.2 间距使用规则
  ❌ 禁止使用非4倍数的间距值（如5px/7px/10px/15px等）
  ✅ 所有间距必须使用--space-X变量
  ✅ 响应式间距可通过断点覆盖（如移动端--space-4=12px）
  ✅ 组件内间距不小于--space-2(8px)
  ✅ 页面级间距不小于--space-8(32px)
————————
六、圆角体系（总法-03）
6.1 圆角定义
类型 | 值 | CSS变量 | 适用元素
------ | ----- | --------- | ---------
**无圆角** | 0px | `--radius-none` | 立绘/背景图/分割线
**超小** | 2px | `--radius-xs` | 极小元素(指示器/小图标背景)
**小** | 4px | `--radius-sm` | 标签/徽章/角标/小按钮
**中** | 8px | `--radius-md` | 按钮/输入框/下拉菜单/Tab项
**大** | 12px | `--radius-lg` | 卡片/剧本卡片/角色卡片/面板
**超大** | 16px | `--radius-xl` | 弹窗/Modal/对话框/Paywall弹窗/退出挽留弹窗
**特大** | 24px | `--radius-2xl` | Hero区域容器/特殊装饰容器
**全圆** | 50% | `--radius-full` | 头像/圆形按钮/进度点/图标容器
**胶囊** | 9999px | `--radius-pill` | 药丸按钮/标签/徽章/搜索框
6.2 圆角红线
  ❌ 禁止使用范围外圆角值（如3px/5px/6px/7px/9px/10px/11px/13px/14px/15px等）
  ❌ 禁止同一层级组件使用不同圆角值
  ✅ 按钮=8px, 卡片=12px, 弹窗=16px, 头像=50%
  ✅ v4.1新增组件（C29-C33）严格遵循：弹窗=16px, 卡片=12px, 按钮=8px
————————
七、阴影层级（总法-05）
7.1 Elevation定义
层级 | 名称 | CSS值 | 用途 | 场景
------ | ------ | ------- | ------ | ------
**E0** | 无阴影 | `none` | 平面元素 | 分割线/背景元素/禁用状态
**E1** | 微阴影 | `0 1px 2px rgba(0,0,0,0.05)` | 静态卡片 | 剧本卡片/设置项/列表项
**E2** | 轻阴影 | `0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.05)` | 悬浮元素 | 下拉菜单/Tooltip/Header
**E3** | 中阴影 | `0 10px 15px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05)` | 弹出元素 | 弹窗/Modal/Paywall/挽留弹窗
**E4** | 重阴影 | `0 20px 25px rgba(0,0,0,0.15), 0 10px 10px rgba(0,0,0,0.04)` | 焦点元素 | 当前选中卡片/推荐方案(Standard)
7.2 深色模式阴影映射
层级 | 深色模式CSS值 | 说明
------ | ------------- | ------
**E1-Dark** | `0 1px 2px rgba(0,0,0,0.3)` | 深色模式阴影加重
**E2-Dark** | `0 4px 6px rgba(0,0,0,0.4), 0 2px 4px rgba(0,0,0,0.3)` | 深色模式阴影加重
**E3-Dark** | `0 10px 15px rgba(0,0,0,0.5), 0 4px 6px rgba(0,0,0,0.3)` | 深色模式阴影加重
**E4-Dark** | `0 20px 25px rgba(0,0,0,0.6), 0 10px 10px rgba(0,0,0,0.2)` | 深色模式阴影加重
7.3 特殊阴影
名称 | CSS值 | 用途
------ | ------- | ------
**品牌光晕** | `0 0 20px rgba(79,70,229,0.3)` | CTA按钮Hover/推荐卡片
**粉色光晕** | `0 0 15px rgba(244,114,182,0.3)` | 好感度升级/恋爱相关动画
**金色光晕** | `0 0 15px rgba(251,191,36,0.3)` | 成就解锁/Standard推荐
**Standard推荐阴影** | `0 8px 24px rgba(79,70,229,0.2)` | W11 Standard方案卡片
**内阴影(输入框)** | `inset 0 1px 2px rgba(0,0,0,0.1)` | 输入框Focus状态
————————
八、图标规范（指法-UI-07）
8.1 图标尺寸体系
尺寸 | 像素 | 用途 | viewBox
------ | ------ | ------ | ---------
**XS** | 16×16px | 内联图标/标签图标/小徽章 | 0 0 16 16
**SM** | 20×20px | 列表图标/导航图标/按钮内图标 | 0 0 20 20
**MD** | 24×24px | 主导航图标/Header图标/操作图标 | 0 0 24 24
**LG** | 32×32px | 功能入口图标/空状态图标/签到网格 | 0 0 32 32
**XL** | 48×48px | 大功能图标/成就图标/分类入口 | 0 0 48 48
8.2 图标风格规范
参数 | 值 | 说明
------ | ----- | ------
**风格** | 线性(Outline) | 统一线性风格，不使用填充图标
**线宽** | 1.5px | 所有图标统一stroke-width: 1.5
**端点** | round | stroke-linecap: round
**连接** | round | stroke-linejoin: round
**颜色** | `currentColor` | 继承父元素颜色
**格式** | SVG (inline) | 全部使用内联SVG，不使用图标字体
**填充区域** | `fill: none` | 线性图标不填充
**交互图标** | 加`cursor: pointer` | 可点击图标
**无障碍** | `aria-hidden="true"` | 装饰图标；功能图标用`aria-label`
8.3 产品专用图标清单
图标名 | 尺寸 | 用途 | 颜色
-------- | ------ | ------ | ------
`icon-bond-heart` | 20/24px | 好感度心形 | `--accent-pink`
`icon-bond-broken` | 20px | 好感度降低 | `--error`
`icon-script-scroll` | 24px | 剧本类型-剧情 | `--primary-light`
`icon-script-mystery` | 24px | 剧本类型-悬疑 | `--neutral-500`
`icon-script-romance` | 24px | 剧本类型-恋爱 | `--accent-pink`
`icon-script-adventure` | 24px | 剧本类型-冒险 | `--accent-green`
`icon-achievement-star` | 24/32px | 成就解锁 | `--accent-gold`
`icon-achievement-locked` | 24/32px | 成就未解锁 | `--neutral-300`
`icon-sub-crown` | 20/24px | Premium标识 | `--accent-gold`
`icon-sub-star` | 20/24px | Standard标识 | `--accent-gold`
`icon-fragment` | 16/20px | 碎片货币 | `--accent-gold`
`icon-streak-fire` | 20/24/32px | Streak火焰 | `--accent-gold`
`icon-streak-fire-active` | 24px | Streak活跃(跳动动画) | `--accent-gold`
`icon-cg-frame` | 24px | CG收集 | `--primary-light`
`icon-cg-locked` | 24px | CG未解锁 | `--neutral-300`
`icon-daily-check` | 20px | 每日任务完成 | `--success`
`icon-daily-pending` | 20px | 每日任务未完成 | `--neutral-400`
`icon-choice-arrow` | 16px | 选择项指示器 | `--primary`
`icon-timeline-dot` | 12px | 关系时间轴节点 | `--primary-light`
`icon-share-twitter` | 20px | 分享到Twitter | `#1DA1F2`
`icon-share-instagram` | 20px | 分享到Instagram | 渐变`#833AB4→#FD1D1D`
`icon-share-copy` | 20px | 复制图片/链接 | `currentColor`
`icon-paywall-lock` | 48px | Paywall锁定图标 | `--primary-light`
`icon-end-true` | 32px | True End标记 | `--accent-gold`
`icon-end-normal` | 32px | Normal End标记 | `--info`
`icon-end-bad` | 32px | Bad End标记 | `--error`
`icon-end-secret` | 32px | Secret End标记 | `--bond-lv4`
————————
九、组件库规范（指法-UI-02）
9.1 按钮组件
9.1.1 主按钮（Primary Button）
状态 | 背景色 | 文字色 | 边框 | 阴影 | 其他
------ | -------- | -------- | ------ | ------ | ------
**Default** | `#4F46E5` | `#FFFFFF` | none | `0 1px 2px rgba(0,0,0,0.05)` | `border-radius: 8px; height: 44px; padding: 0 24px; font-weight: 500; font-size: 14px;`
**Hover** | `#4338CA` | `#FFFFFF` | none | `0 4px 6px rgba(79,70,229,0.3)` | `transform: translateY(-1px); transition: all 150ms ease;`
**Active** | `#3730A3` | `#FFFFFF` | none | `0 1px 2px rgba(0,0,0,0.05)` | `transform: scale(0.97); transition: all 100ms ease;`
**Focus** | `#4F46E5` | `#FFFFFF` | `2px solid #818CF8` (offset 2px) | `0 0 0 4px rgba(129,140,248,0.3)` | outline-none
**Disabled** | `#D1D5DB` | `#9CA3AF` | none | none | `cursor: not-allowed; opacity: 0.6;`
**Loading** | `#4F46E5` | 旋转图标 | none | `0 1px 2px rgba(0,0,0,0.05)` | `pointer-events: none;`
Dark Mode映射：
状态 | 背景色 | 文字色
------ | -------- | --------
Default | `#4338CA` | `#FFFFFF`
Hover | `#6366F1` | `#FFFFFF`
Active | `#4F46E5` | `#FFFFFF`
Disabled | `#374151` | `#6B7280`
9.1.2 次按钮（Secondary Button）
状态 | 背景色 | 文字色 | 边框 | 阴影 | 其他
------ | -------- | -------- | ------ | ------ | ------
**Default** | `transparent` | `#4F46E5` | `1px solid #4F46E5` | none | `border-radius: 8px; height: 44px; padding: 0 24px;`
**Hover** | `rgba(79,70,229,0.08)` | `#4338CA` | `1px solid #4338CA` | none | `transition: all 150ms ease;`
**Active** | `rgba(79,70,229,0.15)` | `#3730A3` | `1px solid #3730A3` | none | `transform: scale(0.97);`
**Focus** | `transparent` | `#4F46E5` | `2px solid #818CF8` | `0 0 0 4px rgba(129,140,248,0.3)` | outline-none
**Disabled** | `transparent` | `#9CA3AF` | `1px solid #D1D5DB` | none | `cursor: not-allowed;`
9.1.3 文字按钮（Text Button）
状态 | 背景色 | 文字色 | 其他
------ | -------- | -------- | ------
**Default** | `transparent` | `#4F46E5` | `padding: 8px 12px; font-weight: 500; text-decoration: none;`
**Hover** | `rgba(79,70,229,0.08)` | `#4338CA` | `text-decoration: underline;`
**Active** | `rgba(79,70,229,0.15)` | `#3730A3` | —
**Disabled** | `transparent` | `#9CA3AF` | `cursor: not-allowed;`
9.1.4 图标按钮（Icon Button）
状态 | 尺寸 | 背景色 | 图标色 | 圆角 | 其他
------ | ------ | -------- | -------- | ------ | ------
**Default** | 44×44px | `transparent` | `--neutral-500` | 8px | `display: flex; align-items: center; justify-content: center;`
**Hover** | 44×44px | `rgba(79,70,229,0.08)` | `--primary` | 8px | `transition: all 150ms ease;`
**Active** | 44×44px | `rgba(79,70,229,0.15)` | `--primary-dark` | 8px | `transform: scale(0.95);`
**Focus** | 44×44px | `transparent` | `--primary` | 8px | `box-shadow: 0 0 0 4px rgba(129,140,248,0.3);`
9.1.5 CTA大按钮（Hero CTA）
状态 | 背景 | 文字色 | 阴影 | 其他
------ | ------ | -------- | ------ | ------
**Default** | `linear-gradient(135deg, #4F46E5, #1E1B4B)` | `#FFFFFF` | `0 4px 14px rgba(79,70,229,0.4)` | `height: 56px; padding: 0 40px; font-size: 18px; font-weight: 600; border-radius: 12px;`
**Hover** | `linear-gradient(135deg, #6366F1, #4F46E5)` | `#FFFFFF` | `0 8px 24px rgba(79,70,229,0.5)` | `transform: translateY(-2px) scale(1.02); transition: all 200ms ease;`
**Active** | `linear-gradient(135deg, #4338CA, #1E1B4B)` | `#FFFFFF` | `0 2px 8px rgba(79,70,229,0.3)` | `transform: scale(0.98);`
9.1.6 方案选择按钮（Subscription CTA）
档位 | 背景 | 文字色 | 高度 | 特殊
------ | ------ | -------- | ------ | ------
**Free** | `#E5E7EB` | `#6B7280` | 44px | `cursor: default; opacity: 0.7;`
**Basic** | `#4F46E5` | `#FFFFFF` | 44px | 标准主按钮
**Standard** | `linear-gradient(135deg, #4F46E5, #1E1B4B)` | `#FFFFFF` | **52px** | `font-size: 16px; box-shadow: 0 8px 24px rgba(79,70,229,0.2);`
**Premium** | `linear-gradient(135deg, #FBBF24, #F59E0B)` | `#1E1B4B` | 44px | 金色渐变
————————
9.2 输入框组件
9.2.1 单行输入框（Text Input）
状态 | 背景色 | 边框 | 文字色 | 其他
------ | -------- | ------ | -------- | ------
**Default** | `#FFFFFF` / `#1F2937`(dark) | `1px solid #E5E7EB` / `#374151` | `--neutral-800` / `--neutral-50`(dark) | `height: 44px; padding: 0 16px; border-radius: 8px; font-size: 14px;`
**Hover** | 同上 | `1px solid #D1D5DB` / `#4B5563` | 同上 | `transition: border-color 150ms ease;`
**Focus** | 同上 | `2px solid #4F46E5` | 同上 | `box-shadow: inset 0 1px 2px rgba(0,0,0,0.1), 0 0 0 4px rgba(79,70,229,0.1);`
**Error** | `#FEF2F2` / `rgba(239,68,68,0.05)` | `2px solid #EF4444` | `--error` | 行内错误文字：12px `#EF4444`
**Disabled** | `#F3F4F6` / `#111827` | `1px solid #E5E7EB` / `#374151` | `--neutral-400` | `cursor: not-allowed;`
9.2.2 多行输入框（Textarea）
参数 | 值
------ | -----
**最小高度** | 88px
**内边距** | 12px 16px
**resize** | vertical
**字号** | 14px
**行高** | 1.6
**其余状态** | 同单行输入框
9.2.3 搜索输入框（Search Input）
参数 | 值
------ | -----
**左侧图标** | 🔍 (icon-search 20px, color: --neutral-400)
**高度** | 44px
**圆角** | `--radius-pill` (9999px)
**背景色** | `#F3F4F6` / `#374151`(dark)
**占位符色** | `--neutral-400`
**padding-left** | 44px（图标+间距）
9.2.4 自由文本输入（Free Text Input — W06游玩页）
参数 | 值
------ | -----
**高度** | 48px（单行）/ 自动扩展（最大120px）
**背景** | `rgba(255,255,255,0.08)` / 深色模式 `rgba(255,255,255,0.05)`
**边框** | `1px solid rgba(255,255,255,0.15)`
**圆角** | 12px
**字号** | 16px
**Focus** | 边框变为 `--primary-light`，背景变为 `rgba(255,255,255,0.12)`
**发送按钮** | 内嵌右侧，44×44px圆形，`--primary`背景
————————
9.3 选择器组件
9.3.1 单选卡片（Radio Card）
状态 | 背景色 | 边框 | 其他
------ | -------- | ------ | ------
**Default** | `--bg-card` | `2px solid --neutral-200` | `border-radius: 12px; padding: 16px; cursor: pointer;`
**Hover** | `--neutral-50` | `2px solid --primary-light` | `transition: all 150ms ease;`
**Selected** | `rgba(79,70,229,0.05)` | `2px solid --primary` | 右上角显示✓图标(`--primary`色)
**Disabled** | `--neutral-50` | `2px solid --neutral-200` | `opacity: 0.5; cursor: not-allowed;`
9.3.2 多选偏好（Preference Chip）
状态 | 背景色 | 文字色 | 边框
------ | -------- | -------- | ------
**Default** | `transparent` | `--neutral-600` | `1px solid --neutral-300`
**Hover** | `rgba(79,70,229,0.05)` | `--primary` | `1px solid --primary-light`
**Selected** | `--primary` | `#FFFFFF` | `1px solid --primary`
规格：height: 36px; padding: 0 16px; border-radius: 9999px; font-size: 14px; font-weight: 500;
9.3.3 下拉筛选（Dropdown Select）
参数 | 值
------ | -----
**触发器高度** | 44px
**触发器圆角** | 8px
**触发器边框** | `1px solid --neutral-200`
**下拉面板圆角** | 12px
**下拉面板阴影** | E2 (`0 4px 6px rgba(0,0,0,0.07)`)
**选项高度** | 40px
**选项Hover** | `background: --neutral-50;`
**选项选中** | `background: rgba(79,70,229,0.08); color: --primary; font-weight: 500;`
9.3.4 开关（Toggle Switch）
状态 | 轨道颜色 | 滑块颜色 | 尺寸
------ | --------- | --------- | ------
**Off** | `--neutral-300` | `#FFFFFF` | 44×24px，滑块20×20px
**On** | `--primary` | `#FFFFFF` | 44×24px，滑块20×20px
**Disabled Off** | `--neutral-200` | `--neutral-100` | `opacity: 0.6;`
**Disabled On** | `--primary-light` | `#FFFFFF` | `opacity: 0.6;`
动画：transition: background-color 200ms ease, transform 200ms ease; 滑块 translateX(20px)
9.3.5 滑块（Range Slider）
参数 | 值
------ | -----
**轨道高度** | 4px
**轨道圆角** | 2px
**轨道已填充色** | `--primary`
**轨道未填充色** | `--neutral-200`
**滑块** | 20×20px圆形，`#FFFFFF`背景，`--primary`边框(2px)，E1阴影
**滑块Hover** | scale(1.2)，`box-shadow: 0 0 0 6px rgba(79,70,229,0.15)`
**当前值标签** | 滑块上方显示，12px `--font-primary`，`--neutral-700`色
————————
9.4 导航组件
9.4.1 Header导航栏
参数 | 移动端(<768px) | 桌面端(≥768px)
------ | --------------- | ---------------
**高度** | 56px | 64px
**背景色** | `rgba(17,24,39,0.95)` + `backdrop-filter: blur(12px)` | 同左
**Logo** | 32px高 | 40px高
**导航项** | 隐藏，使用汉堡菜单 | 水平排列，间距24px
**字体** | — | 14px Medium `--neutral-200`
**活跃项** | — | `color: --primary-light; border-bottom: 2px solid --primary-light;`
**固定** | 顶部固定(position: sticky) | 同左
**阴影** | E1 | E1
**右侧区域** | `[🔥DayX] [⚙️] [👤]` | `[🔥DayX] [📖剧本名] [⚙️] [💾] [👤]`
9.4.2 Tab切换
状态 | 背景色 | 文字色 | 其他
------ | -------- | -------- | ------
**Default** | `transparent` | `--neutral-500` | `padding: 12px 20px; font-size: 14px; font-weight: 500;`
**Hover** | `rgba(79,70,229,0.05)` | `--primary-light` | —
**Active** | `transparent` | `--primary` | `border-bottom: 2px solid --primary;`
**Disabled** | `transparent` | `--neutral-300` | `cursor: not-allowed;`
容器：border-bottom: 1px solid --neutral-200; 底部边框分隔
9.4.3 面包屑（Breadcrumb）
参数 | 值
------ | -----
**字号** | 14px
**颜色** | `--neutral-500`
**当前页** | `--neutral-800`(dark: `--neutral-50`) font-weight: 500
**分隔符** | `>` 或 `/`，色`--neutral-300`
**间距** | 各项间距 8px
**链接Hover** | `color: --primary; text-decoration: underline;`
————————
9.5 反馈组件
9.5.1 Toast通知
类型 | 背景色 | 左侧图标色 | 文字色 | 持续时间
------ | -------- | ----------- | -------- | ---------
**成功** | `#D1FAE5`(L) / `rgba(16,185,129,0.15)`(D) | `#10B981` | `--neutral-800`(L) / `--neutral-50`(D) | 3s
**信息** | `#DBEAFE` / `rgba(59,130,246,0.15)` | `#3B82F6` | 同上 | 4s
**警告** | `#FEF3C7` / `rgba(245,158,11,0.15)` | `#F59E0B` | 同上 | 5s
**错误** | `#FEE2E2` / `rgba(239,68,68,0.15)` | `#EF4444` | 同上 | 不自动关闭(需手动)
规格：padding: 12px 20px; border-radius: 12px; box-shadow: E3; max-width: 400px; font-size: 14px;
位置：顶部居中，距顶24px
动画：fadeIn + translateY(-10px→0)，300ms ease-out
9.5.2 Modal弹窗
参数 | 值
------ | -----
**遮罩** | `rgba(0,0,0,0.6)` + `backdrop-filter: blur(8px)`
**内容区宽度** | 480px(标准) / 600px(大) / 90vw(移动)
**内容区背景** | `#FFFFFF`(L) / `#1F2937`(D)
**圆角** | 16px
**阴影** | E3
**内边距** | 32px(桌面) / 24px(移动)
**关闭按钮** | 右上角，44×44px，`icon-close`
**弹出动画** | `scale(0.9)→scale(1) + opacity(0→1)`，300ms ease-out
**焦点管理** | focus trap，Tab循环，ESC关闭
9.5.3 Alert横幅
类型 | 背景色 | 左侧边框 | 图标色
------ | -------- | --------- | --------
**Info** | `--info-bg` | `4px solid --info` | `--info`
**Warning** | `--warning-bg` | `4px solid --warning` | `--warning`
**Error** | `--error-bg` | `4px solid --error` | `--error`
规格：padding: 16px 20px; border-radius: 8px; font-size: 14px; line-height: 1.5;
9.5.4 Loading加载
类型 | 尺寸 | 颜色 | 速度
------ | ------ | ------ | ------
**Spinner** | 24/32/48px | `--primary` | 1s linear infinite
**Dots** | 3×8px | `--primary-light` | 1.4s ease-in-out infinite
**Progress Bar** | 高度4px | `--primary`渐变`--primary-light` | 根据进度
9.5.5 Skeleton骨架屏
参数 | 值
------ | -----
**背景色** | `--neutral-200`(L) / `--neutral-700`(D)
**动画色** | `--neutral-100`(L) / `--neutral-600`(D)
**圆角** | 4px(文字行) / 12px(卡片)
**动画** | shimmer渐变，1.5s linear infinite
**文字行高度** | 14px（正文）/ 20px（标题）
  @keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
  }
9.5.6 Progress Bar进度条
参数 | 值
------ | -----
**轨道高度** | 8px（标准）/ 4px（细）
**轨道圆角** | 4px / 2px
**轨道背景** | `--neutral-200`(L) / `--neutral-700`(D)
**填充色** | `--primary`（默认）/ 好感度渐变（好感度条）
**动画** | `transition: width 500ms ease-out;`
**标签** | 右侧显示百分比，12px `--neutral-500`
————————
9.6 数据展示组件
9.6.1 表格（Table）
参数 | 值
------ | -----
**表头** | `background: --neutral-50; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; color: --neutral-500;`
**行高** | 48px
**单元格padding** | `12px 16px`
**分隔线** | `border-bottom: 1px solid --neutral-200;`
**Hover行** | `background: --neutral-50;`
**高亮列(Standard)** | `background: #EEF2FF;`(L) / `rgba(79,70,229,0.08);`(D)
**响应式** | md及以下断点转为横向滚动(`overflow-x: auto`)
9.6.2 列表（List）
参数 | 值
------ | -----
**列表项高度** | 最小48px
**列表项padding** | `12px 16px`
**分隔线** | `border-bottom: 1px solid --neutral-100;`
**Hover** | `background: --neutral-50;`
**图标间距** | 图标与文字间距 12px
9.6.3 卡片（Card）
参数 | 值
------ | -----
**背景** | `--bg-card`
**圆角** | 12px
**阴影** | E1
**内边距** | 20px（标准）/ 16px（紧凑）
**Hover** | `box-shadow: E2; transform: translateY(-2px); transition: all 200ms ease;`
**边框** | `1px solid --neutral-200`(L) / `--neutral-700`(D)
9.6.4 统计数字（Stat Card）
参数 | 值
------ | -----
**数字字号** | 36px Bold `--font-display`
**标签字号** | 12px Regular `--neutral-500`
**排列** | xl断点5列，lg 4列，md 3列，sm 2列
**动画** | 进入时从0滚动到实际值，800ms ease-out
**卡片样式** | 标准卡片样式(12px圆角, E1阴影, 20px内边距)
9.6.5 进度条（见9.5.6）
9.6.6 雷达图（Radar Chart — W09角色档案）
参数 | 值
------ | -----
**尺寸** | 240×240px（桌面）/ 200×200px（移动）
**渲染** | SVG
**轴线色** | `--neutral-200`(L) / `--neutral-700`(D)
**填充色** | `rgba(79,70,229,0.2)`
**描边色** | `--primary`
**标签字号** | 12px `--neutral-500`
**维度** | 5个：Openness/Conscientiousness/Extraversion/Agreeableness/Neuroticism
————————
9.7 布局组件
9.7.1 栅格系统
断点 | 列数 | 列间距(Gutter) | 外边距(Margin)
------ | ------ | --------------- | ---------------
**xs (<640px)** | 4列 | 16px | 16px
**sm (≥640px)** | 8列 | 16px | 24px
**md (≥768px)** | 12列 | 24px | 32px
**lg (≥1024px)** | 12列 | 24px | 40px
**xl (≥1440px)** | 12列 | 32px | 40px (max-width: 1440px居中)
  .container {
  width: 100%;
  max-width: 1440px;
  margin: 0 auto;
  padding: 0 var(--container-margin, 16px);
  }
9.7.2 容器（Container）
类型 | 最大宽度 | 用途
------ | --------- | ------
**Container** | 1440px | 页面主容器
**Container-Narrow** | 800px | 文章/详情页
**Container-Wide** | 100% | 全屏区域(Hero)
9.7.3 分割线（Divider）
参数 | 值
------ | -----
**高度** | 1px
**颜色** | `--neutral-200`(L) / `--neutral-700`(D)
**间距** | 上下各24px (`--space-6`)
**变体** | 实线(默认) / 虚线(`border-style: dashed`)
————————
9.8 剧本卡片组件
参数 | 值
------ | -----
**尺寸** | 宽度100%（响应式），封面高度200px
**结构** | 封面图(200px) + 信息区(自适应)
**圆角** | 12px
**阴影** | E1，Hover时E2
**封面遮罩** | `linear-gradient(180deg, transparent 40%, rgba(30,27,75,0.9) 100%)`
**标题** | 18px SemiBold `--text-primary`，封面内底部
**类型标签** | 12px Medium，pill形状，`--accent-pink`/`--accent-green`/`--neutral-500`
**评分** | ⭐ + 14px Medium `--accent-gold`
**路线数/结局数** | 12px `--neutral-500`，如"3 routes · 6 endings"
**简介摘要** | 14px `--neutral-500`，最多2行，溢出ellipsis
**Hover** | `transform: translateY(-4px); box-shadow: E2;`
**网格** | xl 4列 / lg 3列 / md 2列 / sm 1列
————————
9.9 CG卡片组件
状态 | 视觉表现 | 其他
------ | --------- | ------
**已解锁** | 完整CG图片，Hover时轻微放大(scale 1.03) | 底部标题+解锁时间
**未解锁** | 灰色剪影+🔒图标(32px)+模糊(blur 10px) | "???"文字
**Hover(未解锁)** | 微微降低模糊(blur 8px) | 显示解锁条件提示
参数 | 值
------ | -----
**尺寸** | 宽高比16:9，宽度响应式
**圆角** | 12px
**网格** | xl 4列 / lg 3列 / md 2列 / sm 1列
**间距** | 16px
**点击查看** | 已解锁→大图模式(全屏遮罩+居中显示)
————————
9.10 角色立绘组件
参数 | 桌面端(≥768px) | 移动端(<768px)
------ | --------------- | ---------------
**位置** | 左侧面板，固定宽度280px | 顶部区域，全宽
**高度** | 占满游玩区高度(100vh-64px) | 240px固定
**立绘宽度** | 280px | 自适应(最大180px)
**背景** | 透明(叠加在场景背景上) | 同左
**表情切换** | `opacity: 0→1`，300ms ease-out | 同左
**表情标签** | 底部居中标签，pill形状，`rgba(0,0,0,0.6)`背景 | 同左
**好感度指示** | 左侧边缘半隐藏进度条(4px宽，hover展开到8px) | 顶部横条
**名称标签** | 底部：角色名+好感度等级，14px Medium | 同左
————————
9.11 Paywall弹窗组件（C29·v4.1新增）
参数 | 桌面端 | 移动端
------ | -------- | --------
**尺寸** | 600×700px，居中 | 100vw×100vh全屏模态
**遮罩** | `rgba(0,0,0,0.6)` + `backdrop-filter: blur(8px)` | 同左
**内容背景** | `#FFFFFF`(L) / `#1F2937`(D) | 同左
**圆角** | 16px | 0px（全屏）
**关闭按钮** | 右上角44×44px `[✕]` | 同左
**弹出动画** | `scale(0.9)→scale(1) + fadeIn`，300ms ease-out | `translateY(100%)→translateY(0)`，300ms ease-out
**CTA按钮** | 渐变深靛蓝(`#4F46E5→#1E1B4B`)，52px高，宽度≥280px | 宽度100%-32px
**阴影** | E3 | 无（全屏）
**焦点管理** | focus trap + `role="dialog"` + `aria-modal="true"` | 同左
**无障碍** | `aria-labelledby`指向弹窗标题，ESC关闭 | 同左
弹窗内部结构：
  [✕关闭]
  🔒 图标(48px, --primary-light)
  标题(24px SemiBold)："Your 3 daily conversations are used up"
  副标题(16px, --neutral-500)："Don't stop your story here!"
  进度面板(--neutral-50背景, 12px圆角, 16px内边距)：
  - ❤️ Bond: [等级] [分数]/100
  - 📖 剧本进度: X%
  - 🖼️ CG待解锁: X张
  - 🏆 下一成就: 差X步
  推荐方案卡片(Standard高亮, 12px圆角)：
  - ⭐ Standard — $4.99/月
  - 3行权益摘要
  - [🎁 Start 7-Day Free Trial] CTA按钮
  辅助链接："View all plans →"(14px, --primary)
  关闭文字："Maybe later"(14px, --neutral-400)
————————
9.12 Streak签到组件（C30·v4.1新增）
参数 | W06弹出面板 | W07嵌入面板
------ | ------------ | ------------
**宽度** | 320px | 100%（容器宽度）
**背景** | `--bg-card` | `--bg-card`
**圆角** | 16px | 12px
**阴影** | E3 | E1
**内边距** | 24px | 20px
**7天网格** | 7×32px圆形，间距8px | 7×32px圆形，间距12px
**签到✅** | `background: #10B981; color: #FFF;` | 同左
**未签到○** | `border: 2px solid --neutral-300;` | 同左
**连续天数** | 48px Bold `--accent-gold` | 48px Bold `--accent-gold`
**阶梯奖励** | 纵向列表，间距12px | 横向卡片(4列)，间距12px
**已达奖励** | `✅`绿色 + 金色背景(`rgba(251,191,36,0.1)`) | 同左
**未达奖励** | `🔒`灰色 + 普通背景 + "再签X天解锁" | 同左
火焰跳动动画：
  @keyframes flame-bounce {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-3px) scale(1.1); }
  }
  .flame-active { animation: flame-bounce 200ms ease-out; }
————————
9.13 每日任务组件（C31·v4.1新增）
参数 | 值
------ | -----
**容器宽度** | 100%
**标题** | "📋 今日任务 Daily Tasks"，H4，右侧显示"[X/3]"
**任务卡片高度** | 自适应（最小64px）
**任务卡片间距** | 12px (`--space-3`)
**卡片圆角** | 8px
**卡片内边距** | 16px
**已完成卡片** | 左侧4px绿色边框(`#10B981`) + 浅绿背景(`#ECFDF5`(L)/`rgba(16,185,129,0.1)`(D)) + ✅图标
**未完成卡片** | 左侧4px灰色边框 + 白色/深灰背景 + ☐图标
**进度条** | 4px高，`--primary`填充，圆角2px
**碎片标签** | 12px `--accent-gold`，如"+10碎片"
**完成动画** | check图标scale(0→1) 300ms ease-out + 背景渐变
**全完成庆祝** | Canvas/Lottie烟花特效，2秒覆盖任务区域
**刷新动画** | 卡片翻转500ms (rotateX)
————————
9.14 结局分享卡片组件（C32·v4.1新增）
参数 | 值
------ | -----
**生成尺寸** | 1080×1080px（方图，Instagram/Twitter适配）
**格式** | PNG (Canvas API生成)
**背景** | 根据结局类型使用不同渐变（True End/Normal/Bad/Secret）
**内边距** | 40px
**结局类型标签** | 32px，顶部左侧
**结局名称** | 36px Bold `--font-display`，白色
**CG缩略图** | 600×400px，居中，12px圆角
**角色台词** | 24px Italic `--font-dialogue`，白色，60px上间距
**角色名** | 16px Regular，`rgba(255,255,255,0.7)`
**数据统计** | 14px，白色70%透明度，❤️ Bond + ⏱️ 时长 + 选择数
**品牌区** | Logo + Slogan + QR码(80×80px)，底部80px区域
**分享面板** | Modal弹窗(480px宽)，4个分享按钮纵向排列
————————
9.15 退出挽留弹窗组件（C33·v4.1新增）
参数 | 桌面端 | 移动端
------ | -------- | --------
**尺寸** | 480×520px，居中 | 100vw×100vh全屏
**遮罩** | `rgba(0,0,0,0.6)` + `backdrop-filter: blur(8px)` | 同左
**圆角** | 16px | 0px
**CTA按钮** | 渐变深靛蓝(`#4F46E5→#1E1B4B`)，48px高 | 100%-32px宽
**弹出动画** | `scale(0.9→1) + fadeIn`，300ms ease-out | `translateY(100%→0)`
**关闭按钮** | 右上角[✕] 44×44px | 同左
**触发限制** | 每个session最多1次 | 同左
弹窗内容结构：
  [✕]
  ⏳ 图标(40px)
  "Wait! Before you go..."(H3, --text-primary)
  "Try Standard free for 7 days"(18px, --neutral-600)
  权益列表(4项，间距8px)：
  ♾️ 无限对话
  🎤 角色语音互动
  📖 全部剧本解锁
  ⚡ 抢先体验新内容
  "No commitment. Cancel anytime"(14px, --neutral-400)
  [🎁 Start Free Trial](CTA按钮)
  "No thanks, maybe later"(文字按钮, --neutral-400)
————————
9.16 订阅方案卡片组件（4档·v4.1新增）
参数 | Free | Basic | Standard | Premium
------ | ------ | ------- | ---------- | ---------
**宽度** | 等宽(flex:1) | 等宽 | 等宽 | 等宽
**圆角** | 12px | 12px | 12px | 12px
**边框** | `1px solid --neutral-200` | `1px solid --neutral-200` | **`2px solid #FBBF24`** | `1px solid --accent-gold`
**阴影** | E1 | E1 | **`0 8px 24px rgba(79,70,229,0.2)`** | E1
**位移** | 无 | 无 | **translateY(-8px)** | 无
**顶部标签** | 无 | 无 | **"⭐ MOST POPULAR"金色条** | "👑 BEST VALUE"
**方案名** | 20px SemiBold | 20px SemiBold | 20px SemiBold `--primary` | 20px SemiBold `--accent-gold`
**价格** | $0 | $1.99/月 | $4.99/月 | $9.99/月
**价格字号** | 36px Bold | 36px Bold | 36px Bold `--primary` | 36px Bold
**日均成本** | 不显示 | 不显示 | "Less than $0.17/day"(12px green) | "Less than $0.33/day"
**权益列表** | 5项 | 7项 | 10项 | 12项（全部）
**权益图标** | ✅/❌/数值 | ✅/❌/数值 | ✅/❌/数值 | ✅/❌/数值
**CTA** | "Current Plan"(灰) | "Get Basic"(主色) | "Start 7-Day Free Trial"(渐变) | "Get Premium"(金色)
**年付标签** | 无 | "Save $4.78/yr"(绿) | "Save $11.98/yr"(绿) | "Save $23.98/yr"(绿)
响应式布局：
xl断点：4列并排
lg断点：2列(2×2网格)，Standard在右上
md及以下：1列纵向堆叠，Standard排第一
————————
十、响应式适配规范（指法-UI-08）
10.1 断点定义
断点 | 名称 | 宽度范围 | 目标设备 | 栅格列数
------ | ------ | --------- | --------- | ---------
**xs** | Extra Small | < 640px | 手机竖屏 | 4列
**sm** | Small | 640–767px | 手机横屏/大手机 | 8列
**md** | Medium | 768–1023px | 平板 | 12列
**lg** | Large | 1024–1439px | 笔记本 | 12列
**xl** | Extra Large | ≥ 1440px | 桌面显示器 | 12列
  @media (max-width: 639px) { /* xs */ }
  @media (min-width: 640px) and (max-width: 767px) { /* sm */ }
  @media (min-width: 768px) and (max-width: 1023px) { /* md */ }
  @media (min-width: 1024px) and (max-width: 1439px) { /* lg */ }
  @media (min-width: 1440px) { /* xl */ }
10.2 各页面布局策略
W01 首页
断点 | 布局
------ | ------
xs/sm | 单列：Hero(全宽)→精选剧本(1列)→CTA(全宽)
md | 双列：Hero→精选剧本(2列)→CTA
lg/xl | 居中Hero→精选剧本(3列)→CTA
W04 剧本大厅
断点 | 布局
------ | ------
xs | 单列卡片列表
sm | 2列网格
md | 3列网格
lg | 4列网格
xl | 4列网格(最大宽度1440px)
W06 剧本游玩页（核心）
断点 | 布局
------ | ------
**xs** | 单列：场景背景(全屏)→立绘(顶部240px)→对话区(中部)→选择/输入(底部固定)
**sm** | 双列：立绘(左30%)→对话+选择(右70%)
**md** | 三栏：立绘(25%)→对话(50%)→侧栏(25%)
**lg** | 三栏完整：立绘(25%)→对话(55%)→侧栏(20%)
**xl** | 三栏完整+底部工具栏全展开
W07 我的主页
断点 | 布局
------ | ------
xs | 单列纵向：统计(2列)→Streak→每日任务→剧本→好感度→成就
sm | 统计(2列)→Streak→每日任务→其余2列
md | 统计(3列)→左侧(Streak+任务)→右侧(剧本+好感度)
lg | 统计(4列)→三栏布局
xl | 统计(5列)→三栏布局(最大宽度)
W11 订阅/付费页
断点 | 布局
------ | ------
xs/sm | 单列：Hero→方案卡片(1列)→对比表(横滚)→信任条→评价(1列)→FAQ→CTA
md | 方案卡片(2列)→对比表→评价(2列)
lg | 方案卡片(2列2行)→对比表→评价(3列)
xl | 方案卡片(4列并排)→对比表→评价(3列)
————————
十一、双端适配规范（指法-UI-11·总法-37/38）
11.1 M端(移动端) vs P端(PC端) 差异对照表
维度 | M端(<768px) | P端(≥768px)
------ | ------------- | -------------
**导航** | 底部Tab栏(5项) / 汉堡菜单 | 顶部Header导航栏
**侧栏** | 无侧栏，使用底部Sheet | 右侧常驻/可折叠侧栏
**弹窗** | 全屏模态(Bottom Sheet) | 居中Modal
**按钮高度** | 48px(加大触控目标) | 44px
**输入框** | 全宽(100%-32px) | 最大宽度480px
**卡片网格** | 1列(剧本)/1列(任务) | 多列网格
**字体缩放** | H1=32px, Body=14px | H1=48px, Body=14px
**间距缩放** | --space-4=12px | --space-4=16px
**立绘** | 顶部240px固定 | 左侧280px面板
**对话区** | 中部自适应 | 中部55%宽度
**选择项** | 底部固定区域 | 内嵌对话流中
**手势** | 左滑返回/下拉刷新/长按菜单 | 无手势，依赖鼠标交互
**悬浮效果** | 无Hover状态 | Hover状态完整
**右键菜单** | 不支持 | 支持(历史记录/复制)
**键盘快捷键** | 不支持 | ↑↓选择/Enter确认/ESC关闭
11.2 M端独立页面台账
页面 | 路由 | M端特有行为 | M端特有组件
------ | ------ | ------------ | ------------
W01 首页 | `/` | 下拉刷新，精选剧本横滑 | 横滑卡片组
W02 登录 | `/auth` | 全屏表单，键盘弹出适配 | 底部安全区域
W03 引导 | `/onboarding` | 全屏分步，左右滑动切换 | 步骤指示器(底部)
W04 大厅 | `/scripts` | Tab吸顶，下拉刷新 | 底部Tab栏
W05 详情 | `/script/:id` | 封面全宽，底部固定CTA | 底部固定购买栏
W06 游玩 | `/play/:id/:session` | 全屏沉浸，底部输入栏固定 | 底部输入栏+选择Sheet
W07 主页 | `/dashboard` | 下拉刷新，纵向滚动 | 底部Tab栏
W08 画廊 | `/gallery` | 瀑布流单列 | 全屏查看手势
W09 角色 | `/character/:id` | 全宽立绘，横滑表情 | 横滑表情组
W10 设置 | `/settings` | 全屏列表 | 底部安全区域
W11 订阅 | `/subscribe` | 全屏滚动，方案卡片堆叠 | 底部固定CTA
W14 关于 | `/about` | 标准长页面 | —
11.3 P端独立页面台账
页面 | 路由 | P端特有行为 | P端特有组件
------ | ------ | ------------ | ------------
W01 首页 | `/` | 视差滚动，动态演示区 | 宽屏Hero+三列剧本
W04 大厅 | `/scripts` | 侧栏筛选，悬停预览 | 左侧筛选面板
W05 详情 | `/script/:id` | 左图右文双栏 | 横向截图表
W06 游玩 | `/play/:id/:session` | 三栏布局，键盘快捷键 | 侧栏+底部工具栏
W07 主页 | `/dashboard` | 多列网格，统计面板 | 5列统计卡片
W08 画廊 | `/gallery` | 4列网格，悬停放大 | 灯箱查看器
W09 角色 | `/character/:id` | 左立绘+右信息双栏 | 雷达图+时间线
W10 设置 | `/settings` | 左侧导航+右侧内容 | 左侧设置导航
W11 订阅 | `/subscribe` | 4列方案卡片+对比表 | 权益对比大表
————————
十二、深色模式完整适配（指法-UI-09·总法-06）
**核心原则**：深色模式为默认模式（视觉小说沉浸感），所有组件必须定义深色模式色值。
12.1 基础色值映射
元素 | Light Mode | Dark Mode
------ | ----------- | -----------
**页面背景** | `#F9FAFB` | `#111827`
**卡片背景** | `#FFFFFF` | `#1F2937`
**主文字** | `#1F2937` | `#F9FAFB`
**次文字** | `#6B7280` | `#9CA3AF`
**边框** | `#E5E7EB` | `#374151`
**分隔线** | `#E5E7EB` | `#374151`
**悬停背景** | `#F3F4F6` | `#374151`
**输入框背景** | `#FFFFFF` | `#374151`
**表头背景** | `#F9FAFB` | `#1F2937`
12.2 组件深色模式映射
组件 | Light属性 | Dark属性
------ | ---------- | ----------
**主按钮** | `bg: #4F46E5` | `bg: #4338CA`
**次按钮** | `border: #4F46E5, text: #4F46E5` | `border: #6366F1, text: #6366F1`
**输入框** | `border: #E5E7EB, bg: #FFF` | `border: #374151, bg: #374151`
**卡片** | `bg: #FFF, border: #E5E7EB` | `bg: #1F2937, border: #374151`
**Toast** | `bg: 各状态浅色` | `bg: 各状态10%透明度`
**弹窗** | `bg: #FFF` | `bg: #1F2937`
**Header** | `bg: rgba(17,24,39,0.95)` | 同左（Header始终深色）
**骨架屏** | `bg: #E5E7EB, shimmer: #F3F4F6` | `bg: #374151, shimmer: #4B5563`
**Tab(Active)** | `text: #4F46E5, border: #4F46E5` | `text: #6366F1, border: #6366F1`
**好感度进度条** | 各色阶原值 | 各色阶降饱和15%
**Streak签到✅** | `bg: #10B981` | `bg: #059669`
**任务完成✅** | `bg: #ECFDF5, border: #10B981` | `bg: rgba(16,185,129,0.1), border: #059669`
**Standard推荐** | `border: #FBBF24, bg: #EEF2FF` | `border: #F59E0B, bg: rgba(79,70,229,0.08)`
**Paywall CTA** | `gradient: #4F46E5→#1E1B4B` | `gradient: #4338CA→#312E81`
**危险区** | `border: #EF4444` | `border: #DC2626`
**成功状态** | `#10B981` | `#059669`
**错误状态** | `#EF4444` | `#DC2626`
**警告状态** | `#F59E0B` | `#D97706`
**信息状态** | `#3B82F6` | `#2563EB`
12.3 深色模式CSS实现
  /* 深色模式默认变量 */
  :root {
  --bg-page: #111827;
  --bg-card: #1F2937;
  --bg-elevated: #374151;
  --text-primary: #F9FAFB;
  --text-secondary: #9CA3AF;
  --text-tertiary: #6B7280;
  --border: #374151;
  --border-light: #4B5563;
  --primary: #4338CA;
  --primary-light: #6366F1;
  --primary-dark: #312E81;
  --accent-pink: #EC4899;
  --accent-green: #10B981;
  --accent-gold: #F59E0B;
  --success: #059669;
  --info: #2563EB;
  --warning: #D97706;
  --error: #DC2626;
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.4);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.5);
  --shadow-xl: 0 20px 25px rgba(0,0,0,0.6);
  }
————————
十三、标注规范（指法-UI-03）
13.1 标注类型与格式
标注类型 | 格式 | 示例
--------- | ------ | ------
**间距** | `Xpx` / `--space-X` | `16px (--space-4)`
**色值** | `#XXXXXX` / `var(--name)` | `#4F46E5 (var(--primary))`
**字号** | `Xpx / Xrem` | `14px / 0.875rem`
**字重** | 数字值 | `500 (Medium)`
**行高** | 倍数 | `1.7`
**圆角** | `Xpx` / `--radius-X` | `12px (--radius-lg)`
**阴影** | `E1/E2/E3/E4` | `E2 (0 4px 6px rgba(0,0,0,0.07))`
**透明度** | 百分比 | `opacity: 0.6`
**渐变** | CSS gradient | `linear-gradient(135deg, #4F46E5, #1E1B4B)`
13.2 标注示例
  ┌─ 剧本卡片 ──────────────────────────────────────────┐
  │                                                       │
  │  [封面图 200px高, 圆角12px(上)]                       │
  │  └─ 遮罩: linear-gradient(180deg, transparent 40%,    │
  │     rgba(30,27,75,0.9) 100%)                          │
  │                                                       │
  │  ←16px→                                               │
  │  ┌──────────────────────────────────────┐             │
  │  │ 标题: 18px/SemiBold/--text-primary   │             │
  │  │ 间距: 8px (--space-2)                │             │
  │  │ 标签: 12px/Medium/pill/粉色          │             │
  │  │ 间距: 8px                            │             │
  │  │ 评分: ⭐14px/Medium/--accent-gold    │             │
  │  │ 间距: 4px                            │             │
  │  │ 简介: 14px/Regular/--text-secondary  │             │
  │  │ 行高: 1.5, 最多2行, overflow:hidden  │             │
  │  └──────────────────────────────────────┘             │
  │                                                       │
  │  卡片: 圆角12px, 阴影E1, 边框1px --neutral-200        │
  │  Hover: 阴影E2, translateY(-4px), transition 200ms    │
  │                                                       │
  └───────────────────────────────────────────────────────┘
13.3 标注工具规范
场景 | 推荐工具 | 格式要求
------ | --------- | ---------
**Figma标注** | Figma Dev Mode | 使用Auto Layout + Design Tokens插件
**CSS变量** | 代码标注 | 所有色值必须引用CSS变量，不写死色值
**响应式标注** | 多断点截图 | 每个断点单独标注布局变化
**动画标注** | GIF/Lottie + 参数表 | 注明duration/easing/delay
————————
十四、切图资源清单（指法-UI-04）
14.1 切图命名规范
  格式：[类别]_[模块]_[元素]_[状态]_[尺寸].[格式]
  示例：
  icon_script_romance_default_24.svg
  icon_bond_heart_active_20.svg
  bg_play_scene_sakura_1440.webp
  img_cg_sakura_end01_1080.webp
  char_yukino_normal_560.webp
  char_yukino_happy_560.webp
  logo_brand_full_dark.svg
  logo_brand_icon_48.svg
  illust_error_404_320.webp
命名规则：
全小写，下划线分隔
类别前缀：`icon_` / `bg_` / `img_` / `char_` / `logo_` / `illust_`
尺寸标注：像素值（如`_24` / `_48` / `_560` / `_1440`）
状态后缀：`_default` / `_hover` / `_active` / `_disabled` / `_locked`
14.2 格式规范
资源类型 | 格式 | 尺寸 | 说明
--------- | ------ | ------ | ------
**图标** | SVG (inline) | 16/20/24/32/48px | 全部使用内联SVG
**角色立绘** | WebP + PNG降级 | @2x(560px宽) / @3x(840px宽) | 透明背景
**场景背景** | WebP + JPG降级 | @2x(1440px宽) / @3x(1920px宽) | 16:9比例
**CG图片** | WebP + JPG降级 | @2x(1080px宽) / @3x(1620px宽) | 16:9比例
**封面图** | WebP + JPG降级 | @2x(600px宽) / @3x(900px宽) | 3:4比例
**Logo** | SVG | 矢量 | 品牌Logo
**插画** | WebP | @2x / @3x | 空状态/错误页
**头像** | WebP + PNG降级 | @2x(96px) / @3x(144px) | 圆形裁剪
**支付图标** | SVG | 24/32px | Stripe/PayPal/Apple/Google
14.3 资源清单
# | 资源名 | 类型 | 格式 | 尺寸 | 优先级
--- | -------- | ------ | ------ | ------ | --------
1 | `logo_brand_full_dark.svg` | Logo | SVG | 矢量 | P0
2 | `logo_brand_full_light.svg` | Logo | SVG | 矢量 | P0
3 | `logo_brand_icon_48.svg` | Logo | SVG | 48×48px | P0
4 | `char_yukino_normal_560.webp` | 立绘 | WebP | 560×800px | P0
5 | `char_yukino_happy_560.webp` | 立绘 | WebP | 560×800px | P0
6 | `char_yukino_sad_560.webp` | 立绘 | WebP | 560×800px | P0
7 | `char_yukino_angry_560.webp` | 立绘 | WebP | 560×800px | P0
8 | `char_yukino_tense_560.webp` | 立绘 | WebP | 560×800px | P0
9 | `bg_play_scene_sakura_1440.webp` | 背景 | WebP | 1440×810px | P0
10 | `bg_play_scene_night_1440.webp` | 背景 | WebP | 1440×810px | P0
11 | `bg_play_scene_castle_1440.webp` | 背景 | WebP | 1440×810px | P0
12 | `cover_sakura_memory_600.webp` | 封面 | WebP | 600×800px | P0
13 | `cover_dark_knight_600.webp` | 封面 | WebP | 600×800px | P0
14 | `cover_gears_fate_600.webp` | 封面 | WebP | 600×800px | P0
15 | `img_cg_sakura_end01_1080.webp` | CG | WebP | 1080×608px | P0
16 | `img_cg_dark_end01_1080.webp` | CG | WebP | 1080×608px | P0
17 | `illust_error_404_320.webp` | 插画 | WebP | 320×240px | P0
18 | `illust_empty_gallery_320.webp` | 插画 | WebP | 320×240px | P1
19 | `illust_empty_achievement_320.webp` | 插画 | WebP | 320×240px | P1
20 | `icon_streak_fire_24.svg` | 图标 | SVG | 24×24px | P0
21 | `icon_achievement_star_32.svg` | 图标 | SVG | 32×32px | P0
22 | `icon_paywall_lock_48.svg` | 图标 | SVG | 48×48px | P0
23 | `icon_end_true_32.svg` | 图标 | SVG | 32×32px | P1
24 | `icon_end_normal_32.svg` | 图标 | SVG | 32×32px | P1
25 | `icon_end_bad_32.svg` | 图标 | SVG | 32×32px | P1
26 | `icon_end_secret_32.svg` | 图标 | SVG | 32×32px | P1
27 | `pay_stripe_logo.svg` | 支付图标 | SVG | 32×20px | P0
28 | `pay_paypal_logo.svg` | 支付图标 | SVG | 32×20px | P0
29 | `pay_apple_pay.svg` | 支付图标 | SVG | 32×20px | P0
30 | `pay_google_pay.svg` | 支付图标 | SVG | 32×20px | P0
————————
十五、设计交付清单（指法-UI-10）
15.1 交付物Checklist
# | 交付物 | 状态 | 格式 | 说明
--- | -------- | ------ | ------ | ------
1 | 色彩体系定义 | ✅ | CSS变量 + 文档 | 含深色模式映射
2 | 字体体系定义 | ✅ | CSS变量 + 文档 | 含4语言降级策略
3 | 间距体系定义 | ✅ | CSS变量 + 文档 | 4px基础单位12级
4 | 圆角体系定义 | ✅ | CSS变量 + 文档 | 9级圆角
5 | 阴影层级定义 | ✅ | CSS变量 + 文档 | E0-E4 + 深色映射
6 | 图标规范 | ✅ | SVG + 文档 | 5尺寸 + 专用图标清单
7 | 按钮组件规范 | ✅ | 文档 + CSS | 6种按钮×5状态
8 | 输入框组件规范 | ✅ | 文档 + CSS | 4种输入框×5状态
9 | 选择器组件规范 | ✅ | 文档 + CSS | 5种选择器
10 | 导航组件规范 | ✅ | 文档 + CSS | Header/Tab/面包屑
11 | 反馈组件规范 | ✅ | 文档 + CSS | Toast/Modal/Alert/Loading/Skeleton/Progress
12 | 数据展示组件规范 | ✅ | 文档 + CSS | 表格/列表/卡片/统计/雷达图
13 | 布局组件规范 | ✅ | 文档 + CSS | 栅格/容器/分割线
14 | 剧本卡片组件 | ✅ | 文档 + CSS | 含封面+信息+Hover
15 | CG卡片组件 | ✅ | 文档 + CSS | 解锁/锁定/模糊
16 | 角色立绘组件 | ✅ | 文档 + CSS | 280px面板+表情
17 | C29 Paywall弹窗 | ✅ | 文档 + CSS + 线框 | v4.1新增
18 | C30 Streak签到 | ✅ | 文档 + CSS + 线框 | v4.1新增
19 | C31 每日任务 | ✅ | 文档 + CSS + 线框 | v4.1新增
20 | C32 结局分享卡片 | ✅ | 文档 + CSS + 线框 | v4.1新增
21 | C33 退出挽留弹窗 | ✅ | 文档 + CSS + 线框 | v4.1新增
22 | 订阅方案卡片(4档) | ✅ | 文档 + CSS | v4.1新增
23 | 响应式断点定义 | ✅ | CSS + 文档 | 5断点完整策略
24 | 双端适配规范 | ✅ | 文档 | M端/P端差异对照
25 | M端页面台账 | ✅ | 文档 | 12页面M端特有行为
26 | P端页面台账 | ✅ | 文档 | 9页面P端特有行为
27 | 深色模式完整适配 | ✅ | CSS变量 + 文档 | 所有组件深色映射
28 | 标注规范 | ✅ | 文档 | 间距/色值/字号等标注格式
29 | 切图资源清单 | ✅ | 文档 | 命名规范 + 30项资源
30 | 渐变定义 | ✅ | CSS + 文档 | 13种渐变
31 | 动画定义 | ✅ | CSS + 文档 | 按钮/弹窗/签到/任务等动画
32 | 好感度等级色 | ✅ | CSS变量 + 文档 | 5级色彩 + 渐变
33 | 对话文字排版 | ✅ | 文档 | 衬线体+1.9行高+缩进
15.2 V9.2合规检查
制度条目 | 检查项 | 状态
--------- | -------- | ------
**总法-03** | 圆角值仅使用8/12/16px(按钮/卡片/弹窗) | ✅ 合规
**总法-04** | 间距值基于4px倍数 | ✅ 合规（4/8/12/16/20/24/32/40/48/64/80/96）
**总法-05** | 阴影层级E0-E4 | ✅ 合规（5级完整定义）
**总法-06** | 深色模式为默认，所有组件有深色映射 | ✅ 合规
**总法-37** | 双端一致性（M端/P端） | ✅ 合规（差异对照表）
**总法-38** | 双端页面台账 | ✅ 合规（M端12页+P端9页）
**指法-UI-01** | 文档信息完整 | ✅ 合规
**指法-UI-02** | 组件库规范 | ✅ 合规（16类组件）
**指法-UI-03** | 标注规范 | ✅ 合规
**指法-UI-04** | 切图资源清单 | ✅ 合规
**指法-UI-05** | 色彩体系 | ✅ 合规（主色/辅助/中性/好感度/状态/深色映射）
**指法-UI-06** | 字体体系 | ✅ 合规（选型/层级/字重/行高/多语言/对话排版）
**指法-UI-07** | 图标规范 | ✅ 合规（尺寸/风格/颜色/格式/专用清单）
**指法-UI-08** | 响应式适配 | ✅ 合规（5断点+各页面策略）
**指法-UI-09** | 深色模式适配 | ✅ 合规（默认模式+全组件映射）
**指法-UI-10** | 设计交付清单 | ✅ 合规（33项交付物）
**指法-UI-11** | 双端适配规范 | ✅ 合规（差异对照+双端台账）
————————
十六、变更历史
版本 | 日期 | 变更内容 | 变更人
------ | ------ | --------- | --------
v1.0 | 2026-06-03 | 初始版本：基础色彩/字体/组件定义 | Agent07
v3.0 | 2026-06-09 | 技术开发版：设计令牌标准化+组件库初版 | Agent07
v4.0 | 2026-06-24 | 中英双语对齐版：完善色彩体系/字体降级/组件状态定义 | Agent07
**v4.1** | **2026-07-10** | **付费+留存全面升级：新增好感度等级色(5级)；新增13种渐变定义；完善深色模式全组件映射；新增C29-C33共5个组件规范(Paywall弹窗/Streak签到/每日任务/结局分享卡片/退出挽留弹窗)；新增订阅方案卡片(4档)规范；完善响应式5断点各页面策略；新增双端差异对照表+M端/P端独立台账(总法-37/38)；完善对话文字特殊排版规范；完善切图资源清单(30项)；V9.2全条目合规(指法-UI-01~11·总法-03~06·总法-37/38)** | **Agent07 体验架构师**
————————
**文档状态**：✅ 开发就绪
**适用范围**：前端开发 / UI设计师 / 视觉设计师 / 测试
**下一步**：前端开发团队按本文档CSS变量和组件规范实施，优先完成P0组件
**关联PRD**：PRD_IsekaiWanderer_v4.1_完整版_20260710.md
**关联UX文档**：产品3_UX开发交付文档_v4.1_完整版_20260710.md
————————
本文档v4.1由Agent07（体验架构师 pd-m）基于V9.2标准编制 · 2026-07-10
V9.2制度合规：指法-UI-01~11 · 总法-03(圆角) · 总法-04(间距) · 总法-05(阴影) · 总法-06(深色模式) · 总法-37(双端一致) · 总法-38(双端台账)
