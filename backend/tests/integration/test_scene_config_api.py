"""Integration tests for Scene Config API (CR-027 T-005)."""

import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio
async def test_upsert_scene_config(client: AsyncClient, admin_token: str, test_node_id: str):
    """Test creating/updating a scene config."""
    payload = {
        "scene_name": "测试场景",
        "tags": ["测试", "场景"],
        "description": "这是一个测试场景"
    }
    
    response = await client.put(
        f"/api/v1/scene-configs/node/{test_node_id}",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["scene_name"] == "测试场景"
    assert data["tags"] == ["测试", "场景"]
    assert data["description"] == "这是一个测试场景"
    assert data["node_id"] == test_node_id


@pytest.mark.asyncio
async def test_get_scene_config(client: AsyncClient, admin_token: str, test_node_id: str):
    """Test getting a scene config by node_id."""
    # First create a config
    payload = {
        "scene_name": "获取测试场景",
        "tags": ["获取"],
        "description": "获取测试描述"
    }
    await client.put(
        f"/api/v1/scene-configs/node/{test_node_id}",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Then get it
    response = await client.get(
        f"/api/v1/scene-configs/node/{test_node_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["scene_name"] == "获取测试场景"
    assert data["node_id"] == test_node_id


@pytest.mark.asyncio
async def test_delete_scene_config(client: AsyncClient, admin_token: str, test_node_id: str):
    """Test deleting a scene config."""
    # First create a config
    payload = {
        "scene_name": "删除测试场景",
        "tags": ["删除"],
        "description": "即将删除"
    }
    await client.put(
        f"/api/v1/scene-configs/node/{test_node_id}",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Then delete it
    response = await client.delete(
        f"/api/v1/scene-configs/node/{test_node_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Scene config deleted"


@pytest.mark.asyncio
async def test_list_scene_configs(client: AsyncClient, admin_token: str):
    """Test listing scene configs."""
    response = await client.get(
        "/api/v1/scene-configs",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_scene_config_forbidden_for_non_admin(client: AsyncClient, user_token: str, test_node_id: str):
    """Test that non-admin users cannot access scene config API."""
    # Try to upsert
    payload = {
        "scene_name": "未授权",
        "tags": ["测试"],
        "description": "不应该成功"
    }
    response = await client.put(
        f"/api/v1/scene-configs/node/{test_node_id}",
        json=payload,
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403
    
    # Try to list
    response = await client.get(
        "/api/v1/scene-configs",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_scene_config_node_not_found(client: AsyncClient, admin_token: str):
    """Test upserting scene config for non-existent node."""
    fake_node_id = str(uuid4())
    payload = {
        "scene_name": "不存在的节点",
        "tags": ["测试"],
        "description": "应该失败"
    }
    
    response = await client.put(
        f"/api/v1/scene-configs/node/{fake_node_id}",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 404
