"""
MockEmailService — shared email mock for AC-047 (password reset) and AC-057 (recall).

Writes email records to a JSONL log file (one JSON object per line, append mode).
No real SMTP/Resend HTTP calls are made.

Production replacement: swap MockEmailService with a real provider (Resend, SendGrid, etc.)
while keeping the same interface.
"""

import json
import os
from datetime import datetime, timezone
from typing import Any, Optional


class IEmailService:
    """Email service interface — all implementations must satisfy this contract."""

    async def send_password_reset_email(
        self, to: str, token: str, reset_url: str
    ) -> bool:
        raise NotImplementedError

    async def send_recall_email(
        self, to: str, game_link: str, progress_summary: dict[str, Any]
    ) -> bool:
        raise NotImplementedError


class MockEmailService(IEmailService):
    """
    Mock email service that logs to a JSONL file instead of sending real emails.

    Log format: one JSON object per line, append mode.
    Default log path: logs/mock-email.log (relative to project root).
    """

    def __init__(self, log_file: Optional[str] = None):
        if log_file:
            self.log_file = log_file
        else:
            # Default: logs/mock-email.log relative to CWD
            self.log_file = os.path.join("logs", "mock-email.log")

    async def send_password_reset_email(
        self, to: str, token: str, reset_url: str
    ) -> bool:
        """
        AC-047: Log a password-reset email record.

        Args:
            to: Recipient email address.
            token: Password reset token (single-use, 1h TTL).
            reset_url: Full URL the user clicks to reset their password.

        Returns:
            True on success.
        """
        record = {
            "type": "password_reset",
            "to": to,
            "token": token,
            "reset_url": reset_url,
            "subject": "Password Reset Request — Isekai Wanderer",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._append_log(record)
        return True

    async def send_recall_email(
        self, to: str, game_link: str, progress_summary: dict[str, Any]
    ) -> bool:
        """
        AC-057: Log a recall email record.

        Args:
            to: Recipient email address.
            game_link: URL that takes the user back into the game.
            progress_summary: Dict with last_script, last_route, days_inactive, etc.

        Returns:
            True on success.
        """
        record = {
            "type": "recall",
            "to": to,
            "game_link": game_link,
            "progress_summary": progress_summary,
            "subject": "We miss you! Come back to your adventure — Isekai Wanderer",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._append_log(record)
        return True

    # ---- Internal ----

    def _append_log(self, record: dict) -> None:
        """Append a single JSON record to the log file (creates dirs if needed)."""
        log_dir = os.path.dirname(self.log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


# Module-level singleton — import this in services
email_service: IEmailService = MockEmailService()


def get_email_service() -> IEmailService:
    """Return the active email service singleton."""
    return email_service
