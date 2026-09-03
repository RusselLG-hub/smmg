import logging
from typing import Any

import resend

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailProviderError(Exception):
    pass


def _is_placeholder_api_key(key: str | None) -> bool:
    if not key:
        return True
    cleaned = key.strip().lower()
    return (
        cleaned == ""
        or cleaned == "your_resend_api_key"
        or cleaned.startswith("your_")
        or cleaned.startswith("placeholder")
        or cleaned == "dummy"
        or cleaned == "mock"
    )


def send_email(to: str | list[str], subject: str, html: str) -> Any:
    recipients = [to] if isinstance(to, str) else list(to)

    if _is_placeholder_api_key(settings.RESEND_API_KEY) or not settings.EMAIL_FROM:
        logger.warning(
            "[DEV EMAIL] Resend is not configured or using placeholder key. "
            "Simulating delivery for recipient(s): %s (subject: '%s').",
            recipients,
            subject,
        )
        return {"id": "dev-simulated-id", "status": "simulated"}

    resend.api_key = settings.RESEND_API_KEY
    try:
        return resend.Emails.send(
            {
                "from": settings.EMAIL_FROM,
                "to": recipients,
                "subject": subject,
                "html": html,
            }
        )
    except Exception as exc:
        logger.warning(
            "Resend failed to send email to %s: %s", recipients, exc
        )
        if (
            settings.ENVIRONMENT.lower() == "development"
            or _is_placeholder_api_key(settings.RESEND_API_KEY)
        ):
            logger.warning(
                "[DEV EMAIL FALLBACK] Email delivery failed in development mode. "
                "Simulating successful delivery for %s so registration/testing is not blocked.",
                recipients,
            )
            return {"id": "dev-fallback-id", "status": "simulated"}

        logger.exception("Resend failed to send email")
        raise EmailProviderError("Email provider rejected the message") from exc
