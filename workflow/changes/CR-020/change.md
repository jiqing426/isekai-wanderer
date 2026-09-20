# CR-020: 剧本游戏回归缺陷修复（QA 后）

## 变更目标
修复 CR-019 QA 通过后用户验收阶段发现的 4 个遗留/回归缺陷。

## 影响范围
- 前端：GameView.vue、GiftModal.vue、stores/game.ts、FragmentMallView.vue
- 后端：game.py（custom-input / gift / dialogue store）、narrative_engine.py（章节推进逻辑）
- 数据：shop_goods.icon_url

## 问题清单

### P0 - 核心功能问题（2个）
1. **自定义对话等待时间长 + 刷新后进度丢失**
   - 现象：submitCustomInput 后等待很久；刷新页面后对话历史没有保存
   - 根因：submitCustomInput 没有调用 store_dialogue 存储对话；custom-input 端点也没有自动存储
   - 影响：用户刷新页面后丢失所有自定义对话历史

2. **10轮对话后直接结局，没有进入第二章节/解锁路线图**
   - 现象：一个章节10轮对话后应该更新数据到第二章节、解锁路线图，但现在直接对话完到结局
   - 根因：narrative_engine.process_custom_input 里"无选项时取第一个子节点推进"逻辑有问题，可能跳过了章节转换节点
   - 影响：游戏流程断裂，无法体验多章节内容

### P1 - UI/UX问题（2个）
3. **赠送弹框赠送成功后，当前好感度、剩余碎片没有显示数据**
   - 现象：赠送成功弹框里"当前好感度"和"剩余碎片"显示空白
   - 根因：后端返回字段是 `new_affection` / `remaining_fragments`，但前端 sendResult 类型定义是 `new_affection_value` / `remaining_shards`；模板用的是 `sendResult.new_affection` / `sendResult.remaining_fragments`，字段名不匹配
   - 影响：用户无法确认赠送结果

4. **碎片商城中 goods-icon 没有图片**
   - 现象：碎片商城商品图标位置空白
   - 根因：shop_goods.icon_url 字段存在但数据库里没填；前端 fallback 到 getCategoryEmoji 但可能也没显示
   - 影响：商城视觉不完整

## 成功标准
- 自定义对话后立即存储，刷新页面后历史仍在
- 自定义对话响应时间 < 3 秒（当前可能 > 10 秒）
- 10轮对话后正确进入第二章节并解锁路线图
- 赠送成功弹框正确显示好感度和剩余碎片
- 碎片商城商品显示图片

## 风险
- 自定义对话存储可能增加数据库压力（需要批量或异步）
- 章节推进逻辑修改可能影响其他剧本流程
- 碎片商城图片需要确认图片资源位置
