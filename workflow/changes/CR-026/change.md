# CR-026: 角色聊天页面移动端适配

## 变更概述
- **变更类型**: 功能优化
- **优先级**: P1
- **影响范围**: 前端 - 角色聊天页面
- **预计工期**: 0.5天

## 问题描述
角色聊天页面（CharacterChatView.vue）当前采用左右分栏布局，在移动端（屏幕宽度 ≤ 768px）显示效果差：
- 左侧角色列表和右侧聊天窗口同时显示，空间拥挤
- 无法正常使用聊天功能
- 用户体验差

## 解决方案
采用**单列切换式布局**：
1. 移动端默认显示聊天窗口
2. 顶部添加"角色列表"导航按钮
3. 点击按钮可切换到角色选择界面
4. 选择角色后自动返回聊天界面
5. 桌面端保持原有左右分栏布局

## 技术要求
- 响应式检测：`window.innerWidth <= 768px`
- 状态管理：`showCharacterList` 控制显示切换
- 自动返回：选择角色后自动切换到聊天界面
- 样式适配：使用 `@media (max-width: 768px)` 媒体查询

## 验收标准
- [ ] 移动端（≤768px）显示单列布局
- [ ] 顶部有"角色列表/返回聊天"切换按钮
- [ ] 选择角色后自动返回聊天界面
- [ ] 桌面端（>768px）保持原有左右分栏布局
- [ ] 切换流畅，无闪烁

## 任务分配
- **主责**: FE（前端开发）
- **协助**: 无
- **测试**: QA

## 相关文件
- `/root/isekai-wanderer/frontend/src/views/CharacterChatView.vue`
- `/root/isekai-wanderer/frontend/src/components/ChatWindow.vue`
- `/root/isekai-wanderer/frontend/src/components/CharacterList.vue`
