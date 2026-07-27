#!/usr/bin/env python3
"""
DEV-BE-007: 集合点种子数据

为剧本创建集合点（Convergence Points），用于多角色路线汇聚。
"""

import asyncio
import uuid
from pathlib import Path
import sys

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select, text
from app.core.database import async_session_factory
from app.models.script import Script
from app.models.convergence_point import ConvergencePoint

# 使用已有的剧本ID
SCRIPT_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")

# 集合点ID
CP_CH1 = uuid.UUID("66666666-6666-6666-6666-666666666661")
CP_CH2 = uuid.UUID("66666666-6666-6666-6666-666666666662")
CP_CH3 = uuid.UUID("66666666-6666-6666-6666-666666666663")


async def seed():
    """Insert convergence points for 星辰之约 script."""
    async with async_session_factory() as db:
        # 检查剧本是否存在
        stmt = select(Script).where(Script.id == SCRIPT_ID)
        result = await db.execute(stmt)
        script = result.scalar_one_or_none()
        
        if not script:
            print("⚠️  Script not found. Please run seed_script.py first.")
            return
        
        print(f"🌟 Creating convergence points for script: {script.title}")
        
        # 清理旧的集合点
        await db.execute(text("DELETE FROM convergence_points WHERE script_id = :sid"), {"sid": SCRIPT_ID})
        await db.commit()
        
        # 集合点1: 命运的相遇
        print("  📍 Creating convergence point: 命运的相遇")
        cp1 = ConvergencePoint(
            id=CP_CH1,
            script_id=SCRIPT_ID,
            chapter=1,
            title="命运的相遇",
            description="在樱花飘落的季节，你与三位性格迥异的少女相遇...",
            required_rounds={"yukino": 4, "hina": 5, "kaguya": 4},
            content={
                "preset": False,
                "template": "在樱花飘落的季节，你与三位性格迥异的少女相遇...",
            },
            is_final=False,
        )
        db.add(cp1)
        
        # 集合点2: 暗影袭击
        print("  📍 Creating convergence point: 暗影袭击")
        cp2 = ConvergencePoint(
            id=CP_CH2,
            script_id=SCRIPT_ID,
            chapter=2,
            title="暗影袭击",
            description="黑暗势力突然袭来，你们必须联手对抗...",
            required_rounds={"yukino": 9, "hina": 11, "kaguya": 9},
            content={
                "preset": False,
                "template": "黑暗势力突然袭来，你们必须联手对抗...",
            },
            is_final=False,
        )
        db.add(cp2)
        
        # 集合点3: 真相揭露
        print("  📍 Creating convergence point: 真相揭露")
        cp3 = ConvergencePoint(
            id=CP_CH3,
            script_id=SCRIPT_ID,
            chapter=3,
            title="真相揭露",
            description="在最终的考验中，你发现了隐藏在异世界背后的真相...",
            required_rounds={"yukino": 13, "hina": 16, "kaguya": 13},
            content={
                "preset": False,
                "template": "在最终的考验中，你发现了隐藏在异世界背后的真相...",
            },
            is_final=True,
        )
        db.add(cp3)
        
        await db.commit()
        
        print("\n✅ Convergence points created successfully!")
        print(f"   Chapter 1: 命运的相遇 (yukino:4, hina:5, kaguya:4)")
        print(f"   Chapter 2: 暗影袭击 (yukino:9, hina:11, kaguya:9)")
        print(f"   Chapter 3: 真相揭露 (yukino:13, hina:16, kaguya:13) [FINAL]")


if __name__ == "__main__":
    asyncio.run(seed())
