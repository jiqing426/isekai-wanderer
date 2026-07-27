-- Seed nodes + choices for 6 empty routes
-- Each route: 6 nodes + 6 choices
-- Run: docker compose exec -T db psql -U isekai -d isekai < backend/scripts/seed_empty_routes.sql

BEGIN;

-- ============================================================
-- Route 1: 双星线：命运交织 (星月奇缘 / 沈星澜)
-- ============================================================
DO $$
DECLARE
    v_rid UUID := '8ff72661-2954-4665-a611-5a63ce758996';
    v_cid UUID := '900a9744-04ca-4c6b-a276-c79595218672';
    v_cn  TEXT := '沈星澜';
    v_o UUID; v_f UUID; v_c UUID; v_g UUID; v_n UUID; v_b UUID;
    v_cnt INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_cnt FROM nodes WHERE route_id = v_rid;
    IF v_cnt > 0 THEN RAISE NOTICE 'Route 1 skipped (% nodes)', v_cnt; RETURN; END IF;
    v_o := gen_random_uuid(); v_f := gen_random_uuid(); v_c := gen_random_uuid();
    v_g := gen_random_uuid(); v_n := gen_random_uuid(); v_b := gen_random_uuid();

    INSERT INTO nodes (id, route_id, parent_id, node_type, content, created_at) VALUES
    (v_o, v_rid, NULL, 'preset', json_build_object('character',v_cn,'character_id',v_cid::text,'text','天文台的穹顶下，两台望远镜并排指向夜空。沈星澜站在旁边，手指无意识地摩挲着调焦旋钮。「你来了...今晚的双星系统特别亮，我本来想一个人观测的。」','emotion','curious','background','observatory_night','scene','opening'), NOW()),
    (v_f, v_rid, v_o, 'preset', json_build_object('character',v_cn,'character_id',v_cid::text,'text','「你知道吗？天文学里有个概念叫潮汐锁定——两颗星互相吸引，最终永远面向彼此。」她的声音变得轻柔，「我觉得...人和人之间也有类似的引力。」','emotion','warm','background','starry_sky','scene','friendly_path'), NOW()),
    (v_c, v_rid, v_o, 'preset', json_build_object('character',v_cn,'character_id',v_cid::text,'text','「...抱歉，我不该说这些。」她转过身去，目光重新落在目镜上，「你如果不感兴趣的话，可以去看看楼下的展览。我一个人习惯。」','emotion','disappointed','background','observatory_night','scene','cold_path'), NOW()),
    (v_g, v_rid, v_f, 'ending', json_build_object('character',v_cn,'character_id',v_cid::text,'text','「太好了！那...明天同一时间？」她笑着从抽屉里拿出第二把钥匙，「这是天文台的备用钥匙。以后你可以随时来。」星光洒在她微微泛红的脸上。','emotion','happy','background','moonlit_sky','scene','good_ending','ending_type','good','is_ending',true), NOW()),
    (v_n, v_rid, v_f, 'ending', json_build_object('character',v_cn,'character_id',v_cid::text,'text','「嗯...今晚的观测就到这里吧。」她收拾好器材，礼貌地点了点头，「谢谢你陪我。下次...如果有机会的话。」月光下她的背影有些孤单。','emotion','bittersweet','background','observatory_night','scene','normal_ending','ending_type','normal','is_ending',true), NOW()),
    (v_b, v_rid, v_c, 'ending', json_build_object('character',v_cn,'character_id',v_cid::text,'text','「我明白了。」她没有回头，声音平静得像在播报天气，「门在左边，不送。」穹顶重新合上，隔绝了星光和你。','emotion','sad','background','observatory_night','scene','bad_ending','ending_type','bad','is_ending',true), NOW());

    INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, hint, is_hidden, created_at) VALUES
    (gen_random_uuid(), v_o, '我也想一起看双星！', v_f, 5, '表达兴趣', false, NOW()),
    (gen_random_uuid(), v_o, '我对星星不太懂...', v_c, -3, '保持距离', false, NOW()),
    (gen_random_uuid(), v_f, '明天我还想来！', v_g, 8, '约定下次', false, NOW()),
    (gen_random_uuid(), v_f, '今晚很开心，我先走了', v_n, 2, '礼貌告别', false, NOW()),
    (gen_random_uuid(), v_c, '对不起，能再讲讲吗？', v_n, -1, '犹豫挽回', false, NOW()),
    (gen_random_uuid(), v_c, '那我先走了', v_b, -5, '转身离开', false, NOW());
    RAISE NOTICE 'Seeded route 1: 双星线';
