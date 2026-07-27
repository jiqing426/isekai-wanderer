# CR-016 技术方案：订阅付费体系 + 动态对话额度

> 版本：v1.0 | 日期：2026-07-25 | 状态：待 Review

---

## 一、架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Vue 3)                         │
├─────────────────────────────────────────────────────────────────┤
│  SubscriptionStore    │  PaywallManager    │  QuotaDisplay      │
│  - tier/permissions   │  - modal/banner    │  - remaining       │
│  - quota status       │  - toast control   │  - lifecycle stage │
│  - 仅 UI 展示         │  - 接收后端指令     │  - 不自行判断      │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend API Layer                           │
├─────────────────────────────────────────────────────────────────┤
│  /api/subscription/*   │  /api/dialogue/*   │  /api/paywall/*   │
│  - status              │  - quota/status    │  - check-trigger  │
│  - create/cancel       │  - consume         │  - record-event   │
│  - fragment-purchase   │  - add-fragment    │  - daily-count    │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Service Layer                              │
├─────────────────────────────────────────────────────────────────┤
│  SubscriptionService  │  QuotaService       │  PaywallService   │
│  - get_user_tier      │  - lifecycle_calc   │  - check_trigger  │
│  - check_permission   │  - consume_quota    │  - rate_limit     │
│  - on_expired         │  - reset_daily      │  - record_modal   │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Layer (PostgreSQL)                     │
├─────────────────────────────────────────────────────────────────┤
│  subscription_plans  │  dialogue_quotas   │  paywall_events     │
│  users (扩展字段)     │                    │                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、数据模型设计（修正版）

### 2.1 现有代码问题 & 修正

| 问题 | PRD 要求 | BE 实现 | 修正方案 |
|------|----------|---------|----------|
| Free 存档上限 | 1 个 | 0 个 | 改为 1 |
| Basic 对话上限 | 30 次/天 | 无限 | 改为 30 |
| Basic 存档上限 | 5 个 | 10 个 | 改为 5 |
| Basic 碎片折扣 | 无 | 5% | 改为 0 |
| Standard 碎片折扣 | 无 | 10% | 改为 0 |
| Premium 碎片折扣 | 7 折 | 8 折 | 改为 0.7 |
| 回归用户追踪 | 需记录回归激活时间 | 无字段 | 新增 `returnee_activated_at` |

### 2.2 修正后的 TIER_PERMISSIONS

```python
TIER_PERMISSIONS = {
    "free": TierPermissions(
        archive_limit=1,           # PRD: 1个存档位
        script_access="trial_only",
        voice_enabled=False,
        rewind_c15=False,
        ugc_access=False,
        fragment_discount=0.0,     # PRD: 无折扣
        hidden_options=False,
        dialogue_limit=0,          # 使用动态梯度
    ),
    "basic": TierPermissions(
        archive_limit=5,           # PRD: 5个存档位
        script_access="all_normal",
        voice_enabled=False,
        rewind_c15=False,
        ugc_access=False,
        fragment_discount=0.0,     # PRD: 无折扣
        hidden_options=False,
        dialogue_limit=30,         # PRD: 30次/天
    ),
    "standard": TierPermissions(
        archive_limit=-1,          # PRD: 无限
        script_access="all_normal",
        voice_enabled=True,
        rewind_c15=True,
        ugc_access=False,
        fragment_discount=0.0,     # PRD: 无折扣
        hidden_options=True,
        dialogue_limit=-1,         # PRD: 无限
    ),
    "premium": TierPermissions(
        archive_limit=-1,
        script_access="all_including_exclusive",
        voice_enabled=True,
        rewind_c15=True,
        ugc_access=True,
        fragment_discount=0.7,     # PRD: 7折 = 0.7
        hidden_options=True,
        dialogue_limit=-1,
    ),
}
```

### 2.3 User 模型扩展

```sql
-- 新增字段（ALTER TABLE users ADD COLUMN ...）
ALTER TABLE users ADD COLUMN returnee_activated_at TIMESTAMPTZ;
-- 用于追踪回归用户 3 天窗口期结束时间

-- 回归用户判定逻辑：
-- 1. last_login 距今 >= 7天 → 触发回归
-- 2. 设置 returnee_activated_at = now()
-- 3. 3 天内（returnee_activated_at + 3天 > now()）→ 保持 returnee 阶段
-- 4. 3 天后 → 按注册时间计算 normal 阶段
```

### 2.4 完整表结构

```sql
-- 1. 订阅计划表
CREATE TABLE subscription_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    tier VARCHAR(20) NOT NULL,           -- free/basic/standard/premium
    status VARCHAR(20) NOT NULL,         -- active/cancelled/expired
    started_at TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_subscription_user ON subscription_plans(user_id);
CREATE INDEX idx_subscription_status ON subscription_plans(status);

-- 2. 对话额度表（每日一条记录）
CREATE TABLE dialogue_quotas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    date DATE NOT NULL,
    base_quota INTEGER NOT NULL,         -- 当日基础额度（10/5/3/-1）
    consumed INTEGER NOT NULL DEFAULT 0,
    fragment_extra INTEGER NOT NULL DEFAULT 0,  -- 碎片购买额外额度
    fragment_consumed INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id, date)
);
CREATE INDEX idx_quota_user_date ON dialogue_quotas(user_id, date);

-- 3. 付费引导事件表
CREATE TABLE paywall_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    scene VARCHAR(30) NOT NULL,          -- T1_quota/T2_archive/...
    display_type VARCHAR(10) NOT NULL,   -- modal/banner/toast
    triggered_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_paywall_user ON paywall_events(user_id);
CREATE INDEX idx_paywall_date ON paywall_events(triggered_at);
```

---

## 三、核心业务逻辑

### 3.1 动态梯度额度计算流程

```
┌─────────────────────────────────────────────────────────────┐
│                 get_daily_base_quota(user_id)                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. 检查订阅状态                                              │
│     if tier != "free" → return tier.dialogue_limit           │
│     (basic=30, standard=-1, premium=-1)                      │
│                                                              │
│  2. 计算注册天数                                               │
│     days_since_reg = (now - user.created_at).days            │
│                                                              │
│  3. 判断生命周期阶段                                           │
│     ┌────────────────────────────────────────────────────┐  │
│     │ if days_since_reg <= 3:                            │  │
│     │     return 10  # 蜜月期                            │  │
│     │                                                    │  │
│     │ if user.returnee_activated_at:                     │  │
│     │     if now < returnee_activated_at + 3天:          │  │
│     │         return 5  # 回归窗口期内                   │  │
│     │                                                    │  │
│     │ if days_since_reg <= 7:                            │  │
│     │     return 5  # 养成期                             │  │
│     │                                                    │  │
│     │ return 3  # 常规期                                 │  │
│     └────────────────────────────────────────────────────┘  │
│                                                              │
│  4. 回归用户触发检测（在 login 时执行）                        │
│     if user.last_login 距今 >= 7天:                          │
│         user.returnee_activated_at = now()                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 额度消耗流程

```
┌─────────────────────────────────────────────────────────────┐
│                    consume_quota(user_id)                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. 订阅用户直接返回 True（不消耗额度）                        │
│                                                              │
│  2. 获取/创建今日额度记录                                      │
│     quota = get_or_create_quota(user_id, today)              │
│                                                              │
│  3. 消耗顺序：基础额度优先 → 碎片额度                          │
│     ┌────────────────────────────────────────────────────┐  │
│     │ if quota.consumed < quota.base_quota:              │  │
│     │     quota.consumed += 1                            │  │
│     │     return True                                    │  │
│     │                                                    │  │
│     │ if quota.fragment_consumed < quota.fragment_extra: │  │
│     │     quota.fragment_consumed += 1                   │  │
│     │     return True                                    │  │
│     │                                                    │  │
│     │ return False  # 额度耗尽                           │  │
│     └────────────────────────────────────────────────────┘  │
│                                                              │
│  4. 额度重置（UTC 00:00）                                    │
│     - 每天创建新记录，base_quota 重新计算                     │
│     - fragment_extra 从 0 开始（碎片额度不结转）              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 对话接口改造（关键）

```python
# 现有对话 API 改造伪代码
async def chat_with_npc(user_id, script_id, message):
    """
    用户发送消息 → NPC 回复的完整流程
    """
    
    # ========== 免扣场景判定 ==========
    # fixed_scene 开场白、converge_node 收敛节点 → 不扣额度
    if is_free_scene(script_id, message):
        response = await generate_npc_response(script_id, message)
        return {"response": response, "quota_deducted": False}
    
    # ========== 额度检查（前置） ==========
    quota_status = await quota_service.get_user_quota_status(user_id)
    
    if quota_status["remaining"] == 0:
        # 额度耗尽 → 触发 Paywall 检查
        paywall = await paywall_service.check_trigger(user_id, "T1_quota")
        return {
            "error": "quota_exhausted",
            "paywall": paywall,  # 前端根据此展示引导
            "quota_status": quota_status
        }
    
    # ========== 生成 AI 回复 ==========
    response = await generate_npc_response(script_id, message)
    
    # ========== 消耗额度（后置） ==========
    # 只有完整的「用户输入 + AI回复」才消耗 1 次
    success = await quota_service.consume_quota(user_id)
    
    return {
        "response": response,
        "quota_deducted": True,
        "quota_status": await quota_service.get_user_quota_status(user_id)
    }
```

### 3.4 Paywall 限流逻辑

```
┌─────────────────────────────────────────────────────────────┐
│                   check_trigger(user_id, scene)               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. 订阅用户 → 永久关闭所有引导                               │
│     if tier != "free": return {should_show: false}           │
│                                                              │
│  2. 获取用户注册天数、今日弹窗次数                             │
│     days = (now - created_at).days                           │
│     modal_count = get_daily_modal_count(user_id, today)      │
│                                                              │
│  3. 蜜月期保护（注册 < 3 天）                                 │
│     if days < 3:                                             │
│         return {should_show: true, display_type: "banner"}   │
│         # 禁止全屏弹窗                                       │
│                                                              │
│  4. T1 额度耗尽特殊规则                                       │
│     if scene == "T1_quota":                                  │
│         if days <= 3:  # 蜜月期 1-3 天                       │
│             return {display_type: "banner"}                  │
│         else:  # 养成期/常规期                                │
│             if modal_count >= 2:                             │
│                 return {display_type: "banner"}  # 降级      │
│             else:                                            │
│                 return {display_type: "modal"}  # C29弹窗    │
│                                                              │
│  5. 其他场景（T2-T8）                                         │
│     if modal_count >= 2:                                     │
│         return {display_type: "banner"}  # 超限降级          │
│     else:                                                    │
│         return {display_type: scene_default_type}            │
│                                                              │
│  6. 例外：用户主动点击【订阅套餐】入口                         │
│     if user_initiated: return {rate_limited: false}          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 四、API 接口定义

### 4.1 订阅相关

```yaml
# 获取当前订阅状态
GET /api/subscription/status
Response:
  tier: "free" | "basic" | "standard" | "premium"
  status: "active" | "cancelled" | "expired" | null
  expires_at: "2026-08-25T00:00:00Z" | null
  permissions: TierPermissions

# 创建订阅（对接支付回调后调用）
POST /api/subscription/create
Body: { tier: "basic" | "standard" | "premium", payment_id: "xxx" }
Response: { subscription_id: "uuid", expires_at: "..." }

# 取消订阅
POST /api/subscription/cancel
Response: { cancelled_at: "...", expires_at: "..." }

# 碎片购买额外对话
POST /api/subscription/fragment-purchase
Body: { amount: 5 }  # 购买 5 次额外对话
Response: { fragment_added: 5, new_quota_status: {...} }
```

### 4.2 对话额度相关

```yaml
# 获取当前额度状态
GET /api/dialogue/quota/status
Response:
  base_quota: 10
  consumed: 3
  fragment_extra: 0
  fragment_consumed: 0
  remaining: 7
  lifecycle_stage: "honeymoon"
  is_subscriber: false

# 获取生命周期信息
GET /api/dialogue/lifecycle
Response:
  stage: "honeymoon" | "growth" | "regular" | "returnee"
  days_since_registration: 2
  days_since_last_login: null
  daily_base_quota: 10
```

### 4.3 Paywall 相关

```yaml
# 检查是否触发付费引导
POST /api/paywall/check-trigger
Body: { scene: "T1_quota" | "T2_archive" | ... }
Response:
  should_show: true
  display_type: "modal" | "banner" | "toast"
  payload:
    scene: "T1_quota"
    show_upgrade: true
    show_fragment: true

# 记录弹窗展示（前端弹窗关闭时调用）
POST /api/paywall/record-event
Body: { scene: "T1_quota", display_type: "modal" }

# 获取今日弹窗计数
GET /api/paywall/daily-count
Response: { modal_count: 1, limit: 2 }
```

---

## 五、前端组件设计

### 5.1 组件层级

```
PaywallManager.vue (统一入口)
├── QuotaExhaustedModal.vue (C29 全屏弹窗)
│   └── TierComparison.vue (4档对比表)
├── PaywallBanner.vue (横幅提示)
└── PaywallToast.vue (轻提示，队列机制)
```

### 5.2 数据流

```
1. 对话接口返回 quota_exhausted 或 paywall 字段
   ↓
2. SubscriptionStore 更新 paywallTrigger
   ↓
3. PaywallManager 监听 paywallTrigger
   ↓
4. 根据 display_type 渲染对应组件
   ↓
5. 用户操作（关闭/点击升级/点击碎片购买）
   ↓
6. 调用 /api/paywall/record-event 记录
```

### 5.3 关键约束

- **前端不做权限判断**：只负责 UI 渲染，触发条件全部后端计算
- **Toast 队列**：多条提示排队，前一条消失后才显示下一条（3.5s）
- **弹窗关闭按钮**：必须明显，不允许强制等待

---

## 六、安全 & 限流策略

### 6.1 防绕过机制

| 风险点 | 防护措施 |
|--------|----------|
| 前端篡改额度 | 所有额度校验后端执行，前端仅展示 |
| 抓包跳过 Paywall | 对话接口返回 `quota_deducted` 字段，前端无法伪造 |
| 重复请求消耗额度 | 对话接口幂等性设计，同一轮对话只扣 1 次 |
| 碎片额度跨日累积 | UTC 00:00 创建新记录，fragment_extra 从 0 开始 |

### 6.2 限流规则汇总

| 规则 | 实现位置 | 说明 |
|------|----------|------|
| 每日弹窗 ≤ 2 次 | PaywallService | paywall_events 表按日期统计 |
| 蜜月期禁全屏 | PaywallService | 注册 < 3 天强制 banner |
| 订阅用户免引导 | SubscriptionService | tier != free 直接返回 false |
| 超限自动降级 | PaywallService | modal_count >= 2 → banner |
| 主动查询例外 | API 层 | user_initiated=true 时跳过限流 |

---

## 七、待确认问题

### 7.1 支付渠道 ✅ 已确认

- 使用 **Mock 支付**，不对接真实支付渠道
- 后续有变化再改

### 7.2 碎片商城联动 ✅ 已确认

- 碎片购买对话额度定价：**3 碎片 = 1 次额外对话**
- 后续有变化再改

### 7.3 业务细节

- **好感衰减机制** ✅ 暂定方案：见下方 3.5 节
- [ ] Standard 隐藏选项的数据结构？（剧本内配置？）
- [ ] UGC 剧本的功能范围？（Premium 独占）

### 3.5 好感衰减机制（暂定）

> 后续有变化再改

**核心思路：** 用户长时间不登录，与 NPC 角色的好感度逐渐下降，回归时产生「重新建立连接」的动力。

**规则：**
- 连续 3 天未登录：好感度不衰减（短期离开无惩罚）
- 连续 4~7 天未登录：每日好感度 -2
- 连续 7 天以上未登录：每日好感度 -5
- 好感度最低降至 10（不会归零，保留基本连接）
- 回归后触发 returnee 阶段（3 天 5 次/天额度），配合衰减的好感度重新体验「升温」

**存储：**
- users 表新增 `affection_decay_last_calc` 字段（上次计算衰减的时间）
- 登录时实时计算衰减量并更新角色好感度

**实现位置：**
- `AffectionService.apply_decay(user_id)` — 登录时调用
- 衰减计算：`(now - last_login).days` → 按区间计算衰减量

---

## 八、实施计划（修正后）

### Phase 1: 数据层 & 基础服务 ✅ 已完成（需修正）

| 任务 | 状态 | 修正项 |
|------|------|--------|
| BE-001 订阅模型 | ✅ 完成 | 修正 TIER_PERMISSIONS 数值 |
| BE-002 额度引擎 | ✅ 完成 | 新增 returnee_activated_at 逻辑 |
| BE-003 Paywall引擎 | ✅ 完成 | 修正蜜月期判定条件 |
| PL-001 配置文件 | ✅ 完成 | - |

### Phase 2: API 层 & 对话改造（待启动）

| 任务 | 负责 | 预估 |
|------|------|------|
| BE-004 订阅 API 路由 | BE | 0.5天 |
| BE-005 额度 API 路由 | BE | 0.5天 |
| BE-006 Paywall API 路由 | BE | 0.5天 |
| BE-007 对话接口改造 | BE | 1天 |
| FE-003 订阅套餐页 | FE | 1天 |
| FE-004 引导组件库 | FE | 1天 |

### Phase 3: 联调 & 测试

| 任务 | 负责 | 预估 |
|------|------|------|
| BE-FE 联调 | BE+FE | 1天 |
| QA 全量测试 | QA | 1.5天 |

---

## 九、代码审查清单

Review 时重点关注：

- [ ] TIER_PERMISSIONS 数值是否与 PRD 一致
- [ ] 蜜月期判定：`days <= 3` vs `days < 3` 边界条件
- [ ] 回归用户 3 天窗口期计算逻辑
- [ ] 额度消耗：免扣场景是否正确过滤
- [ ] Paywall 限流：弹窗计数时机（展示时 vs 关闭时）
- [ ] UTC 00:00 重置：时区处理是否正确

---

**请 Review 后确认，我将根据反馈修正代码并继续 Phase 2 开发。**
