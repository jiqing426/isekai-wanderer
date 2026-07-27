# CR-011: 订阅付费体系 + 帖子页面重构

## 变更概述

基于2个新PRD文档，新增订阅付费逻辑和帖子页面重构功能。

## 需求分析

### 一、付费订阅逻辑 [P0] [BE+FE]

**核心内容：**
- 4档订阅体系：Free/Basic($1.99)/Standard($4.99)/Premium($9.99)
- 动态对话额度系统（Free用户专属）：蜜月期/养成期/常规期
- 8个付费触发场景（T1-T8）
- Paywall触发边界和全局限流规则
- 碎片商城额外对话购买联动

**工作量估算：**
- BE：约20小时
- FE：约15小时
- 总计：35小时

**BE任务：**
1. 订阅权限校验引擎（6小时）
   - 订阅等级判断
   - 权限校验中间件
   - 订阅状态缓存

2. 动态额度计算（5小时）
   - 蜜月期/养成期/常规期额度规则
   - 额度消耗计数
   - 额度重置逻辑

3. 付费触发计数器（4小时）
   - 8个触发场景计数（T1-T8）
   - 触发阈值判断
   - 计数器持久化

4. 弹窗限流规则（3小时）
   - 全局限流策略
   - 弹窗频率控制
   - 用户行为追踪

5. 碎片商城联动（2小时）
   - 额外对话购买接口
   - 购买后额度更新

**FE任务：**
1. Paywall组件（6小时）
   - 全屏弹窗组件
   - 横幅组件
   - Toast提示组件
   - 触发逻辑封装

2. 订阅套餐展示（4小时）
   - 4档套餐卡片
   - 价格展示
   - 权益对比

3. 额度显示（3小时）
   - 剩余额度展示
   - 额度进度条
   - 刷新按钮

4. 购买流程（2小时）
   - 额外对话购买弹窗
   - 支付确认
   - 购买成功提示

### 二、帖子页面优化重构 [P1] [BE+FE]

**核心内容：**
- 卡片式信息流布局（PC双栏/移动端单列）
- 搜索框+搜索按钮共存（支持回车+点击双触发）
- 4个Tab分类（推荐/最新/热门/我的帖子）
- 帖子删除功能（仅保留删除，无编辑/举报）
- 游客权限限制（可浏览，点赞/发帖需登录）

**工作量估算：**
- BE：约10小时
- FE：约12小时
- 总计：22小时

**BE任务：**
1. 帖子列表API（3小时）
   - 分页查询
   - 排序规则
   - 数据聚合

2. 搜索API（3小时）
   - 关键词搜索
   - 搜索结果排序
   - 搜索建议

3. 点赞API（2小时）
   - 点赞/取消点赞
   - 点赞数统计
   - 用户点赞记录

4. 删除API（2小时）
   - 权限校验（仅作者可删除）
   - 软删除逻辑
   - 关联数据处理

**FE任务：**
1. 卡片组件（4小时）
   - 帖子卡片布局
   - 图片展示
   - 点赞/评论数

2. 搜索组件（3小时）
   - 搜索输入框
   - 搜索按钮
   - 回车触发
   - 搜索历史

3. Tab切换（2小时）
   - 4个Tab标签
   - 切换动画
   - 数据刷新

4. 无限滚动（2小时）
   - 滚动监听
   - 分页加载
   - 加载状态

5. 删除交互（1小时）
   - 删除按钮
   - 确认弹窗
   - 删除后刷新

## API约定

### 订阅相关API

