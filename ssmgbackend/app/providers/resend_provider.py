import resend

from app.core.config import settings

resend.api_key = settings.RESEND_API_KEY


def send_email(to: str | list[str], subject: str, html: str) -> dict | None:
    try:
        response = resend.Emails.send(
            {
                "from": settings.EMAIL_FROM,
                "to": to if isinstance(to, list) else [to],
                "subject": subject,
                "html": html,
            }
        )
        return response
    except Exception:
        return None
