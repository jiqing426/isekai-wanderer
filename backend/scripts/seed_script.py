#!/usr/bin/env python3
"""
DEV-011: 乙女恋爱剧本「星辰之约」种子数据

包含：
- 1 个完整剧本 (Script)
- 1 个男主角色 (Character: 林辰)
- 1 条主线路线 (Route)
- 6 个节点 (Nodes): 开场(带选择) → 友好路线(带选择)/冷淡路线(带选择) → 3 个结局
- 6 个选项 (NodeChoices) 带 affection_delta
"""

import asyncio
import uuid
from pathlib import Path
import sys

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select, text
from app.core.database import async_session_factory
from app.models.script import Script, Route, Node, NodeChoice, Character

# Fixed UUIDs
SCRIPT_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
CHARACTER_ID = uuid.UUID("22222222-2222-2222-2222-222222222222")
ROUTE_ID = uuid.UUID("33333333-3333-3333-3333-333333333333")

# Node IDs
NODE_OPENING = uuid.UUID("44444444-4444-4444-4444-444444444441")
NODE_FRIENDLY = uuid.UUID("44444444-4444-4444-4444-444444444443")
NODE_COLD = uuid.UUID("44444444-4444-4444-4444-444444444444")
NODE_GOOD_ENDING = uuid.UUID("44444444-4444-4444-4444-444444444447")
NODE_NORMAL_ENDING = uuid.UUID("44444444-4444-4444-4444-444444444448")
NODE_BAD_ENDING = uuid.UUID("44444444-4444-4444-4444-444444444449")

# Choice IDs
CHOICE_FRIENDLY = uuid.UUID("55555555-5555-5555-5555-555555555551")
CHOICE_COLD = uuid.UUID("55555555-5555-5555-5555-555555555552")
CHOICE_ACCEPT = uuid.UUID("55555555-5555-5555-5555-555555555553")
CHOICE_DECLINE = uuid.UUID("55555555-5555-5555-5555-555555555554")
CHOICE_GIVE_CHANCE = uuid.UUID("55555555-5555-5555-5555-555555555555")
CHOICE_LEAVE = uuid.UUID("55555555-5555-5555-5555-555555555556")


