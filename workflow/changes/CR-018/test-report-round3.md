# CR-018 回归测试报告 Round 3 - BE 修复验证

**测试时间**: 2026-07-26 10:32  
**测试环境**: Docker Compose (backend + frontend + postgres + redis)  
**后端版本**: 1.0.0  
**测试状态**: ✅ 通过

---

## 测试结果汇总

| 测试项 | 优先级 | 状态 | 说明 |
|-------|-------|------|------|
| T-010: 签到累计碎片 | P1 | ✅ PASS | total_fragments 从 0 增加到 10 |
| T-009: 完成剧本统计 | P1 | ✅ PASS | COUNT DISTINCT 逻辑正确 |

**总计**: 2/2 通过

---

## 详细测试结果

### T-010: 签到累计碎片为 0（P1 - 关键阻塞项）

**修复内容**: sign.py 第 92-98 行添加 FragmentTransaction 创建逻辑

**验证步骤**:
1. ✅ 注册新用户 cr018retest1785033169@testmail.com
2. ✅ 调用 GET /sign/info（签到前）
3. ✅ 调用 POST /sign/checkin
4. ✅ 调用 GET /sign/info（签到后）
5. ✅ 验证数据库 fragment_transactions 表

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
  "total_fragments": 10,  // ✅ 正确更新
  "streak_days": 1,
  "total_checkins": 1
}
```

**数据库验证**:
```sql
SELECT * FROM fragment_transactions WHERE reason = 'daily_checkin';
-- 返回: amount=10, reason='daily_checkin'
```

**结论**: ✅ **PASS** - FragmentTransaction 记录正确创建，total_fragments 正确累加

---

### T-009: 完成剧本统计修正（P1）

**修复内容**: users.py 第 387 行修改为 COUNT DISTINCT script_id

**验证步骤**:
1. ✅ 检查代码修复
2. ✅ 验证 SQL 逻辑
3. ✅ 调用 GET /users/me/stats
4. ✅ 数据库交叉验证

**代码修复**:
```python
# CR-018 T-009: Completed scripts = COUNT DISTINCT script_id
completed_stmt = select(func.count(func.distinct(GameSession.script_id))).where(
    GameSession.user_id == uid,
    GameSession.status == "completed"
)
```

**数据库验证**:
```sql
-- 用户 4ba5aae5 有 4 个 completed sessions，但只有 2 个不同的 script_id
SELECT count(distinct script_id) FROM game_sessions 
WHERE user_id = '4ba5aae5-...' AND status = 'completed';
-- 返回: 2 ✅

SELECT count(*) FROM game_sessions 
WHERE user_id = '4ba5aae5-...' AND status = 'completed';
-- 返回: 4 (旧逻辑会返回错误值)
```

**API 响应**:
```json
{
  "scripts_completed": 0,  // 新用户，正确返回 0
  "total_play_time_minutes": 0,
  "endings_unlocked": 0,
  "cgs_collected": 0,
  "total_dialogues": 0
}
```

**结论**: ✅ **PASS** - COUNT DISTINCT 逻辑正确，同一剧本多次通关只算 1 次

---

## Browser Interaction E2E Results

| 项 | 值 |
|---|---|
| Browser / Tool | Playwright Chromium (headless) |
| 用户动作 | 注册 → 登录 → 导航到个人中心 → 签到 |
| 前端入口 | http://localhost:8081 |
| 后端地址 | http://localhost:8000 |
| API / Proxy Path | /api/v1/sign/checkin, /api/v1/sign/info |
| Mock API | no |
| 覆盖 AC | T-010 |
| 证据链接 | /tmp/cr018-before-signin.png, /tmp/cr018-after-signin.png |
| 测试结果 | ✅ PASS |

**测试脚本**: `tests/e2e/cr018-sign-regression.spec.ts`  
**执行时间**: 11.0s  
**状态**: 1 passed

---

## 前端字段一致性检查

| 页面 | 字段名 | API 返回字段 | 状态 |
|-----|-------|-------------|------|
| PersonalCenterView.vue | `stats?.scripts_completed` | `scripts_completed` | ✅ 一致 |
| ProfileView.vue | `stats.completed_scripts` | `scripts_completed` | ⚠️ 不一致 |

**发现**: ProfileView.vue 使用 `completed_scripts` 但 API 返回 `scripts_completed`，可能导致显示为 undefined。

**建议**: 统一字段名或在前端做映射。

---

## 发现的问题

### 问题-001: ProfileView.vue 字段名不一致 [P3]

| 项 | 值 |
|---|---|
| 严重度 | P3 |
| 影响范围 | Profile 页面"完成剧本数"可能显示为 0 或 undefined |
| 根因 | 前端使用 `completed_scripts` 但 API 返回 `scripts_completed` |
| 复现步骤 | 访问 /profile 页面，查看统计数据 |
| 修复建议 | 统一字段名或在 ProfileView.vue 做字段映射 |
| 退回对象 | fe（前端） |

---

## API 端点覆盖

| 端点 | 方法 | 测试状态 |
|-----|------|---------|
| `/api/v1/sign/checkin` | POST | ✅ 已测试 |
| `/api/v1/sign/info` | GET | ✅ 已测试 |
| `/api/v1/users/me/stats` | GET | ✅ 已测试 |

---

## 结论

**✅ 2/2 P1 修复验证通过**

- ✅ T-010: 签到累计碎片 BUG 已修复，total_fragments 正确显示
- ✅ T-009: 完成剧本统计 BUG 已修复，COUNT DISTINCT 逻辑正确
- ✅ Browser Interaction E2E 通过

**建议**:
1. 通知 PL 修复验证通过，可继续下一任务
2. 前端修复 ProfileView.vue 字段名不一致问题（P3，非阻塞）

---

**测试脚本**: `tests/e2e/cr018-sign-regression.spec.ts`  
**测试执行**: QA Agent  
**报告生成时间**: 2026-07-26 10:45
