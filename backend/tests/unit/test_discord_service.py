"""
Test cases for MockDiscordService (DEV-CR2-006).

AC-055: Discord Bot sends notifications when new endings are unlocked.
Mock: logs to file instead of making real HTTP requests.
"""

import pytest
import os
import json


def _read_last_log_entry(log_file: str) -> dict:
    with open(log_file, "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    return json.loads(lines[-1])


def _read_all_log_entries(log_file: str) -> list[dict]:
    with open(log_file, "r") as f:
        return [json.loads(l) for l in f if l.strip()]


class TestMockDiscordService:
    """Test MockDiscordService for AC-055."""

    @pytest.fixture
    def temp_log_file(self, tmp_path):
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        return str(log_dir / "mock-discord.log")

    @pytest.fixture
    def mock_discord_service(self, temp_log_file):
        from app.services.discord_service import MockDiscordService
        return MockDiscordService(log_file=temp_log_file)

    @pytest.mark.asyncio
    async def test_send_ending_notification_logs_to_file(self, mock_discord_service, temp_log_file):
        """AC-055: Ending notification should be logged, not sent via HTTP."""
        result = await mock_discord_service.send_ending_notification(
            webhook_url="https://discord.com/api/webhooks/test/hook",
            channel_name="test-channel",
            ending_data={
                "user_name": "Player1",
                "script_title": "Dragon's Quest",
                "route_title": "Hero's Path",
                "ending_type": "good",
            },
        )

        assert result is True
        assert os.path.exists(temp_log_file)

        log_data = _read_last_log_entry(temp_log_file)
        assert log_data["type"] == "ending_notification"
        assert log_data["webhook_url"] == "https://discord.com/api/webhooks/test/hook"
        assert log_data["channel_name"] == "test-channel"
        assert log_data["ending_data"]["ending_type"] == "good"
        assert "timestamp" in log_data

    @pytest.mark.asyncio
    async def test_send_ending_notification_contains_embed(self, mock_discord_service, temp_log_file):
        """AC-055: Discord embed should contain ending details."""
        await mock_discord_service.send_ending_notification(
            webhook_url="https://discord.com/api/webhooks/test/hook",
            channel_name="general",
            ending_data={
                "user_name": "Player2",
                "script_title": "Isekai Tales",
                "route_title": "Magic Academy",
                "ending_type": "bad",
            },
        )

        log_data = _read_last_log_entry(temp_log_file)
        assert "embed" in log_data or "content" in log_data

    @pytest.mark.asyncio
    async def test_multiple_notifications_appended(self, mock_discord_service, temp_log_file):
        """Multiple notifications should be appended as separate lines."""
        await mock_discord_service.send_ending_notification(
            webhook_url="https://discord.com/api/webhooks/test/hook",
            channel_name="ch1",
            ending_data={"user_name": "A", "script_title": "S1", "route_title": "R1", "ending_type": "good"},
        )
        await mock_discord_service.send_ending_notification(
            webhook_url="https://discord.com/api/webhooks/test/hook2",
            channel_name="ch2",
            ending_data={"user_name": "B", "script_title": "S2", "route_title": "R2", "ending_type": "normal"},
        )

        entries = _read_all_log_entries(temp_log_file)
        assert len(entries) == 2
        assert entries[0]["ending_data"]["user_name"] == "A"
        assert entries[1]["ending_data"]["user_name"] == "B"

    def test_default_log_file_path(self):
        from app.services.discord_service import MockDiscordService
        svc = MockDiscordService()
        assert "mock-discord.log" in svc.log_file

    def test_configurable_log_file_path(self, temp_log_file):
        from app.services.discord_service import MockDiscordService
        svc = MockDiscordService(log_file=temp_log_file)
        assert svc.log_file == temp_log_file

    @pytest.mark.asyncio
    async def test_creates_log_directory(self, tmp_path):
        from app.services.discord_service import MockDiscordService
        log_file = str(tmp_path / "a" / "b" / "mock-discord.log")
        svc = MockDiscordService(log_file=log_file)

        result = await svc.send_ending_notification(
            webhook_url="https://discord.com/api/webhooks/test/hook",
            channel_name="test",
            ending_data={"user_name": "X", "script_title": "T", "route_title": "R", "ending_type": "good"},
        )

        assert result is True
        assert os.path.exists(os.path.dirname(log_file))


class TestDiscordConfigModel:
    """Test DiscordConfig SQLAlchemy model."""

    @pytest.mark.asyncio
    async def test_discord_config_crud(self, db_session):
        """CRUD operations on discord_configs table."""
        from app.models.discord import DiscordConfig

        config = DiscordConfig(
            webhook_url="https://discord.com/api/webhooks/test/hook",
            channel_name="endings",
            enabled=True,
            events=["ending_unlocked"],
        )
        db_session.add(config)
        await db_session.commit()
        await db_session.refresh(config)

        assert config.id is not None
        assert config.enabled is True
        assert "ending_unlocked" in config.events

        # Update
        config.enabled = False
        await db_session.commit()
        await db_session.refresh(config)
        assert config.enabled is False
