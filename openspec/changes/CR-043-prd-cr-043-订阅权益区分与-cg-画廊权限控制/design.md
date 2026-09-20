# Design — CR-043: 订阅权益区分与 CG 画廊权限控制

## Overview

- CR-043 是权益保护类变更，目标是在执行层面强制落地已定义的 `TIER_PERMISSIONS` 权限。
- 现有系统已完整定义 free/basic/standard/premium 四档权益（`SubscriptionService` + `TIER_PERMISSIONS`），但后端 API 层未强制执行：CG 画廊只检查 `UnlockedCG` 表不检查订阅等级；`game.py` 开始游戏时不检查 `script_access`；前端功能入口无锁/升级提示；订阅成功后前端状态不同步。
- 本 CR 不修改 `TIER_PERMISSIONS` 定义、数据库结构、`SubscriptionService` 核心逻辑。仅在 API 端点层和前端组件层增加权益检查逻辑。

## Technology Decisions

本 CR 不引入新技术选型。所有实现基于现有技术栈（Python FastAPI + Vue 3 + Pinia + Naive UI），复用现有 `SubscriptionService.get_user_tier()` / `get_tier_permissions()` / `check_permission()` 方法和 `useSubscriptionStore`。

| Decision | Selected | Status | Evidence |
| --- | --- | --- | --- |
| 语言 / 框架 | Python FastAPI + Vue 3 + TypeScript | Accepted | docs/decisions/decisions.md |
| 数据库 / 存储 | PostgreSQL（不修改表结构） | Accepted | docs/decisions/decisions.md |
| 缓存 / 队列 | Redis（不修改） | Accepted | docs/decisions/decisions.md |
| 云服务 / 部署方式 | Docker + Nginx（不修改） | Accepted | 现有部署不变，PL 确认 |
| 模型供应商 / AI 工具 | 不涉及 | Not Required | 本 CR 不涉及 LLM 调用 |
| 权限检查位置 | API 端点层（非中间件） | Accepted | docs/decisions/decisions.md |
| is_accessible 字段设计 | 每项 CG/script 对象内嵌布尔字段 | Accepted | Architect 确认（Q-001），见 design.md Q-001 |
| script_access 映射规则 | 基于 genre + hot_value 运行时虚拟字段 | Accepted | Architect 确认（Q-002），见 design.md Q-002 |

## Technical Approach

### Q 编号确认

#### Q-001：is_accessible 字段 API 契约设计（CEO 附条件 C1）

**确认结论**：在每个 CG 项对象中新增 `is_accessible: boolean` 字段。

**API 契约**：

```json
// GET /api/v1/gallery/collections/{script_id} 响应
{
  "items": [
    {
      "id": "uuid",
      "collection_id": "uuid",
      "title": "CG 标题",
      "thumbnail_url": "/assets/cg/1_thumb.jpg",
      "full_url": "/assets/cg/1_full.jpg",
      "script_name": "剧本名",
      "unlock_status": "unlocked" | "locked",
      "unlock_condition": "完成特定剧情节点",
      "is_accessible": true   // ← 新增字段
    }
  ]
}
```

**计算逻辑**：
```python
is_accessible = is_unlocked or tier_allows_full_gallery
```

其中 `tier_allows_full_gallery` 判定：
- `tier == 'standard'` 或 `tier == 'premium'` → `True`（可访问全部 CG）
- `tier == 'free'` 或 `tier == 'basic'` → `False`（仅可访问已解锁 CG）

即：standard+ 用户对所有 CG `is_accessible=True`；free/basic 用户仅对已通过剧情解锁的 CG `is_accessible=True`。

**实现位置**：`gallery.py` → `get_collection_items()` 端点。

**安全约束**：`is_accessible` 由后端基于 `SubscriptionService.get_user_tier()` 计算，前端不可篡改。

#### Q-002：script_access 三档映射到剧本表结构（CEO 附条件 C2）

