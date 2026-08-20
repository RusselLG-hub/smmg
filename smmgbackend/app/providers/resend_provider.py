import logging
from typing import Any

import resend

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailProviderError(Exception):
    pass


def send_email(to: str | list[str], subject: str, html: str) -> Any:
    if not settings.RESEND_API_KEY or not settings.EMAIL_FROM:
        logger.error("Resend is not configured: RESEND_API_KEY and EMAIL_FROM are required")
        raise EmailProviderError("Email provider is not configured")

    resend.api_key = settings.RESEND_API_KEY
    try:
        return resend.Emails.send(
            {
                "from": settings.EMAIL_FROM,
                "to": to if isinstance(to, list) else [to],
                "subject": subject,
                "html": html,
            }
        )
    except Exception as exc:
        logger.exception("Resend failed to send email")
        raise EmailProviderError("Email provider rejected the message") from exc
