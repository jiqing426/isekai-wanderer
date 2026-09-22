"""
Email service — supports mock (dev) and SMTP (production) modes.

When SMTP_HOST is configured (not localhost) and credentials are set,
uses real SMTP sending (supports 163 mail and standard SMTP providers).
Otherwise falls back to MockEmailService that logs to a JSONL file.
"""

import json
import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from typing import Any, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class IEmailService:
    """Email service interface — all implementations must satisfy this contract."""

    async def send_verification_code(
        self, to: str, code: str
    ) -> bool:
        raise NotImplementedError

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
    Used in development mode or when SMTP is not configured.
    """

    def __init__(self, log_file: Optional[str] = None):
        if log_file:
            self.log_file = log_file
        else:
            self.log_file = os.path.join("logs", "mock-email.log")

    async def send_password_reset_email(
        self, to: str, token: str, reset_url: str
    ) -> bool:
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

    async def send_verification_code(
        self, to: str, code: str
    ) -> bool:
        record = {
            "type": "verification_code",
            "to": to,
            "code": code,
            "subject": "注册验证码 — 异世界漫游",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._append_log(record)
        return True

    async def send_recall_email(
        self, to: str, game_link: str, progress_summary: dict[str, Any]
    ) -> bool:
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

    def _append_log(self, record: dict) -> None:
        log_dir = os.path.dirname(self.log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


class SMTPEmailService(IEmailService):
    """
    Real SMTP email service — supports 163 mail and standard SMTP providers.

    Uses SMTP_SSL for port 465, SMTP with STARTTLS for port 587.
    """

    def __init__(self):
        self.host = settings.smtp_host
        self.port = settings.smtp_port
        self.user = settings.smtp_user
        self.password = settings.smtp_password
        self.from_addr = settings.smtp_from or self.user

    def _send(self, to: str, subject: str, html_body: str) -> bool:
        """Send email via SMTP. Returns True on success, False on failure."""
        msg = MIMEMultipart("alternative")
        msg["From"] = self.from_addr
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        try:
            if self.port == 465:
                server = smtplib.SMTP_SSL(self.host, self.port, timeout=30)
            else:
                server = smtplib.SMTP(self.host, self.port, timeout=30)
                server.starttls()

            server.login(self.user, self.password)
            server.sendmail(self.from_addr, [to], msg.as_string())
            server.quit()
            return True
        except Exception as e:
            logger.warning(f"[SMTP] Failed to send email to {to}: {e}")
            return False

    async def send_password_reset_email(
        self, to: str, token: str, reset_url: str
    ) -> bool:
        subject = "密码重置 — 异世界漫游"
        html = f"""
        <div style="max-width:480px;margin:0 auto;font-family:sans-serif;">
            <h2 style="color:#6b46c1;">异世界漫游 — 密码重置</h2>
            <p>您收到这封邮件是因为有人请求重置您账户的密码。</p>
            <p>请点击下方链接重置密码（1 小时内有效）：</p>
            <p><a href="{reset_url}" style="display:inline-block;padding:10px 24px;background:#6b46c1;color:#fff;text-decoration:none;border-radius:6px;">重置密码</a></p>
            <p style="color:#999;font-size:12px;">如果这不是您本人的操作，请忽略此邮件。</p>
        </div>
        """
        return self._send(to, subject, html)

    async def send_verification_code(
        self, to: str, code: str
    ) -> bool:
        subject = "注册验证码 — 异世界漫游"
        html = f"""
        <div style="max-width:480px;margin:0 auto;font-family:sans-serif;">
            <h2 style="color:#6b46c1;">异世界漫游 — 注册验证码</h2>
            <p>您的验证码是：</p>
            <p style="font-size:32px;font-weight:bold;letter-spacing:8px;color:#6b46c1;">{code}</p>
            <p style="color:#999;font-size:12px;">验证码 5 分钟内有效。如果这不是您本人的操作，请忽略此邮件。</p>
        </div>
        """
        return self._send(to, subject, html)

    async def send_recall_email(
        self, to: str, game_link: str, progress_summary: dict[str, Any]
    ) -> bool:
        subject = "我们想你了！回来继续你的冒险吧 — 异世界漫游"
        last_script = progress_summary.get("last_script", "未知")
        days = progress_summary.get("days_inactive", "?")
        html = f"""
        <div style="max-width:480px;margin:0 auto;font-family:sans-serif;">
            <h2 style="color:#6b46c1;">异世界漫游 — 冒险还在继续</h2>
            <p>你已经离开 {days} 天了，你的故事还没有讲完。</p>
            <p>上次进度：<b>{last_script}</b></p>
            <p><a href="{game_link}" style="display:inline-block;padding:10px 24px;background:#6b46c1;color:#fff;text-decoration:none;border-radius:6px;">继续冒险</a></p>
        </div>
        """
        return self._send(to, subject, html)


def _create_email_service() -> IEmailService:
    """Create the appropriate email service based on configuration."""
    # Use SMTP when host is configured and not localhost, and credentials are set
    if (
        settings.smtp_host
        and settings.smtp_host != "localhost"
        and settings.smtp_user
        and settings.smtp_password
    ):
        logger.info(f"[Email] Using SMTP service ({settings.smtp_host}:{settings.smtp_port})")
        return SMTPEmailService()
    else:
        logger.info("[Email] Using mock email service (logging to file)")
        return MockEmailService()


# Module-level singleton — auto-selects mock or SMTP based on config
email_service: IEmailService = _create_email_service()


def get_email_service() -> IEmailService:
    """Return the active email service singleton."""
    return email_service


def reload_email_service() -> None:
    """Reload email service after SMTP config changed in DB.
    Re-reads settings and rebuilds the singleton.
    """
    global email_service
    # Reload settings from DB if load_system_configs is available
    try:
        from app.core.config import load_system_configs
        load_system_configs()
    except Exception:
        pass
    email_service = _create_email_service()
    logger.info(f"[Email] Service reloaded — {'SMTP' if isinstance(email_service, SMTPEmailService) else 'Mock'}")