END $$;

-- ============================================================
-- Route 2: 星澜线：星辰之约 (星月奇缘 / 沈星澜)
-- ============================================================
DO $$
DECLARE
    v_rid UUID := 'a41282b0-c27d-4868-aa1c-88ba08d50040';
    v_cid UUID := '900a9744-04ca-4c6b-a276-c79595218672';
    v_cn  TEXT := '沈星澜';
    v_o UUID; v_f UUID; v_c UUID; v_g UUID; v_n UUID; v_b UUID;
    v_cnt INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_cnt FROM nodes WHERE route_id = v_rid;
    IF v_cnt > 0 THEN RAISE NOTICE 'Route 2 skipped (% nodes)', v_cnt; RETURN; END IF;
    v_o := gen_random_uuid(); v_f := gen_random_uuid(); v_c := gen_random_uuid();
    v_g := gen_random_uuid(); v_n := gen_random_uuid(); v_b := gen_random_uuid();

    INSERT INTO nodes (id, route_id, parent_id, node_type, content, created_at) VALUES
    (v_o, v_rid, NULL, 'preset', json_build_object('character',v_cn,'character_id',v_cid::text,'text','大学天文社的活动室里贴满了星图。沈星澜正踮着脚把一张新的星座图钉上墙，听到开门声差点从椅子上摔下来。「你...你是新社员？我还以为没人会来呢。」','emotion','surprised','background','club_room','scene','opening'), NOW()),
    (v_f, v_rid, v_o, 'preset', json_build_object('character',v_cn,'character_id',v_cid::text,'text','「你看这颗——天蝎座的心宿二，古代叫它大火。」她的手指在星图上划过，「每个文明都给星星起名字，但星星不在乎。它们只是燃烧。」她忽然看向你，「但有人愿意一起看，就不一样了。」','emotion','passionate','background','starry_sky','scene','friendly_path'), NOW()),
    (v_c, v_rid, v_o, 'preset', json_build_object('character',v_cn,'character_id',v_cid::text,'text','「也是...天文社本来就冷门。」她默默把椅子收好，声音低了下去，「我以为至少会有一个人对星星感兴趣的。」','emotion','dejected','background','club_room','scene','cold_path'), NOW()),
    (v_g, v_rid, v_f, 'ending', json_build_object('character',v_cn,'character_id',v_cid::text,'text','「真的？！」她的眼睛亮得像星星，「那...我任命你为副社长！不，共同社长！」她拉起你的手，「走，去天台，今晚有英仙座流星雨！」','emotion','ecstatic','background','rooftop_stars','scene','good_ending','ending_type','good','is_ending',true), NOW()),
    (v_n, v_rid, v_f, 'ending', json_build_object('character',v_cn,'character_id',v_cid::text,'text','「这样啊...那欢迎随时来坐坐。」她递给你一杯热可可，「活动室的门永远开着。」你喝着可可看她继续整理星图，感觉这个安静的角落也不坏。','emotion','gentle','background','club_room','scene','normal_ending','ending_type','normal','is_ending',true), NOW()),
    (v_b, v_rid, v_c, 'ending', json_build_object('character',v_cn,'character_id',v_cid::text,'text','「好吧。」她把最后一张星图钉好，退后两步看了看，然后头也不回地说，「门带上，谢谢。」活动室的灯灭了。','emotion','resigned','background','club_room_dark','scene','bad_ending','ending_type','bad','is_ending',true), NOW());

    INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, hint, is_hidden, created_at) VALUES
    (gen_random_uuid(), v_o, '这些星图好酷！能教我吗？', v_f, 5, '表达热情', false, NOW()),
    (gen_random_uuid(), v_o, '我只是路过看看...', v_c, -3, '随意态度', false, NOW()),
    (gen_random_uuid(), v_f, '我想加入天文社！', v_g, 8, '正式加入', false, NOW()),
    (gen_random_uuid(), v_f, '当观众也挺有趣的', v_n, 2, '保持距离', false, NOW()),
    (gen_random_uuid(), v_c, '等等，我改主意了', v_n, -1, '犹豫挽回', false, NOW()),
    (gen_random_uuid(), v_c, '那我走了', v_b, -5, '直接离开', false, NOW());
    RAISE NOTICE 'Seeded route 2: 星澜线';
