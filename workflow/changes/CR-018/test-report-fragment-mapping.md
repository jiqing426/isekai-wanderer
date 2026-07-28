# CR-018 碎片交易明细中文映射验收报告

**验收时间**: 2026-07-27 12:00  
**验收环境**: Docker Compose (backend)  
**后端版本**: 1.0.0  
**Mock API**: no  

---

## 验收结果汇总

| AC-ID | 验收项 | 状态 | 详情 |
|-------|--------|------|------|
| AC-MAP-01 | `gift:gift_001` → 显示"送礼支出" | ❌ FAIL | 实际显示 `gift:gift_001` |
| AC-MAP-02 | `dialogue_quota_purchase:1` → 显示"碎片兑换对话" | ✅ PASS | 前缀匹配成功 |
| AC-MAP-03 | `recharge:mock` → 显示"充值" | ❌ FAIL | 映射表中无 `recharge` |
| AC-MAP-04 | `purchase:fragments_100` → 显示"碎片购买" | ❌ FAIL | 映射表中无 `purchase` |
| AC-MAP-05 | `achievement_unlock:ACH-001` → 显示"成就解锁奖励" | ❌ FAIL | 映射表中无 `achievement_unlock` |

**总计**: 1/5 通过 ❌

---

## 详细测试结果

### 测试方法
调用 `GET /api/v1/shards/transactions` API，检查返回的 `reason_label` 字段。

### 测试结果

| 交易类型 | 期望标签 | 实际标签 | 状态 |
|---------|---------|---------|------|
| `gift:gift_001` | 送礼支出 | gift:gift_001 | ❌ |
| `dialogue_quota_purchase:1` | 碎片兑换对话 | 碎片兑换对话 | ✅ |
| `recharge:mock` | 充值 | recharge:mock | ❌ |
| `purchase:fragments_100` | 碎片购买 | purchase:fragments_100 | ❌ |
| `achievement_unlock:ACH-001` | 成就解锁奖励 | achievement_unlock:ACH-001 | ❌ |

---

## 问题分析

### 当前映射表 (`backend/app/api/v1/shards.py:25-35`)

```python
REASON_LABELS = {
    "daily_checkin": "每日签到",
    "streak_milestone": "连续签到奖励",
    "gift_send": "送礼支出",
    "gift_receive": "收到礼物",
    "dialogue_quota_purchase": "碎片兑换对话",
    "shop_purchase": "商城购买",
    "refund": "退款",
    "admin_adjustment": "管理员调整",
    "system_reward": "系统奖励",
    "achievement_reward": "成就奖励",
}
```

### 问题 1: 映射表 key 与实际 reason 格式不匹配

- 映射表有 `gift_send`，但实际 reason 是 `gift:gift_001`
- 映射表有 `achievement_reward`，但实际 reason 是 `achievement_unlock:ACH-001`

### 问题 2: 映射表缺少交易类型

- 缺少 `recharge`（充值）
- 缺少 `purchase`（碎片购买）
- 缺少 `achievement_unlock`（成就解锁奖励）

### 问题 3: 前缀匹配逻辑无法处理 `:` 分隔符

当前 `_get_reason_label` 函数使用前缀匹配，但无法正确处理 `gift:gift_001` 这种带参数的格式。

---

## 修复建议

### 方案 1: 扩展映射表 + 改进匹配逻辑

```python
REASON_LABELS = {
    "daily_checkin": "每日签到",
    "streak_milestone": "连续签到奖励",
    "gift": "送礼支出",  # 改为前缀
    "gift_send": "送礼支出",
    "gift_receive": "收到礼物",
    "dialogue_quota_purchase": "碎片兑换对话",
    "shop_purchase": "商城购买",
    "purchase": "碎片购买",  # 新增
    "refund": "退款",
    "admin_adjustment": "管理员调整",
    "system_reward": "系统奖励",
    "achievement_reward": "成就奖励",
    "achievement_unlock": "成就解锁奖励",  # 新增
    "recharge": "充值",  # 新增
}

def _get_reason_label(reason: str) -> str:
    """将交易类型映射为中文标签"""
    # 精确匹配
    if reason in REASON_LABELS:
        return REASON_LABELS[reason]
    
    # 提取基础类型（去除 : 后的参数）
    base_type = reason.split(":")[0]
    if base_type in REASON_LABELS:
        return REASON_LABELS[base_type]
    
    # 前缀匹配
    for key, label in REASON_LABELS.items():
        if reason.startswith(key):
            return label
    
    # 默认返回原始值
    return reason
```

---

## 结论

**整体判定**: ❌ **验收失败**

**退回对象**: BE

**原因**: 
1. 映射表缺少 3 个交易类型（recharge, purchase, achievement_unlock）
2. 映射表 key 与实际 reason 格式不匹配（gift_send vs gift:xxx）
3. 前缀匹配逻辑无法处理带参数的格式

**下一步**: 
1. BE 修复映射表和匹配逻辑
2. 修复后重新验收