**确认结论**：在 `scripts.py` 的 `list_scripts()` 和 `get_script()` 端点中，通过运行时虚拟字段 `is_exclusive` 和 `genre` 计算 `is_accessible`，不修改数据库表结构。

**映射规则**：

当前 `scripts` 表无 `is_exclusive` 或 `is_trial` 字段。PRD Non-Goals 明确"不修改数据库结构"。因此采用运行时判定：

| script_access 值 | 可访问剧本范围 | 判定规则 |
| --- | --- | --- |
| `trial_only` (free) | 试用剧本 | `genre == 'romance' AND hot_value >= 50`（最高热度恋爱剧本作为试用剧本） |
| `all_normal` (basic/standard) | 所有非独家剧本 | 所有剧本（当前无剧本标记为独家） |
| `all_including_exclusive` (premium) | 所有剧本 | 所有剧本无限制 |

**判定逻辑实现**（伪代码）：
```python
def _compute_script_accessible(tier: str, script: Script) -> bool:
    permissions = await sub_service.get_tier_permissions(tier)
    access = permissions.script_access  # trial_only / all_normal / all_including_exclusive
    
    if access == "all_including_exclusive":
        return True  # premium 可玩所有
    if access == "all_normal":
        return True  # basic/standard 可玩所有普通剧本（当前无独家剧本，全部可玩）
    if access == "trial_only":
        # free 用户：仅试用剧本
        return script.genre == 'romance' and (script.hot_value or 0) >= 50
    return False
```

**关于"试用剧本"的具体范围（Q-003 确认）**：采用 PRD 建议默认值——trial = `genre == 'romance' AND hot_value >= 50` 的剧本。这是一个运行时判定规则，不持久化到数据库。如果未来需要调整试用范围，只需修改此判定函数，不影响数据库结构。

**关于独家剧本**：当前系统无剧本标记为"独家"（`is_exclusive` 字段不存在于 `scripts` 表）。premium 的 `all_including_exclusive` 权限当前等同于 `all_normal`。但权限检查逻辑仍然保留三档分支，为未来添加独家剧本预留扩展点。如果未来新增独家剧本，可在 `scripts` 表增加 `is_exclusive BOOLEAN DEFAULT FALSE` 字段，届时 `all_normal` 档需追加 `AND NOT script.is_exclusive` 条件。

#### Q-003："试用剧本"的具体范围

**确认结论**：采用 PRD 建议默认值。trial = `genre == 'romance' AND hot_value >= 50`。运行时判定，不持久化。

#### Q-004：standard+ 用户查看 CG 显示方式

**确认结论**：standard+ 用户查看未通过剧情解锁的 CG 时，显示完整大图。因为 standard+ 的权益就是"可访问完整画廊"，`is_accessible=True` 时前端不显示锁图标，点击可查看完整图片。

#### Q-005：权限检查放 API 层还是中间件

**确认结论**：放 API 端点层，不使用中间件。

**理由**：
- CG 画廊和剧本列表的权限检查逻辑不同（gallery 检查 `ugc_access`/订阅等级，scripts 检查 `script_access`），不适合统一中间件
- `game.py` 的 `start_game` 端点需要检查 `script_access`，这是业务逻辑判断，不适合放在通用中间件
- 现有 `SubscriptionService.check_permission()` 已封装权限检查逻辑，端点层直接调用即可
- 与现有代码风格一致（端点层调用 service 层）

### 模块变更设计

#### DEV-001：后端 gallery.py — is_accessible 字段

**变更文件**：`backend/app/api/v1/gallery.py`

**变更内容**：
1. `get_collection_items()` 端点增加订阅等级检查逻辑
2. 每个 CG 项新增 `is_accessible` 布尔字段

