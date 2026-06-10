"""Health check endpoints — liveness and readiness probes."""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from importlib.metadata import version

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from zenith_ops.core.inference_service import InferenceService
from zenith_ops.core.settings import Settings

_Version = version("zenith-ops")


def get_version() -> str:
    """Return the current application version from package metadata.

    Cached at module level — no I/O after first import.
    """
    return _Version


@asynccontextmanager
async def _get_engine(url: str) -> AsyncGenerator[AsyncEngine, None]:
    """Create an async engine and ensure it is disposed on exit."""
    engine = create_async_engine(url)
    try:
        yield engine
    finally:
        await engine.dispose()


async def check_database(settings: Settings | None = None) -> str:
    """Ping the database via SQLAlchemy async connection.

    Returns ``"up"`` if ``SELECT 1`` succeeds, ``"down"`` otherwise.
    """
    if settings is None:
        settings = Settings()  # type: ignore[call-arg]
    url = str(settings.DATABASE_URL)
    try:
        async with _get_engine(url) as engine, engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return "up"
    except Exception:
        return "down"


def check_model_cache() -> bool:
    """Return ``True`` if at least one model is cached in InferenceService."""
    return bool(InferenceService._models)


router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
async def liveness() -> dict[str, str]:
    """Liveness probe — returns immediately, zero I/O."""
    return {
        "status": "up",
        "version": _Version,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/ready")
async def readiness() -> JSONResponse:
    """Readiness probe — checks database and model cache concurrently."""
    db_status, model_cached = await asyncio.gather(
        check_database(),
        asyncio.to_thread(check_model_cache),
    )

    all_up = db_status == "up" and model_cached is True

    return JSONResponse(
        status_code=200 if all_up else 503,
        content={
            "status": "up" if all_up else "down",
            "version": _Version,
            "timestamp": datetime.now(UTC).isoformat(),
            "components": {
                "database": db_status,
                "model_cached": model_cached,
            },
        },
    )

