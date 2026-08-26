-- BUG-029-001: 补充第二章和第三章负好感度选项
-- 第二章路线ID: 52e3c109-d95e-4e28-992b-d112a5422a48
-- 第三章路线ID: 78a05749-9b17-41d8-bef3-31e848da123e

-- ============ 第二章：星辰之约 ============

-- 1. 节点 1515de6e (天文社活动室) - 添加冷淡选项
INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, is_hidden, required_affection, created_at)
VALUES (
    'b0290009-0000-0000-0000-000000000009',
    '1515de6e-de3f-422f-ab52-08e9ab9f9872',
    '没什么，我只是随便看看。',
    '5121f0a7-b797-4841-8535-c022baa3d540',
    -2,
    false,
    0,
    NOW()
);

-- 2. 节点 5121f0a7 (最喜欢的星星) - 添加敷衍选项
INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, is_hidden, required_affection, created_at)
VALUES (
    'b029000a-0000-0000-0000-00000000000a',
    '5121f0a7-b797-4841-8535-c022baa3d540',
    '星星不就是星星吗，有什么区别。',
    '329f80d1-d7fd-401e-9297-09d8f1a98957',
    -2,
    false,
    0,
    NOW()
);

-- 3. 节点 329f80d1 (天狼星话题) - 添加不感兴趣选项
INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, is_hidden, required_affection, created_at)
VALUES (
    'b029000b-0000-0000-0000-00000000000b',
    '329f80d1-d7fd-401e-9297-09d8f1a98957',
    '我对天文不太感兴趣，我们聊点别的吧。',
    '06195fc7-d860-4b01-9d0a-52dc2e0bfbcf',
    -3,
    false,
    0,
    NOW()
);

-- 4. 节点 06195fc7 (潮汐锁定话题) - 添加直男选项
INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, is_hidden, required_affection, created_at)
VALUES (
    'b029000c-0000-0000-0000-00000000000c',
    '06195fc7-d860-4b01-9d0a-52dc2e0bfbcf',
    '听起来好复杂，我不太懂。',
    'a40b1f8c-d353-4b76-81db-c4e512c9c979',
    -1,
    false,
    0,
    NOW()
);

-- 5. 节点 a40b1f8c (流星雨邀请) - 添加拒绝选项
INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, is_hidden, required_affection, created_at)
VALUES (
    'b029000d-0000-0000-0000-00000000000d',
    'a40b1f8c-d353-4b76-81db-c4e512c9c979',
    '不了，我最近比较忙。',
    '583300d8-bea4-4557-901c-01d0daae3ad2',
    -3,
    false,
    0,
    NOW()
);

-- 6. 节点 583300d8 (天文台约会) - 添加冷淡选项
INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, is_hidden, required_affection, created_at)
VALUES (
    'b029000e-0000-0000-0000-00000000000e',
    '583300d8-bea4-4557-901c-01d0daae3ad2',
    '...（沉默地看星星）',
    '356ea631-c284-41d2-8aa6-5a3284f8ccc6',
    -2,
    false,
    0,
    NOW()
);

-- 7. 节点 356ea631 (小时候觉得星星不会背叛) - 添加敷衍选项
INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, is_hidden, required_affection, created_at)
VALUES (
    'b029000f-0000-0000-0000-00000000000f',
    '356ea631-c284-41d2-8aa6-5a3284f8ccc6',
    '嗯...是吗。',
    '9f55245e-02f3-43b7-981d-2f4106b25055',
    -1,
    false,
    0,
    NOW()
);

-- 8. 节点 9f55245e (流星许愿) - 添加不解风情选项
INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, is_hidden, required_affection, created_at)
VALUES (
    'b0290010-0000-0000-0000-000000000010',
    '9f55245e-02f3-43b7-981d-2f4106b25055',
    '许愿有什么用，都是骗人的。',
    '179841d1-b659-4041-8eac-d4ca20b9b439',
    -3,
    false,
    0,
    NOW()
);

-- 9. 节点 179841d1 (双星系统话题) - 添加直男选项
INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, is_hidden, required_affection, created_at)
VALUES (
    'b0290011-0000-0000-0000-000000000011',
    '179841d1-b659-4041-8eac-d4ca20b9b439',
    '所以你想说什么？',
    'be0f73cd-70a4-429c-85df-76abd0db8e5d',
    -2,
    false,
    0,
    NOW()
);

