"""
Test cases for MockEmailService (DEV-CR2-011).

AC-047: Password reset email
AC-057: Recall email

TDD: Red phase confirmed (ModuleNotFoundError). Green phase: implement below.
Log format: JSONL (one JSON object per line, append mode).
"""

import pytest
import os
import json
from pathlib import Path


def _read_last_log_entry(log_file: str) -> dict:
    """Read the last JSON line from a JSONL log file."""
    with open(log_file, "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    return json.loads(lines[-1])


def _read_all_log_entries(log_file: str) -> list[dict]:
    """Read all JSON lines from a JSONL log file."""
    with open(log_file, "r") as f:
        return [json.loads(l) for l in f if l.strip()]


class TestMockEmailService:
    """Test MockEmailService shared layer for AC-047 and AC-057."""

    @pytest.fixture
    def temp_log_file(self, tmp_path):
        """Create a temporary log file path."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        return str(log_dir / "mock-email.log")

    @pytest.fixture
    def mock_email_service(self, temp_log_file):
        """Create MockEmailService with temp log path."""
        from app.core.email import MockEmailService
        return MockEmailService(log_file=temp_log_file)

    # ---- AC-047: Password Reset Email ----

    @pytest.mark.asyncio
    async def test_send_password_reset_email_logs_to_file(self, mock_email_service, temp_log_file):
        """AC-047: Password reset email should be logged to file, not sent via SMTP."""
        email = "test@example.com"
        token = "test-reset-token-12345"
        reset_url = "https://isekai-wanderer.example.com/reset-password?token=test-reset-token-12345"

        result = await mock_email_service.send_password_reset_email(email, token, reset_url)

        assert result is True
        assert os.path.exists(temp_log_file)

        log_data = _read_last_log_entry(temp_log_file)
        assert log_data["type"] == "password_reset"
        assert log_data["to"] == email
        assert log_data["token"] == token
        assert log_data["reset_url"] == reset_url
        assert "timestamp" in log_data

    @pytest.mark.asyncio
    async def test_password_reset_email_contains_subject(self, mock_email_service, temp_log_file):
        """AC-047: Password reset email log should contain subject line."""
        await mock_email_service.send_password_reset_email(
            "user@example.com", "tok123", "https://example.com/reset?token=tok123"
        )

        log_data = _read_last_log_entry(temp_log_file)
        assert "subject" in log_data
        assert "reset" in log_data["subject"].lower() or "password" in log_data["subject"].lower()

    # ---- AC-057: Recall Email ----

    @pytest.mark.asyncio
    async def test_send_recall_email_logs_to_file(self, mock_email_service, temp_log_file):
        """AC-057: Recall email should be logged to file, not sent via SMTP."""
        email = "inactive@example.com"
        game_link = "https://isekai-wanderer.example.com/game"
        progress_summary = {
            "last_script": "Dragon's Quest",
            "last_route": "Hero's Path",
            "days_inactive": 7,
        }

        result = await mock_email_service.send_recall_email(email, game_link, progress_summary)

        assert result is True
        assert os.path.exists(temp_log_file)

        log_data = _read_last_log_entry(temp_log_file)
        assert log_data["type"] == "recall"
        assert log_data["to"] == email
        assert log_data["game_link"] == game_link
        assert log_data["progress_summary"] == progress_summary
        assert "timestamp" in log_data

    @pytest.mark.asyncio
    async def test_recall_email_contains_subject(self, mock_email_service, temp_log_file):
        """AC-057: Recall email log should contain subject line."""
        await mock_email_service.send_recall_email(
            "user@example.com", "https://example.com/game", {}
        )

        log_data = _read_last_log_entry(temp_log_file)
        assert "subject" in log_data

    # ---- General: Interface Contract ----

    @pytest.mark.asyncio
    async def test_send_email_returns_true_on_success(self, mock_email_service):
        """MockEmailService should return True on successful log."""
        result = await mock_email_service.send_password_reset_email(
            "user@example.com", "token", "https://example.com/reset"
        )
        assert result is True

    def test_log_file_path_is_configurable(self):
        """Log file path should be configurable via constructor."""
        from app.core.email import MockEmailService

        custom_path = "/tmp/custom-email.log"
        service = MockEmailService(log_file=custom_path)
        assert service.log_file == custom_path

    def test_default_log_file_path(self):
        """Default log file path should be logs/mock-email.log."""
        from app.core.email import MockEmailService

        service = MockEmailService()
        assert "mock-email.log" in service.log_file

    @pytest.mark.asyncio
    async def test_send_email_creates_log_directory_if_not_exists(self, tmp_path):
        """MockEmailService should create log directory if it doesn't exist."""
        from app.core.email import MockEmailService

        log_file = str(tmp_path / "nonexistent" / "subdir" / "mock-email.log")
        service = MockEmailService(log_file=log_file)

        result = await service.send_password_reset_email(
            "test@example.com", "token", "https://example.com/reset"
        )

        assert result is True
        assert os.path.exists(os.path.dirname(log_file))

    @pytest.mark.asyncio
    async def test_multiple_emails_appended_to_log(self, mock_email_service, temp_log_file):
        """Multiple emails should be appended as separate lines."""
        await mock_email_service.send_password_reset_email(
            "a@example.com", "tok1", "https://example.com/reset?token=tok1"
        )
        await mock_email_service.send_recall_email(
            "b@example.com", "https://example.com/game", {"days": 14}
        )

        entries = _read_all_log_entries(temp_log_file)
        assert len(entries) == 2
        assert entries[0]["type"] == "password_reset"
        assert entries[0]["to"] == "a@example.com"
        assert entries[1]["type"] == "recall"
        assert entries[1]["to"] == "b@example.com"