```typescript
// 获取订阅信息
GET /api/v1/users/me/subscription
Response: {
  tier: 'free' | 'basic' | 'standard' | 'premium';
  quota: {
    total: number;
    used: number;
    remaining: number;
    period: 'honeymoon' | 'nurture' | 'regular';
  };
  expires_at: string;
  auto_renew: boolean;
}

// 获取订阅套餐列表
GET /api/v1/subscription/plans
Response: {
  plans: Array<{
    tier: string;
    price: number;
    currency: string;
    features: string[];
    quota: number;
  }>;
}

// 订阅套餐
POST /api/v1/subscription/subscribe
Request: {
  tier: string;
  payment_method: string;
}
Response: {
  status: 'success' | 'pending';
  subscription_id: string;
}

// 购买额外对话
POST /api/v1/fragment/exchange
Request: {
  goods_id: string;
  quantity: number;
}
Response: {
  status: 'success';
  new_quota: number;
  fragments_spent: number;
}

// 检查付费触发
GET /api/v1/paywall/check
Query: {
  scene: string; // T1-T8
}
Response: {
  should_show: boolean;
  type: 'fullscreen' | 'banner' | 'toast';
  message: string;
}
```

### 帖子相关API

```typescript
// 获取帖子列表
GET /api/v1/community/posts
Query: {
  tab: 'recommend' | 'latest' | 'hot' | 'mine';
  page: number;
  page_size: number;
  search?: string;
}
Response: {
  posts: Array<{
    id: string;
    title: string;
    content: string;
    images: string[];
    author: {
      id: string;
      name: string;
      avatar: string;
    };
    stats: {
      likes: number;
      comments: number;
      views: number;
    };
    is_liked: boolean;
    created_at: string;
  }>;
  total: number;
  has_more: boolean;
}

// 点赞帖子
POST /api/v1/community/posts/{id}/like
Response: {
  status: 'success';
  likes_count: number;
}

// 取消点赞
DELETE /api/v1/community/posts/{id}/like
Response: {
  status: 'success';
  likes_count: number;
}

// 删除帖子
DELETE /api/v1/community/posts/{id}
Response: {
  status: 'success';
}

// 搜索帖子
GET /api/v1/community/posts/search
Query: {
  keyword: string;
  page: number;
  page_size: number;
}
Response: {
  posts: Array<Post>;
  total: number;
  suggestions: string[];
}
```

## 任务分配

### BE任务（总计：30小时）

**P0（20小时）：**
1. 订阅权限校验引擎（6小时）
2. 动态额度计算（5小时）
3. 付费触发计数器（4小时）
4. 弹窗限流规则（3小时）
5. 碎片商城联动（2小时）

**P1（10小时）：**
1. 帖子列表API（3小时）
2. 搜索API（3小时）
3. 点赞API（2小时）
4. 删除API（2小时）

### FE任务（总计：27小时）

**P0（15小时）：**
1. Paywall组件（6小时）
2. 订阅套餐展示（4小时）
3. 额度显示（3小时）
4. 购买流程（2小时）

**P1（12小时）：**
1. 卡片组件（4小时）
2. 搜索组件（3小时）
3. Tab切换（2小时）
4. 无限滚动（2小时）
5. 删除交互（1小时）

## 执行顺序

### 第一阶段：P0任务（并行）
1. BE：订阅权限校验 → 动态额度 → 付费触发
2. FE：Paywall组件 → 订阅套餐展示 → 额度显示
3. 前后端并行开发，最后联调

### 第二阶段：P1任务（并行）
1. BE：帖子列表API → 搜索API → 点赞/删除API
2. FE：卡片组件 → 搜索组件 → Tab切换 → 无限滚动
3. 前后端并行开发，最后联调

## 风险识别

1. **订阅权限校验**：需要与现有认证系统集成，可能影响性能
2. **动态额度计算**：规则复杂，需要充分测试
3. **付费触发计数器**：高并发场景下需要保证准确性
4. **帖子搜索**：大数据量下搜索性能需要优化

## 验收标准

- 4档订阅体系正常工作
- 动态额度计算准确
- 8个付费触发场景正确触发Paywall
- 帖子列表、搜索、点赞、删除功能正常
- 游客权限限制生效

## 时间估算

- P0任务：3天
- P1任务：2天
- 联调测试：1天
- **总计：6天**
