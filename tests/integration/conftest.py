"""Integration test fixtures.

PostgreSQL-backed tests opt in via ``@pytest.mark.postgres``. Tests that
inject mocks (e.g. ``test_model_registry_api.py``) run without a database.
"""

from __future__ import annotations

import asyncio
import os

# TestClient runs the app on a different event loop than asyncio.run() setup.
# NullPool must be set before zenith_ops.db.session creates the engine.
if os.environ.get("DATABASE_URL"):
    os.environ["ZENITH_OPS_DB_NULL_POOL"] = "1"

from collections.abc import Generator

import pytest
from sqlalchemy import delete, text
from sqlalchemy.exc import OperationalError
from zenith_ops.core.exceptions import DuplicateModelError
from zenith_ops.core.model_registry_db import PostgresModelRegistry
from zenith_ops.db.models.model_registry import ModelRegistryEntry
from zenith_ops.db.models.prediction_metadata import PredictionMetadata
from zenith_ops.db.session import async_session_factory, engine
from zenith_ops.services.predictor import InferenceService

MODEL_ID = "iris-classifier"
MODEL_VERSION = "1.0.0"


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "postgres: integration test requires a reachable PostgreSQL instance",
    )


def _database_url_configured() -> bool:
    """Return True when DATABASE_URL is set in the environment."""
    return bool(os.environ.get("DATABASE_URL"))


async def _postgres_reachable() -> bool:
    """Probe PostgreSQL with a lightweight SELECT 1."""
    if not _database_url_configured():
        return False
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except (OperationalError, OSError):
        return False


@pytest.fixture(scope="session")
def postgres_available() -> bool:
    """True when DATABASE_URL points to a live PostgreSQL instance."""
    return asyncio.run(_postgres_reachable())


async def _truncate_registry_tables() -> None:
    """Remove all rows from registry tables (FK-safe order)."""
    async with async_session_factory() as session:
        await session.execute(delete(PredictionMetadata))
        await session.execute(delete(ModelRegistryEntry))
        await session.commit()


async def _seed_iris_classifier() -> None:
    """Insert iris-classifier row and write the .joblib artifact."""
    registry = PostgresModelRegistry(async_session_factory)
    try:
        await registry.register_and_build_model(
            name=MODEL_ID,
            version=MODEL_VERSION,
            framework="sklearn",
            model_type="dummy_iris",
            description="Dummy Iris classifier for integration tests",
            tags=["classification", "iris", "multiclass"],
        )
    except DuplicateModelError:
        return


def _reset_app_state() -> None:
    """Clear singleton caches so each test starts from a clean slate."""
    import zenith_ops.core.model_registry_db as reg_db
    from zenith_ops import app as _app

    InferenceService._registry = None
    InferenceService._models.clear()
    InferenceService._idempotency_cache.clear()
    reg_db._registry_instance = None
    _app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def _postgres_integration_lifecycle(
    request: pytest.FixtureRequest,
    postgres_available: bool,
) -> Generator[None, None, None]:
    """Seed PostgreSQL and reset caches for tests marked ``postgres``."""
    if request.node.get_closest_marker("postgres") is None:
        yield
        return

    if not postgres_available:
        pytest.skip("PostgreSQL not available — set DATABASE_URL and run migrations")

    asyncio.run(_truncate_registry_tables())
    asyncio.run(_seed_iris_classifier())
    _reset_app_state()

    yield

    _reset_app_state()