END $$;

-- ============================================================
-- Route 3: 辉夜线：月影传说 (星月奇缘 / 辉夜)
-- ============================================================
DO $$
DECLARE
    v_rid UUID := '90cf1451-80db-45a2-968e-aa84507bb854';
    v_cid UUID := '900a9744-04ca-4c6b-a276-c79595218672';
    v_cn  TEXT := '辉夜';
    v_o UUID; v_f UUID; v_c UUID; v_g UUID; v_n UUID; v_b UUID;
    v_cnt INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_cnt FROM nodes WHERE route_id = v_rid;
    IF v_cnt > 0 THEN RAISE NOTICE 'Route 3 skipped (% nodes)', v_cnt; RETURN; END IF;
    v_o := gen_random_uuid(); v_f := gen_random_uuid(); v_c := gen_random_uuid();
    v_g := gen_random_uuid(); v_n := gen_random_uuid(); v_b := gen_random_uuid();

    INSERT INTO nodes (id, route_id, parent_id, node_type, content, created_at) VALUES
    (v_o, v_rid, NULL, 'preset', json_build_object('character',v_cn,'character_id',v_cid::text,'text','满月之夜，你在神社后面的竹林里发现了一个穿着白色和服的少女。她赤足站在月光下，长发如瀑布般垂落。「...你能看到我？」她的声音像月光一样清冷，「已经很久没有人能看到我了。」','emotion','mysterious','background','bamboo_forest_night','scene','opening'), NOW()),
    (v_f, v_rid, v_o, 'preset', json_build_object('character',v_cn,'character_id',v_cid::text,'text','「千年前，我因为犯了错被贬到人间。每个月圆之夜才能现出形体。」她伸出手接住一片竹叶，「我看过无数个满月，但从来没有人陪我一起看过。」月光在她指尖流淌。','emotion','melancholic','background','moonlit_clearing','scene','friendly_path'), NOW()),
    (v_c, v_rid, v_o, 'preset', json_build_object('character',v_cn,'character_id',v_cid::text,'text','「...果然，人类都是一样的。」她的身影开始变得透明，「害怕未知的东西，然后转身逃走。」竹林恢复了寂静，只有风吹竹叶的沙沙声。','emotion','cold','background','bamboo_forest_night','scene','cold_path'), NOW()),
    (v_g, v_rid, v_f, 'ending', json_build_object('character',v_cn,'character_id',v_cid::text,'text','「你...愿意陪我？」她的眼中映着月光，第一次露出了笑容。竹林中浮现出无数光点，像萤火虫，又像星辰。「那让我给你看一样东西——只有人类朋友才能看到的。」她牵起你的手，月光化为通往天宫的阶梯。','emotion','joyful','background','celestial_palace','scene','good_ending','ending_type','good','is_ending',true), NOW()),
    (v_n, v_rid, v_f, 'ending', json_build_object('character',v_cn,'character_id',v_cid::text,'text','「月亮要落了。」她的身影在晨曦中渐渐淡去，「下次满月...如果你还记得来这里的话。」竹林恢复了寻常模样，但你手心还残留着一丝凉意。','emotion','wistful','background','bamboo_forest_dawn','scene','normal_ending','ending_type','normal','is_ending',true), NOW()),
    (v_b, v_rid, v_c, 'ending', json_build_object('character',v_cn,'character_id',v_cid::text,'text','她消失了。竹林恢复了寂静，月光冷冷地照着地面。你低头发现脚边有一根白色的羽毛，在微风中轻轻颤动。也许...那只是一个梦。','emotion','lonely','background','bamboo_forest_night','scene','bad_ending','ending_type','bad','is_ending',true), NOW());

    INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, hint, is_hidden, created_at) VALUES
    (gen_random_uuid(), v_o, '你是谁？我能帮你什么？', v_f, 5, '善意接近', false, NOW()),
    (gen_random_uuid(), v_o, '你...你是鬼吗？！', v_c, -3, '恐惧反应', false, NOW()),
    (gen_random_uuid(), v_f, '我愿意陪你到月亮落下', v_g, 8, '陪伴到底', false, NOW()),
    (gen_random_uuid(), v_f, '我需要回去了，但我会记住你', v_n, 2, '温柔告别', false, NOW()),
    (gen_random_uuid(), v_c, '等等！我不是害怕...', v_n, -1, '犹豫挽回', false, NOW()),
    (gen_random_uuid(), v_c, '...（沉默）', v_b, -5, '无言以对', false, NOW());
    RAISE NOTICE 'Seeded route 3: 辉夜线';
