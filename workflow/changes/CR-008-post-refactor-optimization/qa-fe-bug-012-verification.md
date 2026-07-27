# QA FE-BUG-012 签到累计获得修复验证报告

**验证时间**: 2026-07-24  
**验证方式**: 代码审查 + API 测试  
**Mock API**: no

---

## 验证结果

| # | 验证项 | 状态 | 证据 |
|---|--------|------|------|
| 1 | 签到卡片显示三项数据 | ✅ PASS | streak_days, total_checkins, total_fragments 均显示 |
| 2 | total_fragments 字段从后端正确获取 | ❌ FAIL | 后端 API 不返回 total_fragments 字段 |
| 3 | 构建通过 | ✅ PASS | npm run build 成功（有无关 TS 错误） |
| 4 | Mock API=no | ✅ PASS | 无 mock 代码 |

---

## 详细发现

### 前端实现 ✅

**文件**: `frontend/src/types/personal-center.ts`
```typescript
export interface SignInfo {
  checked_in_today: boolean;
  streak_days: number;
  total_checkins: number;
  total_fragments: number;  // ✅ 已添加
  this_week: boolean[];
  next_milestone: { ... } | null;
}
```

**文件**: `frontend/src/views/PersonalCenterView.vue`
```vue
<div class="checkin-info">
  <div class="streak-days">
    <span class="streak-value">{{ signInfo?.streak_days || 0 }}</span>
    <span class="streak-label">连续签到</span>
  </div>
  <div class="total-checkins">
    <span class="total-value">{{ signInfo?.total_checkins || 0 }}</span>
    <span class="total-label">累计签到</span>
  </div>
  <div class="total-fragments">
    <span class="total-value">{{ signInfo?.total_fragments || 0 }}</span>
    <span class="total-label">累计获得</span>
  </div>
</div>
```

### 后端 API ❌

**文件**: `backend/app/api/v1/sign.py` (第 20-78 行)

```python
@router.get("/info")
async def get_sign_info(...):
    # ... 计算 streak_days, total_checkins ...
    
    return {
        "checked_in_today": checked_in_today,
        "streak_days": streak_days,
        "total_checkins": total_checkins,
        "this_week": this_week,
        "next_milestone": next_milestone,
        # ❌ 缺少 total_fragments 字段！
    }
```

**问题**: 后端 API 不返回 `total_fragments`，前端显示的值始终为 0（因为 `signInfo?.total_fragments || 0`）。

---

## API 测试

```bash
$ curl -s http://localhost:8000/api/v1/sign/info \
  -H "Authorization: Bearer $TOKEN" | jq .

{
  "checked_in_today": false,
  "streak_days": 0,
  "total_checkins": 0,
  "this_week": [false, false, false, false, false, false, false],
  "next_milestone": {
    "days": 7,
    "reward_type": "fragment",
    "reward_amount": 100
  }
}
```

**结果**: 响应中无 `total_fragments` 字段。

---

## 结论

**验证失败** ❌

前端实现正确，但后端 API 缺少 `total_fragments` 字段。需要 BE 修复：

1. 在 `backend/app/api/v1/sign.py` 的 `get_sign_info` 函数中计算累计获得碎片数
2. 在返回的 JSON 中添加 `total_fragments` 字段

**退回**: BE Agent 需补充后端实现。

---

**验证状态**: 失败 - 后端 API 缺少字段
