#!/usr/bin/env python3
"""
T-008: UUID v4 数据迁移脚本

将硬编码的 UUID 迁移为随机 UUID v4。
使用 DEFERRED 约束或在事务中按正确顺序更新。
"""

import asyncio
import uuid
from sqlalchemy import text
from app.core.database import async_session_factory


# 硬编码的旧 ID 映射到新 UUID v4
OLD_TO_NEW = {
    # Scripts
    '11111111-1111-1111-1111-111111111111': str(uuid.uuid4()),
    'a1111111-1111-1111-1111-111111111111': str(uuid.uuid4()),
    '66666666-6666-6666-6666-666666666666': str(uuid.uuid4()),
    
    # Characters
    '22222222-2222-2222-2222-222222222222': str(uuid.uuid4()),
    'a2222222-2222-2222-2222-222222222222': str(uuid.uuid4()),
    '77777777-7777-7777-7777-777777777777': str(uuid.uuid4()),
    
    # Routes
    '33333333-3333-3333-3333-333333333333': str(uuid.uuid4()),
    'a3333333-3333-3333-3333-333333333333': str(uuid.uuid4()),
    '88888888-8888-8888-8888-888888888888': str(uuid.uuid4()),
    'b1111111-1111-1111-1111-111111111111': str(uuid.uuid4()),
    'b2222222-2222-2222-2222-222222222222': str(uuid.uuid4()),
    'b3333333-3333-3333-3333-333333333333': str(uuid.uuid4()),
    'c1111111-1111-1111-1111-111111111111': str(uuid.uuid4()),
    'c2222222-2222-2222-2222-222222222222': str(uuid.uuid4()),
    'c3333333-3333-3333-3333-333333333333': str(uuid.uuid4()),
    'd1111111-1111-1111-1111-111111111111': str(uuid.uuid4()),
    'd2222222-2222-2222-2222-222222222222': str(uuid.uuid4()),
    'd3333333-3333-3333-3333-333333333333': str(uuid.uuid4()),
}


async def migrate_uuid():
    """执行 UUID v4 迁移"""
    async with async_session_factory() as db:
        print("=== T-008: UUID v4 数据迁移 ===\n")
        
        # 打印映射关系
        print("旧 ID -> 新 UUID v4:")
        for old_id, new_id in OLD_TO_NEW.items():
            print(f"  {old_id} -> {new_id}")
        print()
        
        # 禁用外键约束（PostgreSQL 支持 SET CONSTRAINTS ALL DEFERRED）
        await db.execute(text("SET CONSTRAINTS ALL DEFERRED"))
        
        # 按正确顺序更新：先主表，后引用表
        update_order = [
            # 1. 主表（被引用的表）
            ("scripts", "id"),
            ("characters", "id"),
            ("routes", "id"),
            
            # 2. 引用 script_id 的表
            ("characters", "script_id"),
            ("routes", "script_id"),
            ("game_sessions", "script_id"),
            ("convergence_points", "script_id"),
            ("endings", "script_id"),
            ("free_chat_sessions", "script_id"),
            ("scenes", "script_id"),
            ("unlocked_scripts", "script_id"),
            ("user_dialogue_counts", "script_id"),
            ("cg_assets", "script_id"),
            
            # 3. 引用 character_id 的表
            ("affection", "character_id"),
            ("affection_history", "character_id"),
            ("character_memories", "character_id"),
            ("character_sprites", "character_id"),
            ("dialogue_history", "character_id"),
            ("free_chat_sessions", "character_id"),
            ("gift_records", "character_id"),
            
            # 4. 引用 route_id 的表
            ("nodes", "route_id"),
            ("endings", "route_id"),
            ("game_sessions", "route_id"),
            ("cg_assets", "route_id"),
        ]
        
        for table, column in update_order:
            for old_id, new_id in OLD_TO_NEW.items():
                # 检查该列是否包含这个旧 ID
                check_sql = f"SELECT COUNT(*) FROM {table} WHERE {column}::text = :old_id"
                result = await db.execute(text(check_sql), {"old_id": old_id})
                count = result.scalar()
                
                if count > 0:
                    update_sql = f"UPDATE {table} SET {column} = :new_id WHERE {column}::text = :old_id"
                    await db.execute(text(update_sql), {"new_id": new_id, "old_id": old_id})
                    print(f"✓ {table}.{column}: {count} 条记录 {old_id[:8]}... -> {new_id[:8]}...")
        
        await db.commit()
        print("\n=== 迁移完成 ===")
        
        # 验证
        print("\n验证新 ID:")
        for table in ["scripts", "characters", "routes"]:
            result = await db.execute(text(f"SELECT id::text FROM {table}"))
            ids = [row[0] for row in result.fetchall()]
            print(f"  {table}: {len(ids)} 条记录")
            for id in ids[:3]:
                print(f"    {id}")


if __name__ == "__main__":
    asyncio.run(migrate_uuid())
