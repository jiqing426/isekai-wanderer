"""
DEV-CR2-008: RecallService Red tests (AC-057).

Tests:
- Should send recall email to user inactive for >= 7 days
- Should NOT send recall email to user inactive for < 7 days
- Should NOT send duplicate recall email within cooldown period
- Should include progress summary in recall email
- Should skip users who already received a recall email recently
"""

import json
import os
import tempfile
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.services.recall_service import RecallService
from app.core.email import MockEmailService


@pytest.fixture
def temp_log():
    """Provide a temporary log file for MockEmailService."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield os.path.join(tmpdir, "logs", "mock-email.log")


class TestRecallServiceEligibility:
    """Test which users are eligible for recall emails."""

    @pytest.mark.asyncio
    async def test_user_inactive_7_days_is_eligible(self, temp_log):
        """User with last_login >= 7 days ago should receive recall email."""
        email_svc = MockEmailService(log_file=temp_log)
        recall_svc = RecallService(email_service=email_svc)

        now = datetime.now(timezone.utc)
        eligible_user = {
            "id": str(uuid.uuid4()),
            "email": "inactive7@example.com",
            "display_name": "Inactive7",
            "last_login": (now - timedelta(days=7)).isoformat(),
            "progress_summary": {
                "last_script": "Dragon Quest",
                "last_route": "Hero Path",
                "days_inactive": 7,
            },
        }

        result = await recall_svc.check_and_send(eligible_user)
        assert result is True

        with open(temp_log) as f:
            records = [json.loads(line) for line in f if line.strip()]
        assert len(records) == 1
        assert records[0]["type"] == "recall"
        assert records[0]["to"] == "inactive7@example.com"
        assert records[0]["progress_summary"]["last_script"] == "Dragon Quest"

    @pytest.mark.asyncio
    async def test_user_inactive_6_days_not_eligible(self, temp_log):
        """User with last_login < 7 days ago should NOT receive recall email."""
        email_svc = MockEmailService(log_file=temp_log)
        recall_svc = RecallService(email_service=email_svc)

        now = datetime.now(timezone.utc)
        user = {
            "id": str(uuid.uuid4()),
            "email": "active6@example.com",
            "display_name": "Active6",
            "last_login": (now - timedelta(days=6)).isoformat(),
        }

        result = await recall_svc.check_and_send(user)
        assert result is False

    @pytest.mark.asyncio
    async def test_user_never_logged_in_not_eligible(self, temp_log):
        """User with no last_login should NOT receive recall email."""
        email_svc = MockEmailService(log_file=temp_log)
        recall_svc = RecallService(email_service=email_svc)

        user = {
            "id": str(uuid.uuid4()),
            "email": "never@example.com",
            "display_name": "Never",
            "last_login": None,
        }

        result = await recall_svc.check_and_send(user)
        assert result is False


class TestRecallServiceCooldown:
    """Test cooldown / duplicate prevention."""

    @pytest.mark.asyncio
    async def test_duplicate_recall_blocked_within_cooldown(self, temp_log):
        """Second recall within cooldown should be blocked."""
        email_svc = MockEmailService(log_file=temp_log)
        recall_svc = RecallService(email_service=email_svc)

        now = datetime.now(timezone.utc)
        user = {
            "id": str(uuid.uuid4()),
            "email": "cooldown@example.com",
            "display_name": "Cooldown",
            "last_login": (now - timedelta(days=10)).isoformat(),
            "progress_summary": {"last_script": "S", "days_inactive": 10},
        }

        # First send succeeds
        r1 = await recall_svc.check_and_send(user)
        assert r1 is True

        # Second send within cooldown is blocked
        r2 = await recall_svc.check_and_send(user)
        assert r2 is False

    @pytest.mark.asyncio
    async def test_recall_email_includes_progress_summary(self, temp_log):
        """Recall email should contain the user's progress summary."""
        email_svc = MockEmailService(log_file=temp_log)
        recall_svc = RecallService(email_service=email_svc)

        now = datetime.now(timezone.utc)
        summary = {
            "last_script": "Sakura Academy",
            "last_route": "Romance Path",
            "days_inactive": 14,
        }
        user = {
            "id": str(uuid.uuid4()),
            "email": "summary@example.com",
            "display_name": "Summary",
            "last_login": (now - timedelta(days=14)).isoformat(),
            "progress_summary": summary,
        }

        await recall_svc.check_and_send(user)

        with open(temp_log) as f:
            records = [json.loads(line) for line in f if line.strip()]
        assert records[0]["progress_summary"]["last_script"] == "Sakura Academy"
        assert records[0]["progress_summary"]["days_inactive"] == 14
        assert records[0]["game_link"].startswith("https://")
