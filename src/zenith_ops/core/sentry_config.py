"""Sentry error-tracking configuration.

Initializes the Sentry SDK when ``SENTRY_DSN`` is set.  Local development
works without Sentry — an empty DSN skips initialization entirely.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import sentry_sdk
import structlog
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.types import Event
from structlog.contextvars import get_contextvars

if TYPE_CHECKING:
    from zenith_ops.core.settings import Settings


def _enrich_event_with_correlation_id(
    event: Event,
    hint: dict[str, Any],
) -> Event | None:
    """Attach structlog ``correlation_id`` to Sentry events as a tag."""
    _ = hint
    correlation_id = get_contextvars().get("correlation_id")
    if correlation_id is not None:
        tags = event.setdefault("tags", {})
        if isinstance(tags, dict):
            tags["correlation_id"] = correlation_id
    return event


def configure_sentry(settings: Settings) -> bool:
    """Initialize the Sentry SDK when a DSN is configured.

    Args:
        settings: Application settings loaded from environment variables.

    Returns:
        ``True`` if Sentry was initialized, ``False`` when disabled (no DSN).
    """
    if not settings.sentry_enabled:
        structlog.get_logger(__name__).info(
            "sentry_disabled",
            reason="SENTRY_DSN not set",
        )
        return False

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        integrations=[
            FastApiIntegration(),
            StarletteIntegration(),
        ],
        before_send=_enrich_event_with_correlation_id,
        send_default_pii=False,
    )
    structlog.get_logger(__name__).info(
        "sentry_initialized",
        environment=settings.SENTRY_ENVIRONMENT,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
    )
    return True


def capture_exception(exc: BaseException) -> None:
    """Send *exc* to Sentry when the SDK is active.

    Safe to call when Sentry is disabled — becomes a no-op.
    """
    client = sentry_sdk.get_client()
    if client is not None and client.is_active():
        sentry_sdk.capture_exception(exc)
