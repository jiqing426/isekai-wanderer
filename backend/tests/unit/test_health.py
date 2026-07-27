"""Health endpoint tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test that health endpoint returns 200 with correct response."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


@pytest.mark.asyncio
async def test_health_endpoint_no_auth(client: AsyncClient):
    """Test that health endpoint doesn't require authentication."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
