#!/usr/bin/env python3
"""
DEV-012: 乙女恋爱剧本「樱花恋曲」种子数据

包含：
- 1 个完整剧本 (Script)
- 1 个男主角色 (Character: 藤原雪)
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
SCRIPT_ID = uuid.UUID("a1111111-1111-1111-1111-111111111111")
CHARACTER_ID = uuid.UUID("a2222222-2222-2222-2222-222222222222")
ROUTE_ID = uuid.UUID("a3333333-3333-3333-3333-333333333333")

# Node IDs
NODE_OPENING = uuid.UUID("a4444444-4444-4444-4444-444444444441")
NODE_FRIENDLY = uuid.UUID("a4444444-4444-4444-4444-444444444442")
NODE_COLD = uuid.UUID("a4444444-4444-4444-4444-444444444443")
NODE_GOOD_ENDING = uuid.UUID("a4444444-4444-4444-4444-444444444444")
NODE_NORMAL_ENDING = uuid.UUID("a4444444-4444-4444-4444-444444444445")
NODE_BAD_ENDING = uuid.UUID("a4444444-4444-4444-4444-444444444446")

# Choice IDs
CHOICE_FRIENDLY = uuid.UUID("a5555555-5555-5555-5555-555555555551")
CHOICE_COLD = uuid.UUID("a5555555-5555-5555-5555-555555555552")
CHOICE_ACCEPT = uuid.UUID("a5555555-5555-5555-5555-555555555553")
CHOICE_DECLINE = uuid.UUID("a5555555-5555-5555-5555-555555555554")
CHOICE_GIVE_CHANCE = uuid.UUID("a5555555-5555-5555-5555-555555555555")
CHOICE_LEAVE = uuid.UUID("a5555555-5555-5555-5555-555555555556")


async def seed():
    """Insert seed data for 樱花恋曲 script."""
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

        print("🌸 Creating script: 樱花恋曲")

        # 1. Script
        script = Script(
            id=SCRIPT_ID,
            slug="cherry-blossom-romance",
            title="樱花恋曲",
            description="在樱花盛开的季节，你与温柔的文学教授藤原雪相遇。古典文学与现代情感的碰撞，开启了一段诗意的恋情...",
            genre="romance",
            cover_image_url="/assets/covers/cherry-blossom-romance.jpg",
        )
        db.add(script)
        await db.flush()

        # 2. Character
        print("  👤 Creating character: 藤原雪")
        character = Character(
            id=CHARACTER_ID,
            script_id=SCRIPT_ID,
            name="藤原雪",
            description="大学文学教授，专攻古典日本文学。性格温和儒雅，擅长用诗歌表达情感。相信文字能传递心意，每个季节都有独特的美。",
            dialogue_style="gentle",
        )
        db.add(character)

        # 3. Route
        print("  🛤️  Creating route: 樱花树下")
        route = Route(
            id=ROUTE_ID,
            script_id=SCRIPT_ID,
            title="樱花树下",
            description="在樱花盛开的校园小径上，一段诗意的邂逅",
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
                "character": "藤原雪",
                "character_id": str(CHARACTER_ID),
                "text": "你好，我是藤原雪，文学系的教授。你也是来看樱花的吗？每年的这个时节，我都会来这里坐一会儿。古人说「花开堪折直须折」，樱花的美总是转瞬即逝...你读过多少关于樱花的和歌吗？",
                "emotion": "gentle",
                "background": "cherry_blossom_path",
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
                "character": "藤原雪",
                "character_id": str(CHARACTER_ID),
                "text": "真好！你对文学的兴趣让我很高兴。其实，樱花在日本文化中象征着生命的短暂与美丽。就像这首和歌：「樱花飘零时，何须叹息声，不如共赏月，同醉此夜情」。你愿意听我多讲一些吗？",
                "emotion": "delighted",
                "background": "cherry_blossom_path",
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
                "character": "藤原雪",
                "character_id": str(CHARACTER_ID),
                "text": "啊...抱歉，我太啰嗦了。其实我只是觉得，在樱花树下分享故事是一件很美好的事。你如果只是路过，可以继续你的散步。我只是...有时候会过于沉浸在自己的世界里。",
                "emotion": "apologetic",
                "background": "cherry_blossom_path",
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
                "character": "藤原雪",
                "character_id": str(CHARACTER_ID),
                "text": "太好了！其实...我最近正在写一本关于樱花与爱情的书。也许我们可以一起收集更多的素材？下周末有个文学沙龙，如果你愿意的话...我很想再见到你。",
                "emotion": "happy",
                "background": "sunset_cherry_blossom",
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
                "character": "藤原雪",
                "character_id": str(CHARACTER_ID),
                "text": "没关系，我理解。现代生活节奏很快，不是每个人都有时间沉浸在文学里。不过...如果你哪天想读一首诗，或者只是想找人聊聊天，我的办公室随时欢迎你。樱花会记住我们的相遇。",
                "emotion": "bittersweet",
                "background": "cherry_blossom_path",
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
                "character": "藤原雪",
                "character_id": str(CHARACTER_ID),
                "text": "我明白了...也许我确实不该打扰你的散步。抱歉，我太自以为是了。樱花会继续飘落，而我会继续在这里等待有缘人。祝你有个美好的夜晚。",
                "emotion": "sad",
                "background": "cherry_blossom_path",
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
            text="我读过一些和歌，能给我讲讲樱花在文学中的意义吗？",
            next_node_id=NODE_FRIENDLY,
            affection_delta=3,
        ))
        db.add(NodeChoice(
            id=CHOICE_COLD,
            node_id=NODE_OPENING,
            text="我对古典文学不太感兴趣，只是路过看看。",
            next_node_id=NODE_COLD,
            affection_delta=-2,
        ))

        # Friendly path choices
        db.add(NodeChoice(
            id=CHOICE_ACCEPT,
            node_id=NODE_FRIENDLY,
            text="当然愿意！我对你的研究很感兴趣！",
            next_node_id=NODE_GOOD_ENDING,
            affection_delta=5,
        ))
        db.add(NodeChoice(
            id=CHOICE_DECLINE,
            node_id=NODE_FRIENDLY,
            text="谢谢，但我现在没时间，下次吧。",
            next_node_id=NODE_NORMAL_ENDING,
            affection_delta=-1,
        ))

        # Cold path choices
        db.add(NodeChoice(
            id=CHOICE_GIVE_CHANCE,
            node_id=NODE_COLD,
            text="既然来了，就听你讲讲吧。",
            next_node_id=NODE_NORMAL_ENDING,
            affection_delta=2,
        ))
        db.add(NodeChoice(
            id=CHOICE_LEAVE,
            node_id=NODE_COLD,
            text="不用了，我还有事。再见。",
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
