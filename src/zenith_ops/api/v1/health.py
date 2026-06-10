"""Health check endpoints — liveness and readiness probes."""

from importlib.metadata import version

from fastapi import APIRouter

_Version = version("zenith-ops")


def get_version() -> str:
    """Return the current application version from package metadata.

    Cached at module level — no I/O after first import.
    """
    return _Version


router = APIRouter()


@router.get("/healthy")
async def get_health_status() -> dict[str, str]:
    return {"status": "ok"}
