"""Health check endpoints — liveness and readiness probes."""

from datetime import datetime, timezone
from importlib.metadata import version

from fastapi import APIRouter

_Version = version("zenith-ops")


def get_version() -> str:
    """Return the current application version from package metadata.

    Cached at module level — no I/O after first import.
    """
    return _Version


router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
async def liveness() -> dict[str, str]:
    """Liveness probe — returns immediately, zero I/O."""
    return {
        "status": "up",
        "version": _Version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

