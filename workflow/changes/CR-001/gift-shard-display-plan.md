# 修复方案：送礼弹框展示碎片信息

**CR-ID**: CR-001-gift-shard-display  
**制定时间**: 2026-07-27 12:00  
**制定人**: PM  
**状态**: 待执行

---

## 1. 需求分析

**用户需求**：送礼弹框中需要展示当前礼物多少碎片

**分析结果**：
- 礼物碎片价格（cost）已在所有弹框中展示 ✅
- **问题**：GameView 送礼弹框未显示用户当前碎片余额

## 2. 当前状态

| 位置 | 文件 | 礼物价格 | 用户余额 |
|------|------|----------|----------|
| GameView 送礼弹框 | `GameView.vue:128-170` | ✅ `💎 {{ gift.cost }} 碎片` | ❌ 未显示 |
| CharacterDetailView 送礼弹框 | `CharacterDetailView.vue:196-240` | ✅ `💎 {{ gift.cost }}` | ✅ `💎 {{ shardBalance }}` |
| GiftView 送礼页面 | `GiftView.vue:20-26` | ✅ `💎 {{ gift.cost }}` | ✅ `💎 {{ shardBalance }}` |

## 3. 修复方案

### 方案：在 GameView 送礼弹框增加碎片余额显示

**修改文件**：`frontend/src/views/GameView.vue`

**修改内容**：
1. 在送礼弹框顶部增加碎片余额显示
2. 添加 `shardBalance` 响应式变量
3. 在 `openGiftModal` 函数中调用 `gameApi.getShardBalance()` 获取余额

**UI 设计**：
```vue
<!-- 在礼物列表上方增加余额行 -->
<div class="shard-balance-row">
  <span class="balance-label">我的碎片</span>
  <span class="balance-value">💎 {{ shardBalance }}</span>
</div>
```

## 4. 执行计划

| 步骤 | 负责 | 内容 | 预计时间 |
|------|------|------|----------|
| 1 | FE | 修改 GameView.vue，增加余额显示 | 15 min |
| 2 | FE | 验证构建通过 | 5 min |
| 3 | QA | 验证弹框显示正确 | 10 min |

## 5. 验收标准

| AC-ID | 验收项 | 验证方式 |
|-------|--------|----------|
| AC-GIFT-01 | GameView 送礼弹框显示用户碎片余额 | 视觉检查 |
| AC-GIFT-02 | 余额数值与实际一致 | 对比 API 返回 |
| AC-GIFT-03 | 礼物价格仍正常显示 | 视觉检查 |
| AC-GIFT-04 | 构建无报错 | `npm run build` |

## 6. 风险评估

| 风险 | 等级 | 缓解措施 |
|------|------|----------|
| API 调用失败 | 低 | 已有 `/shards/balance` API，稳定 |
| 样式冲突 | 低 | 使用内联样式，不影响其他组件 |

## 7. BE 改动

**无需 BE 改动**。已有 API：
- `GET /api/v1/shards/balance` - 返回用户碎片余额
- `GET /api/v1/characters/gifts/catalog` - 返回礼物列表（含价格）

## 8. 备注

- CharacterDetailView 和 GiftView 已有余额显示，无需修改
- 仅需修改 GameView.vue
