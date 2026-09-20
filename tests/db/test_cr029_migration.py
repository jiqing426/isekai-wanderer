"""
CR-029 Database Migration Test
验证 nodes 表新增 character_id 字段
"""
import pytest
from sqlalchemy import text
from app.core.database import async_session_factory


@pytest.mark.asyncio
async def test_nodes_table_has_character_id_column():
    """验证 nodes 表包含 character_id 字段"""
    async with async_session_factory() as session:
        result = await session.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'nodes' AND column_name = 'character_id'
        """))
        column = result.fetchone()
        
        assert column is not None, "nodes 表应该包含 character_id 字段"
        assert column[0] == 'character_id'
        assert column[1] == 'uuid'
        assert column[2] == 'YES'  # is_nullable


@pytest.mark.asyncio
async def test_nodes_table_has_character_id_index():
    """验证 nodes 表包含 character_id 索引"""
    async with async_session_factory() as session:
        result = await session.execute(text("""
            SELECT indexname
            FROM pg_indexes
            WHERE tablename = 'nodes' AND indexdef LIKE '%character_id%'
        """))
        indexes = result.fetchall()
        
        assert len(indexes) > 0, "nodes 表应该包含 character_id 索引"


@pytest.mark.asyncio
async def test_existing_nodes_have_null_character_id():
    """验证现有节点的 character_id 为 NULL"""
    async with async_session_factory() as session:
        result = await session.execute(text("""
            SELECT COUNT(*) FROM nodes WHERE character_id IS NULL
        """))
        null_count = result.scalar()
        
        result = await session.execute(text("""
            SELECT COUNT(*) FROM nodes
        """))
        total_count = result.scalar()
        
        # 大部分现有节点的 character_id 应该为 NULL
        assert null_count > 0, "应该存在 character_id 为 NULL 的节点"
        assert null_count >= total_count * 0.9, "90% 以上的节点 character_id 应该为 NULL"


@pytest.mark.asyncio
async def test_branch_nodes_have_character_id():
    """验证分支节点包含 character_id"""
    async with async_session_factory() as session:
        result = await session.execute(text("""
            SELECT COUNT(*) FROM nodes WHERE character_id IS NOT NULL
        """))
        branch_count = result.scalar()
        
        assert branch_count > 0, "应该存在 character_id 不为 NULL 的分支节点"


@pytest.mark.asyncio
async def test_migration_version():
    """验证迁移版本为 cr029_node_branch"""
    async with async_session_factory() as session:
        result = await session.execute(text("""
            SELECT version_num FROM alembic_version
        """))
        version = result.scalar()
        
        assert version == 'cr029_node_branch', f"迁移版本应该是 cr029_node_branch，实际为 {version}"
