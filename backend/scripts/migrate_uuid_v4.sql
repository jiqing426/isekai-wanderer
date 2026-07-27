-- T-008: UUID v4 数据迁移
-- 将硬编码的 UUID 迁移为随机 UUID v4
-- 策略：先删除外键约束，更新所有 ID，再重建约束

BEGIN;

-- ============================================================
-- Step 1: 生成 UUID 映射表
-- ============================================================
CREATE TEMPORARY TABLE IF NOT EXISTS uuid_mapping (
    old_id UUID PRIMARY KEY,
    new_id UUID NOT NULL
);
DELETE FROM uuid_mapping;

-- Scripts
INSERT INTO uuid_mapping VALUES
    ('11111111-1111-1111-1111-111111111111', gen_random_uuid()),
    ('a1111111-1111-1111-1111-111111111111', gen_random_uuid()),
    ('66666666-6666-6666-6666-666666666666', gen_random_uuid());

-- Characters
INSERT INTO uuid_mapping VALUES
    ('22222222-2222-2222-2222-222222222222', gen_random_uuid()),
    ('a2222222-2222-2222-2222-222222222222', gen_random_uuid()),
    ('77777777-7777-7777-7777-777777777777', gen_random_uuid());

-- Routes
INSERT INTO uuid_mapping VALUES
    ('33333333-3333-3333-3333-333333333333', gen_random_uuid()),
    ('a3333333-3333-3333-3333-333333333333', gen_random_uuid()),
    ('88888888-8888-8888-8888-888888888888', gen_random_uuid()),
    ('b1111111-1111-1111-1111-111111111111', gen_random_uuid()),
    ('b2222222-2222-2222-2222-222222222222', gen_random_uuid()),
    ('b3333333-3333-3333-3333-333333333333', gen_random_uuid()),
    ('c1111111-1111-1111-1111-111111111111', gen_random_uuid()),
    ('c2222222-2222-2222-2222-222222222222', gen_random_uuid()),
    ('c3333333-3333-3333-3333-333333333333', gen_random_uuid()),
    ('d1111111-1111-1111-1111-111111111111', gen_random_uuid()),
    ('d2222222-2222-2222-2222-222222222222', gen_random_uuid()),
    ('d3333333-3333-3333-3333-333333333333', gen_random_uuid());

-- ============================================================
-- Step 2: 删除外键约束
-- ============================================================
ALTER TABLE characters DROP CONSTRAINT IF EXISTS characters_script_id_fkey;
ALTER TABLE routes DROP CONSTRAINT IF EXISTS routes_script_id_fkey;
ALTER TABLE game_sessions DROP CONSTRAINT IF EXISTS game_sessions_script_id_fkey;
ALTER TABLE game_sessions DROP CONSTRAINT IF EXISTS game_sessions_route_id_fkey;
ALTER TABLE convergence_points DROP CONSTRAINT IF EXISTS convergence_points_script_id_fkey;
ALTER TABLE endings DROP CONSTRAINT IF EXISTS endings_script_id_fkey;
ALTER TABLE endings DROP CONSTRAINT IF EXISTS endings_route_id_fkey;
ALTER TABLE free_chat_sessions DROP CONSTRAINT IF EXISTS free_chat_sessions_script_id_fkey;
ALTER TABLE free_chat_sessions DROP CONSTRAINT IF EXISTS free_chat_sessions_character_id_fkey;
ALTER TABLE scenes DROP CONSTRAINT IF EXISTS scenes_script_id_fkey;
ALTER TABLE unlocked_scripts DROP CONSTRAINT IF EXISTS unlocked_scripts_script_id_fkey;
ALTER TABLE user_dialogue_counts DROP CONSTRAINT IF EXISTS user_dialogue_counts_script_id_fkey;
ALTER TABLE cg_assets DROP CONSTRAINT IF EXISTS cg_assets_script_id_fkey;
ALTER TABLE cg_assets DROP CONSTRAINT IF EXISTS cg_assets_route_id_fkey;
ALTER TABLE affection DROP CONSTRAINT IF EXISTS affection_character_id_fkey;
ALTER TABLE affection_history DROP CONSTRAINT IF EXISTS affection_history_character_id_fkey;
ALTER TABLE character_memories DROP CONSTRAINT IF EXISTS character_memories_character_id_fkey;
ALTER TABLE character_sprites DROP CONSTRAINT IF EXISTS character_sprites_character_id_fkey;
ALTER TABLE dialogue_history DROP CONSTRAINT IF EXISTS dialogue_history_character_id_fkey;
ALTER TABLE gift_records DROP CONSTRAINT IF EXISTS gift_records_character_id_fkey;
ALTER TABLE nodes DROP CONSTRAINT IF EXISTS nodes_route_id_fkey;

