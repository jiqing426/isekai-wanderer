# CR-020 任务分配

## T-001: 自定义对话存储与刷新保持 (P0)
- **负责人**: BE + FE
- **范围**: 
  - BE: custom-input 端点自动调用 store_dialogue 存储对话
  - FE: submitCustomInput 后调用 store_dialogue 存储用户输入
- **验证**: 刷新页面后 HistoryDrawer 能显示之前的对话记录
- **回滚**: 回退 custom-input 端点修改
- **绑定 AC**: AC-001-01, AC-001-02, AC-001-03
- **不覆盖 AC**: 无
- **预估工时**: 3h

## T-002: 章节推进与路线图解锁 (P0)
- **负责人**: BE
- **范围**: 
  - 修复 narrative_engine.process_custom_input 的章节推进逻辑
  - 确认剧本节点结构，确保10轮对话后正确进入第二章节
  - 确保路线图正确解锁
- **验证**: 10轮对话后进入第二章节，路线图解锁，不会直接跳到结局
- **回滚**: 回退 narrative_engine.py 修改
- **绑定 AC**: AC-002-01, AC-002-02, AC-002-03
- **不覆盖 AC**: 无
- **预估工时**: 4h

## T-003: 赠送成功弹框数据显示 (P1)
- **负责人**: FE
- **范围**: 
  - 修复 GiftModal.vue 的 sendResult 类型定义
  - 确保模板字段名与后端返回字段匹配
- **验证**: 赠送成功后显示正确的好感度和剩余碎片
- **回滚**: 回退 GiftModal.vue 修改
- **绑定 AC**: AC-003-01, AC-003-02
- **不覆盖 AC**: 无
- **预估工时**: 0.5h

## T-004: 碎片商城图片显示 (P1)
- **负责人**: BE + FE
- **范围**: 
  - BE: 确认 shop_goods 表的 icon_url 字段是否有数据
  - BE: 如果没有数据，添加默认图片 URL
  - FE: 确认 FragmentMallView.vue 的图片显示逻辑
- **验证**: 碎片商城商品显示图片
- **回滚**: 回退数据库修改和前端修改
- **绑定 AC**: AC-004-01, AC-004-02
- **不覆盖 AC**: 无
- **预估工时**: 2h

## 任务依赖
- T-001 和 T-002 是 P0，优先修复
- T-003 和 T-004 是 P1，可以并行修复
- 无任务间依赖

## 允许写入范围
- BE: backend/app/api/v1/game.py, backend/app/services/narrative/narrative_engine.py
- FE: frontend/src/stores/game.ts, frontend/src/components/GiftModal.vue, frontend/src/views/FragmentMallView.vue
- DB: shop_goods 表（icon_url 字段）
