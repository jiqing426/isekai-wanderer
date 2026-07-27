"""Unit tests for Discover API endpoints."""
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_get_trending(client):
    """Test GET /api/v1/discover/trending returns 200 with trending list."""
    response = await client.get("/api/v1/discover/trending")
    assert response.status_code == 200
    data = response.json()
    assert "trending" in data
    assert isinstance(data["trending"], list)
    assert "total" in data


@pytest.mark.asyncio
async def test_get_recommendations(client):
    """Test GET /api/v1/discover/recommendations returns 200 with recommendations list."""
    response = await client.get("/api/v1/discover/recommendations")
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)
    assert "total" in data


@pytest.mark.asyncio
async def test_get_categories(client):
    """Test GET /api/v1/discover/categories returns 200 with categories list."""
    response = await client.get("/api/v1/discover/categories")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert isinstance(data["categories"], list)
    # Should have predefined categories
    assert len(data["categories"]) > 0


@pytest.mark.asyncio
async def test_get_characters(client):
    """Test GET /api/v1/characters returns 200 with characters list."""
    response = await client.get("/api/v1/characters")
    assert response.status_code == 200
    data = response.json()
    assert "characters" in data
    assert isinstance(data["characters"], list)
    assert "total" in data


@pytest.mark.asyncio
async def test_get_saves(client):
    """Test GET /api/v1/saves returns 200 with saves list."""
    response = await client.get("/api/v1/saves")
    assert response.status_code == 200
    data = response.json()
    assert "saves" in data
    assert isinstance(data["saves"], list)
