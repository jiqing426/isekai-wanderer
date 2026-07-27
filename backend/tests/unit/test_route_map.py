"""
Test cases for Route Map endpoint (DEV-CR2-001).

AC-045: After completing a script, the user can view a route exploration map
from the script detail page. Explored branches are highlighted, unexplored
branches are grayed out.

API: GET /api/v1/game/{scriptId}/route-map
Auth: Bearer
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.script import Script, Route, Node, NodeChoice
from app.models.game import GameSession
from app.models.user import User


@pytest.mark.asyncio
async def test_route_map_returns_script_routes(client: AsyncClient, db_session: AsyncSession):
    """AC-045: Route map should return all routes for a script."""
    from app.core.security import create_access_token, get_password_hash

    user = User(email="test@example.com", password_hash=get_password_hash("password"), display_name="Test", email_verified=True)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    script = Script(slug="test-script", title="Test Script", genre="fantasy")
    db_session.add(script)
    await db_session.commit()
    await db_session.refresh(script)

    route1 = Route(script_id=script.id, title="Route A", description="First route")
    route2 = Route(script_id=script.id, title="Route B", description="Second route")
    db_session.add_all([route1, route2])
    await db_session.commit()

    token = create_access_token({"sub": str(user.id)})

    resp = await client.get(
        f"/api/v1/game/{script.id}/route-map",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert "routes" in data
    assert len(data["routes"]) == 2
    route_titles = {r["title"] for r in data["routes"]}
    assert route_titles == {"Route A", "Route B"}


@pytest.mark.asyncio
async def test_route_map_marks_explored_routes(client: AsyncClient, db_session: AsyncSession):
    """AC-045: Routes with completed game sessions should be marked as explored."""
    from app.core.security import create_access_token

    user = User(email="test2@example.com", password_hash="hash", display_name="Test2", email_verified=True)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    script = Script(slug="explored-script", title="Explored Script", genre="fantasy")
    db_session.add(script)
    await db_session.commit()
    await db_session.refresh(script)

    route_a = Route(script_id=script.id, title="Explored Route", description="Done")
    route_b = Route(script_id=script.id, title="Unexplored Route", description="Not done")
    db_session.add_all([route_a, route_b])
    await db_session.commit()
    await db_session.refresh(route_a)
    await db_session.refresh(route_b)

    # Create a completed game session for route_a
    game_session = GameSession(
        user_id=user.id,
        script_id=script.id,
        route_id=route_a.id,
        status="completed",
        ending_type="good",
    )
    db_session.add(game_session)
    await db_session.commit()

    token = create_access_token({"sub": str(user.id)})
    resp = await client.get(
        f"/api/v1/game/{script.id}/route-map",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200
    data = resp.json()

    for r in data["routes"]:
        if r["title"] == "Explored Route":
            assert r["explored"] is True
            assert r["endings"] is not None
        elif r["title"] == "Unexplored Route":
            assert r["explored"] is False


@pytest.mark.asyncio
async def test_route_map_requires_auth(client: AsyncClient, db_session: AsyncSession):
    """AC-045: Route map endpoint requires authentication."""
    script = Script(slug="auth-test", title="Auth Test", genre="fantasy")
    db_session.add(script)
    await db_session.commit()
    await db_session.refresh(script)

    # No Authorization header
    resp = await client.get(f"/api/v1/game/{script.id}/route-map")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_route_map_returns_nodes_and_choices(client: AsyncClient, db_session: AsyncSession):
    """AC-045: Each route should include its nodes and choice branches."""
    from app.core.security import create_access_token

    user = User(email="nodetest@example.com", password_hash="hash", display_name="NodeTest", email_verified=True)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    script = Script(slug="node-script", title="Node Script", genre="fantasy")
    db_session.add(script)
    await db_session.commit()
    await db_session.refresh(script)

    route = Route(script_id=script.id, title="Main Route", description="Main")
    db_session.add(route)
    await db_session.commit()
    await db_session.refresh(route)

    # Create nodes
    root_node = Node(route_id=route.id, node_type="start", content={"text": "Beginning"})
    db_session.add(root_node)
    await db_session.commit()
    await db_session.refresh(root_node)

    child_node = Node(route_id=route.id, node_type="scene", content={"text": "Middle"}, parent_id=root_node.id)
    db_session.add(child_node)
    await db_session.commit()
    await db_session.refresh(child_node)

    choice = NodeChoice(node_id=root_node.id, text="Go forward", next_node_id=child_node.id, affection_delta=5)
    db_session.add(choice)
    await db_session.commit()

    token = create_access_token({"sub": str(user.id)})
    resp = await client.get(
        f"/api/v1/game/{script.id}/route-map",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200
    data = resp.json()
    route_data = data["routes"][0]
    assert "nodes" in route_data
    assert len(route_data["nodes"]) >= 2


@pytest.mark.asyncio
async def test_route_map_invalid_script_id(client: AsyncClient, db_session: AsyncSession):
    """AC-045: Non-existent script should return 404."""
    from app.core.security import create_access_token
    import uuid

    user = User(email="404test@example.com", password_hash="hash", display_name="T", email_verified=True)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    fake_id = str(uuid.uuid4())
    resp = await client.get(
        f"/api/v1/game/{fake_id}/route-map",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 404
