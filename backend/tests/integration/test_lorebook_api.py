"""Integration tests for Lorebook API (CR-027 T-003)."""

import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio
async def test_create_lorebook_entry(client: AsyncClient, admin_token: str):
    """Test creating a lorebook entry."""
    payload = {
        "title": "测试条目",
        "content": "这是测试内容",
        "tags": ["测试", "集成"],
        "priority": 10
    }
    
    response = await client.post(
        "/api/v1/lorebook",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "测试条目"
    assert data["content"] == "这是测试内容"
    assert data["tags"] == ["测试", "集成"]
    assert data["priority"] == 10
    assert data["status"] == "active"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_lorebook_entries(client: AsyncClient, admin_token: str):
    """Test listing lorebook entries."""
    response = await client.get(
        "/api/v1/lorebook",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_list_lorebook_with_tag_filter(client: AsyncClient, admin_token: str):
    """Test listing lorebook entries with tag filter."""
    response = await client.get(
        "/api/v1/lorebook?tag=测试",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


@pytest.mark.asyncio
async def test_get_lorebook_entry(client: AsyncClient, admin_token: str):
    """Test getting a specific lorebook entry."""
    # First create an entry
    create_payload = {
        "title": "获取测试",
        "content": "获取测试内容",
        "tags": ["获取"],
        "priority": 5
    }
    create_response = await client.post(
        "/api/v1/lorebook",
        json=create_payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    entry_id = create_response.json()["id"]
    
    # Then get it
    response = await client.get(
        f"/api/v1/lorebook/{entry_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == entry_id
    assert data["title"] == "获取测试"


@pytest.mark.asyncio
async def test_update_lorebook_entry(client: AsyncClient, admin_token: str):
    """Test updating a lorebook entry."""
    # Create entry
    create_payload = {
        "title": "更新前",
        "content": "原始内容",
        "tags": ["原始"],
        "priority": 1
    }
    create_response = await client.post(
        "/api/v1/lorebook",
        json=create_payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    entry_id = create_response.json()["id"]
    
    # Update it
    update_payload = {
        "title": "更新后",
        "content": "更新内容",
        "tags": ["更新"],
        "priority": 10
    }
    response = await client.put(
        f"/api/v1/lorebook/{entry_id}",
        json=update_payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "更新后"
    assert data["content"] == "更新内容"
    assert data["tags"] == ["更新"]
    assert data["priority"] == 10


@pytest.mark.asyncio
async def test_delete_lorebook_entry(client: AsyncClient, admin_token: str):
    """Test soft deleting a lorebook entry."""
    # Create entry
    create_payload = {
        "title": "删除测试",
        "content": "即将删除",
        "tags": ["删除"],
        "priority": 1
    }
    create_response = await client.post(
        "/api/v1/lorebook",
        json=create_payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    entry_id = create_response.json()["id"]
    
    # Delete it
    response = await client.delete(
        f"/api/v1/lorebook/{entry_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Lorebook entry deleted"


@pytest.mark.asyncio
async def test_lorebook_forbidden_for_non_admin(client: AsyncClient, user_token: str):
    """Test that non-admin users cannot access lorebook API."""
    # Try to list
    response = await client.get(
        "/api/v1/lorebook",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403
    
    # Try to create
    payload = {
        "title": "未授权",
        "content": "不应该成功",
        "tags": ["测试"],
        "priority": 1
    }
    response = await client.post(
        "/api/v1/lorebook",
        json=payload,
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403
