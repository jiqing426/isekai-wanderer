"""CorvusClient — HTTP client for Corvus-Story-Core (127.0.0.1:8082).

Encapsulates all HTTP calls to the Corvus Express API:
- POST /api/games — create a new game
- GET /api/games/{gameId} — get game state
- GET /api/games/{gameId}/characters — list NPCs
- GET /api/games/{gameId}/characters/{npcId} — get NPC detail
- PATCH /api/games/{gameId}/characters/{npcId} — update NPC knownInfo
- POST /api/games/{gameId}/messages — stream messages (SSE)
"""

import json
import logging
from typing import AsyncGenerator
import httpx

logger = logging.getLogger(__name__)

# Corvus service base URL — 127.0.0.1 only, never public
CORVUS_BASE_URL = "http://10.255.0.1:8082"
CORVUS_TIMEOUT = 300  # SSE needs long timeout


class CorvusClient:
    """Async HTTP client for Corvus-Story-Core."""

    def __init__(self, base_url: str = CORVUS_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=CORVUS_TIMEOUT,
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def create_game(
        self,
        player_name: str,
        backstory: str,
        appearance: str,
        world_setting: dict | None = None,
        player_inventory: list | None = None,
    ) -> str:
        """POST /api/games — create a new Corvus game.

        Returns the Corvus game_id (slug format, e.g. "dark-fantasy-abc123").
        """
        client = await self._get_client()

        # Build request body matching Corvus API
        body = {
            "name": f"isekai-{player_name}",
            "genre": "visual-novel",
            "description": f"Isekai Wanderer — {player_name}",
            "world": {
                "setting": (world_setting or {}).get("setting", "modern-fantasy"),
                "tone": (world_setting or {}).get("tone", "mysterious"),
                "rules": (world_setting or {}).get("rules", []),
                "currencyName": (world_setting or {}).get("currencyName", "星尘"),
                "era": (world_setting or {}).get("era", "modern"),
            },
            "player": {
                "name": player_name,
                "backstory": backstory or "",
                "appearance": appearance or "",
                "stats": {},
                "money": 100,
                "abilities": [],
                "inventory": player_inventory or [],
                "relationships": [],
            },
        }

        resp = await client.post("/api/games", json=body)
        resp.raise_for_status()
        data = resp.json()
        game_id = data["id"]
        logger.info(f"[CorvusClient] create_game → {game_id}")
        return game_id

    async def get_game(self, game_id: str) -> dict:
        """GET /api/games/{gameId} — get game state."""
        client = await self._get_client()
        resp = await client.get(f"/api/games/{game_id}")
        resp.raise_for_status()
        return resp.json()

    async def get_characters(self, game_id: str) -> list[dict]:
        """GET /api/games/{gameId}/characters — list NPCs."""
        client = await self._get_client()
        resp = await client.get(f"/api/games/{game_id}/characters")
        resp.raise_for_status()
        return resp.json()

    async def get_npc(self, game_id: str, npc_id: str) -> dict:
        """GET /api/games/{gameId}/characters/{npcId} — get NPC detail (with memory[] and knownInfo)."""
        client = await self._get_client()
        resp = await client.get(f"/api/games/{game_id}/characters/{npc_id}")
        resp.raise_for_status()
        return resp.json()

    async def update_npc_knowninfo(
        self, game_id: str, npc_id: str, knowninfo: str
    ) -> dict:
        """PATCH /api/games/{gameId}/characters/{npcId} — update NPC knownInfo."""
        client = await self._get_client()
        resp = await client.patch(
            f"/api/games/{game_id}/characters/{npc_id}",
            json={"knownInfo": knowninfo},
        )
        resp.raise_for_status()
        return resp.json()

    async def stream_message(
        self, game_id: str, content: str
    ) -> AsyncGenerator[dict, None]:
        """POST /api/games/{gameId}/messages — stream SSE events.

        Yields parsed SSE event dicts. Each dict has a 'type' key.
        Corvus event types observed:
        - user: echo of user message
        - context-assembled: context info (filtered out)
        - token: incremental text chunk {"type":"token","content":"..."}
        - narrator: narrator marker {"type":"narrator"}
        - gm-start: GM turn begins
        - gm_update: world state changes (affinity, inventory, etc.)
        - done: complete assistant message {"type":"done",...}
        - stream_end: stream finished
        - error: error event
        """
        client = await self._get_client()

        async with client.stream(
            "POST",
            f"/api/games/{game_id}/messages",
            json={"content": content},
            headers={"Accept": "text/event-stream"},
        ) as resp:
            resp.raise_for_status()

            event_data = ""
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    event_data = line[6:]  # strip "data: " prefix
                elif line == "" and event_data:
                    # Empty line = event boundary
                    try:
                        parsed = json.loads(event_data)
                        yield parsed
                    except json.JSONDecodeError:
                        logger.warning(
                            f"[CorvusClient] Failed to parse SSE: {event_data[:200]}"
                        )
                    event_data = ""


# Module-level singleton for convenience
_corvus_client: CorvusClient | None = None


def get_corvus_client() -> CorvusClient:
    """Get or create the singleton CorvusClient."""
    global _corvus_client
    if _corvus_client is None:
        _corvus_client = CorvusClient()
    return _corvus_client