END $$;

-- ============================================================
-- Route 4: 月夜线：静谧之恋 (樱花恋曲 / 月夜)
-- ============================================================
DO $$
DECLARE
    v_rid UUID := '89424ab0-74d6-4fad-be8c-d2fd911f7323';
    v_cid UUID := '6982c07f-bb69-4abe-9919-f54ea94297a4';
    v_cn  TEXT := '月夜';
    v_o UUID; v_f UUID; v_c UUID; v_g UUID; v_n UUID; v_b UUID;
    v_cnt INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_cnt FROM nodes WHERE route_id = v_rid;
    IF v_cnt > 0 THEN RAISE NOTICE 'Route 4 skipped (% nodes)', v_cnt; RETURN; END IF;
    v_o := gen_random_uuid(); v_f := gen_random_uuid(); v_c := gen_random_uuid();
    v_g := gen_random_uuid(); v_n := gen_random_uuid(); v_b := gen_random_uuid();

    INSERT INTO nodes (id, route_id, parent_id, node_type, content, created_at) VALUES
    (v_o, v_rid, NULL, 'preset', json_build_object('character',v_cn,'character_id',v_cid::text,'text','深夜的校园花园里，你看到一个坐在长椅上的女孩。月光洒在她的银色短发上，她正对着一本旧日记发呆。「...啊，抱歉，我不知道这里有人。」她合上日记，露出一个温柔的微笑，「月光这么美，你也是来看月亮的吗？」','emotion','gentle','background','garden_night','scene','opening'), NOW()),
    (v_f, v_rid, v_o, 'preset', json_build_object('character',v_cn,'character_id',v_cid::text,'text','「这本日记是我祖母留下的。」她翻开一页，「她说每个月的满月之夜，花园里的玫瑰会发出淡淡的香气。我以前不信...但今晚，好像真的闻到了。」夜风中确实飘来若有若无的花香。','emotion','nostalgic','background','rose_garden_moonlight','scene','friendly_path'), NOW()),
    (v_c, v_rid, v_o, 'preset', json_build_object('character',v_cn,'character_id',v_cid::text,'text','「...也是，深夜的花园确实不适合陌生人。」她把日记放回包里，站起身来，「打扰了，我先走了。」月光下她的表情有些落寞。','emotion','shy','background','garden_night','scene','cold_path'), NOW()),
    (v_g, v_rid, v_f, 'ending', json_build_object('character',v_cn,'character_id',v_cid::text,'text','「真的吗？那下个月圆之夜...我们还在这里见面？」她从长椅上拿起一朵白玫瑰递给你，「这是花园的礼物。」她的笑容在月光下格外温柔，「我叫做月夜，请记住这个名字。」','emotion','happy','background','rose_garden_moonlight','scene','good_ending','ending_type','good','is_ending',true), NOW()),
    (v_n, v_rid, v_f, 'ending', json_build_object('character',v_cn,'character_id',v_cid::text,'text','「夜深了，我该回去了。」她轻轻站起来，拍了拍裙子上的花瓣，「谢谢你今晚的陪伴。虽然只是短暂的相遇...但月光会记住的。」','emotion','peaceful','background','garden_night','scene','normal_ending','ending_type','normal','is_ending',true), NOW()),
    (v_b, v_rid, v_c, 'ending', json_build_object('character',v_cn,'character_id',v_cid::text,'text','她走了，脚步声在石板路上渐渐消失。花园重新安静下来，只有月光和玫瑰。你低头看到长椅上落着一片花瓣，拿起来闻了闻——确实有淡淡的香气。','emotion','melancholic','background','garden_night','scene','bad_ending','ending_type','bad','is_ending',true), NOW());

    INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, hint, is_hidden, created_at) VALUES
    (gen_random_uuid(), v_o, '这里的月光确实很美', v_f, 5, '共鸣', false, NOW()),
    (gen_random_uuid(), v_o, '这么晚了，一个人安全吗？', v_c, -3, '过度关心', false, NOW()),
    (gen_random_uuid(), v_f, '下个月我还想来', v_g, 8, '约定再会', false, NOW()),
    (gen_random_uuid(), v_f, '今晚很美好，晚安', v_n, 2, '温柔告别', false, NOW()),
    (gen_random_uuid(), v_c, '请等一下！', v_n, -1, '挽留', false, NOW()),
    (gen_random_uuid(), v_c, '...（让她离开）', v_b, -5, '沉默', false, NOW());
    RAISE NOTICE 'Seeded route 4: 月夜线';
