# CR-010: 功能增强与优化（第三批）

## 变更概述

基于用户需求，新增6个功能模块，包含成就系统、角色设定、剧本详情、帖子页面、碎片逻辑、个人中心优化。

## 需求分析

### 一、成就设定 [P0] [BE+FE]
**工作量：19小时**

**BE任务（10小时）：**
1. 成就条件检测引擎（5小时）
   - 15个成就触发条件（ACH-001 ~ ACH-015）
   - 自动检测：游戏时长、对话次数、选择次数、CG收集、结局解锁等
   - 实时监听 + 批量检测

2. 成就解锁API（3小时）
   - POST /api/v1/achievements/{id}/unlock - 手动解锁（测试用）
   - GET /api/v1/achievements - 获取成就列表（含解锁状态）
   - 碎片即时发放逻辑

3. 碎片发放集成（2小时）
   - 成就解锁后自动发放碎片（30~300不等）
   - 记录发放日志

**FE任务（9小时）：**
1. 成就卡片组件（4小时）
   - 3种稀有度样式（🟢普通、🔵稀有、🟣史诗）
   - 解锁/未解锁状态
   - 进度条展示

2. 解锁动画（3小时）
   - 全屏动画效果
   - 碎片飞入动画
   - 音效播放

3. 成就列表页面（2小时）
   - 网格布局
   - 筛选功能（全部/已解锁/未解锁）
   - 稀有度排序

---

### 二、角色设定 [P0] [BE+FE]
**工作量：14小时**

**BE任务（8小时）：**
1. 角色数据库入库（2小时）
   - 3个角色：白鳥雪乃、花野美月、凛
   - 性格标签、台词特征、好感度偏好

2. 性格标签系统（3小时）
   - 性格标签定义（温柔、傲娇、活泼等）
   - 标签匹配算法

3. 好感度偏好匹配（2小时）
   - 礼物偏好
   - 对话风格偏好

4. AI对话校验引擎（1小时）
   - 5项校验：角色名一致性、情感极性匹配、敏感词过滤、长度控制、世界观词汇

**FE任务（6小时）：**
1. 角色详情页优化（3小时）
   - 性格标签展示
   - 好感度偏好提示
   - 台词特征展示

2. 角色选择界面（2小时）
   - 角色卡片
   - 性格标签预览

3. AI对话校验UI（1小时）
   - 校验失败提示
   - 重新生成按钮

---

### 三、剧本详情页面 [P0] [BE+FE]
**工作量：12小时**

**BE任务（6小时）：**
1. 剧本详情API补全（3小时）
   - GET /api/v1/scripts/{id} - 返回完整角色数据
   - GET /api/v1/scripts/{id}/routes - 路线探索数据
   - GET /api/v1/scripts/{id}/endings - 结局收集数据

2. 节点数据补全（3小时）
   - 6种节点类型：fixed_scene、ai_dialog、choice_point、converge_node、cg_trigger、ending_node
   - 节点关系图

**FE任务（6小时）：**
1. 页面分层渲染（3小时）
   - 头部信息
   - 章节折叠面板
   - 节点卡片

2. 节点卡片组件（2小时）
   - 6种节点类型样式
   - 解锁/未解锁状态

3. 路线探索可视化（1小时）
   - 节点连接图
   - 进度展示

---

### 四、帖子页面优化 [P1] [FE]
**工作量：8小时**

**FE任务（8小时）：**
1. 卡片式信息流布局（3小时）
   - 帖子卡片
   - 图片预览
   - 点赞/评论数

2. 搜索框+按钮共存（2小时）
   - 搜索输入框
   - 搜索按钮
   - 实时搜索 + 按钮触发

3. 4个Tab分类（2小时）
   - 最新、热门、关注、我的
   - Tab切换逻辑

4. 帖子删除功能（1小时）
   - 删除按钮
   - 确认弹窗
   - 删除后刷新

---

### 五、碎片逻辑优化 [P1] [BE+FE]
**工作量：10小时**

**BE任务（6小时）：**
1. 双类型资产系统（4小时）
   - 赠送碎片（月底清零）
   - 订阅配额碎片（永久）
   - 扣费优先级：赠送碎片 → 订阅配额

2. 签到阶梯奖励（2小时）
   - 连续签到奖励递增
   - 月度签到奖励

**FE任务（4小时）：**
1. 碎片余额展示（2小时）
   - 双类型余额展示
   - 到期提示

2. 签到日历（2小时）
   - 签到日历组件
   - 阶梯奖励展示

