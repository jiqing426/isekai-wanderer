-- CR-029: 星月奇缘角色分支节点数据
-- MVP 剧本：星月奇缘 (script_id: de1c935a-3e82-4e29-aff9-c69c3a460418)
-- 第一章：月夜邂逅 (route_id: a1000001-0000-0000-0000-0000a1000001)
--
-- 角色：
-- - 沈星澜: 900a9744-04ca-4c6b-a276-c79595218672
-- - 白夜: 0dfedba2-1f5d-417d-a6a8-74f52d954a46
-- - 暮雪: dd7dacc0-fea8-434d-b63b-f4efbe4de615
--
-- 分支结构：
-- [分支起点] (公共) → 选择 → [沈星澜分支] / [白夜分支] / [暮雪分支] → [汇合节点] (公共)

-- 1. 创建分支起点节点（公共选择节点）
INSERT INTO nodes (id, route_id, node_type, content, character_id, created_at)
VALUES (
    'b2000001-0000-0000-0000-0000b2000001',
    'a1000001-0000-0000-0000-0000a1000001',
    'choice',
    '{"text": "月光下，三位少女同时出现在你面前。她们各自散发着不同的气息，等待你的回应。你会走向谁？", "emotion": "neutral"}',
    NULL,
    NOW()
);

-- 2. 创建沈星澜专属分支节点
INSERT INTO nodes (id, route_id, node_type, content, character_id, created_at)
VALUES (
    'b2000002-0000-0000-0000-0000b2000002',
    'a1000001-0000-0000-0000-0000a1000001',
    'preset',
    '{"text": "你走向沈星澜。她微微一笑，眼中映着月光。「你选择了我吗...我很高兴。」她伸出手，「让我们一起，看看这月色下的世界。」", "emotion": "happy", "character_name": "沈星澜"}',
    '900a9744-04ca-4c6b-a276-c79595218672',
    NOW()
);

-- 3. 创建白夜专属分支节点
INSERT INTO nodes (id, route_id, node_type, content, character_id, created_at)
VALUES (
    'b2000003-0000-0000-0000-0000b2000003',
    'a1000001-0000-0000-0000-0000a1000001',
    'preset',
    '{"text": "你走向白夜。她静静地看着你，月光在她银白的发丝上流淌。「...你来了。」她的声音很轻，却带着不易察觉的温柔，「我等你很久了。」", "emotion": "gentle", "character_name": "白夜"}',
    '0dfedba2-1f5d-417d-a6a8-74f52d954a46',
    NOW()
);

-- 4. 创建暮雪专属分支节点
INSERT INTO nodes (id, route_id, node_type, content, character_id, created_at)
VALUES (
    'b2000004-0000-0000-0000-0000b2000004',
    'a1000001-0000-0000-0000-0000a1000001',
    'preset',
    '{"text": "你走向暮雪。她活泼地跳到你面前，笑容灿烂如星。「嘿嘿，你选我了对吧！」她拉起你的手，「快走快走，我带你去看个好地方！」", "emotion": "excited", "character_name": "暮雪"}',
    'dd7dacc0-fea8-434d-b63b-f4efbe4de615',
    NOW()
);

-- 5. 创建汇合节点（公共节点）
INSERT INTO nodes (id, route_id, node_type, content, character_id, created_at)
VALUES (
    'b2000005-0000-0000-0000-0000b2000005',
    'a1000001-0000-0000-0000-0000a1000001',
    'preset',
    '{"text": "月光下，你们一起漫步在竹林小径。远处的山峦笼罩在薄雾中，萤火虫在四周飞舞。这一刻，时间仿佛静止了。", "emotion": "peaceful"}',
    NULL,
    NOW()
);

-- 6. 创建选择项：从分支起点指向三个角色分支
INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, created_at)
VALUES
    -- 选择沈星澜
    ('c2000001-0000-0000-0000-0000c2000001', 'b2000001-0000-0000-0000-0000b2000001', 
     '走向沈星澜，她的笑容如月光般温柔', 
     'b2000002-0000-0000-0000-0000b2000002', 2, NOW()),
    -- 选择白夜
    ('c2000002-0000-0000-0000-0000c2000002', 'b2000001-0000-0000-0000-0000b2000001', 
     '走向白夜，她静静等待的身影让人心疼', 
     'b2000003-0000-0000-0000-0000b2000003', 2, NOW()),
    -- 选择暮雪
    ('c2000003-0000-0000-0000-0000c2000003', 'b2000001-0000-0000-0000-0000b2000001', 
     '走向暮雪，她的活力感染了你', 
     'b2000004-0000-0000-0000-0000b2000004', 2, NOW());

-- 7. 创建选择项：从每个角色分支指向汇合节点
INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, created_at)
VALUES
    -- 沈星澜分支 → 汇合
    ('c2000004-0000-0000-0000-0000c2000004', 'b2000002-0000-0000-0000-0000b2000002', 
     '继续一起赏月', 
     'b2000005-0000-0000-0000-0000b2000005', 1, NOW()),
    -- 白夜分支 → 汇合
    ('c2000005-0000-0000-0000-0000c2000005', 'b2000003-0000-0000-0000-0000b2000003', 
     '继续一起赏月', 
     'b2000005-0000-0000-0000-0000b2000005', 1, NOW()),
    -- 暮雪分支 → 汇合
    ('c2000006-0000-0000-0000-0000c2000006', 'b2000004-0000-0000-0000-0000b2000004', 
     '继续一起赏月', 
     'b2000005-0000-0000-0000-0000b2000005', 1, NOW());

-- 验证插入结果
SELECT '分支起点节点' as type, id, node_type, character_id FROM nodes WHERE id = 'b2000001-0000-0000-0000-0000b2000001';
SELECT '角色分支节点' as type, id, node_type, character_id FROM nodes WHERE id IN ('b2000002-0000-0000-0000-0000b2000002', 'b2000003-0000-0000-0000-0000b2000003', 'b2000004-0000-0000-0000-0000b2000004');
SELECT '汇合节点' as type, id, node_type, character_id FROM nodes WHERE id = 'b2000005-0000-0000-0000-0000b2000005';
SELECT '选择项' as type, id, node_id, text FROM node_choices WHERE id LIKE 'c200000%';