END $$;

-- ============================================================
-- Route 5: 阳菜线：夏日恋歌 (樱花恋曲 / 阳菜)
-- ============================================================
DO $$
DECLARE
    v_rid UUID := '55761d28-289f-445b-82ef-fa9709d5d507';
    v_cid UUID := '6982c07f-bb69-4abe-9919-f54ea94297a4';
    v_cn  TEXT := '阳菜';
    v_o UUID; v_f UUID; v_c UUID; v_g UUID; v_n UUID; v_b UUID;
    v_cnt INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_cnt FROM nodes WHERE route_id = v_rid;
    IF v_cnt > 0 THEN RAISE NOTICE 'Route 5 skipped (% nodes)', v_cnt; RETURN; END IF;
    v_o := gen_random_uuid(); v_f := gen_random_uuid(); v_c := gen_random_uuid();
    v_g := gen_random_uuid(); v_n := gen_random_uuid(); v_b := gen_random_uuid();

    INSERT INTO nodes (id, route_id, parent_id, node_type, content, created_at) VALUES
    (v_o, v_rid, NULL, 'preset', json_build_object('character',v_cn,'character_id',v_cid::text,'text','夏日祭典的夜晚，你在苹果糖摊位前遇到了一个穿着浴衣的女孩。她正踮着脚够最高处的那个苹果糖，回头看到你时露出灿烂的笑容。「嘿！能帮我拿那个吗？作为回报，我请你吃章鱼烧！」','emotion','cheerful','background','festival_night','scene','opening'), NOW()),
    (v_f, v_rid, v_o, 'preset', json_build_object('character',v_cn,'character_id',v_cid::text,'text','「你知道吗？我每年祭典都来，但总是一个人。」她咬着章鱼烧，眼睛亮晶晶的，「今年不一样！有人帮我拿苹果糖，还有人陪我逛。」远处传来烟花的声音，「啊！烟花要开始了！快去那边！」','emotion','excited','background','festival_fireworks','scene','friendly_path'), NOW()),
    (v_c, v_rid, v_o, 'preset', json_build_object('character',v_cn,'character_id',v_cid::text,'text','「啊...好吧。」她放下够苹果糖的手，笑容淡了一些，「那我自己来吧。祭典嘛，一个人也挺好的！」她转身走向人群，浴衣的裙摆轻轻摆动。','emotion','disappointed','background','festival_night','scene','cold_path'), NOW()),
    (v_g, v_rid, v_f, 'ending', json_build_object('character',v_cn,'character_id',v_cid::text,'text','「太棒了！」她拉着你的手跑向高处，烟花在头顶绽放。「许个愿吧！」她闭上眼睛，然后偷偷睁开一只眼看你，「我许的愿是...明年祭典还能遇到你！」','emotion','ecstatic','background','fireworks_sky','scene','good_ending','ending_type','good','is_ending',true), NOW()),
    (v_n, v_rid, v_f, 'ending', json_build_object('character',v_cn,'character_id',v_cid::text,'text','「烟花好美啊...」她靠在栏杆上，轻声说，「谢谢你今晚的陪伴。虽然祭典快结束了，但今天很开心。」她递给你一根新的苹果糖，「下次再见！」','emotion','warm','background','festival_fireworks','scene','normal_ending','ending_type','normal','is_ending',true), NOW()),
    (v_b, v_rid, v_c, 'ending', json_build_object('character',v_cn,'character_id',v_cid::text,'text','她走了，消失在熙攘的人群中。你手里还拿着那个苹果糖，咬了一口——很甜，但总觉得少了什么。远处烟花还在绽放，但好像没有刚才那么亮了。','emotion','lonely','background','festival_night','scene','bad_ending','ending_type','bad','is_ending',true), NOW());

    INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, hint, is_hidden, created_at) VALUES
    (gen_random_uuid(), v_o, '当然！我帮你拿', v_f, 5, '热心帮助', false, NOW()),
    (gen_random_uuid(), v_o, '你自己拿不到吗？', v_c, -3, '冷淡回应', false, NOW()),
    (gen_random_uuid(), v_f, '明年我还来陪你！', v_g, 8, '约定明年', false, NOW()),
    (gen_random_uuid(), v_f, '今晚很开心，我先走了', v_n, 2, '友好告别', false, NOW()),
    (gen_random_uuid(), v_c, '等等，我开玩笑的！', v_n, -1, '后悔了', false, NOW()),
    (gen_random_uuid(), v_c, '...（看着她离开）', v_b, -5, '无动于衷', false, NOW());
    RAISE NOTICE 'Seeded route 5: 阳菜线';