-- ============================================================
-- Step 3: 更新所有 ID
-- ============================================================

-- 3a. 主表主键
UPDATE scripts s SET id = m.new_id FROM uuid_mapping m WHERE s.id = m.old_id;
UPDATE characters c SET id = m.new_id FROM uuid_mapping m WHERE c.id = m.old_id;
UPDATE routes r SET id = m.new_id FROM uuid_mapping m WHERE r.id = m.old_id;

-- 3b. 引用 script_id
UPDATE characters SET script_id = m.new_id FROM uuid_mapping m WHERE script_id = m.old_id;
UPDATE routes SET script_id = m.new_id FROM uuid_mapping m WHERE script_id = m.old_id;
UPDATE game_sessions SET script_id = m.new_id FROM uuid_mapping m WHERE script_id = m.old_id;
UPDATE convergence_points SET script_id = m.new_id FROM uuid_mapping m WHERE script_id = m.old_id;
UPDATE endings SET script_id = m.new_id FROM uuid_mapping m WHERE script_id = m.old_id;
UPDATE free_chat_sessions SET script_id = m.new_id FROM uuid_mapping m WHERE script_id = m.old_id;
UPDATE scenes SET script_id = m.new_id FROM uuid_mapping m WHERE script_id = m.old_id;
UPDATE unlocked_scripts SET script_id = m.new_id FROM uuid_mapping m WHERE script_id = m.old_id;
UPDATE user_dialogue_counts SET script_id = m.new_id FROM uuid_mapping m WHERE script_id = m.old_id;
UPDATE cg_assets SET script_id = m.new_id FROM uuid_mapping m WHERE script_id = m.old_id;

-- 3c. 引用 character_id
UPDATE affection SET character_id = m.new_id FROM uuid_mapping m WHERE character_id = m.old_id;
UPDATE affection_history SET character_id = m.new_id FROM uuid_mapping m WHERE character_id = m.old_id;
UPDATE character_memories SET character_id = m.new_id FROM uuid_mapping m WHERE character_id = m.old_id;
UPDATE character_sprites SET character_id = m.new_id FROM uuid_mapping m WHERE character_id = m.old_id;
UPDATE dialogue_history SET character_id = m.new_id FROM uuid_mapping m WHERE character_id = m.old_id;
UPDATE free_chat_sessions SET character_id = m.new_id FROM uuid_mapping m WHERE character_id = m.old_id;
UPDATE gift_records SET character_id = m.new_id FROM uuid_mapping m WHERE character_id = m.old_id;

-- 3d. 引用 route_id
UPDATE nodes SET route_id = m.new_id FROM uuid_mapping m WHERE route_id = m.old_id;
UPDATE endings SET route_id = m.new_id FROM uuid_mapping m WHERE route_id = m.old_id;
UPDATE game_sessions SET route_id = m.new_id FROM uuid_mapping m WHERE route_id = m.old_id;
UPDATE cg_assets SET route_id = m.new_id FROM uuid_mapping m WHERE route_id = m.old_id;

