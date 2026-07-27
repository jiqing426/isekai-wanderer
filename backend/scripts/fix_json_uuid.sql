-- 修复 JSON 字段中的硬编码 UUID
-- 将 nodes.content.character_id 等 JSON 字段中的旧 UUID 更新为新 UUID v4

BEGIN;

-- 创建旧 UUID 到新 UUID 的映射表
CREATE TEMPORARY TABLE uuid_mapping (
    old_uuid UUID,
    new_uuid UUID
);

-- 插入字符 ID 映射
INSERT INTO uuid_mapping VALUES
    ('22222222-2222-2222-2222-222222222222', '40e4c04a-5a07-4fc7-8f8b-4431f0e1194b'),  -- 林辰
    ('a2222222-2222-2222-2222-222222222222', '6982c07f-bb69-4abe-9919-f54ea94297a4'),  -- 藤原雪
    ('77777777-7777-7777-7777-777777777777', '900a9744-04ca-4c6b-a276-c79595218672');  -- 沈星澜

-- 1. 更新 nodes.content.character_id
UPDATE nodes
SET content = jsonb_set(
    content::jsonb,
    '{character_id}',
    to_jsonb(m.new_uuid::text)
)
FROM uuid_mapping m
WHERE content->>'character_id' = m.old_uuid::text;

-- 2. 更新 game_sessions.metadata 中的 character_id（如果存在）
UPDATE game_sessions
SET metadata = jsonb_set(
    metadata::jsonb,
    '{character_id}',
    to_jsonb(m.new_uuid::text)
)
FROM uuid_mapping m
WHERE metadata->>'character_id' = m.old_uuid::text;

-- 3. 检查并更新其他可能包含旧 UUID 的 JSON 字段
-- characters.personality (如果有引用其他角色)
-- convergence_points.content (如果有角色引用)
-- 这些需要检查实际数据

-- 验证更新结果
SELECT 'nodes.content.character_id 更新后' as check_item, 
       content->>'character_id' as character_id,
       COUNT(*) as count
FROM nodes
WHERE content->>'character_id' IS NOT NULL
GROUP BY content->>'character_id';

SELECT 'game_sessions.metadata.character_id 更新后' as check_item,
       metadata->>'character_id' as character_id,
       COUNT(*) as count
FROM game_sessions
WHERE metadata->>'character_id' IS NOT NULL
GROUP BY metadata->>'character_id';

-- 检查是否还有旧 UUID 残留
SELECT '检查 nodes 中是否还有旧 UUID' as check_item,
       content->>'character_id' as old_uuid
FROM nodes
WHERE content->>'character_id' IN (
    '22222222-2222-2222-2222-222222222222',
    'a2222222-2222-2222-2222-222222222222',
    '77777777-7777-7777-7777-777777777777'
);

COMMIT;
