# 个人中心"累计获得"数据测试报告

**测试时间**: 2026-07-25  
**测试环境**: Docker Compose (backend + postgres + redis)  
**后端版本**: 1.0.0  
**测试状态**: ⚠️ 发现问题

---

## 测试结果汇总

| 测试项 | 状态 | 说明 |
|-------|------|------|
| 碎片资产 API | ✅ PASS | `/api/v1/users/me/asset` 正常返回数据 |
| 签到信息 API | ✅ PASS | `/api/v1/sign/info` 正常返回数据 |
| 签到功能 | ✅ PASS | `/api/v1/sign/checkin` 签到成功 |
| 累计获得碎片 | ❌ FAIL | 签到后 `total_fragments` 仍为 0 |
| 个人中心页面 | ⚠️ INFO | 新用户被重定向到 onboarding（正常行为） |

**总计**: 3 PASS / 1 FAIL / 1 INFO

---

## 详细测试结果

### 1. 碎片资产 API ✅

**接口**: `GET /api/v1/users/me/asset`

**响应数据**:
```json
{
  "balance": 0,
  "total_earned": 0,
  "total_spent": 0
}
```

**验证点**:
- ✅ 接口正常返回 200
- ✅ 数据结构正确（balance, total_earned, total_spent）
- ✅ 新用户数据均为 0

---

### 2. 签到信息 API ✅

**接口**: `GET /api/v1/sign/info`

**响应数据**:
```json
{
  "checked_in_today": false,
  "streak_days": 0,
  "total_checkins": 0,
  "total_fragments": 0,
  "this_week": [false, false, false, false, false, false, false],
  "next_milestone": {
    "days": 3,
    "reward_type": "fragment",
    "reward_amount": 10
  }
}
```

**验证点**:
- ✅ 接口正常返回 200
- ✅ 数据结构完整
- ✅ 新用户数据均为 0

---

### 3. 签到功能 ✅

**接口**: `POST /api/v1/sign/checkin`

**响应数据**:
```json
{
  "status": "success",
  "streak_days": 1,
  "reward": 10,
  "base_reward": 10,
  "tiered_reward": 0,
  "message": "签到成功！连续签到 1 天，获得 10 碎片"
}
```

**验证点**:
- ✅ 签到成功返回 200
- ✅ 获得 10 碎片奖励
- ✅ 连续签到天数更新为 1

---

### 4. 累计获得碎片 ❌ **发现 BUG**

**问题描述**: 签到成功后，重新获取签到信息，`total_fragments` 仍为 0

**签到后数据**:
```json
{
  "total_fragments": 0,  // ❌ 应该 > 0
  "streak_days": 1,      // ✅ 正确更新
  "total_checkins": 1    // ✅ 正确更新
}
```

**预期行为**:
- `total_fragments` 应该显示累计获得的碎片总数
- 签到获得 10 碎片后，`total_fragments` 应该至少为 10

**实际行为**:
- `total_fragments` 始终为 0，即使签到成功获得碎片

**根因分析**:
查看后端代码 `backend/app/api/v1/sign.py` 第 165-170 行：
```python
total_fragments_stmt = select(func.sum(FragmentTransaction.amount)).where(
    FragmentTransaction.user_id == user_id
)
total_fragments_result = await db.execute(total_fragments_stmt)
total_fragments = total_fragments_result.scalar() or 0
```

`total_fragments` 是从 `FragmentTransaction` 表计算的，但签到奖励可能没有创建 `FragmentTransaction` 记录，导致累计数据为 0。

**影响**:
- 个人中心页面的"累计获得"显示不正确
- 用户无法看到通过签到获得的碎片累计

**严重程度**: P1（功能缺陷）

**退回对象**: be（后端）

---

### 5. 个人中心页面 ⚠️

**测试结果**: 新用户访问 `/personal-center` 被重定向到 `/onboarding`

**说明**: 这是正常行为，新用户需要完成 onboarding 引导流程才能访问个人中心。

**验证点**:
- ✅ 路由守卫正常工作
- ✅ 新用户行为符合预期

---

## API 端点覆盖

| 端点 | 方法 | 测试状态 |
|-----|------|---------|
| `/api/v1/users/me/asset` | GET | ✅ 已测试 |
| `/api/v1/sign/info` | GET | ✅ 已测试 |
| `/api/v1/sign/checkin` | POST | ✅ 已测试 |

---

## 发现的问题

### BUG-001: 签到后 total_fragments 未更新 [P1]

| 项 | 值 |
|---|---|
| 严重度 | P1 |
| 影响范围 | 个人中心"累计获得"数据显示不正确 |
| 根因 | 签到奖励未创建 FragmentTransaction 记录 |
| 复现步骤 | 1. 注册新用户 → 2. 签到 → 3. 查询 /sign/info → total_fragments 仍为 0 |
| 退回对象 | be |

---

## 结论

⚠️ **发现 1 个 P1 BUG**

- ✅ 碎片资产 API 正常
- ✅ 签到功能正常
- ❌ 签到后 `total_fragments` 未正确累计
- ℹ️ 新用户需要完成 onboarding 才能访问个人中心

**建议**: 需要后端修复签到奖励的 FragmentTransaction 记录创建逻辑。

---

**测试脚本**: `tests/e2e/personal-center.spec.ts`  
**测试执行**: QA Agent  
**报告生成时间**: 2026-07-25