END $$;

-- ============================================================
-- Route 6: 雪乃线：樱花树下的约定 (樱花恋曲 / 雪乃)
-- ============================================================
DO $$
DECLARE
    v_rid UUID := '8bb89d32-d99e-41ee-8a93-33b1f36ff3ee';
    v_cid UUID := '6982c07f-bb69-4abe-9919-f54ea94297a4';
    v_cn  TEXT := '雪乃';
    v_o UUID; v_f UUID; v_c UUID; v_g UUID; v_n UUID; v_b UUID;
    v_cnt INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_cnt FROM nodes WHERE route_id = v_rid;
    IF v_cnt > 0 THEN RAISE NOTICE 'Route 6 skipped (% nodes)', v_cnt; RETURN; END IF;
    v_o := gen_random_uuid(); v_f := gen_random_uuid(); v_c := gen_random_uuid();
    v_g := gen_random_uuid(); v_n := gen_random_uuid(); v_b := gen_random_uuid();

    INSERT INTO nodes (id, route_id, parent_id, node_type, content, created_at) VALUES
    (v_o, v_rid, NULL, 'preset', json_build_object('character',v_cn,'character_id',v_cid::text,'text','大学图书馆的角落里，一个戴着眼镜的女生正专注地翻阅一本厚重的诗集。窗外飘着细雪，她抬头看到你时微微一愣。「...你也是来避雪的吗？」她合上书，封面写着《冬之短歌》。「这首诗让我想起了一个约定。」','emotion','quiet','background','library_window','scene','opening'), NOW()),
    (v_f, v_rid, v_o, 'preset', json_build_object('character',v_cn,'character_id',v_cid::text,'text','「小时候，我和姐姐在樱花树下约定，每年初雪的时候都要读一首诗给她听。」她的声音很轻，像怕惊扰了什么，「但后来她搬走了...这个约定就只剩下我一个人记得。」窗外的雪下得更大了。','emotion','nostalgic','background','library_snowfall','scene','friendly_path'), NOW()),
    (v_c, v_rid, v_o, 'preset', json_build_object('character',v_cn,'character_id',v_cid::text,'text','「...抱歉，说了些奇怪的话。」她重新戴上眼镜，低头翻书，「你如果不感兴趣的话，那边还有空位。」图书馆恢复了安静，只有翻书的沙沙声。','emotion','reserved','background','library_window','scene','cold_path'), NOW()),
    (v_g, v_rid, v_f, 'ending', json_build_object('character',v_cn,'character_id',v_cid::text,'text','「你...愿意听我读诗吗？」她摘下眼镜，眼中有一丝从未有过的光亮，「这首《雪之约定》——初雪落下时，愿有人共读一页。也许...这个约定不再只是一个人的了。」她微微一笑，窗外的雪映着暖光。','emotion','hopeful','background','library_warmth','scene','good_ending','ending_type','good','is_ending',true), NOW()),
    (v_n, v_rid, v_f, 'ending', json_build_object('character',v_cn,'character_id',v_cid::text,'text','「雪好像停了。」她看了看窗外，把书放回书架，「谢谢你听我说话。虽然只是关于一首诗的闲谈...但有人愿意听，就很好了。」她轻轻点了点头，重新投入到书本中。','emotion','content','background','library_window','scene','normal_ending','ending_type','normal','is_ending',true), NOW()),
    (v_b, v_rid, v_c, 'ending', json_build_object('character',v_cn,'character_id',v_cid::text,'text','她没有再抬头。你走出图书馆时回头看了一眼——她依然坐在那个角落，窗外的雪已经停了。桌上那本《冬之短歌》翻到了某一页，你看不清写了什么。','emotion','melancholic','background','library_snowfall','scene','bad_ending','ending_type','bad','is_ending',true), NOW());

    INSERT INTO node_choices (id, node_id, text, next_node_id, affection_delta, hint, is_hidden, created_at) VALUES
    (gen_random_uuid(), v_o, '什么约定？能告诉我吗？', v_f, 5, '好奇倾听', false, NOW()),
    (gen_random_uuid(), v_o, '我在找座位，打扰了', v_c, -3, '无意停留', false, NOW()),
    (gen_random_uuid(), v_f, '以后我可以陪你读诗', v_g, 8, '许下约定', false, NOW()),
    (gen_random_uuid(), v_f, '这首诗真美，我先走了', v_n, 2, '欣赏告别', false, NOW()),
    (gen_random_uuid(), v_c, '其实我想听听那个故事', v_n, -1, '犹豫挽回', false, NOW()),
    (gen_random_uuid(), v_c, '...（安静离开）', v_b, -5, '默默离开', false, NOW());
    RAISE NOTICE 'Seeded route 6: 雪乃线';
END $$;

COMMIT;