async def seed():
    """Insert seed data for 星辰之约 script."""
    async with async_session_factory() as db:
        # Check if script already exists
        stmt = select(Script).where(Script.id == SCRIPT_ID)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            print("⚠️  Script already exists, cleaning up first...")
            # Delete in FK-safe order
            await db.execute(text("DELETE FROM game_progress WHERE session_id IN (SELECT id FROM game_sessions WHERE script_id = :sid)"), {"sid": SCRIPT_ID})
            await db.execute(text("DELETE FROM game_sessions WHERE script_id = :sid"), {"sid": SCRIPT_ID})
            await db.execute(text("DELETE FROM node_choices WHERE node_id IN (SELECT id FROM nodes WHERE route_id = :rid)"), {"rid": ROUTE_ID})
            await db.execute(text("DELETE FROM nodes WHERE route_id = :rid"), {"rid": ROUTE_ID})
            await db.execute(text("DELETE FROM routes WHERE id = :rid"), {"rid": ROUTE_ID})
            await db.execute(text("DELETE FROM characters WHERE script_id = :sid"), {"sid": SCRIPT_ID})
            await db.execute(text("DELETE FROM scripts WHERE id = :sid"), {"sid": SCRIPT_ID})
            await db.commit()

        print("🌟 Creating script: 星辰之约")

        # 1. Script
        script = Script(
            id=SCRIPT_ID,
            slug="starry-vow",
            title="星辰之约",
            description="在星光璀璨的夜晚，你与温柔的占星师林辰相遇。命运的齿轮开始转动，你们的故事即将展开...",
            genre="romance",
            cover_image_url="/assets/covers/starry-vow.jpg",
        )
        db.add(script)
        await db.flush()

        # 2. Character
        print("  👤 Creating character: 林辰")
        character = Character(
            id=CHARACTER_ID,
            script_id=SCRIPT_ID,
            name="林辰",
            description="温柔的占星师，擅长解读星象。性格温和体贴，偶尔带点神秘感。相信命运和缘分，对每个人都充满善意。",
            dialogue_style="gentle",
        )
        db.add(character)

        # 3. Route
        print("  🛤️  Creating route: 星夜邂逅")
        route = Route(
            id=ROUTE_ID,
            script_id=SCRIPT_ID,
            title="星夜邂逅",
            description="在咖啡厅的偶然相遇，开启了一段星辰交织的故事",
        )
        db.add(route)
        await db.flush()

        # 4. Nodes (choices on preset nodes directly — no separate choice nodes)
        print("  📖 Creating nodes...")

        # Opening: preset with dialogue + choices
        db.add(Node(
            id=NODE_OPENING,
            route_id=ROUTE_ID,
            parent_id=None,
            node_type="preset",
            content={
                "character": "林辰",
                "character_id": str(CHARACTER_ID),
                "text": "你好，我是林辰。今晚的星象很美，猎户座和天狼星形成了罕见的角度...啊，抱歉，我是不是吓到你了？我只是太喜欢观星了。你也是来看星星的吗？",
                "emotion": "warm",
                "background": "cafe_night",
                "scene": "opening",
            },
        ))

        # Friendly path: preset with dialogue + choices
        db.add(Node(
            id=NODE_FRIENDLY,
            route_id=ROUTE_ID,
            parent_id=NODE_OPENING,
            node_type="preset",
            content={
                "character": "林辰",
                "character_id": str(CHARACTER_ID),
                "text": "真的吗？太好了！你也喜欢星星啊。你知道吗，在占星学里，两个人的星盘如果契合，就会产生奇妙的共鸣。我可以帮你看看你的星盘...如果你愿意的话。",
                "emotion": "excited",
                "background": "cafe_night",
                "scene": "friendly_path",
            },
        ))

        # Cold path: preset with dialogue + choices
        db.add(Node(
            id=NODE_COLD,
            route_id=ROUTE_ID,
            parent_id=NODE_OPENING,
            node_type="preset",
            content={
                "character": "林辰",
                "character_id": str(CHARACTER_ID),
                "text": "啊...抱歉，我太唐突了。我只是...有时候会过于沉浸在自己的世界里。如果你不介意的话，我可以请你喝杯咖啡当作赔礼吗？",
                "emotion": "apologetic",
                "background": "cafe_night",
                "scene": "cold_path",
            },
        ))

        # Good ending
        db.add(Node(
            id=NODE_GOOD_ENDING,
            route_id=ROUTE_ID,
            parent_id=NODE_FRIENDLY,
            node_type="ending",
            content={
                "character": "林辰",
                "character_id": str(CHARACTER_ID),
                "text": "太好了！那我们约好了，明晚天文馆见。我会为你准备一份特别的星盘解读...也许，这会是我们故事的开始。",
                "emotion": "happy",
                "background": "starry_sky",
                "scene": "good_ending",
                "ending_type": "good",
                "is_ending": True,
            },
        ))

        # Normal ending
        db.add(Node(
            id=NODE_NORMAL_ENDING,
            route_id=ROUTE_ID,
            parent_id=NODE_FRIENDLY,
            node_type="ending",
            content={
                "character": "林辰",
                "character_id": str(CHARACTER_ID),
                "text": "没关系，我理解。也许下次有机会再见。祝你今晚愉快...星空会记住我们短暂的相遇。",
                "emotion": "bittersweet",
                "background": "cafe_night",
                "scene": "normal_ending",
                "ending_type": "normal",
                "is_ending": True,
            },
        ))

        # Bad ending
        db.add(Node(
            id=NODE_BAD_ENDING,
            route_id=ROUTE_ID,
            parent_id=NODE_COLD,
            node_type="ending",
            content={
                "character": "林辰",
                "character_id": str(CHARACTER_ID),
                "text": "我明白了...抱歉打扰了。希望你今晚能找到你想要的...再见。",
                "emotion": "sad",
                "background": "cafe_night",
                "scene": "bad_ending",
                "ending_type": "bad",
                "is_ending": True,
            },
        ))

        await db.flush()

        # 5. Choices (attached directly to preset/ending nodes)
        print("  🎯 Creating choices...")

        # Opening node choices → friendly or cold
        db.add(NodeChoice(
            id=CHOICE_FRIENDLY,
            node_id=NODE_OPENING,
            text="我也很喜欢星星！能告诉我更多关于星象的知识吗？",
            next_node_id=NODE_FRIENDLY,
            affection_delta=3,
        ))
        db.add(NodeChoice(
            id=CHOICE_COLD,
            node_id=NODE_OPENING,
            text="抱歉，我只是来喝咖啡的，不太懂星象。",
            next_node_id=NODE_COLD,
            affection_delta=-2,
        ))

        # Friendly path choices → good or normal ending
        db.add(NodeChoice(
            id=CHOICE_ACCEPT,
            node_id=NODE_FRIENDLY,
            text="好啊！我很想看看我的星盘，什么时候方便？",
            next_node_id=NODE_GOOD_ENDING,
            affection_delta=5,
        ))
        db.add(NodeChoice(
            id=CHOICE_DECLINE,
            node_id=NODE_FRIENDLY,
            text="谢谢你的邀请，不过我最近比较忙，可能没时间。",
            next_node_id=NODE_NORMAL_ENDING,
            affection_delta=-1,
        ))

        # Cold path choices → normal or bad ending
        db.add(NodeChoice(
            id=CHOICE_GIVE_CHANCE,
            node_id=NODE_COLD,
            text="好吧，那就一杯咖啡。不过我真的很忙。",
            next_node_id=NODE_NORMAL_ENDING,
            affection_delta=2,
        ))
        db.add(NodeChoice(
            id=CHOICE_LEAVE,
            node_id=NODE_COLD,
            text="不用了，谢谢。我先走了。",
            next_node_id=NODE_BAD_ENDING,
            affection_delta=-3,
        ))

        await db.commit()

        print("\n✅ Seed data created successfully!")
        print(f"   Script ID:  {SCRIPT_ID}")
        print(f"   Character:  {CHARACTER_ID}")
        print(f"   Route:      {ROUTE_ID}")
        print(f"   Starting:   {NODE_OPENING}")
        print(f"\n📊 6 Nodes, 6 Choices, 3 Endings (Good/Normal/Bad)")


if __name__ == "__main__":
    asyncio.run(seed())