-- ============================================================
-- Step 4: 重建外键约束
-- ============================================================
ALTER TABLE characters ADD CONSTRAINT characters_script_id_fkey FOREIGN KEY (script_id) REFERENCES scripts(id);
ALTER TABLE routes ADD CONSTRAINT routes_script_id_fkey FOREIGN KEY (script_id) REFERENCES scripts(id);
ALTER TABLE game_sessions ADD CONSTRAINT game_sessions_script_id_fkey FOREIGN KEY (script_id) REFERENCES scripts(id);
ALTER TABLE game_sessions ADD CONSTRAINT game_sessions_route_id_fkey FOREIGN KEY (route_id) REFERENCES routes(id);
ALTER TABLE convergence_points ADD CONSTRAINT convergence_points_script_id_fkey FOREIGN KEY (script_id) REFERENCES scripts(id) ON DELETE CASCADE;
ALTER TABLE endings ADD CONSTRAINT endings_script_id_fkey FOREIGN KEY (script_id) REFERENCES scripts(id);
ALTER TABLE endings ADD CONSTRAINT endings_route_id_fkey FOREIGN KEY (route_id) REFERENCES routes(id);
ALTER TABLE free_chat_sessions ADD CONSTRAINT free_chat_sessions_script_id_fkey FOREIGN KEY (script_id) REFERENCES scripts(id);
ALTER TABLE free_chat_sessions ADD CONSTRAINT free_chat_sessions_character_id_fkey FOREIGN KEY (character_id) REFERENCES characters(id);
ALTER TABLE scenes ADD CONSTRAINT scenes_script_id_fkey FOREIGN KEY (script_id) REFERENCES scripts(id);
ALTER TABLE unlocked_scripts ADD CONSTRAINT unlocked_scripts_script_id_fkey FOREIGN KEY (script_id) REFERENCES scripts(id);
ALTER TABLE user_dialogue_counts ADD CONSTRAINT user_dialogue_counts_script_id_fkey FOREIGN KEY (script_id) REFERENCES scripts(id);
ALTER TABLE cg_assets ADD CONSTRAINT cg_assets_script_id_fkey FOREIGN KEY (script_id) REFERENCES scripts(id);
ALTER TABLE cg_assets ADD CONSTRAINT cg_assets_route_id_fkey FOREIGN KEY (route_id) REFERENCES routes(id);
ALTER TABLE affection ADD CONSTRAINT affection_character_id_fkey FOREIGN KEY (character_id) REFERENCES characters(id);
ALTER TABLE affection_history ADD CONSTRAINT affection_history_character_id_fkey FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE;
ALTER TABLE character_memories ADD CONSTRAINT character_memories_character_id_fkey FOREIGN KEY (character_id) REFERENCES characters(id);
ALTER TABLE character_sprites ADD CONSTRAINT character_sprites_character_id_fkey FOREIGN KEY (character_id) REFERENCES characters(id);
ALTER TABLE dialogue_history ADD CONSTRAINT dialogue_history_character_id_fkey FOREIGN KEY (character_id) REFERENCES characters(id);
ALTER TABLE gift_records ADD CONSTRAINT gift_records_character_id_fkey FOREIGN KEY (character_id) REFERENCES characters(id);
ALTER TABLE nodes ADD CONSTRAINT nodes_route_id_fkey FOREIGN KEY (route_id) REFERENCES routes(id);

-- ============================================================
-- Step 5: 验证
-- ============================================================
SELECT '=== 迁移后验证 ===' as info;
SELECT 'scripts' as table_name, id::text as new_uuid FROM scripts
UNION ALL SELECT 'characters', id::text FROM characters
UNION ALL SELECT 'routes', id::text FROM routes;

-- 检查外键完整性
SELECT '=== 外键完整性检查 ===' as info;
SELECT 'characters.script_id' as fk, COUNT(*) as orphans FROM characters c LEFT JOIN scripts s ON c.script_id = s.id WHERE s.id IS NULL
UNION ALL SELECT 'routes.script_id', COUNT(*) FROM routes r LEFT JOIN scripts s ON r.script_id = s.id WHERE s.id IS NULL
UNION ALL SELECT 'game_sessions.script_id', COUNT(*) FROM game_sessions gs LEFT JOIN scripts s ON gs.script_id = s.id WHERE s.id IS NULL
UNION ALL SELECT 'game_sessions.route_id', COUNT(*) FROM game_sessions gs LEFT JOIN routes r ON gs.route_id = r.id WHERE r.id IS NULL
UNION ALL SELECT 'nodes.route_id', COUNT(*) FROM nodes n LEFT JOIN routes r ON n.route_id = r.id WHERE r.id IS NULL;

COMMIT;
