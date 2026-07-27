#!/usr/bin/env python3
"""
CR-018 修复：重写「星辰之约」剧本种子数据

问题：
1. 旧数据只有 2 轮对话就到 ending（太短）
2. 新路线（林辰线/流星线/银河线）节点全是占位符，parent_id=NULL，无 choices 连接
3. cg_trigger/fixed_scene 等节点 content 为空

修复：
1. 删除旧的占位符节点
2. 为每条路线创建完整的节点树（5-8 层深度）
3. 正确设置 parent_id 和 node_choices
4. 在关键节点添加 cg_trigger 和 converge_node 的解锁内容
"""

import asyncio
import uuid
from pathlib import Path
import sys

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text as sa_text
from app.core.database import async_session_factory
from app.models.script import Script, Route, Node, NodeChoice, Character

# ─── 固定 UUID ───────────────────────────────────────────────────────────────

SCRIPT_ID = uuid.UUID("e56ca348-cc08-45f2-a6fa-baa4c725d192")
CHARACTER_ID = uuid.UUID("22222222-2222-2222-2222-222222222222")

# 路线 UUID
ROUTE_STAR = uuid.UUID("5a24665f-67d9-420e-afa9-dba4a0ba8b5c")
ROUTE_LINCHEN = uuid.UUID("9a662bb7-a4d2-43d4-892d-bb8841b50961")
ROUTE_METEOR = uuid.UUID("6b1a1b14-1db2-43e0-95ad-8fae25c5d841")
ROUTE_GALAXY = uuid.UUID("2cfff4ef-5dd2-41e7-a3aa-d0adea049544")


