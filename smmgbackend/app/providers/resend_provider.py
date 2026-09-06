"""Backward-compatible alias for Brevo email provider."""

from app.providers.brevo_provider import (
    EmailProviderError,
    _is_placeholder_api_key,
    send_email,
    settings,
)

__all__ = ["EmailProviderError", "_is_placeholder_api_key", "send_email", "settings"]
