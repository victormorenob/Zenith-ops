"""Logging configuration — env-aware structlog setup.

Called once at import time by ``zenith_ops.__init__`` to configure
structlog globally before any request arrives.

Env vars:
    LOG_LEVEL (default: "INFO"): One of DEBUG, INFO, WARNING, ERROR, CRITICAL.
    LOG_FORMAT (default: "console"): Set to ``"json"`` for JSONRenderer output.

This module reads ``os.environ`` directly to avoid circular imports with
``Settings`` at application startup.
"""

import logging
import os

import structlog


def configure_logging() -> None:
    """Configure structlog globally with env-aware processors.

    Sets up:
    - Log level from ``LOG_LEVEL`` env var (default ``INFO``)
    - ``ConsoleRenderer`` (dev) or ``JSONRenderer`` (production) based on
      ``LOG_FORMAT`` env var
    - Stdlib logging capture via ``structlog.stdlib.LoggerFactory``

    The renderer lives in ``ProcessorFormatter``, NOT in the structlog
    processor chain — that avoids a ``'tuple' object has no attribute 'pop'``
    error from ``wrap_for_formatter`` + renderer being in the same chain.
    """
    log_level = os.environ.get("LOG_LEVEL", "INFO")

    # ── Common processors (always present) ──────────────────────────────
    structlog_processors: list[structlog.types.Processor] = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        # wrap_for_formatter MUST be the last structlog processor; the
        # renderer lives in ProcessorFormatter instead.
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]

    # ── Renderer selection (dev vs production) ──────────────────────────
    if os.environ.get("LOG_FORMAT", "").lower() == "json":
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=structlog_processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # ── Route stdlib logging through structlog ──────────────────────────
    # foreign_pre_chain processes log records that originate from stdlib
    # loggers (third-party libraries).  It MUST NOT include filter_by_level
    # because foreign records arrive as raw strings, not event dicts.
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
        ],
        processor=renderer,
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level.upper())

    # Suppress pre-existing handlers on the root logger to avoid duplicates
    root_logger.handlers[:] = [h for h in root_logger.handlers if h is handler]
