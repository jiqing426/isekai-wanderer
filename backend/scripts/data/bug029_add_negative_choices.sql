-- BUG-029-001: 补充主剧本负好感度选项
-- 问题：主剧本"星月奇缘"的32个有选项的节点中，只有1个节点有负好感度选项
-- 解决：为主要游戏路径上的节点添加负好感度选项

-- 脚本ID: de1c935a-3e82-4e29-aff9-c69c3a460418 (星月奇缘)
-- 第一章路线ID: a8f3a894-fe57-43e4-b494-0fa38e4a940c

-- 1. 节点 56282db8 (满月之夜竹林初遇) - 添加冷淡回应选项
INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, is_hidden, required_affection, created_at)
VALUES (
    'b0290001-0000-0000-0000-000000000001',
    '56282db8-e475-428c-9e19-9eabb93fc472',
    '你谁啊？大半夜在这里吓人。',
    '6b93f523-54fe-4bfc-815c-1dbf224cd2f2',
    -3,
    false,
    0,
    NOW()
);

-- 2. 节点 75035c78 (仙女话题) - 添加不信任选项
INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, is_hidden, required_affection, created_at)
VALUES (
    'b0290002-0000-0000-0000-000000000002',
    '75035c78-b512-431c-a565-cbc12071e205',
    '别开玩笑了，这一点都不好笑。',
    'a7e0cdd3-bba9-4d46-8d1e-9307f128cf97',
    -2,
    false,
    0,
    NOW()
);

-- 3. 节点 a7e0cdd3 (月亮话题) - 添加敷衍回应选项
INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, is_hidden, required_affection, created_at)
VALUES (
    'b0290003-0000-0000-0000-000000000003',
    'a7e0cdd3-bba9-4d46-8d1e-9307f128cf97',
    '月亮就是月亮，有什么好问的。',
    'ce457b21-5eb9-4cb6-95e9-139815fe6cd0',
    -2,
    false,
    0,
    NOW()
);

-- 4. 节点 ce457b21 (千年孤独话题) - 添加打断选项
INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, is_hidden, required_affection, created_at)
VALUES (
    'b0290004-0000-0000-0000-000000000004',
    'ce457b21-5eb9-4cb6-95e9-139815fe6cd0',
    '行了行了，别卖惨了。',
    '6b93f523-54fe-4bfc-815c-1dbf224cd2f2',
    -3,
    false,
    0,
    NOW()
);

-- 5. 节点 6b93f523 (第一个看见她的人) - 添加质疑选项
INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, is_hidden, required_affection, created_at)
VALUES (
    'b0290005-0000-0000-0000-000000000005',
    '6b93f523-54fe-4bfc-815c-1dbf224cd2f2',
    '这种搭讪方式太老套了。',
    '9704e612-e6f4-4cdb-b059-411eb1d447d4',
    -2,
    false,
    0,
    NOW()
);

-- 6. 节点 9baa8f19 (一千年没人说过这样的话) - 添加冷淡选项
INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, is_hidden, required_affection, created_at)
VALUES (
    'b0290006-0000-0000-0000-000000000006',
    '9baa8f19-9c5f-4687-b53f-64aeeacc89be',
    '...（沉默不语）',
    '9704e612-e6f4-4cdb-b059-411eb1d447d4',
    -1,
    false,
    0,
    NOW()
);

-- 7. 节点 9704e612 (朋友话题) - 添加拒绝选项
INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, is_hidden, required_affection, created_at)
VALUES (
    'b0290007-0000-0000-0000-000000000007',
    '9704e612-e6f4-4cdb-b059-411eb1d447d4',
    '我只是路过，别想太多。',
    '13b24735-e133-4777-99cc-935bcad338c5',
    -2,
    false,
    0,
    NOW()
);

-- 8. 节点 147262e4 (月宫话题) - 添加不想继续选项
INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, is_hidden, required_affection, created_at)
VALUES (
    'b0290008-0000-0000-0000-000000000008',
    '147262e4-a47c-4dbe-b78c-2280dc95541a',
    '听起来好危险，我想回去了。',
    '13b24735-e133-4777-99cc-935bcad338c5',
    -2,
    false,
    0,
    NOW()
);

-- 验证插入结果
SELECT '新增负好感度选项统计' as info, COUNT(*) as count
FROM node_choices
WHERE id::text LIKE 'b029%' AND affection_delta < 0;