---

### 六、个人中心优化 [P1] [BE+FE]
**工作量：8小时**

**BE任务（4小时）：**
1. 签到功能逻辑（2小时）
   - 碎片获取规则
   - 连续签到检测

2. 游戏统计API（2小时）
   - GET /api/v1/users/me/game-stats
   - 游戏时长、对话次数、选择次数

**FE任务（4小时）：**
1. 签到UI（2小时）
   - 签到按钮
   - 已签到日期高亮
   - 禁止重复签到

2. 游戏统计卡片（1小时）
   - 统计数据展示

3. 快速继续模块（1小时）
   - 最近游戏会话
   - 继续游戏按钮

---

## 任务分配

### BE任务（总计：44小时）
**P0（32小时）：**
- 成就系统：10小时
- 角色设定：8小时
- 剧本详情：6小时
- 碎片逻辑：6小时
- 个人中心：4小时

**P1（12小时）：**
- 帖子页面：8小时（FE为主）
- 其他优化：4小时

### FE任务（总计：41小时）
**P0（21小时）：**
- 成就系统：9小时
- 角色设定：6小时
- 剧本详情：6小时

**P1（20小时）：**
- 帖子页面：8小时
- 碎片逻辑：4小时
- 个人中心：4小时
- 其他优化：4小时

---

## 执行顺序

### 第一阶段：P0任务（并行）
1. BE：成就系统 → 角色设定 → 剧本详情
2. FE：成就卡片 → 角色详情 → 剧本详情页面
3. 前后端并行开发，最后联调

### 第二阶段：P1任务（并行）
1. BE：碎片逻辑 → 个人中心
2. FE：帖子页面 → 碎片逻辑 → 个人中心
3. 前后端并行开发，最后联调

---

## API约定（新增）

### 成就系统
```typescript
// 获取成就列表
GET /api/v1/achievements
Response: {
  achievements: Achievement[];
  total: number;
  unlocked_count: number;
}

interface Achievement {
  id: string;
  name: string;
  description: string;
  rarity: 'common' | 'rare' | 'epic';
  icon: string;
  condition: string;
  reward_amount: number;
  is_unlocked: boolean;
  unlocked_at: string | null;
  progress: number;
  target: number;
}

// 手动解锁（测试用）
POST /api/v1/achievements/{id}/unlock
Response: {
  status: 'ok';
  achievement_id: string;
  fragments_earned: number;
}
```

### 角色设定
```typescript
// 获取角色详情
GET /api/v1/characters/{id}
Response: {
  id: string;
  name: string;
  personality_tags: string[];
  dialogue_style: string;
  gift_preferences: string[];
  affection_level: number;
}

interface Character {
  id: string;
  name: string;
  personality_tags: string[];
  dialogue_style: string;
  gift_preferences: string[];
  affection_level: number;
}
```

### 剧本详情
```typescript
// 获取剧本详情（补全）
GET /api/v1/scripts/{id}
Response: {
  id: string;
  title: string;
  characters: Character[];
  routes: Route[];
  endings: Ending[];
  nodes: Node[];
}

interface Node {
  id: string;
  type: 'fixed_scene' | 'ai_dialog' | 'choice_point' | 'converge_node' | 'cg_trigger' | 'ending_node';
  title: string;
  content: string;
  is_unlocked: boolean;
}
```

### 碎片逻辑
```typescript
// 获取碎片余额（双类型）
GET /api/v1/users/me/fragments
Response: {
  gift_fragments: number;
  subscription_fragments: number;
  total: number;
  gift_expires_at: string;
}

interface FragmentBalance {
  gift_fragments: number;
  subscription_fragments: number;
  total: number;
  gift_expires_at: string;
}
```

---

## 风险识别

1. **成就检测引擎**：需要监听多个事件，可能影响性能
2. **AI对话校验**：校验规则复杂，需要充分测试
3. **双类型碎片**：扣费优先级逻辑需要仔细设计
4. **帖子页面重构**：工作量大，需要充分测试

---

## 验收标准

- 15个成就全部可解锁，碎片正确发放
- 3个角色数据完整，AI对话校验通过
- 剧本详情页面正常渲染，节点数据完整
- 帖子页面卡片式布局，搜索功能正常
- 双类型碎片余额正确展示，扣费优先级正确
- 个人中心签到、统计、快速继续功能正常

---

## 时间估算

- P0任务：3天
- P1任务：2天
- 联调测试：1天
- **总计：6天**
