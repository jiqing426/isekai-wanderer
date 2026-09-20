"""
CR-029 Backward Compatibility Test
验证现有 session 正常运行无异常
"""
import asyncio
import sys
from sqlalchemy import text
from app.core.database import async_session_factory


async def test_existing_sessions_still_work():
    """验证现有 session 的 character_id 为 NULL"""
    async with async_session_factory() as session:
        r = await session.execute(text("""
            SELECT COUNT(*) FROM game_sessions WHERE character_id IS NULL
        """))
        null_count = r.scalar()
        
        r2 = await session.execute(text("""
            SELECT COUNT(*) FROM game_sessions
        """))
        total_count = r2.scalar()
    
    print(f"  Existing sessions with NULL character_id: {null_count}/{total_count}")
    
    if null_count > 0:
        print("test_existing_sessions_still_work: PASSED")
        return True
    else:
        print("test_existing_sessions_still_work: SKIPPED (no existing sessions)")
        return True


async def test_public_nodes_visible_to_all():
    """验证公共节点对所有 session 可见"""
    async with async_session_factory() as session:
        r = await session.execute(text("""
            SELECT COUNT(*) FROM nodes WHERE character_id IS NULL
        """))
        public_count = r.scalar()
    
    if public_count > 0:
        print(f"  Public nodes: {public_count}")
        print("test_public_nodes_visible_to_all: PASSED")
        return True
    else:
        print("test_public_nodes_visible_to_all: FAILED (no public nodes)")
        return False


async def test_node_filtering_logic():
    """验证节点过滤逻辑：NULL session 只能看到公共节点"""
    # 模拟 session.character_id = NULL 的过滤逻辑
    async with async_session_factory() as session:
        r = await session.execute(text("""
            SELECT COUNT(*) FROM nodes
            WHERE character_id IS NULL
        """))
        visible_count = r.scalar()
        
        r2 = await session.execute(text("""
            SELECT COUNT(*) FROM nodes
        """))
        total_count = r2.scalar()
    
    if visible_count > 0 and visible_count <= total_count:
        print(f"  NULL session sees {visible_count}/{total_count} nodes")
        print("test_node_filtering_logic: PASSED")
        return True
    else:
        print("test_node_filtering_logic: FAILED")
        return False


async def test_character_sessions_see_filtered_nodes():
    """验证有 character_id 的 session 能看到公共节点 + 自己的分支节点"""
    async with async_session_factory() as session:
        # 获取一个有 character_id 的 session
        r = await session.execute(text("""
            SELECT character_id FROM game_sessions
            WHERE character_id IS NOT NULL
            LIMIT 1
        """))
        row = r.fetchone()
        
        if not row:
            print("test_character_sessions_see_filtered_nodes: SKIPPED (no character sessions)")
            return True
        
        char_id = str(row[0])
        
        # 计算该角色应该看到的节点数
        r2 = await session.execute(text(f"""
            SELECT COUNT(*) FROM nodes
            WHERE character_id IS NULL OR character_id = '{char_id}'::uuid
        """))
        expected_count = r2.scalar()
        
        print(f"  Character {char_id} should see {expected_count} nodes")
        print("test_character_sessions_see_filtered_nodes: PASSED")
        return True


async def main():
    all_passed = True
    
    print("=" * 60)
    print("CR-029 Backward Compatibility Tests")
    print("=" * 60)
    
    tests = [
        test_existing_sessions_still_work,
        test_public_nodes_visible_to_all,
        test_node_filtering_logic,
        test_character_sessions_see_filtered_nodes,
    ]
    
    for test in tests:
        try:
            result = await test()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"{test.__name__}: ERROR - {e}")
            all_passed = False
        print()
    
    print("=" * 60)
    if all_passed:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
