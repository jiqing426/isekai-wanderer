# CR-020 执行计划

## 概述
修复 CR-019 QA 通过后发现的 4 个遗留/回归缺陷。

## 任务执行顺序

### Phase 1: P0 核心功能修复（优先级最高）

#### T-001: 自定义对话存储与刷新保持 (P0)
**负责人**: BE + FE  
**预估工时**: 3h  
**绑定 AC**: AC-001-01, AC-001-02, AC-001-03

##### BE 执行步骤
1. **修改文件**: `backend/app/api/v1/game.py`
2. **修改位置**: `submit_custom_input` 函数（第791行）
3. **具体修改**:
   ```python
   # 在 process_custom_input 返回后，添加对话存储逻辑
   result = await engine.process_custom_input(...)
   
   # 存储用户输入
   user_dialogue = DialogueHistory(
       session_id=UUID(session_id),
       user_id=UUID(user_id),
       role='user',
       content=request.text.strip(),
   )
   db.add(user_dialogue)
   
   # 存储角色回应
   assistant_dialogue = DialogueHistory(
       session_id=UUID(session_id),
       user_id=UUID(user_id),
       role='assistant',
       content=result.get('text', ''),
       character_id=result.get('character_id'),
       emotion=result.get('emotion'),
   )
   db.add(assistant_dialogue)
   await db.commit()
   ```
4. **验证方法**:
   - 启动后端服务
   - 使用 curl 调用 `/game/{session_id}/custom-input`
   - 检查 `dialogue_history` 表是否有新记录

##### FE 执行步骤
1. **修改文件**: `frontend/src/stores/game.ts`
2. **修改位置**: `submitCustomInput` 函数（第227行）
3. **具体修改**:
   ```typescript
   // 在 submitCustomInput 中，发送消息后存储用户输入
   const resp = await api.post(...)
   
   // 存储用户输入（后端已自动存储，前端可选）
   // 如果后端已存储，前端不需要重复调用
   
   // 更新对话内容
   if (resp.text) {
     currentDialogue.value = { ... }
   }
   ```
4. **验证方法**:
   - 启动前端开发服务器
   - 进入剧本游戏，发送自定义输入
   - 刷新页面，打开历史对话抽屉
   - 确认显示刚才的对话记录

##### 回滚方案
- BE: `git checkout backend/app/api/v1/game.py`
- FE: `git checkout frontend/src/stores/game.ts`

---

#### T-002: 章节推进与路线图解锁 (P0)
**负责人**: BE  
**预估工时**: 4h  
**绑定 AC**: AC-002-01, AC-002-02, AC-002-03

##### BE 执行步骤
1. **分析问题**:
   - 检查 `narrative_engine.process_custom_input` 的节点推进逻辑
   - 确认"无选项时取第一个子节点"是否正确
   - 检查剧本节点结构，确认章节转换节点

2. **修改文件**: `backend/app/services/narrative/narrative_engine.py`
3. **修改位置**: `process_custom_input` 函数（第214行）
4. **具体修改**:
   ```python
   # 检查当前逻辑
   if next_choices:
       first_choice = next_choices[0]
       await self.script_service.advance_session(session_id, first_choice.id)
   else:
       # 无选项时查找子节点
       child_node_result = await self.db.execute(
           select(Node).where(Node.parent_id == current_node.id).limit(1)
       )
       child_node = child_node_result.scalar_one_or_none()
       
       if child_node:
           session.current_node_id = child_node.id
       # 问题：这里没有调用 advance_session，可能导致状态不一致
   
   # 修复：统一使用 advance_session
   if child_node:
       # 找到子节点的 choice，调用 advance_session
       # 或者直接更新 current_node_id 并保存
   ```

5. **验证方法**:
   - 检查剧本节点结构：`SELECT * FROM nodes WHERE script_id = 'xxx'`
   - 确认章节转换节点的 parent_id 和 choices
   - 进行10轮对话，检查是否进入第二章节
   - 检查路线图是否解锁

##### 回滚方案
- `git checkout backend/app/services/narrative/narrative_engine.py`

---

### Phase 2: P1 UI/UX 修复（可并行）

#### T-003: 赠送成功弹框数据显示 (P1)
**负责人**: FE  
**预估工时**: 0.5h  
**绑定 AC**: AC-003-01, AC-003-02

##### FE 执行步骤
1. **分析问题**:
   - 后端返回字段: `new_affection`, `remaining_fragments`
   - 前端模板用的: `sendResult.new_affection`, `sendResult.remaining_fragments`
   - 检查字段映射是否正确

