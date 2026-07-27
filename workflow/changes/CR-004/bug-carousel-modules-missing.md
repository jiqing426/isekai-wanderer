# BUG-MOB-003: 轮播图模块消失问题分析

## 问题描述

老大验收 Demo 时发现：
1. 页面中几个模块消失了 - 原本应该改成轮播图的模块，现在整个模块都不见了
2. 轮播图没有正确显示 - 看不到轮播图效果

## 影响范围

### 受影响的页面和模块

| 页面 | 模块 | 原始类名 | 当前状态 |
|------|------|----------|----------|
| HomeView | 羁绊概览 | `.affection-grid` | ❌ 模块消失 |
| HomeView | 剧本列表 | `.script-grid` | ❌ 模块消失 |
| DiscoverView | 热门剧本 | `.trending-scroll` | ❌ 模块消失 |
| DiscoverView | 推荐剧本 | `.script-grid` | ❌ 模块消失 |
| CharacterListView | 角色网格 | `.character-grid` | ❌ 模块消失 |

## 根因分析

### 1. 数据条件导致模块隐藏

#### HomeView - 羁绊概览模块
```vue
<section class="section" v-if="affectionStore.affections.length > 0">
  <div class="affection-grid mobile-carousel">
    <!-- 轮播图内容 -->
  </div>
</section>
```

**问题**：如果 `affectionStore.affections` 为空数组，整个 section 不会渲染。

**验证**：
```bash
curl -s http://localhost:8000/api/v1/affection -H "Authorization: Bearer $TOKEN"
```

#### HomeView - 剧本列表模块
```vue
<n-spin :show="loadingScripts">
  <n-empty v-if="!loadingScripts && filteredScripts.length === 0" />
  <div class="script-grid mobile-carousel" v-else>
    <!-- 轮播图内容 -->
  </div>
</n-spin>
```

**问题**：如果 `filteredScripts` 为空数组，显示 `<n-empty>` 而不是轮播图。

**验证**：
```bash
curl -s http://localhost:8000/api/v1/scripts
```

#### DiscoverView - 热门剧本模块
```vue
<section class="section" v-if="trending.length > 0">
  <div class="trending-scroll mobile-carousel">
    <!-- 轮播图内容 -->
  </div>
</section>
```

**问题**：如果 `trending` 为空数组，整个 section 不会渲染。

**验证**：
```bash
curl -s http://localhost:8000/api/v1/discover/trending
```

#### DiscoverView - 推荐剧本模块
```vue
<section class="section" v-if="recommendations.length > 0">
  <div class="script-grid mobile-carousel">
    <!-- 轮播图内容 -->
  </div>
</section>
```

**问题**：如果 `recommendations` 为空数组，整个 section 不会渲染。

**验证**：
```bash
curl -s http://localhost:8000/api/v1/discover/recommended
```

#### CharacterListView - 角色网格模块
```vue
<n-spin :show="loading">
  <n-empty v-if="!loading && characters.length === 0" />
  <div class="character-grid mobile-carousel" v-else>
    <!-- 轮播图内容 -->
  </div>
</n-spin>
```

**问题**：如果 `characters` 为空数组，显示 `<n-empty>` 而不是轮播图。

**验证**：
```bash
curl -s http://localhost:8000/api/v1/characters
```

### 2. CSS 样式问题

#### 轮播图容器样式
```css
.affection-grid.mobile-carousel {
  display: flex;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  gap: 12px;
  padding-bottom: 8px;
  scrollbar-width: none;
}
```

**问题**：
- `display: flex` 是正确的
- `overflow-x: auto` 允许横向滚动
- `scroll-snap-type: x mandatory` 实现吸附效果
- `scrollbar-width: none` 隐藏滚动条

**结论**：CSS 样式看起来是正确的。

#### 轮播图项目样式
```css
.affection-grid.mobile-carousel .carousel-item {
  flex: 0 0 85%;
  min-width: 0;
  scroll-snap-align: start;
}
```

**问题**：
- `flex: 0 0 85%` 表示每个项目占 85% 宽度
- `min-width: 0` 防止 flex 项目溢出
- `scroll-snap-align: start` 实现吸附对齐

**结论**：CSS 样式看起来是正确的。

### 3. 数据加载问题

#### 可能的原因

1. **API 返回空数据**
   - 后端没有初始化测试数据
   - 数据库为空

2. **认证问题**
   - 未登录或 token 过期
   - API 返回 401 Unauthorized

3. **网络问题**
   - API 请求失败
   - 跨域问题

4. **前端逻辑问题**
   - 数据解析错误
   - 状态管理问题

## 修复方案

### 方案 A: 验证数据并初始化测试数据

**步骤**：
1. 检查 API 是否返回数据
2. 如果没有数据，初始化测试数据
3. 确保用户已登录

**优点**：
- 解决根本问题
- 确保轮播图有内容可显示

**缺点**：
- 需要后端支持

### 方案 B: 添加空状态提示

