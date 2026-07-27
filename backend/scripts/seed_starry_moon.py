#!/usr/bin/env python3
"""
DEV-012: 乙女恋爱剧本「星月奇缘」种子数据

包含：
- 1 个完整剧本 (Script)
- 1 个男主角色 (Character: 沈星澜)
- 1 条主线路线 (Route)
- 6 个节点 (Nodes): 开场(带选择) → 友好/冷淡分支 → 3 个结局
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
SCRIPT_ID = uuid.UUID("66666666-6666-6666-6666-666666666666")
CHARACTER_ID = uuid.UUID("77777777-7777-7777-7777-777777777777")
ROUTE_ID = uuid.UUID("88888888-8888-8888-8888-888888888888")

# Node IDs
NODE_OPENING = uuid.UUID("99999999-9999-9999-9999-999999999991")
NODE_FRIENDLY = uuid.UUID("99999999-9999-9999-9999-999999999992")
NODE_COLD = uuid.UUID("99999999-9999-9999-9999-999999999993")
NODE_GOOD_ENDING = uuid.UUID("99999999-9999-9999-9999-999999999994")
NODE_NORMAL_ENDING = uuid.UUID("99999999-9999-9999-9999-999999999995")
NODE_BAD_ENDING = uuid.UUID("99999999-9999-9999-9999-999999999996")

# Choice IDs
CHOICE_FRIENDLY = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
CHOICE_COLD = uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
CHOICE_ACCEPT = uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
CHOICE_DECLINE = uuid.UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")
CHOICE_GIVE_CHANCE = uuid.UUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee")
CHOICE_LEAVE = uuid.UUID("ffffffff-ffff-ffff-ffff-ffffffffffff")


async def seed():
    """Insert seed data for 星月奇缘 script."""
    async with async_session_factory() as db:
        # Check if script already exists
        stmt = select(Script).where(Script.id == SCRIPT_ID)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            print("⚠️  Script already exists, cleaning up first...")
            await db.execute(text("DELETE FROM game_progress WHERE session_id IN (SELECT id FROM game_sessions WHERE script_id = :sid)"), {"sid": SCRIPT_ID})
            await db.execute(text("DELETE FROM game_sessions WHERE script_id = :sid"), {"sid": SCRIPT_ID})
            await db.execute(text("DELETE FROM node_choices WHERE node_id IN (SELECT id FROM nodes WHERE route_id = :rid)"), {"rid": ROUTE_ID})
            await db.execute(text("DELETE FROM nodes WHERE route_id = :rid"), {"rid": ROUTE_ID})
            await db.execute(text("DELETE FROM routes WHERE id = :rid"), {"rid": ROUTE_ID})
            await db.execute(text("DELETE FROM characters WHERE script_id = :sid"), {"sid": SCRIPT_ID})
            await db.execute(text("DELETE FROM scripts WHERE id = :sid"), {"sid": SCRIPT_ID})
            await db.commit()

        print("🌙 Creating script: 星月奇缘")

        # 1. Script
        script = Script(
            id=SCRIPT_ID,
            slug="star-moon-fate",
            title="星月奇缘",
            description="在神秘的月夜下，你与天才天文学家沈星澜相遇。星辰与月光的交织，开启了一段奇幻的缘分...",
            genre="romance",
            cover_image_url="/assets/covers/star-moon-fate.jpg",
        )
        db.add(script)
        await db.flush()

        # 2. Character
        print("  👤 Creating character: 沈星澜")
        character = Character(
            id=CHARACTER_ID,
            script_id=SCRIPT_ID,
            name="沈星澜",
            description="天才天文学家，专注于研究月相与潮汐的关系。外表冷峻，内心却有着不为人知的温柔。相信科学能解释一切，包括缘分。",
            dialogue_style="mysterious",
        )
        db.add(character)

        # 3. Route
        print("  🛤️  Creating route: 月夜邂逅")
        route = Route(
            id=ROUTE_ID,
            script_id=SCRIPT_ID,
            title="月夜邂逅",
            description="在天文台的偶然相遇，开启了一段星月交织的奇幻故事",
        )
        db.add(route)
        await db.flush()

        # 4. Nodes
        print("  📖 Creating nodes...")

        # Opening
        db.add(Node(
            id=NODE_OPENING,
            route_id=ROUTE_ID,
            parent_id=None,
            node_type="preset",
            content={
                "character": "沈星澜",
                "character_id": str(CHARACTER_ID),
                "text": "你也是来看月相的吗？今晚的月亮正好是上弦月，适合观测潮汐变化。我是沈星澜，天文台的研究员。你看起来...不像是天文学爱好者。",
                "emotion": "curious",
                "background": "observatory_night",
                "scene": "opening",
            },
        ))

        # Friendly path
        db.add(Node(
            id=NODE_FRIENDLY,
            route_id=ROUTE_ID,
            parent_id=NODE_OPENING,
            node_type="preset",
            content={
                "character": "沈星澜",
                "character_id": str(CHARACTER_ID),
                "text": "有意思...你对星辰的好奇心让我想起了自己刚开始研究天文学的时候。其实，月相不仅影响潮汐，在古老的占星学中，月亮的位置被认为会影响人的命运。你相信吗？",
                "emotion": "intrigued",
                "background": "observatory_night",
                "scene": "friendly_path",
            },
        ))

        # Cold path
        db.add(Node(
            id=NODE_COLD,
            route_id=ROUTE_ID,
            parent_id=NODE_OPENING,
            node_type="preset",
            content={
                "character": "沈星澜",
                "character_id": str(CHARACTER_ID),
                "text": "啊...抱歉，我习惯了用专业术语。其实我只是想说，今晚的月亮很美，适合一个人静静地看。你如果没什么事的话，可以继续你的散步。",
                "emotion": "disappointed",
                "background": "observatory_night",
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
                "character": "沈星澜",
                "character_id": str(CHARACTER_ID),
                "text": "太好了！其实...我一直想找人分享这些。也许我们可以一起观测下一次的月全食？据说那会是非常罕见的天象。这算是...我们的约定吗？",
                "emotion": "happy",
                "background": "moonlit_sky",
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
                "character": "沈星澜",
                "character_id": str(CHARACTER_ID),
                "text": "没关系，我理解。科学研究需要大量的时间投入。不过...如果你哪天对天文学感兴趣了，天文台随时欢迎你。今晚的月色，我会记住的。",
                "emotion": "bittersweet",
                "background": "observatory_night",
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
                "character": "沈星澜",
                "character_id": str(CHARACTER_ID),
                "text": "我明白了...也许我确实太沉浸在自己的世界里了。抱歉打扰了你的夜晚。月亮会继续升起，而我会继续观测。再见。",
                "emotion": "sad",
                "background": "observatory_night",
                "scene": "bad_ending",
                "ending_type": "bad",
                "is_ending": True,
            },
        ))

        await db.flush()

        # 5. Choices
        print("  🎯 Creating choices...")

        # Opening choices
        db.add(NodeChoice(
            id=CHOICE_FRIENDLY,
            node_id=NODE_OPENING,
            text="虽然不是爱好者，但我对星空很好奇！能给我讲讲月相吗？",
            next_node_id=NODE_FRIENDLY,
            affection_delta=3,
        ))
        db.add(NodeChoice(
            id=CHOICE_COLD,
            node_id=NODE_OPENING,
            text="我只是路过，对天文学没什么兴趣。",
            next_node_id=NODE_COLD,
            affection_delta=-2,
        ))

        # Friendly path choices
        db.add(NodeChoice(
            id=CHOICE_ACCEPT,
            node_id=NODE_FRIENDLY,
            text="我相信！科学与占星并不矛盾，我想了解更多！",
            next_node_id=NODE_GOOD_ENDING,
            affection_delta=5,
        ))
        db.add(NodeChoice(
            id=CHOICE_DECLINE,
            node_id=NODE_FRIENDLY,
            text="我更喜欢脚踏实地，占星太玄乎了。",
            next_node_id=NODE_NORMAL_ENDING,
            affection_delta=-1,
        ))

        # Cold path choices
        db.add(NodeChoice(
            id=CHOICE_GIVE_CHANCE,
            node_id=NODE_COLD,
            text="既然来了，就听听你的研究吧。",
            next_node_id=NODE_NORMAL_ENDING,
            affection_delta=2,
        ))
        db.add(NodeChoice(
            id=CHOICE_LEAVE,
            node_id=NODE_COLD,
            text="不用了，我更喜欢安静地散步。再见。",
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
