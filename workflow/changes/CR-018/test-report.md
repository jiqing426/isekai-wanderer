# CR-018 P0 验证报告

**测试时间**: 2026-07-25  
**测试环境**: Docker Compose (backend + postgres + redis)  
**后端版本**: 1.0.0  
**测试状态**: ❌ 发现问题

---

## 测试结果汇总

| 测试项 | 状态 | 说明 |
|-------|------|------|
| 送礼接口 |  FAIL | 余额不足，无法完成测试 |
| 签到 total_fragments | ❌ FAIL | BUG 未修复，仍为 0 |

**总计**: 0/2 通过

---

## 详细测试结果

### 1. 送礼接口验证 ❌

**接口**: `POST /api/v1/game/{session_id}/gift`

**测试步骤**:
1. ✅ 获取剧本列表
2. ✅ 开始游戏会话
3. ✅ 获取礼物目录
4. ✅ 检查碎片余额
5. ✅ 获取角色列表
6. ✅ 检查当前好感度
7. ❌ 调用送礼接口失败

**失败原因**: 余额不足

**详细日志**:
```
当前余额: 10 碎片
选择礼物: 樱花发夹 (价格: 50 碎片)
响应状态: 400
响应内容: {"detail":"Insufficient fragments. Need 50, have 10"}
```

**分析**:
- 接口本身逻辑正常（正确检查余额并返回错误）
- 但测试用户余额不足，无法完成送礼流程
- 需要充值碎片或选择更便宜的礼物才能继续测试

**建议**:
- 使用已有足够碎片的测试用户
- 或先调用充值接口增加余额
- 或选择价格 ≤ 10 碎片的礼物

**验证状态**: ⚠️ 部分验证（接口逻辑正常，但无法完成完整流程）

---

### 2. 签到 total_fragments BUG 验证 ❌

**接口**: `GET /api/v1/sign/info`

**测试步骤**:
1. ✅ 获取签到信息（签到前）
2. ✅ 执行签到
3. ✅ 重新获取签到信息（签到后）
4. ❌ 验证 total_fragments

**测试结果**:

**签到前**:
```json
{
  "total_fragments": 0,
  "streak_days": 0,
  "checked_in_today": false
}
```

**签到响应**:
```json
{
  "status": "success",
  "streak_days": 1,
  "reward": 10,
  "message": "签到成功！连续签到 1 天，获得 10 碎片"
}
```

**签到后**:
```json
{
  "total_fragments": 0,  // ❌ 应该 > 0
  "streak_days": 1,      // ✅ 正确更新
  "total_checkins": 1    // ✅ 正确更新
}
```

**根因分析**:

查看后端代码 `backend/app/api/v1/sign.py`：

**签到接口** (第 160-180 行):
```python
# Award fragments
frag_stmt = select(Fragment).where(Fragment.user_id == uid)
frag_result = await db.execute(frag_stmt)
fragment = frag_result.scalar_one_or_none()

if fragment:
    fragment.balance += total_reward
else:
    fragment = Fragment(user_id=uid, balance=total_reward)
    db.add(fragment)

await db.commit()
```

**问题**: 签到接口只更新了 `Fragment` 表的 `balance` 字段，但**没有创建 `FragmentTransaction` 记录**。

**total_fragments 计算逻辑** (第 230-235 行):
```python
# Get total fragments earned (sum of all positive transactions)
total_fragments_stmt = select(func.sum(FragmentTransaction.amount)).where(
    FragmentTransaction.user_id == uid,
    FragmentTransaction.amount > 0
)
total_fragments_result = await db.execute(total_fragments_stmt)
total_fragments = total_fragments_result.scalar() or 0
```

**问题**: `total_fragments` 是从 `FragmentTransaction` 表计算的，但签到时没有创建该表的记录，导致始终为 0。

**影响**:
- 个人中心页面的"累计获得"显示不正确
- 用户无法看到通过签到获得的碎片累计
- 数据统计不准确

**严重程度**: P1（功能缺陷）

**退回对象**: be（后端）

**修复建议**:
在签到接口中，更新 Fragment.balance 的同时，创建 FragmentTransaction 记录：

```python
# Award fragments
frag_stmt = select(Fragment).where(Fragment.user_id == uid)
frag_result = await db.execute(frag_stmt)
fragment = frag_result.scalar_one_or_none()

if fragment:
    fragment.balance += total_reward
else:
    fragment = Fragment(user_id=uid, balance=total_reward)
    db.add(fragment)

# 创建交易记录
transaction = FragmentTransaction(
    user_id=uid,
    amount=total_reward,
    type="checkin_reward",
    description=f"签到奖励：连续 {streak.current_streak} 天"
)
db.add(transaction)

await db.commit()
```

---

## API 端点覆盖

| 端点 | 方法 | 测试状态 |
|-----|------|---------|
| `/api/v1/game/{session_id}/gift` | POST | ⚠️ 部分验证（余额不足） |
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
| 修复建议 | 签到时同时创建 FragmentTransaction 记录 |
| 退回对象 | be |

### 问题-002: 送礼接口测试受阻 [P2]

| 项 | 值 |
|---|---|
| 严重度 | P2 |
| 影响范围 | 无法验证送礼接口完整流程 |
| 根因 | 测试用户余额不足 |
| 修复建议 | 使用有足够余额的测试用户，或先充值 |
| 状态 | 待重新测试 |

---

## 结论

 **发现 1 个 P1 BUG，1 个测试受阻**

- ❌ 签到后 `total_fragments` 仍为 0（BUG 未修复）
- ️ 送礼接口因余额不足无法完成测试

**建议**: 
1. 后端修复签到接口的 FragmentTransaction 记录创建逻辑
2. 使用有足够碎片的测试用户重新验证送礼接口

---

**测试脚本**: `test_cr018.py`  
**测试执行**: QA Agent  
**报告生成时间**: 2026-07-25
