"""
MockDiscordService — logs ending notifications to JSONL file (AC-055).

No real HTTP requests to Discord are made.
Production replacement: swap with real webhook POST implementation.
"""

import json
import os
from datetime import datetime, timezone
from typing import Any, Optional


class IDiscordService:
    """Discord service interface."""

    async def send_ending_notification(
        self, webhook_url: str, channel_name: str, ending_data: dict[str, Any]
    ) -> bool:
        raise NotImplementedError


class MockDiscordService(IDiscordService):
    """
    Mock Discord service that logs ending notifications to a JSONL file.

    Log format: one JSON object per line, append mode.
    Default log path: logs/mock-discord.log.
    """

    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file or os.path.join("logs", "mock-discord.log")

    async def send_ending_notification(
        self, webhook_url: str, channel_name: str, ending_data: dict[str, Any]
    ) -> bool:
        """
        AC-055: Log a Discord ending notification.

        Args:
            webhook_url: Discord webhook URL (mock — not actually called).
            channel_name: Channel to post to.
            ending_data: Dict with user_name, script_title, route_title, ending_type.

        Returns:
            True on success.
        """
        # Build a Discord-style embed
        embed = {
            "title": f"🎉 New Ending Unlocked!",
            "description": (
                f"**{ending_data.get('user_name', 'Unknown')}** unlocked the "
                f"**{ending_data.get('ending_type', 'unknown')}** ending in "
                f"*{ending_data.get('script_title', 'Unknown')}* "
                f"via {ending_data.get('route_title', 'Unknown')} route!"
            ),
            "color": 0x5865F2,
            "fields": [
                {"name": "Script", "value": ending_data.get("script_title", "—"), "inline": True},
                {"name": "Route", "value": ending_data.get("route_title", "—"), "inline": True},
                {"name": "Ending", "value": ending_data.get("ending_type", "—"), "inline": True},
            ],
        }

        record = {
            "type": "ending_notification",
            "webhook_url": webhook_url,
            "channel_name": channel_name,
            "ending_data": ending_data,
            "embed": embed,
            "content": f"🏆 {ending_data.get('user_name', 'Player')} unlocked **{ending_data.get('ending_type', '')}** ending!",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        self._append_log(record)
        return True

    def _append_log(self, record: dict) -> None:
        """Append a JSON record to the log file."""
        log_dir = os.path.dirname(self.log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


# Module-level singleton
discord_service: IDiscordService = MockDiscordService()


def get_discord_service() -> IDiscordService:
    """Return the active Discord service singleton."""
    return discord_service