**实现逻辑**：
```python
@router.get("/collections/{script_id}")
async def get_collection_items(
    script_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    # ... 现有 CG 查询逻辑不变 ...
    
    # 获取用户订阅等级
    sub_service = SubscriptionService(db)
    tier = await sub_service.get_user_tier(UUID(user_id))
    permissions = await sub_service.get_tier_permissions(tier)
    
    # standard+ 用户可访问全部 CG
    tier_allows_full = tier in ("standard", "premium")
    
    items = []
    for cg_asset, route in cg_assets:
        cg_id = str(cg_asset.id)
        is_unlocked = cg_id in unlocked_cg_ids
        is_accessible = is_unlocked or tier_allows_full
        
        items.append({
            # ... 现有字段不变 ...
            "is_accessible": is_accessible,
        })
    
    return {"items": items}
```

**消费者**：前端 `GalleryView.vue` + `api/gallery.ts`

#### DEV-002：前端 GalleryView.vue + 剧本/角色选择组件 — 锁/升级提示

**变更文件**：
- `frontend/src/views/GalleryView.vue`
- `frontend/src/api/gallery.ts`
- `frontend/src/views/script/` 下的剧本列表和角色选择组件
- `frontend/src/stores/subscription.ts`（只调用，不修改核心逻辑）

**变更内容**：
1. GalleryView 对 `is_accessible=false` 的 CG 显示锁图标和升级提示
2. 剧本列表组件对 `is_accessible=false` 的剧本显示锁定状态
3. 角色选择组件对不可用剧本的角色显示锁定
4. 前端通过 `useSubscriptionStore` 获取 tier 和 permissions，不硬编码权限映射
5. 前端以 API 返回的 `is_accessible` 为权威值

**GalleryView 变更**：
```vue
<!-- 对 is_accessible=false 的 CG 显示锁 -->
<div v-if="!item.is_accessible" class="cg-lock-overlay">
  <span class="cg-lock-icon">🔒</span>
  <span class="cg-lock-hint">升级订阅解锁</span>
</div>
<!-- 点击锁定 CG 不展开完整图片 -->
@click="item.is_accessible ? previewCG(item) : showUpgradeHint()"
```

**剧本列表变更**：
- 剧本卡片对 `is_accessible=false` 的显示锁定遮罩
- 点击锁定剧本不进入游戏，显示升级提示

**角色选择变更**：
- 对不可用剧本的角色显示锁定状态
- 点击锁定角色显示升级提示

#### DEV-003：后端 game.py + scripts.py — script_access 强制检查

**变更文件**：
- `backend/app/api/v1/game.py`（`start_game` 端点）
- `backend/app/api/v1/scripts.py`（`list_scripts` 和 `get_script` 端点）

**变更内容**：

1. **`scripts.py` → `list_scripts()`**：每个剧本项新增 `is_accessible` 字段
   - 当前 `list_scripts` 是公开端点（无 Bearer 认证），需要改为认证端点或可选认证
   - 若改为认证端点：未认证用户 `is_accessible` 基于 free 判定
   - 若保持公开：不返回 `is_accessible` 字段（需认证时才返回）
   - **设计决定**：保持公开端点，但当用户已认证时（通过可选 Bearer token）返回 `is_accessible` 字段；未认证时不返回该字段
   - 实际实现：使用 `Optional[depends(get_current_user_id)]` 模式

2. **`scripts.py` → `get_script()`**：返回的剧本对象新增 `is_accessible` 字段

3. **`game.py` → `start_game()`**：在创建 GameSession 前检查 `script_access`
   ```python
   # 获取用户 tier 和 script_access
   sub_service = SubscriptionService(db)
   tier = await sub_service.get_user_tier(UUID(user_id))
   permissions = await sub_service.get_tier_permissions(tier)
   script_access = permissions.script_access
   
   # 检查剧本是否可访问
   script = await db.execute(select(Script).where(Script.id == script_uuid))
   script = script.scalar_one_or_none()
   
   if not _check_script_access(script_access, script):
       raise AppException("SCRIPT_ACCESS_DENIED", 403, 
           "当前订阅等级无法游玩此剧本，请升级订阅")
   ```

4. **新增错误码**：
   | Error Code | HTTP Status | Meaning |
   | --- | --- | --- |
   | SCRIPT_ACCESS_DENIED | 403 | 订阅等级不足以游玩此剧本 |