-- ============ 第三章：命运交织 ============

-- 10. 节点 f5602702 (辉夜有话要说) - 添加不耐烦选项
INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, is_hidden, required_affection, created_at)
VALUES (
    'b0290012-0000-0000-0000-000000000012',
    'f5602702-142e-4691-b725-ae60ba3dfefe',
    '有话快说，别磨磨蹭蹭的。',
    '1c99084f-27d0-4773-9fa6-dbb3f3ac5330',
    -3,
    false,
    0,
    NOW()
);

-- 11. 节点 1c99084f (月宫公主身份) - 添加质疑选项
INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, is_hidden, required_affection, created_at)
VALUES (
    'b0290013-0000-0000-0000-000000000013',
    '1c99084f-27d0-4773-9fa6-dbb3f3ac5330',
    '你在编故事吧？',
    '6075a5fb-5694-444d-a6da-379132dc5142',
    -3,
    false,
    0,
    NOW()
);

-- 12. 节点 6075a5fb (一千年前的凡人) - 添加嫉妒选项
INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, is_hidden, required_affection, created_at)
VALUES (
    'b0290014-0000-0000-0000-000000000014',
    '6075a5fb-5694-444d-a6da-379132dc5142',
    '所以我是替代品？',
    '6883c75d-514a-4354-ac91-38c67383a50c',
    -2,
    false,
    0,
    NOW()
);

-- 13. 节点 6883c75d (月宫要召她回去) - 添加逃避选项
INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, is_hidden, required_affection, created_at)
VALUES (
    'b0290015-0000-0000-0000-000000000015',
    '6883c75d-514a-4354-ac91-38c67383a50c',
    '那...我们还是保持距离吧。',
    'f2069cc8-ce36-4ad9-9ce7-f41af5c1918e',
    -3,
    false,
    0,
    NOW()
);

-- 14. 节点 f2069cc8 (留在人间会变普通人) - 添加犹豫选项
INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, is_hidden, required_affection, created_at)
VALUES (
    'b0290016-0000-0000-0000-000000000016',
    'f2069cc8-ce36-4ad9-9ce7-f41af5c1918e',
    '变成普通人...那还是算了吧。',
    'def713e1-60d8-4887-a14b-31848e96c9a6',
    -2,
    false,
    0,
    NOW()
);

-- 15. 节点 def713e1 (不再让你一个人) - 添加冷淡选项
INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, is_hidden, required_affection, created_at)
VALUES (
    'b0290017-0000-0000-0000-000000000017',
    'def713e1-60d8-4887-a14b-31848e96c9a6',
    '...（没有回应）',
    '37be98a9-3106-46ac-a88e-45cf54a5c2b6',
    -2,
    false,
    0,
    NOW()
);

-- 16. 节点 37be98a9 (桂花树镜子话题) - 添加敷衍选项
INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, is_hidden, required_affection, created_at)
VALUES (
    'b0290018-0000-0000-0000-000000000018',
    '37be98a9-3106-46ac-a88e-45cf54a5c2b6',
    '听起来好麻烦。',
    '5c0ce38a-3f26-4bf6-811f-7ac31f2410af',
    -2,
    false,
    0,
    NOW()
);

-- 17. 节点 5c0ce38a (确定留在人间) - 添加犹豫选项
INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, is_hidden, required_affection, created_at)
VALUES (
    'b0290019-0000-0000-0000-000000000019',
    '5c0ce38a-3f26-4bf6-811f-7ac31f2410af',
    '你...确定不会后悔吗？',
    '00b96aae-0fbc-4409-916e-d76c5ead2697',
    -1,
    false,
    0,
    NOW()
);

-- 18. 节点 00b96aae (什么请求) - 添加拒绝选项
INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, is_hidden, required_affection, created_at)
VALUES (
    'b029001a-0000-0000-0000-00000000001a',
    '00b96aae-0fbc-4409-916e-d76c5ead2697',
    '抱歉，我做不到。',
    'af29693f-7da4-4fcf-a625-bb28dfdd0e68',
    -2,
    false,
    0,
    NOW()
);

-- 验证插入结果
SELECT '新增第二三章负好感度选项统计' as info, COUNT(*) as count
FROM node_choices
WHERE id::text BETWEEN 'b0290009-0000-0000-0000-000000000009' AND 'b029001a-0000-0000-0000-00000000001a'
AND affection_delta < 0;