**步骤**：
1. 在模块为空时显示友好的空状态提示
2. 提示用户"暂无数据"或"请先登录"
3. 提供操作按钮（如"探索剧本"）

**优点**：
- 用户体验更好
- 明确告知用户原因

**缺点**：
- 不解决根本问题

### 方案 C: 回滚轮播图修改

**步骤**：
1. 移除所有 `mobile-carousel` 类和相关逻辑
2. 恢复原始的网格布局
3. 仅在 `mobile.css` 中添加移动端样式

**优点**：
- 符合 CR-004 范围（只改 CSS）
- 不引入新的业务逻辑
- 风险最低

**缺点**：
- 无法实现轮播图效果（需要新的 CR）

## 修复任务

### TASK-MOB-036: 验证数据并初始化测试数据

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-036 |
| 负责人 | fe + be |
| 优先级 | P0（阻塞验收） |
| 允许写入范围 | `backend/scripts/seed_data.py`, `frontend/src/views/*.vue` |
| 关联验收项 | AC-MOB-002, AC-MOB-005, AC-MOB-006 |
| 验证方式 | 1. API 返回数据<br>2. 轮播图正常显示<br>3. 构建成功 |
| 回滚方案 | 恢复 git 历史版本 |

**任务描述**：
1. 检查所有相关 API 是否返回数据
2. 如果没有数据，运行 `python backend/scripts/seed_data.py` 初始化测试数据
3. 确保用户已登录（使用测试账号 `test@example.com`）
4. 验证轮播图是否正常显示
5. 如果仍然不显示，检查前端数据加载逻辑

### TASK-MOB-037: 添加空状态提示

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-037 |
| 负责人 | fe |
| 优先级 | P1 |
| 允许写入范围 | `frontend/src/views/HomeView.vue`, `frontend/src/views/DiscoverView.vue`, `frontend/src/views/CharacterListView.vue` |
| 关联验收项 | AC-MOB-002, AC-MOB-005, AC-MOB-006 |
| 验证方式 | 1. 空状态提示正常显示<br>2. 用户体验良好<br>3. 构建成功 |
| 回滚方案 | 恢复 git 历史版本 |

**任务描述**：
1. 在模块为空时显示友好的空状态提示
2. 提示用户"暂无数据"或"请先登录"
3. 提供操作按钮（如"探索剧本"）
4. 确保空状态提示在移动端和 PC 端都正常显示

### TASK-MOB-038: 回滚轮播图修改（备选方案）

| 项 | 内容 |
| --- | --- |
| 任务 ID | TASK-MOB-038 |
| 负责人 | fe |
| 优先级 | P0（如果方案 A 和 B 失败） |
| 允许写入范围 | `frontend/src/views/HomeView.vue`, `frontend/src/views/DiscoverView.vue`, `frontend/src/views/CharacterListView.vue`, `frontend/src/styles/mobile.css` |
| 关联验收项 | AC-MOB-002, AC-MOB-005, AC-MOB-006 |
| 验证方式 | 1. 所有模块正常显示<br>2. 无 `mobile-carousel` 类<br>3. 构建成功 |
| 回滚方案 | 恢复 git 历史版本 |

**任务描述**：
1. 移除 HomeView.vue 中的 `mobile-carousel` 相关代码
2. 移除 DiscoverView.vue 中的 `mobile-carousel` 相关代码
3. 移除 CharacterListView.vue 中的 `mobile-carousel` 相关代码
4. 恢复原始的网格布局
5. 确保 `mobile.css` 中的样式不影响原始布局

## 流程规范重申

### 所有修改必须走 PL 流程

1. **需求提出**：老大/用户提出需求
2. **PL 拆解**：PL 创建 CR，拆解任务
3. **分配执行**：PL 分配任务给 FE/BE/AI
4. **验收确认**：PL 验收，老大确认
5. **发布上线**：经过 QA/Security/RELEASE_GATE

### 禁止事项

- ❌ FE 直接修改业务代码
- ❌ 不经过 PL 拆解和分配
- ❌ 不更新 acceptance.md 和 tasks.md
- ❌ 超出 CR 范围的修改

## 下一步

1. **立即执行** TASK-MOB-036（验证数据并初始化测试数据）
2. **如果失败**，执行 TASK-MOB-037（添加空状态提示）
3. **如果仍然失败**，执行 TASK-MOB-038（回滚轮播图修改）
4. **老大验收** 修复后的 Demo
5. **老大确认** 是否需要创建 CR-005 实现轮播图功能

## 沟通记录

| 时间 | from | to | 内容 | 状态 |
|------|------|-----|------|------|
| 2026-07-21T11:30:00Z | main | pl | 老大验收 Demo 发现模块消失 | received |
| 2026-07-21T11:35:00Z | pl | fe | 分配 TASK-MOB-036 验证数据任务 | sent_msg |
| 2026-07-21T11:40:00Z | fe | pl | 确认收到，开始验证数据 | acked_msg |