5. **审计日志**：403 权限拒绝时记录 `(user_id, script_id, tier, timestamp)`

#### DEV-004：前端 SubscriptionPlans.vue + auth.ts + types — 订阅状态同步

**变更文件**：
- `frontend/src/components/SubscriptionPlans.vue`
- `frontend/src/stores/auth.ts`
- `frontend/src/stores/subscription.ts`（只调用，不修改核心逻辑）
- `frontend/src/router/index.ts`（路由守卫）
- `frontend/src/types/user.ts`
- `frontend/src/types/auth.ts`

**变更内容**：

1. **SubscriptionPlans.vue**：订阅成功后调用 `subscriptionStore.fetchSubscriptionStatus()` 和 `authApi.getProfile()`
   ```typescript
   async function handleSubscribe(planId: string) {
     // ... 现有订阅逻辑 ...
     if (response.status === 'success') {
       message.success('订阅成功！');
       // 刷新订阅状态
       await subscriptionStore.fetchSubscriptionStatus();
       // 刷新用户信息（含 subscription_tier）
       await authApi.getProfile().then(profile => {
         authStore.setUser(profile);
       });
       await loadPlans();
     }
   }
   ```

2. **auth.ts**：登录成功后自动加载订阅状态
   ```typescript
   // 在 login() 成功后
   await subscriptionStore.fetchSubscriptionStatus();
   ```

3. **types/user.ts**：`UserProfile.subscription_tier` 类型补齐 `'basic'`
   ```typescript
   subscription_tier: 'free' | 'basic' | 'standard' | 'premium';
   ```

4. **MemberInfo.tier** 和 **SubscriptionStatus.tier** 类型也补齐 `'basic'`

#### DEV-005：后端 settings.py — get_member_info 数据源修复

**变更文件**：`backend/app/api/v1/settings.py`（`get_member_info` 端点）

**变更内容**：

1. `tier` 从 `SubscriptionService.get_user_tier()` 获取，不再直接读 `user.subscription_tier`
2. `status` 和 `expires_at` 从 `SubscriptionService.get_user_subscription()` 读取 Subscription 表数据
3. 不再依赖 `User.trial_started_at` / `User.trial_ends_at` 字段

**修复后逻辑**：
```python
@router.get("/member-info")
async def get_member_info(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    sub_service = SubscriptionService(db)
    user_uuid = UUID(user_id)
    
    # tier 从 SubscriptionService 获取（统一数据源）
    tier = await sub_service.get_user_tier(user_uuid)
    
    # status 和 expires_at 从 Subscription 表获取
    subscription = await sub_service.get_user_subscription(user_uuid)
    
    if subscription:
        member_status = "active" if subscription.status == "active" else "inactive"
        expires_at = subscription.expires_at.isoformat() if subscription.expires_at else None
        member_since = subscription.started_at.isoformat() if subscription.started_at else None
    else:
        member_status = "inactive"
        expires_at = None
        member_since = None
    
    # ... 其余逻辑不变（fragment_balance, recent_bills, benefits） ...
    
    return {
        "tier": tier,  # ← 从 SubscriptionService 获取
        "status": member_status,
        "member_since": member_since,
        "expires_at": expires_at,  # ← 从 Subscription 表获取
        # ... 其余字段不变 ...
    }
```

### 安全检查点设计（CEO 附条件 C3）

**安全约束**：
1. 后端通过 `SubscriptionService.get_user_tier(user_id)` 从服务端数据库获取用户 tier，**不接受客户端请求中的 tier 参数**
2. `POST /game/start` 在创建 GameSession 前检查 `script_access`，基于服务端 tier
3. Gallery API `is_accessible` 字段由后端计算
4. Scripts API `is_accessible` 字段由后端计算
5. 403 权限拒绝记录审计日志（user_id, script_id, tier, timestamp）
6. 前端不硬编码 tier→permissions 映射，以后端 API 返回的 `is_accessible` 为权威值