async def seed():
    async with async_session_factory() as db:
        print("🧹 清理旧数据...")
        # 清理所有关联数据（按外键依赖顺序）
        # 先清理 game_sessions 的所有依赖
        await db.execute(sa_text("DELETE FROM character_memories WHERE source_session_id IN (SELECT id FROM game_sessions WHERE script_id = :sid)"), {"sid": SCRIPT_ID})
        await db.execute(sa_text("DELETE FROM dialogue_history WHERE session_id IN (SELECT id FROM game_sessions WHERE script_id = :sid)"), {"sid": SCRIPT_ID})
        await db.execute(sa_text("DELETE FROM game_progress WHERE session_id IN (SELECT id FROM game_sessions WHERE script_id = :sid)"), {"sid": SCRIPT_ID})
        await db.execute(sa_text("DELETE FROM affection_history WHERE source_session_id IN (SELECT id FROM game_sessions WHERE script_id = :sid)"), {"sid": SCRIPT_ID})
        await db.execute(sa_text("DELETE FROM share_cards WHERE session_id IN (SELECT id FROM game_sessions WHERE script_id = :sid)"), {"sid": SCRIPT_ID})
        await db.execute(sa_text("DELETE FROM save_snapshots WHERE session_id IN (SELECT id FROM game_sessions WHERE script_id = :sid)"), {"sid": SCRIPT_ID})
        await db.execute(sa_text("DELETE FROM gift_records WHERE session_id IN (SELECT id FROM game_sessions WHERE script_id = :sid)"), {"sid": SCRIPT_ID})
        await db.execute(sa_text("DELETE FROM game_sessions WHERE script_id = :sid"), {"sid": SCRIPT_ID})
        # 清理 nodes 依赖
        await db.execute(sa_text("DELETE FROM node_choices WHERE node_id IN (SELECT n.id FROM nodes n JOIN routes r ON n.route_id = r.id WHERE r.script_id = :sid)"), {"sid": SCRIPT_ID})
        await db.execute(sa_text("DELETE FROM save_snapshots WHERE current_node_id IN (SELECT n.id FROM nodes n JOIN routes r ON n.route_id = r.id WHERE r.script_id = :sid)"), {"sid": SCRIPT_ID})
        await db.execute(sa_text("DELETE FROM game_progress WHERE node_id IN (SELECT n.id FROM nodes n JOIN routes r ON n.route_id = r.id WHERE r.script_id = :sid)"), {"sid": SCRIPT_ID})
        await db.execute(sa_text("DELETE FROM game_sessions WHERE current_node_id IN (SELECT n.id FROM nodes n JOIN routes r ON n.route_id = r.id WHERE r.script_id = :sid)"), {"sid": SCRIPT_ID})
        await db.execute(sa_text("DELETE FROM nodes WHERE route_id IN (SELECT id FROM routes WHERE script_id = :sid)"), {"sid": SCRIPT_ID})
        # 清理 characters 依赖
        await db.execute(sa_text("DELETE FROM character_memories WHERE character_id IN (SELECT id FROM characters WHERE script_id = :sid)"), {"sid": SCRIPT_ID})
        await db.execute(sa_text("DELETE FROM free_chat_sessions WHERE character_id IN (SELECT id FROM characters WHERE script_id = :sid)"), {"sid": SCRIPT_ID})
        await db.execute(sa_text("DELETE FROM dialogue_history WHERE character_id IN (SELECT id FROM characters WHERE script_id = :sid)"), {"sid": SCRIPT_ID})
        await db.execute(sa_text("DELETE FROM affection_history WHERE character_id IN (SELECT id FROM characters WHERE script_id = :sid)"), {"sid": SCRIPT_ID})
        await db.execute(sa_text("DELETE FROM character_sprites WHERE character_id IN (SELECT id FROM characters WHERE script_id = :sid)"), {"sid": SCRIPT_ID})
        await db.execute(sa_text("DELETE FROM affection WHERE character_id IN (SELECT id FROM characters WHERE script_id = :sid)"), {"sid": SCRIPT_ID})
        await db.execute(sa_text("DELETE FROM gift_records WHERE character_id IN (SELECT id FROM characters WHERE script_id = :sid)"), {"sid": SCRIPT_ID})
        await db.execute(sa_text("DELETE FROM characters WHERE script_id = :sid"), {"sid": SCRIPT_ID})
        # 清理 routes 依赖
        await db.execute(sa_text("DELETE FROM endings WHERE route_id IN (SELECT id FROM routes WHERE script_id = :sid)"), {"sid": SCRIPT_ID})
        await db.execute(sa_text("DELETE FROM cg_assets WHERE route_id IN (SELECT id FROM routes WHERE script_id = :sid)"), {"sid": SCRIPT_ID})
        await db.execute(sa_text("DELETE FROM game_sessions WHERE route_id IN (SELECT id FROM routes WHERE script_id = :sid)"), {"sid": SCRIPT_ID})
        await db.execute(sa_text("DELETE FROM routes WHERE script_id = :sid"), {"sid": SCRIPT_ID})
        # 清理 scripts 依赖
        await db.execute(sa_text("DELETE FROM user_dialogue_counts WHERE script_id = :sid"), {"sid": SCRIPT_ID})
        await db.execute(sa_text("DELETE FROM cg_assets WHERE script_id = :sid"), {"sid": SCRIPT_ID})
        await db.execute(sa_text("DELETE FROM scenes WHERE script_id = :sid"), {"sid": SCRIPT_ID})
        await db.execute(sa_text("DELETE FROM free_chat_sessions WHERE script_id = :sid"), {"sid": SCRIPT_ID})
        await db.execute(sa_text("DELETE FROM endings WHERE script_id = :sid"), {"sid": SCRIPT_ID})
        await db.execute(sa_text("DELETE FROM convergence_points WHERE script_id = :sid"), {"sid": SCRIPT_ID})
        await db.execute(sa_text("DELETE FROM unlocked_scripts WHERE script_id = :sid"), {"sid": SCRIPT_ID})
        await db.execute(sa_text("DELETE FROM scripts WHERE id = :sid"), {"sid": SCRIPT_ID})
        await db.commit()
        print("✅ 旧数据清理完成")

        # ─── 剧本 ────────────────────────────────────────────────────────
        print("\n🌟 创建剧本：星辰之约")
        script = Script(
            id=SCRIPT_ID, slug="starry-vow", title="星辰之约",
            description="在星光璀璨的夜晚，你与温柔的占星师林辰相遇。命运的齿轮开始转动...",
            genre="romance", cover_image_url="/assets/covers/starry-vow.jpg",
            total_convergence_points=4, characters_per_script=1,
        )
        db.add(script)
        await db.flush()

        # ─── 角色 ────────────────────────────────────────────────────────
        print("  👤 创建角色：林辰")
        character = Character(
            id=CHARACTER_ID, script_id=SCRIPT_ID, name="林辰",
            description="温柔的占星师，擅长解读星象。性格温和体贴，偶尔带点神秘感。相信命运和缘分，对每个人都充满善意。",
            dialogue_style="gentle", is_main=True,
            age=26, height=180, birthday="11月23日",
            likes=["星空", "占星术", "咖啡", "古典音乐", "天文观测"],
            personality={
                "traits": ["温柔", "体贴", "神秘", "浪漫", "专注"],
                "mbti": "INFP",
                "enneagram": "Type 4",
            },
        )
        db.add(character)
        await db.flush()

        # ═══════════════════════════════════════════════════════════════
        # 路线 1：星夜邂逅（主线）- 7 层深度
        # ═══════════════════════════════════════════════════════════════
        print("\n🛤️  创建路线：星夜邂逅")
        route_star = Route(id=ROUTE_STAR, script_id=SCRIPT_ID, title="星夜邂逅",
                           description="在咖啡厅的偶然相遇，开启了一段星辰交织的故事")
        db.add(route_star)
        await db.flush()

        # 生成 UUID 列表
        import uuid as _uuid
        def nid(route_prefix, idx):
            return _uuid.UUID(f"{route_prefix}0000001-0001-0001-0001-{idx:012d}")
        def cid(route_prefix, idx):
            return _uuid.UUID(f"{route_prefix}0000002-0001-0001-0001-{idx:012d}")

        # ── 星夜邂逅节点 ──
        s_nodes = {}
        s_data = [
            ("open", "preset", None, {
                "text": "你好，我是林辰。今晚的星象很美，猎户座和天狼星形成了罕见的角度...啊，抱歉，我是不是吓到你了？我只是看到有人一直在看窗外，忍不住想分享。",
                "emotion": "gentle", "scene": "咖啡厅",
            }),
            ("friendly", "preset", "open", {
                "text": "真的吗？太好了！你也喜欢星星啊。你知道吗，在占星学里，两个人的星盘如果契合，就会产生奇妙的共鸣。我可以...帮你看看吗？",
                "emotion": "happy", "scene": "咖啡厅",
            }),
            ("cold", "preset", "open", {
                "text": "啊...抱歉，我太唐突了。我只是...有时候会过于沉浸在自己的世界里。如果你不介意的话，我可以请你喝杯咖啡，当作赔礼？",
                "emotion": "apologetic", "scene": "咖啡厅",
            }),
            ("deep", "preset", "friendly", {
                "text": "你的星盘...很有意思。月亮落在第七宫，说明你重视人际关系。金星在第五宫，你对浪漫有着天然的向往。啊，不好意思，我说得太多了吗？",
                "emotion": "thoughtful", "scene": "咖啡厅",
            }),
            ("promise", "preset", "deep", {
                "text": "太好了！那我们约好了，明晚天文馆见。我会为你准备一份特别的星盘解读...也许，这会是我们故事的开始。",
                "emotion": "happy", "scene": "天文馆",
            }),
            ("end_good", "ending", "promise", {
                "text": "太好了！那我们约好了，明晚天文馆见。我会为你准备一份特别的星盘解读...也许，这会是我们故事的开始。",
                "ending_type": "good", "is_ending": True,
            }),
            ("end_normal", "ending", "deep", {
                "text": "没关系，我理解。也许下次有机会再见。祝你今晚愉快...星空会记住我们短暂的相遇。",
                "ending_type": "normal", "is_ending": True,
            }),
            ("end_bad", "ending", "cold", {
                "text": "我明白了...抱歉打扰了。希望你今晚能找到你想要的...再见。",
                "ending_type": "bad", "is_ending": True,
            }),
        ]
        for key, ntype, parent_key, content in s_data:
            parent_id = s_nodes[parent_key] if parent_key else None
            n = Node(route_id=ROUTE_STAR, parent_id=parent_id, node_type=ntype, content=content)
            db.add(n)
            await db.flush()
            s_nodes[key] = n.id

        # 星夜邂逅选项
        s_choices = [
            ("open", "我也很喜欢星星！能告诉我更多关于星象的知识吗？", "friendly", 3),
            ("open", "抱歉，我只是来喝咖啡的，不太懂星象。", "cold", -2),
            ("friendly", "好啊！我很想看看我的星盘，什么时候方便？", "promise", 5),
            ("friendly", "谢谢你的邀请，不过我最近比较忙，可能没时间。", "end_normal", -1),
            ("cold", "好吧，那就一杯咖啡。不过我真的很忙。", "end_normal", 2),
            ("cold", "不用了，谢谢。我先走了。", "end_bad", -3),
        ]
        for from_key, text, to_key, delta in s_choices:
            c = NodeChoice(node_id=s_nodes[from_key], text=text,
                          next_node_id=s_nodes[to_key], affection_delta=delta)
            db.add(c)
        await db.flush()
        print(f"      ✅ 星夜邂逅：{len(s_nodes)} 节点，{len(s_choices)} 选项")

        # ═══════════════════════════════════════════════════════════════
        # 路线 2：林辰线 - 8 层深度 + CG 触发
        # ═══════════════════════════════════════════════════════════════
        print("\n🛤️  创建路线：林辰线：星光指引")
        route_lc = Route(id=ROUTE_LINCHEN, script_id=SCRIPT_ID, title="林辰线：星光指引",
                         description="深入了解林辰的内心世界，在星光下找到彼此的共鸣")
        db.add(route_lc)
        await db.flush()

        lc_nodes = {}
        lc_data = [
            ("open", "preset", None, {
                "text": "你也是来看星象的吗？今晚的猎户座特别明亮，据说看到它的人会遇到命中注定的人...啊，不好意思，我说了奇怪的话。我是林辰，天文台的占星师。",
                "emotion": "gentle", "scene": "天文台", "character_id": str(CHARACTER_ID),
            }),
            ("interest", "preset", "open", {
                "text": "其实...我一直觉得占星不只是预测未来，更是理解自己的过程。每个人都有自己的星盘密码，解开它，就能找到内心的答案。你...愿意让我帮你解读吗？",
                "emotion": "thoughtful", "scene": "天文台", "character_id": str(CHARACTER_ID),
            }),
            ("cg_scene", "cg_trigger", "interest", {
                "title": "星光下的约定", "description": "林辰为你绘制了专属星盘，你们的关系更进一步！",
                "text": "看，这是你的星盘。月亮和金星形成了美好的相位...说明你内心渴望被理解。我...能成为那个理解你的人吗？",
                "emotion": "romantic", "image": "/assets/cg/starlight_promise.jpg", "rarity": "SR",
                "character_id": str(CHARACTER_ID),
            }),
            ("observe", "preset", "cg_scene", {
                "text": "太好了...其实，我最近正在研究一个特殊的星象组合。据说只有心灵相通的人才能看到它的光芒。你...愿意和我一起观测吗？",
                "emotion": "hopeful", "scene": "天文台观测室", "character_id": str(CHARACTER_ID),
            }),
            ("converge", "converge_node", "observe", {
                "title": "命运的交汇", "description": "你和林辰的故事线在此汇聚，命运的齿轮开始转动！",
                "text": "观测室的门轻轻关上，只剩下你们两人。窗外的星空似乎比任何时候都要明亮...林辰轻声说：'这一刻，我等了很久。'",
                "emotion": "romantic", "rarity": "SR",
                "character_id": str(CHARACTER_ID),
            }),
            ("promise", "preset", "converge", {
                "text": "明晚...我准备了特别的观测计划。如果能看到那个星象，据说会迎来永恒的幸福。我...很想和你一起见证。",
                "emotion": "romantic", "scene": "天文台", "character_id": str(CHARACTER_ID),
            }),
            ("end_good", "ending", "promise", {
                "text": "你看到了...那个星象真的出现了。林辰轻轻握住你的手，'谢谢你...让我不再孤单。从今以后，每一颗星都是我们的见证。'",
                "ending_type": "good", "is_ending": True,
            }),
            ("end_normal", "ending", "observe", {
                "text": "没关系...也许下次有机会。星空会一直在这里，我也会。",
                "ending_type": "normal", "is_ending": True,
            }),
            ("end_bad", "ending", "interest", {
                "text": "我理解...也许是我太急切了。抱歉，打扰了你的夜晚。",
                "ending_type": "bad", "is_ending": True,
            }),
        ]
        for key, ntype, parent_key, content in lc_data:
            parent_id = lc_nodes[parent_key] if parent_key else None
            n = Node(route_id=ROUTE_LINCHEN, parent_id=parent_id, node_type=ntype, content=content)
            db.add(n)
            await db.flush()
            lc_nodes[key] = n.id

        lc_choices = [
            ("open", "你好！我对占星很感兴趣，能多聊聊吗？", "interest", 3),
            ("open", "只是路过看看，不太懂这些。", "interest", 0),
            ("interest", "好啊！我很想了解自己的星盘。", "cg_scene", 5),
            ("interest", "谢谢，但我得走了。", "end_bad", -3),
            ("cg_scene", "当然愿意！一起观测一定很浪漫。", "observe", 5),
            ("cg_scene", "我...需要考虑一下。", "end_normal", -1),
            ("observe", "好啊！我也很期待。", "converge", 5),
            ("observe", "抱歉，我最近比较忙。", "end_normal", -2),
            ("converge", "我也很期待明晚的观测！", "promise", 5),
            ("converge", "我...还没准备好。", "end_normal", -1),
            ("promise", "一定会的！我也很想和你一起见证。", "end_good", 5),
        ]
        for from_key, text, to_key, delta in lc_choices:
            c = NodeChoice(node_id=lc_nodes[from_key], text=text,
                          next_node_id=lc_nodes[to_key], affection_delta=delta)
            db.add(c)
        await db.flush()
        print(f"      ✅ 林辰线：{len(lc_nodes)} 节点，{len(lc_choices)} 选项")

        # ═══════════════════════════════════════════════════════════════
        # 路线 3：流星线 - 6 层深度
        # ═══════════════════════════════════════════════════════════════
        print("\n🛤️  创建路线：流星线：刹那永恒")
        route_mt = Route(id=ROUTE_METEOR, script_id=SCRIPT_ID, title="流星线：刹那永恒",
                         description="在流星划过的瞬间，你们的故事悄然开始")
        db.add(route_mt)
        await db.flush()

        mt_nodes = {}
        mt_data = [
            ("open", "preset", None, {
                "text": "快看！流星！...啊，你也被吸引了吗？我是林辰。据说看到流星时许愿，愿望就会实现。你...许了什么愿？",
                "emotion": "excited", "scene": "郊外观星点", "character_id": str(CHARACTER_ID),
            }),
            ("share", "preset", "open", {
                "text": "我的愿望啊...说出来就不灵了。不过，可以告诉你一个秘密：我每个月都会来这里看流星雨。一个人...有时候会觉得有点孤单。",
                "emotion": "shy", "scene": "郊外观星点", "character_id": str(CHARACTER_ID),
            }),
            ("together", "preset", "share", {
                "text": "真的吗？那...以后我们能一起来吗？我知道一个更好的观星点，可以看到更完整的星空。",
                "emotion": "hopeful", "scene": "郊外观星点", "character_id": str(CHARACTER_ID),
            }),
            ("cg_meteor", "cg_trigger", "together", {
                "title": "流星之吻", "description": "在流星划过天际的瞬间，林辰轻轻靠近了你...",
                "text": "又一颗流星！快看...啊，你的眼睛比流星还要明亮。对不起，我说了奇怪的话...但是，我是认真的。",
                "emotion": "romantic", "image": "/assets/cg/meteor_kiss.jpg", "rarity": "SSR",
                "character_id": str(CHARACTER_ID),
            }),
            ("end_good", "ending", "cg_meteor", {
                "text": "林辰轻轻握住你的手，'以后每一个流星雨夜，我们都一起看，好吗？'你点了点头，星光在你们眼中闪烁。",
                "ending_type": "good", "is_ending": True,
            }),
            ("end_normal", "ending", "share", {
                "text": "也许...下次吧。流星还在划过，但 moment 已经过去了。林辰微笑着说：'没关系，星空会记住你的。'",
                "ending_type": "normal", "is_ending": True,
            }),
            ("end_bad", "ending", "open", {
                "text": "啊...抱歉，我不该问这种问题的。林辰转过头，继续独自看着星空。",
                "ending_type": "bad", "is_ending": True,
            }),
        ]
        for key, ntype, parent_key, content in mt_data:
            parent_id = mt_nodes[parent_key] if parent_key else None
            n = Node(route_id=ROUTE_METEOR, parent_id=parent_id, node_type=ntype, content=content)
            db.add(n)
            await db.flush()
            mt_nodes[key] = n.id

        mt_choices = [
            ("open", "我没有许愿...不过，能和你一起看流星很开心。", "share", 3),
            ("open", "我只是路过。", "end_bad", -2),
            ("share", "好啊！我很想去那个更好的观星点。", "together", 5),
            ("share", "谢谢，但我得回去了。", "end_normal", -1),
            ("together", "当然！每个流星雨夜都一起来！", "cg_meteor", 5),
            ("together", "我...考虑一下吧。", "end_normal", -1),
            ("cg_meteor", "好啊...我也希望能一直和你一起看。", "end_good", 5),
        ]
        for from_key, text, to_key, delta in mt_choices:
            c = NodeChoice(node_id=mt_nodes[from_key], text=text,
                          next_node_id=mt_nodes[to_key], affection_delta=delta)
            db.add(c)
        await db.flush()
        print(f"      ✅ 流星线：{len(mt_nodes)} 节点，{len(mt_choices)} 选项")

        # ═══════════════════════════════════════════════════════════════
        # 路线 4：银河线 - 7 层深度 + 隐藏选项
        # ═══════════════════════════════════════════════════════════════
        print("\n🛤️  创建路线：银河线：命运交汇")
        route_gx = Route(id=ROUTE_GALAXY, script_id=SCRIPT_ID, title="银河线：命运交汇",
                         description="穿越银河的旅途，你们在命运交汇处相遇")
        db.add(route_gx)
        await db.flush()

        gx_nodes = {}
        gx_data = [
            ("open", "preset", None, {
                "text": "欢迎来到银河车站。我是这里的向导林辰。你也是来等待通往银河的列车的吗？据说只有被命运选中的人才能看到它。",
                "emotion": "mysterious", "scene": "银河车站", "character_id": str(CHARACTER_ID),
            }),
            ("believe", "preset", "open", {
                "text": "你相信命运吗？我以前只觉得这是浪漫的说法。但自从遇见你...我开始觉得，也许命运真的存在。",
                "emotion": "thoughtful", "scene": "银河车站", "character_id": str(CHARACTER_ID),
            }),
            ("ticket", "preset", "believe", {
                "text": "看，这是通往银河的车票。上面写着两个人的名字...奇怪，我之前看到的时候明明只有我一个人。",
                "emotion": "surprised", "scene": "银河车站", "character_id": str(CHARACTER_ID),
            }),
            ("cg_galaxy", "cg_trigger", "ticket", {
                "title": "银河之旅", "description": "你和林辰一起踏上了通往银河的列车！",
                "text": "列车缓缓启动，窗外的星空开始流动。林辰坐在你身旁，轻声说：'不管终点在哪里，能和你一起，就是最好的旅途。'",
                "emotion": "romantic", "image": "/assets/cg/galaxy_journey.jpg", "rarity": "SSR",
                "character_id": str(CHARACTER_ID),
            }),
            ("destination", "preset", "cg_galaxy", {
                "text": "列车长说，银河的终点会根据乘客的心愿改变。你...希望去哪里？不管哪里，我都陪你。",
                "emotion": "gentle", "scene": "银河列车", "character_id": str(CHARACTER_ID),
            }),
            ("end_good", "ending", "destination", {
                "text": "列车停在了一个由星光构成的站台。林辰牵着你的手走下车，'到了...这里就是属于我们的星球。'从此，你们在银河的尽头开始了新的生活。",
                "ending_type": "good", "is_ending": True,
            }),
            ("end_normal", "ending", "believe", {
                "text": "列车终究没有来。林辰微笑着说：'也许...我们就是彼此的银河。'你们在车站告别，但心中多了一份温暖。",
                "ending_type": "normal", "is_ending": True,
            }),
            ("end_bad", "ending", "open", {
                "text": "你摇了摇头，转身离开。林辰在身后轻声说：'银河会记住每一个路过的人...'",
                "ending_type": "bad", "is_ending": True,
            }),
        ]
        for key, ntype, parent_key, content in gx_data:
            parent_id = gx_nodes[parent_key] if parent_key else None
            n = Node(route_id=ROUTE_GALAXY, parent_id=parent_id, node_type=ntype, content=content)
            db.add(n)
            await db.flush()
            gx_nodes[key] = n.id

        gx_choices = [
            ("open", "我相信！能和我讲讲银河的故事吗？", "believe", 3),
            ("open", "我只是好奇来看看。", "believe", 0),
            ("open", "不太相信这些。", "end_bad", -2),
            ("believe", "真的吗？车票上为什么会有两个人的名字？", "ticket", 5),
            ("believe", "也许吧...但我该走了。", "end_normal", -1),
            ("ticket", "太好了！我们一起上车吧！", "cg_galaxy", 5),
            ("ticket", "我...有点紧张。", "cg_galaxy", 2),
            ("cg_galaxy", "去哪里都好，只要和你一起。", "destination", 5),
            ("cg_galaxy", "让我想想...先去最近的地方吧。", "destination", 2),
            ("destination", "去银河的尽头！我想看看那里有什么。", "end_good", 5),
        ]
        for from_key, text, to_key, delta in gx_choices:
            c = NodeChoice(node_id=gx_nodes[from_key], text=text,
                          next_node_id=gx_nodes[to_key], affection_delta=delta)
            db.add(c)

        # 添加一个隐藏选项（好感度 >= 10 才能看到）
        hidden_choice = NodeChoice(
            node_id=gx_nodes["destination"],
            text="其实...我不想只是旅伴。我想和你一起留在银河。",
            next_node_id=gx_nodes["end_good"],
            affection_delta=10,
            is_hidden=True,
            required_affection=10,
            hint="💫 需要足够的好感度才能解锁",
        )
        db.add(hidden_choice)

        await db.flush()
        print(f"      ✅ 银河线：{len(gx_nodes)} 节点，{len(gx_choices)+1} 选项（含 1 个隐藏）")

        await db.commit()
        print("\n🎉 种子数据创建完成！")
        print(f"   剧本：星辰之约 ({SCRIPT_ID})")
        print(f"   角色：林辰 ({CHARACTER_ID})")
        print(f"   路线：4 条")
        print(f"   总节点：{len(s_nodes) + len(lc_nodes) + len(mt_nodes) + len(gx_nodes)}")
        print(f"   总选项：{len(s_choices) + len(lc_choices) + len(mt_choices) + len(gx_choices) + 1}")


if __name__ == "__main__":
    asyncio.run(seed())
