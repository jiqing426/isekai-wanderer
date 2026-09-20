"""Unit tests for LorebookService (CR-027)."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.services.lorebook_service import LorebookService
from app.schemas.lorebook import LorebookEntryCreate, LorebookEntryUpdate
from uuid import UUID


@pytest_asyncio.fixture
async def lorebook_service():
    """Provide LorebookService instance."""
    return LorebookService()


@pytest.mark.asyncio
async def test_create(db_session: AsyncSession, lorebook_service: LorebookService):
    """Test creating a lorebook entry."""
    data = LorebookEntryCreate(
        title="月光森林",
        content="一片神秘的森林，月光透过树叶洒落。",
        tags=["森林", "夜晚", "神秘"],
        priority=10,
    )
    entry = await lorebook_service.create(db_session, data)

    assert entry.id is not None
    assert entry.title == "月光森林"
    assert entry.content == "一片神秘的森林，月光透过树叶洒落。"
    assert entry.tags == ["森林", "夜晚", "神秘"]
    assert entry.priority == 10
    assert entry.status == "active"


@pytest.mark.asyncio
async def test_get(db_session: AsyncSession, lorebook_service: LorebookService):
    """Test getting a lorebook entry by ID."""
    data = LorebookEntryCreate(
        title="古堡",
        content="一座废弃的古堡，充满神秘气息。",
        tags=["古堡", "废弃", "神秘"],
        priority=5,
    )
    created = await lorebook_service.create(db_session, data)
    retrieved = await lorebook_service.get(db_session, UUID(created.id))

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.title == "古堡"


@pytest.mark.asyncio
async def test_get_not_found(db_session: AsyncSession, lorebook_service: LorebookService):
    """Test getting a non-existent lorebook entry."""
    retrieved = await lorebook_service.get(db_session, uuid4())
    assert retrieved is None


@pytest.mark.asyncio
async def test_update(db_session: AsyncSession, lorebook_service: LorebookService):
    """Test updating a lorebook entry."""
    data = LorebookEntryCreate(
        title="原始标题",
        content="原始内容",
        tags=["原始"],
        priority=1,
    )
    created = await lorebook_service.create(db_session, data)

    update_data = LorebookEntryUpdate(
        title="更新标题",
        content="更新内容",
        tags=["更新", "测试"],
        priority=10,
    )
    updated = await lorebook_service.update(db_session, UUID(created.id), update_data)

    assert updated is not None
    assert updated.title == "更新标题"
    assert updated.content == "更新内容"
    assert updated.tags == ["更新", "测试"]
    assert updated.priority == 10


@pytest.mark.asyncio
async def test_update_not_found(db_session: AsyncSession, lorebook_service: LorebookService):
    """Test updating a non-existent lorebook entry."""
    update_data = LorebookEntryUpdate(title="新标题")
    updated = await lorebook_service.update(db_session, uuid4(), update_data)
    assert updated is None


@pytest.mark.asyncio
async def test_soft_delete(db_session: AsyncSession, lorebook_service: LorebookService):
    """Test soft deleting a lorebook entry."""
    data = LorebookEntryCreate(
        title="待删除",
        content="即将被删除的条目",
        tags=["测试"],
        priority=0,
    )
    created = await lorebook_service.create(db_session, data)

    # Soft delete
    success = await lorebook_service.soft_delete(db_session, UUID(created.id))
    assert success is True

    # Should not be retrievable
    retrieved = await lorebook_service.get(db_session, UUID(created.id))
    assert retrieved is None


@pytest.mark.asyncio
async def test_soft_delete_not_found(db_session: AsyncSession, lorebook_service: LorebookService):
    """Test soft deleting a non-existent lorebook entry."""
    success = await lorebook_service.soft_delete(db_session, uuid4())
    assert success is False


@pytest.mark.asyncio
async def test_list(db_session: AsyncSession, lorebook_service: LorebookService):
    """Test listing lorebook entries with pagination."""
    # Create multiple entries
    for i in range(5):
        data = LorebookEntryCreate(
            title=f"条目{i}",
            content=f"内容{i}",
            tags=["测试"],
            priority=i,
        )
        await lorebook_service.create(db_session, data)

    # List with pagination
    result = await lorebook_service.list(db_session, page=1, page_size=3)
    assert result.total == 5
    assert len(result.items) == 3
    assert result.page == 1
    assert result.page_size == 3

    # Second page
    result2 = await lorebook_service.list(db_session, page=2, page_size=3)
    assert len(result2.items) == 2


@pytest.mark.asyncio
async def test_list_empty(db_session: AsyncSession, lorebook_service: LorebookService):
    """Test listing when no entries exist."""
    result = await lorebook_service.list(db_session, page=1, page_size=20)
    assert result.total == 0
    assert len(result.items) == 0


@pytest.mark.asyncio
async def test_list_by_tag(db_session: AsyncSession, lorebook_service: LorebookService):
    """Test listing lorebook entries filtered by tag."""
    # Create entries with different tags
    await lorebook_service.create(
        db_session,
        LorebookEntryCreate(title="森林", content="内容", tags=["森林", "自然"], priority=1),
    )
    await lorebook_service.create(
        db_session,
        LorebookEntryCreate(title="古堡", content="内容", tags=["古堡", "历史"], priority=2),
    )
    await lorebook_service.create(
        db_session,
        LorebookEntryCreate(title="森林古堡", content="内容", tags=["森林", "古堡"], priority=3),
    )

    # Filter by tag "森林"
    result = await lorebook_service.list(db_session, tag="森林")
    assert result.total == 2
    assert all("森林" in item.tags for item in result.items)


@pytest.mark.asyncio
async def test_match_by_tags(db_session: AsyncSession, lorebook_service: LorebookService):
    """Test matching lorebook entries by tag intersection."""
    # Create entries
    await lorebook_service.create(
        db_session,
        LorebookEntryCreate(title="森林", content="内容", tags=["森林", "夜晚"], priority=5),
    )
    await lorebook_service.create(
        db_session,
        LorebookEntryCreate(title="古堡", content="内容", tags=["古堡", "神秘"], priority=10),
    )
    await lorebook_service.create(
        db_session,
        LorebookEntryCreate(title="森林古堡", content="内容", tags=["森林", "古堡"], priority=8),
    )

    # Match by tags ["森林", "神秘"]
    matched = await lorebook_service.match_by_tags(db_session, ["森林", "神秘"])
    assert len(matched) == 3
    # Should be ordered by priority DESC
    assert matched[0].priority == 10  # 古堡
    assert matched[1].priority == 8   # 森林古堡
    assert matched[2].priority == 5   # 森林


@pytest.mark.asyncio
async def test_match_by_tags_empty(db_session: AsyncSession, lorebook_service: LorebookService):
    """Test matching with empty tags list."""
    matched = await lorebook_service.match_by_tags(db_session, [])
    assert matched == []


@pytest.mark.asyncio
async def test_match_by_tags_no_match(db_session: AsyncSession, lorebook_service: LorebookService):
    """Test matching when no entries match."""
    await lorebook_service.create(
        db_session,
        LorebookEntryCreate(title="森林", content="内容", tags=["森林"], priority=1),
    )

    matched = await lorebook_service.match_by_tags(db_session, ["不存在的标签"])
    assert matched == []