**Security 阶段审查范围**：
- API 层面是否可伪造 tier 绕过权限
- `get_user_tier()` 是否信任了客户端输入
- 审计日志是否完整记录权限拒绝事件
- 前端是否有硬编码权限映射可被篡改

## ADR

### ADR-043-01: 权限检查放在 API 端点层

**Date**: 2026-09-16
**Status**: Accepted
**CR**: CR-043

**Context**: Q-005 暂缓到 DESIGN 阶段确认权限检查放在 API 层还是中间件层。CG 画廊和剧本访问的权限检查逻辑各不相同，需要决定放置位置。

**Decision**: 放在 API 端点层，不使用中间件。

**Alternatives Considered**:

| Dimension | API 端点层 (Selected) | 中间件层 |
|-----------|----------------------|---------|
| 灵活性 | ✅ 每个端点可定制检查逻辑 | ❌ 通用中间件难以覆盖不同权限场景 |
| 与现有代码一致 | ✅ 端点层调用 Service 层 | ❌ 需新增中间件层 |
| 代码可读性 | ✅ 权限检查在端点内可见 | ❌ 中间件隐式拦截 |
| 维护成本 | ✅ 低 | ❌ 需维护中间件配置 |

**Rationale**: CG 画廊检查订阅等级（standard+ 可访问全部），剧本检查 `script_access`（三档映射），`game.py` 检查 `script_access` + 剧本分类。三种场景逻辑不同，不适合统一中间件。端点层调用 `SubscriptionService` 的方式与现有代码风格一致。

**Consequences**:
- `gallery.py`、`game.py`、`scripts.py` 各自调用 `SubscriptionService` 进行权限检查
- 不新增中间件
- 权限检查逻辑在端点代码中可见

### ADR-043-02: script_access 映射采用运行时虚拟判定

**Date**: 2026-09-16
**Status**: Accepted
**CR**: CR-043

**Context**: Q-002/C2 要求确认 `script_access` 三档如何映射到剧本表结构。PRD Non-Goals 明确"不修改数据库结构"。

**Decision**: 通过运行时虚拟字段判定，不修改 `scripts` 表。

**判定规则**:
- `trial_only` (free)：`genre == 'romance' AND hot_value >= 50`
- `all_normal` (basic/standard)：所有剧本（当前无独家剧本）
- `all_including_exclusive` (premium)：所有剧本

**Rationale**:
- PRD 明确不修改数据库结构
- 当前系统无独家剧本，不需要 `is_exclusive` 字段
- 运行时判定函数可随业务调整，不触发数据库迁移
- 试用剧本范围采用 PRD 建议默认值（Q-003 确认）

**Consequences**:
- `scripts.py` 和 `game.py` 中新增 `_compute_script_accessible()` 辅助函数
- 未来如需新增独家剧本，可在 `scripts` 表增加 `is_exclusive` 字段，届时 `all_normal` 档追加 `AND NOT is_exclusive` 条件
- 试用剧本范围调整只需修改判定函数

## Document Sync

| Target Doc | Status | Summary / Evidence |
| --- | --- | --- |
| `docs/architecture/architecture.md` | Synced | 追加 CR-043 权限检查模块依赖关系和设计落点 |
| `docs/api/api.md` | Synced | 追加 CR-043 is_accessible 字段契约、SCRIPT_ACCESS_DENIED 错误码、member-info 数据源修复说明 |
| `docs/database/database.md` | Synced | Not Required: 无 DB 表结构变更；is_accessible 为运行时计算字段 |
| `docs/security/security.md` | Synced | 追加 CR-043 权限边界变更安全约束和安全检查清单 |
| `docs/decisions/decisions.md` | Synced | 追加 ADR-043-01（权限检查位置）和 ADR-043-02（script_access 运行时判定） |
| `docs/runtime/runtime-contract.md` | Synced | 追加 CR-043 端点变更说明、Browser E2E 用户动作扩展 |
