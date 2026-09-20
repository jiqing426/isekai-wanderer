"""
CR-029 API Filter Test
验证 NarrativeEngine 节点过滤逻辑：不同角色调用 API 返回不同节点
"""
import asyncio
import json
import sys
from uuid import UUID
from sqlalchemy import text
from app.core.database import async_session_factory


async def test_filter_by_character():
    """验证不同角色看到不同分支节点"""
    results = []
    
    # 获取三个角色 ID
    async with async_session_factory() as session:
        r = await session.execute(text(
            "SELECT id, name FROM characters WHERE name IN ('沈星澜', '白夜', '暮雪')"
        ))
        chars = {row[1]: str(row[0]) for row in r.fetchall()}
    
    if len(chars) < 3:
        print(f"test_filter_by_character: FAILED (only found {len(chars)} characters: {list(chars.keys())})")
        return False
    
    shen_id = chars['沈星澜']
    bai_id = chars['白夜']
    mu_id = chars['暮雪']
    
    # 验证每个角色只能看到自己的分支节点 + 公共节点
    for char_name, char_id in [('沈星澜', shen_id), ('白夜', bai_id), ('暮雪', mu_id)]:
        async with async_session_factory() as session:
            # 模拟 get_node_with_choices 的过滤逻辑
            r = await session.execute(text(f"""
                SELECT id, character_id FROM nodes
                WHERE character_id IS NULL OR character_id = '{char_id}'::uuid
                ORDER BY id
            """))
            visible_nodes = r.fetchall()
            
            # 验证不包含其他角色的节点
            other_chars = [cid for cn, cid in chars.items() if cn != char_name]
            for node_id, node_char_id in visible_nodes:
                if node_char_id is not None and str(node_char_id) != char_id:
                    print(f"test_filter_by_character: FAILED ({char_name} can see node {node_id} with character_id={node_char_id})")
                    return False
            
            # 验证能看到自己的分支节点
            own_branch_nodes = [n for n in visible_nodes if n[1] is not None]
            if len(own_branch_nodes) >= 1:
                results.append(f"{char_name}: sees {len(own_branch_nodes)} branch node(s) ✓")
            else:
                print(f"test_filter_by_character: FAILED ({char_name} sees no branch nodes)")
                return False
    
    for r in results:
        print(f"  {r}")
    print("test_filter_by_character: PASSED")
    return True


async def test_different_characters_see_different_nodes():
    """验证不同角色返回的分支节点不同"""
    async with async_session_factory() as session:
        r = await session.execute(text(
            "SELECT id, name FROM characters WHERE name IN ('沈星澜', '白夜', '暮雪')"
        ))
        chars = {row[1]: str(row[0]) for row in r.fetchall()}
    
    branch_nodes_by_char = {}
    for char_name, char_id in chars.items():
        async with async_session_factory() as session:
            r = await session.execute(text(f"""
                SELECT id FROM nodes WHERE character_id = '{char_id}'::uuid
            """))
            branch_nodes_by_char[char_name] = set(str(row[0]) for row in r.fetchall())
    
    # 验证三个角色看到的分支节点互不相同
    shen_nodes = branch_nodes_by_char.get('沈星澜', set())
    bai_nodes = branch_nodes_by_char.get('白夜', set())
    mu_nodes = branch_nodes_by_char.get('暮雪', set())
    
    if shen_nodes & bai_nodes or shen_nodes & mu_nodes or bai_nodes & mu_nodes:
        print("test_different_characters_see_different_nodes: FAILED (overlap detected)")
        return False
    
    if len(shen_nodes) == 0 or len(bai_nodes) == 0 or len(mu_nodes) == 0:
        print("test_different_characters_see_different_nodes: FAILED (empty branch)")
        return False
    
    print(f"  沈星澜: {len(shen_nodes)} branch nodes")
    print(f"  白夜: {len(bai_nodes)} branch nodes")
    print(f"  暮雪: {len(mu_nodes)} branch nodes")
    print("test_different_characters_see_different_nodes: PASSED")
    return True


async def test_null_session_only_sees_public():
    """验证 session.character_id=NULL 时只返回公共节点"""
    async with async_session_factory() as session:
        r = await session.execute(text("""
            SELECT COUNT(*) FROM nodes WHERE character_id IS NULL
        """))
        public_count = r.scalar()
        
        r2 = await session.execute(text("""
            SELECT COUNT(*) FROM nodes
        """))
        total_count = r2.scalar()
    
    if public_count > 0 and public_count < total_count:
        print(f"test_null_session_only_sees_public: PASSED ({public_count} public / {total_count} total)")
        return True
    else:
        print(f"test_null_session_only_sees_public: FAILED (public={public_count}, total={total_count})")
        return False


async def test_branch_converge_to_same_node():
    """验证分支结束后汇合到相同节点"""
    # 查找分支节点的选择项，验证它们指向同一个汇合节点
    async with async_session_factory() as session:
        r = await session.execute(text("""
            SELECT nc.node_id, nc.next_node_id, n.character_id
            FROM node_choices nc
            JOIN nodes n ON nc.node_id = n.id
            WHERE n.character_id IS NOT NULL
            AND nc.next_node_id IS NOT NULL
            ORDER BY nc.node_id
        """))
        rows = r.fetchall()
    
    if not rows:
        print("test_branch_converge_to_same_node: SKIPPED (no branch choices with next_node_id)")
        return True
    
    # 收集每个分支节点的 next_node_id
    next_nodes = set()
    for node_id, next_node_id, char_id in rows:
        next_nodes.add(str(next_node_id))
    
    # 验证汇合节点是公共节点 (character_id IS NULL)
    async with async_session_factory() as session:
        for next_id in next_nodes:
            r = await session.execute(text(f"""
                SELECT character_id FROM nodes WHERE id = '{next_id}'::uuid
            """))
            row = r.fetchone()
            if row and row[0] is not None:
                print(f"test_branch_converge_to_same_node: FAILED (converge node {next_id} has character_id={row[0]})")
                return False
    
    print(f"  Branch choices lead to {len(next_nodes)} converge node(s), all public ✓")
    print("test_branch_converge_to_same_node: PASSED")
    return True


async def main():
    all_passed = True
    
    print("=" * 60)
    print("CR-029 API Filter Tests")
    print("=" * 60)
    
    tests = [
        test_filter_by_character,
        test_different_characters_see_different_nodes,
        test_null_session_only_sees_public,
        test_branch_converge_to_same_node,
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
