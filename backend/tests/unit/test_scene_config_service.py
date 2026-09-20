"""Unit tests for SceneConfigService (CR-027)."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.services.scene_config_service import SceneConfigService
from app.schemas.scene_config import SceneConfigUpsert
from app.models.script import Script, Route, Node


@pytest_asyncio.fixture
async def scene_config_service():
    """Provide SceneConfigService instance."""
    return SceneConfigService()


@pytest_asyncio.fixture
async def test_node(db_session: AsyncSession):
    """Create a test node for scene config tests."""
    # Create script
    script = Script(
        id=uuid4(),
        slug="test-script",
        title="测试剧本",
        description="测试描述",
        genre="fantasy",
    )
    db_session.add(script)
    await db_session.flush()

    # Create route
    route = Route(
        id=uuid4(),
        script_id=script.id,
        title="测试路线",
    )
    db_session.add(route)
    await db_session.flush()

    # Create node
    node = Node(
        id=uuid4(),
        route_id=route.id,
        node_type="dialogue",
        content={"text": "测试节点内容"},
    )
    db_session.add(node)
    await db_session.commit()

    return node


@pytest.mark.asyncio
async def test_upsert_create(
    db_session: AsyncSession,
    scene_config_service: SceneConfigService,
    test_node: Node,
):
    """Test creating a new scene config."""
    data = SceneConfigUpsert(
        scene_name="月光森林",
        tags=["森林", "夜晚", "神秘"],
        description="月光透过树叶洒落，营造神秘氛围。",
    )
    config = await scene_config_service.upsert(db_session, test_node.id, data)

    assert config.id is not None
    assert config.node_id == str(test_node.id)
    assert config.scene_name == "月光森林"
    assert config.tags == ["森林", "夜晚", "神秘"]
    assert config.description == "月光透过树叶洒落，营造神秘氛围。"


@pytest.mark.asyncio
async def test_upsert_update(
    db_session: AsyncSession,
    scene_config_service: SceneConfigService,
    test_node: Node,
):
    """Test updating an existing scene config."""
    # Create initial config
    data1 = SceneConfigUpsert(
        scene_name="原始场景",
        tags=["原始"],
        description="原始描述",
    )
    await scene_config_service.upsert(db_session, test_node.id, data1)

    # Update config
    data2 = SceneConfigUpsert(
        scene_name="更新场景",
        tags=["更新", "测试"],
        description="更新描述",
    )
    updated = await scene_config_service.upsert(db_session, test_node.id, data2)

    assert updated.scene_name == "更新场景"
    assert updated.tags == ["更新", "测试"]
    assert updated.description == "更新描述"


@pytest.mark.asyncio
async def test_upsert_node_not_found(
    db_session: AsyncSession,
    scene_config_service: SceneConfigService,
):
    """Test upserting scene config for non-existent node."""
    data = SceneConfigUpsert(scene_name="测试", tags=["测试"])

    with pytest.raises(ValueError, match="Node .* not found"):
        await scene_config_service.upsert(db_session, uuid4(), data)


@pytest.mark.asyncio
async def test_get_by_node_id(
    db_session: AsyncSession,
    scene_config_service: SceneConfigService,
    test_node: Node,
):
    """Test getting scene config by node ID."""
    data = SceneConfigUpsert(
        scene_name="古堡",
        tags=["古堡", "历史"],
        description="一座废弃的古堡",
    )
    created = await scene_config_service.upsert(db_session, test_node.id, data)
    retrieved = await scene_config_service.get_by_node_id(db_session, test_node.id)

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.scene_name == "古堡"


@pytest.mark.asyncio
async def test_get_by_node_id_not_found(
    db_session: AsyncSession,
    scene_config_service: SceneConfigService,
):
    """Test getting scene config for node without config."""
    retrieved = await scene_config_service.get_by_node_id(db_session, uuid4())
    assert retrieved is None


@pytest.mark.asyncio
async def test_delete(
    db_session: AsyncSession,
    scene_config_service: SceneConfigService,
    test_node: Node,
):
    """Test deleting a scene config."""
    data = SceneConfigUpsert(
        scene_name="待删除",
        tags=["测试"],
    )
    await scene_config_service.upsert(db_session, test_node.id, data)

    # Delete
    success = await scene_config_service.delete(db_session, test_node.id)
    assert success is True

    # Should not be retrievable
    retrieved = await scene_config_service.get_by_node_id(db_session, test_node.id)
    assert retrieved is None


@pytest.mark.asyncio
async def test_delete_not_found(
    db_session: AsyncSession,
    scene_config_service: SceneConfigService,
):
    """Test deleting non-existent scene config."""
    success = await scene_config_service.delete(db_session, uuid4())
    assert success is False


@pytest.mark.asyncio
async def test_list(
    db_session: AsyncSession,
    scene_config_service: SceneConfigService,
    test_node: Node,
):
    """Test listing scene configs."""
    # Create config
    data = SceneConfigUpsert(
        scene_name="测试场景",
        tags=["测试"],
    )
    await scene_config_service.upsert(db_session, test_node.id, data)

    # List all
    configs = await scene_config_service.list(db_session)
    assert len(configs) >= 1
    assert any(c.node_id == str(test_node.id) for c in configs)


@pytest.mark.asyncio
async def test_list_empty(db_session: AsyncSession, scene_config_service: SceneConfigService):
    """Test listing when no scene configs exist."""
    configs = await scene_config_service.list(db_session)
    # May have configs from other tests, but should not error
    assert isinstance(configs, list)


@pytest.mark.asyncio
async def test_get_by_node_id_returns_none_for_unconfigured_node(
    db_session: AsyncSession,
    scene_config_service: SceneConfigService,
    test_node: Node,
):
    """Test that get_by_node_id returns None for node without scene config."""
    # Node exists but has no scene config
    retrieved = await scene_config_service.get_by_node_id(db_session, test_node.id)
    assert retrieved is None