2. **修改文件**: `frontend/src/components/GiftModal.vue`
3. **修改位置**: 
   - 类型定义（第125行）
   - 模板显示（第80-88行）
4. **具体修改**:
   ```typescript
   // 确认 sendResult 类型定义
   const sendResult = ref<{
     affection_delta: number;
     new_affection: number;
     remaining_fragments: number;
     // ... 其他字段
   } | null>(null);
   
   // 确认模板字段名
   // <span class="result-value">{{ sendResult.new_affection }}</span>
   // <span class="result-value">💎 {{ sendResult.remaining_fragments }}</span>
   ```

5. **验证方法**:
   - 进入剧本游戏，打开礼物弹框
   - 选择一个礼物，确认赠送
   - 检查赠送成功弹框是否显示正确的好感度和剩余碎片

##### 回滚方案
- `git checkout frontend/src/components/GiftModal.vue`

---

#### T-004: 碎片商城图片显示 (P1)
**负责人**: BE + FE  
**预估工时**: 2h  
**绑定 AC**: AC-004-01, AC-004-02

##### BE 执行步骤
1. **检查数据库**:
   ```sql
   SELECT id, name, icon_url FROM shop_goods;
   ```
2. **如果 icon_url 为空**:
   - 添加默认图片 URL
   - 或者创建数据迁移脚本
3. **修改文件**: `backend/app/models/shop_goods.py`（如需）
4. **验证方法**:
   - 调用 `/fragment/shop` API
   - 检查返回的 goods 列表是否有 icon_url

##### FE 执行步骤
1. **检查文件**: `frontend/src/views/FragmentMallView.vue`
2. **检查位置**: 图片显示逻辑（第54-56行）
3. **确认逻辑**:
   ```vue
   <img v-if="goods.icon_url" :src="goods.icon_url" :alt="goods.name" />
   <span v-else class="goods-emoji">{{ getCategoryEmoji(goods.category) }}</span>
   ```
4. **如果 fallback 不工作**:
   - 检查 `getCategoryEmoji` 函数
   - 确认 CSS 样式

##### 回滚方案
- BE: `git checkout backend/app/models/shop_goods.py` + 回滚数据库迁移
- FE: `git checkout frontend/src/views/FragmentMallView.vue`

---

## 时间线

| 时间 | 任务 | 负责人 | 状态 |
|------|------|--------|------|
| Day 1 上午 | T-001 BE 部分 | BE | 待开始 |
| Day 1 上午 | T-001 FE 部分 | FE | 待开始 |
| Day 1 下午 | T-002 BE 部分 | BE | 待开始 |
| Day 1 下午 | T-003 FE 部分 | FE | 待开始 |
| Day 2 上午 | T-004 BE 部分 | BE | 待开始 |
| Day 2 上午 | T-004 FE 部分 | FE | 待开始 |
| Day 2 下午 | QA 验证 | QA | 待开始 |

## 验证清单

### T-001 验证
- [ ] 发送自定义输入后，`dialogue_history` 表有新记录
- [ ] 刷新页面后，历史对话抽屉显示刚才的对话
- [ ] 自定义输入和角色回应都正确存储

### T-002 验证
- [ ] 进行10轮对话后，进入第二章节
- [ ] 路线图正确解锁
- [ ] 不会直接跳到结局

### T-003 验证
- [ ] 赠送成功后，弹框显示正确的好感度数值
- [ ] 赠送成功后，弹框显示正确的剩余碎片数值

### T-004 验证
- [ ] 碎片商城商品显示图片
- [ ] 如果图片不存在，fallback 到 emoji 显示

## 风险与缓解

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| T-001 存储影响性能 | 中 | 中 | 添加异步存储，不阻塞主流程 |
| T-002 修改影响其他剧本 | 高 | 高 | 测试多个剧本确认无副作用 |
| T-004 图片资源缺失 | 中 | 低 | 使用默认图片或 emoji fallback |

## 完成后流程

1. BE/FE 完成修复后，在 `review.md` 记录完成情况
2. 通知 PL（我）任务完成
3. PL 运行 `check-task-completion-readiness.py` 检查任务完成度
4. PL 通知 QA 开始验证
5. QA 运行测试用例，记录测试结果
6. QA 通过后，PL 运行 `check-gate-readiness.py --gate release`
7. 用户确认后，进入 RELEASE_GATE
