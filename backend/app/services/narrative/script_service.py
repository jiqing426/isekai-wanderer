"""ScriptService - state machine for script node loading and transitions."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.script import Script, Route, Node, NodeChoice, Character
from app.models.game import GameSession, GameProgress
from app.core.exceptions import AppException


class ScriptService:
    """Manages script loading, node transitions, and state machine logic."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ---- Script / Route / Node loading ----

    async def get_script_with_routes(self, script_id: UUID) -> Optional[Script]:
        """Load script with all routes and nodes."""
        stmt = (
            select(Script)
            .options(
                selectinload(Script.routes).selectinload(Route.nodes).selectinload(Node.choices),
            )
            .where(Script.id == script_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_node_with_choices(self, node_id: UUID) -> Optional[Node]:
        """Load a single node with its choices."""
        stmt = (
            select(Node)
            .options(selectinload(Node.choices))
            .where(Node.id == node_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_starting_node(self, route_id: UUID) -> Node:
        """Get the starting node for a route (root node with no parent).
        
        Priority:
        1. preset type nodes (most reliable)
        2. Nodes with choices
        3. Any node with parent_id=None
        """
        # First try: preset type nodes
        stmt = (
            select(Node)
            .where(
                Node.route_id == route_id,
                Node.parent_id.is_(None),
                Node.node_type == "preset"
            )
            .order_by(Node.id)  # Consistent ordering
            .limit(1)
        )
        result = await self.db.execute(stmt)
        node = result.scalar_one_or_none()
        
        if node:
            return node
        
        # Second try: any node with parent_id=None, ordered by id
        stmt = (
            select(Node)
            .where(Node.route_id == route_id, Node.parent_id.is_(None))
            .order_by(Node.id)
            .limit(1)
        )
        result = await self.db.execute(stmt)
        node = result.scalar_one_or_none()

        if not node:
            raise AppException(
                error_code="SCRIPT_NO_START_NODE",
                status_code=404,
                message=f"No starting node found for route {route_id}",
            )

        return node

    # ---- Choice validation & transition ----

    async def get_next_node(self, choice_id: UUID) -> Optional[Node]:
        """Get the next node based on a choice."""
        stmt = select(NodeChoice).where(NodeChoice.id == choice_id)
        result = await self.db.execute(stmt)
        choice = result.scalar_one_or_none()

        if not choice or not choice.next_node_id:
            return None

        return await self.get_node_with_choices(choice.next_node_id)

    async def validate_choice(self, node_id: UUID, choice_id: UUID) -> bool:
        """Validate that a choice belongs to a node."""
        stmt = (
            select(NodeChoice)
            .where(NodeChoice.id == choice_id, NodeChoice.node_id == node_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    # ---- Node classification ----

    async def is_terminal_node(self, node: Node) -> bool:
        """Check if a node is terminal (explicitly marked as ending)."""
        # Only end session if node is explicitly marked as ending
        if node.content and node.content.get("is_ending"):
            return True
        
        # Check node_type for ending indicators
        if node.node_type in ["ending", "ending_node"]:
            return True
        
        # cg_trigger and converge_node are NOT terminal — they continue the story
        # fixed_scene, ai_dialog, choice_point are also NOT terminal
        
        # Node without choices is NOT terminal - it may be a dialogue node
        # that should continue or wait for user input
        return False

    def get_node_character_id(self, node: Node) -> Optional[UUID]:
        """Extract character_id from node content JSON."""
        if node.content and "character_id" in node.content:
            return UUID(node.content["character_id"])
        return None

    def get_ending_type(self, node: Node) -> Optional[str]:
        """Extract ending_type from node content JSON."""
        if node.content and "ending_type" in node.content:
            return node.content["ending_type"]
        return None

    # ---- Game session state ----

    async def get_game_session_state(self, session_id: UUID) -> Dict[str, Any]:
        """Get current game session state with current node."""
        stmt = select(GameSession).where(GameSession.id == session_id)
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()

        if not session:
            raise AppException(
                error_code="GAME_SESSION_NOT_FOUND",
                status_code=404,
                message=f"Game session {session_id} not found",
            )

        current_node = None
        if session.current_node_id:
            current_node = await self.get_node_with_choices(session.current_node_id)

        return {
            "session": session,
            "current_node": current_node,
            "is_ended": session.status == "completed",
        }

    async def advance_session(
        self, session_id: UUID, choice_id: UUID
    ) -> Dict[str, Any]:
        """Advance game session by making a choice and moving to next node."""
        state = await self.get_game_session_state(session_id)
        session = state["session"]
        current_node = state["current_node"]

        if state["is_ended"]:
            raise AppException(
                error_code="GAME_SESSION_ENDED",
                status_code=400,
                message="Game session has already ended",
            )

        if not current_node:
            raise AppException(
                error_code="GAME_NO_CURRENT_NODE",
                status_code=400,
                message="Session has no current node",
            )

        is_valid = await self.validate_choice(current_node.id, choice_id)
        if not is_valid:
            raise AppException(
                error_code="GAME_INVALID_CHOICE",
                status_code=400,
                message=f"Choice {choice_id} is not valid for current node",
            )

        # Get next node
        next_node = await self.get_next_node(choice_id)

        # Record progress
        progress = GameProgress(
            session_id=session_id,
            node_id=current_node.id,
            choice_id=choice_id,
        )
        self.db.add(progress)

        # Append to choice_history
        # CR-018: Use flag_modified to ensure JSON field is updated in database
        from sqlalchemy.orm.attributes import flag_modified
        if session.choice_history is None:
            session.choice_history = []
        session.choice_history.append({
            "node_id": str(current_node.id),
            "choice_id": str(choice_id),
        })
        flag_modified(session, "choice_history")

        # Update session
        if next_node:
            session.current_node_id = next_node.id

            if await self.is_terminal_node(next_node):
                session.status = "completed"
                ending_type = self.get_ending_type(next_node)
                if ending_type:
                    session.ending_type = ending_type
                from datetime import datetime
                session.completed_at = datetime.utcnow()
        else:
            session.status = "completed"
            from datetime import datetime
            session.completed_at = datetime.utcnow()

        await self.db.flush()

        return {
            "session": session,
            "current_node": next_node,
            "is_ended": session.status == "completed",
        }

    # ---- Route Map (CR-002 AC-045) ----

    async def get_route_map(self, script_id: UUID, user_id: UUID) -> Dict[str, Any]:
        """
        Build the route exploration map for a script.

        Returns all routes with their node graphs. Each route is annotated
        with `explored` (bool) based on whether the user has a completed
        game session for that route, and `endings` (list of ending_type strings).
        """
        # Load script with routes, nodes, choices
        script = await self.get_script_with_routes(script_id)
        if not script:
            raise AppException(
                error_code="SCRIPT_NOT_FOUND",
                status_code=404,
                message=f"Script {script_id} not found",
            )

        # Load user's completed game sessions for this script
        completed_stmt = (
            select(GameSession)
            .where(
                GameSession.user_id == user_id,
                GameSession.script_id == script_id,
                GameSession.status == "completed",
            )
        )
        completed_result = await self.db.execute(completed_stmt)
        completed_sessions = completed_result.scalars().all()

        # Build set of explored route IDs and ending types
        explored_route_ids: set = set()
        route_endings: Dict[UUID, list] = {}
        for session in completed_sessions:
            explored_route_ids.add(session.route_id)
            if session.ending_type:
                route_endings.setdefault(session.route_id, []).append(session.ending_type)

        # Build response
        routes_data = []
        for route in script.routes:
            nodes_data = []
            for node in route.nodes:
                choices_data = [
                    {
                        "id": str(c.id),
                        "text": c.text,
                        "next_node_id": str(c.next_node_id) if c.next_node_id else None,
                        "affection_delta": c.affection_delta,
                    }
                    for c in (node.choices or [])
                ]
                nodes_data.append({
                    "id": str(node.id),
                    "node_type": node.node_type,
                    "parent_id": str(node.parent_id) if node.parent_id else None,
                    "choices": choices_data,
                })

            is_explored = route.id in explored_route_ids
            routes_data.append({
                "id": str(route.id),
                "title": route.title,
                "description": route.description,
                "explored": is_explored,
                "endings": route_endings.get(route.id, []),
                "nodes": nodes_data,
            })

        return {
            "script_id": str(script.id),
            "title": script.title,
            "routes": routes_data,
        }

    # ---- Character lookup ----

    async def get_character(self, character_id: UUID) -> Optional[Character]:
        """Load character by ID."""
        stmt = select(Character).where(Character.id == character_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
