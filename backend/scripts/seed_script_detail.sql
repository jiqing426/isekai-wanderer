-- 剧本详情测试数据
-- 剧本：樱花纷飞的季节

-- 1. 插入剧本
INSERT INTO scripts (script_id, title, cover, description, author) VALUES
('550e8400-e29b-41d4-a716-446655440000', '樱花纷飞的季节', 'https://cdn.example.com/covers/sakura.jpg', '一个关于青春和爱情的故事，发生在樱花盛开的季节...', '剧本作者');

-- 2. 插入角色
INSERT INTO characters (character_id, script_id, name, avatar, description) VALUES
('char-001', '550e8400-e29b-41d4-a716-446655440000', '樱', 'https://cdn.example.com/characters/sakura.png', '温柔的青梅竹马，喜欢在樱花树下读书'),
('char-002', '550e8400-e29b-41d4-a716-446655440000', '凛', 'https://cdn.example.com/characters/rin.png', '神秘的转学生，总是独来独往');

-- 3. 插入结局
INSERT INTO endings (ending_id, script_id, title, type, description, unlock_condition) VALUES
('ending-001', '550e8400-e29b-41d4-a716-446655440000', '永远的约定', 'good', '两人约定永远在一起', '在第三章选择接受邀请'),
('ending-002', '550e8400-e29b-41d4-a716-446655440000', '错过的季节', 'normal', '错过了表白的时机', '在第三章选择婉拒'),
('ending-003', '550e8400-e29b-41d4-a716-446655440000', '樱花凋零', 'bad', '最终没有在一起', '在第二章做出错误选择');

-- 4. 插入CG
INSERT INTO cgs (cg_id, script_id, title, url, thumbnail, trigger_node_id) VALUES
('cg-001', '550e8400-e29b-41d4-a716-446655440000', '樱花树下的约定', 'https://cdn.example.com/cg/sakura_promise.jpg', 'https://cdn.example.com/cg/thumb/sakura_promise.jpg', NULL),
('cg-002', '550e8400-e29b-41d4-a716-446655440000', '月光下的告白', 'https://cdn.example.com/cg/moonlight.jpg', 'https://cdn.example.com/cg/thumb/moonlight.jpg', NULL);

-- 5. 插入章节
INSERT INTO chapters (chapter_id, script_id, title, order_number) VALUES
('chapter-001', '550e8400-e29b-41d4-a716-446655440000', '第一章：相遇', 1),
('chapter-002', '550e8400-e29b-41d4-a716-446655440000', '第二章：相知', 2),
('chapter-003', '550e8400-e29b-41d4-a716-446655440000', '第三章：选择', 3);

-- 6. 插入节点（第一章）
INSERT INTO nodes (node_id, chapter_id, type, title, content, background, order_number) VALUES
('node-001', 'chapter-001', 'fixed_scene', '樱花树下', '春天，樱花树下，花瓣随风飘落...', 'https://cdn.example.com/bg/sakura_tree.jpg', 1);

INSERT INTO nodes (node_id, chapter_id, type, title, character_id, dialogue_options, order_number) VALUES
('node-002', 'chapter-001', 'ai_dialog', '与樱的对话', 'char-001', '["你好", "今天天气不错", "你在看什么书？"]', 2);

-- 7. 插入节点（第二章）
INSERT INTO nodes (node_id, chapter_id, type, title, content, order_number) VALUES
('node-003', 'chapter-002', 'fixed_scene', '图书馆', '安静的图书馆里，阳光透过窗户洒在书桌上...', 1);

INSERT INTO nodes (node_id, chapter_id, type, title, choices, order_number) VALUES
('node-004', 'chapter-002', 'choice_point', '重要选择', '[{"text": "邀请她一起看书", "nextNodeId": "node-005"}, {"text": "独自离开", "nextNodeId": "node-006"}]', 2);

-- 8. 插入节点（第三章）
INSERT INTO nodes (node_id, chapter_id, type, title, description, order_number) VALUES
('node-005', 'chapter-003', 'converge_node', '故事汇聚', '无论选择什么，故事都会在这里汇聚...', 1);

INSERT INTO nodes (node_id, chapter_id, type, title, cg_id, order_number) VALUES
('node-006', 'chapter-003', 'cg_trigger', '特殊CG', 'cg-001', 2);

INSERT INTO nodes (node_id, chapter_id, type, title, ending_type, description, order_number) VALUES
('node-007', 'chapter-003', 'ending_node', '结局：永远的约定', 'good', '两人约定永远在一起，樱花见证了他们的爱情...', 3);

-- 9. 插入用户进度（测试用户）
INSERT INTO user_script_progress (user_id, script_id, selected_character_id, unlocked_nodes, unlocked_endings, unlocked_cgs, completion_rate) VALUES
('user-001', '550e8400-e29b-41d4-a716-446655440000', 'char-001', 
 '["node-001", "node-002", "node-003", "node-004"]',
 '["ending-001"]',
 '["cg-001"]',
 57.14);
