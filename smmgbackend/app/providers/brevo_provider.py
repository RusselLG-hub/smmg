import json
import logging
import urllib.error
import urllib.request
from typing import Any

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
        or cleaned == "your_brevo_api_key"
        or cleaned == "your_resend_api_key"
        or cleaned.startswith("your_")
        or cleaned.startswith("placeholder")
        or cleaned == "dummy"
        or cleaned == "mock"
    )


def send_email(to: str | list[str], subject: str, html: str) -> Any:
    recipients = [to] if isinstance(to, str) else list(to)
    api_key = settings.BREVO_API_KEY or getattr(settings, "RESEND_API_KEY", "")
    from_email = settings.EMAIL_FROM or "noreply@smmg.site"
    from_name = getattr(settings, "EMAIL_FROM_NAME", "SMMG") or "SMMG"

    if settings.is_local_jmeter_bypass or _is_placeholder_api_key(api_key) or not from_email:
        logger.warning(
            "[DEV EMAIL] Local JMeter bypass active or Brevo is not configured. "
            "Simulating delivery for recipient(s): %s (subject: '%s').",
            recipients,
            subject,
        )
        return {"id": "dev-simulated-id", "status": "simulated"}

    payload = {
        "sender": {
            "name": from_name,
            "email": from_email,
        },
        "to": [{"email": recipient} for recipient in recipients],
        "subject": subject,
        "htmlContent": html,
    }

    req = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            body = response.read().decode("utf-8")
            data = json.loads(body) if body else {}
            logger.info("Brevo email sent to %s: messageId=%s", recipients, data.get("messageId"))
            return data
    except Exception as exc:
        logger.warning(
            "Brevo failed to send email to %s: %s", recipients, exc
        )
        if (
            settings.ENVIRONMENT.lower() == "development"
            or _is_placeholder_api_key(api_key)
        ):
            logger.warning(
                "[DEV EMAIL FALLBACK] Email delivery failed in development mode. "
                "Simulating successful delivery for %s so registration/testing is not blocked.",
                recipients,
            )
            return {"id": "dev-fallback-id", "status": "simulated"}

        logger.exception("Brevo failed to send email")
        raise EmailProviderError("Email provider rejected the message") from exc
