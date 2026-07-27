"""
RecallService — sends recall emails to inactive users (CR-002 AC-057).

Eligibility: last_login >= 7 days ago and no recall email within cooldown (14 days).
Uses MockEmailService for MVP; swap with real provider in production.
"""

import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from app.core.email import IEmailService, get_email_service


# Cooldown: don't re-send recall within 14 days
RECALL_COOLDOWN_DAYS = 14
INACTIVE_THRESHOLD_DAYS = 7


class RecallService:
    """Service to check user inactivity and send recall emails."""

    def __init__(self, email_service: Optional[IEmailService] = None, log_file: Optional[str] = None):
        self.email_service = email_service or get_email_service()
        # In-memory cooldown cache: user_id -> last sent datetime
        # Production: use DB (recall_emails table) or Redis
        self._cooldown_cache: dict[str, datetime] = {}
        self.log_file = log_file or os.path.join("logs", "recall-cooldown.log")

    async def check_and_send(self, user: dict[str, Any]) -> bool:
        """
        Check if user is eligible for recall email and send if so.

        Args:
            user: Dict with id, email, display_name, last_login (ISO string or None),
                  progress_summary (optional dict).

        Returns:
            True if recall email was sent, False otherwise.
        """
        user_id = user.get("id", "")
        last_login_str = user.get("last_login")

        # No login history → skip
        if not last_login_str:
            return False

        now = datetime.now(timezone.utc)
        last_login = datetime.fromisoformat(last_login_str)
        if last_login.tzinfo is None:
            last_login = last_login.replace(tzinfo=timezone.utc)

        days_inactive = (now - last_login).days

        # Not inactive enough
        if days_inactive < INACTIVE_THRESHOLD_DAYS:
            return False

        # Cooldown check
        if self._is_in_cooldown(user_id, now):
            return False

        # Build progress summary
        progress = user.get("progress_summary", {})
        progress["days_inactive"] = days_inactive

        # Build game link
        game_link = f"https://isekai-wanderer.com/game?recall={user_id}"

        # Send recall email
        success = await self.email_service.send_recall_email(
            to=user.get("email", ""),
            game_link=game_link,
            progress_summary=progress,
        )

        if success:
            self._record_cooldown(user_id, now)
            self._log_cooldown(user_id, now)

        return success

    def _is_in_cooldown(self, user_id: str, now: datetime) -> bool:
        """Check if user is within cooldown period."""
        last_sent = self._cooldown_cache.get(user_id)
        if not last_sent:
            return False
        return (now - last_sent).days < RECALL_COOLDOWN_DAYS

    def _record_cooldown(self, user_id: str, now: datetime) -> None:
        """Record that a recall email was sent."""
        self._cooldown_cache[user_id] = now

    def _log_cooldown(self, user_id: str, now: datetime) -> None:
        """Append cooldown record to log file (for audit)."""
        record = {
            "user_id": user_id,
            "sent_at": now.isoformat(),
            "cooldown_days": RECALL_COOLDOWN_DAYS,
        }
        log_dir = os.path.dirname(self.log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")


# Cron job runner — call from scheduler or main.py startup
async def run_recall_cron(db_session=None) -> int:
    """
    Run the recall cron job: query inactive users and send recall emails.

    Args:
        db_session: Optional async DB session. If None, uses a new session.

    Returns:
        Number of recall emails sent.
    """
    from app.core.database import get_db
    from sqlalchemy import select
    from app.models.user import User

    recall_svc = RecallService()
    sent_count = 0

    if db_session is None:
        async for db in get_db():
            db_session = db
            break

    now = datetime.now(timezone.utc)
    threshold = now - timedelta(days=INACTIVE_THRESHOLD_DAYS)

    # Query users whose last_login is before threshold
    # Note: User model needs last_login field; if not present, skip
    if not hasattr(User, "last_login"):
        return 0

    stmt = select(User).where(
        User.last_login.isnot(None),
        User.last_login <= threshold,
    )
    result = await db_session.execute(stmt)
    users = result.scalars().all()

    for user in users:
        user_dict = {
            "id": str(user.id),
            "email": user.email,
            "display_name": user.display_name,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "progress_summary": {},
        }
        success = await recall_svc.check_and_send(user_dict)
        if success:
            sent_count += 1

    return sent_count
