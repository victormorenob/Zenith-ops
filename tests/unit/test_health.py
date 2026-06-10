"""Unit tests for health check endpoints.

Tests use TestClient against the real FastAPI application, mocking
external dependencies to verify zero-I/O behavior for liveness.
"""

import re
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import status
from fastapi.testclient import TestClient

from zenith_ops import app
from zenith_ops.api.v1.health import check_database, check_model_cache, get_version

client = TestClient(app)

from zenith_ops.core.inference_service import InferenceService
from zenith_ops.core.settings import Settings

ISO_8601_REGEX = (
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$"
)


class TestLiveEndpoint:
    """GET /health/live — liveness probe, zero I/O."""

    def test_returns_200_with_up_status(self) -> None:
        """Liveness endpoint should return 200 with status 'up'."""
        response = client.get("/health/live")
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["status"] == "up"

    def test_returns_version_from_package_metadata(self) -> None:
        """Version field should match importlib.metadata."""
        response = client.get("/health/live")
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["version"] == get_version()

    def test_iso_8601_timestamp(self) -> None:
        """Timestamp should be ISO 8601 format in UTC."""
        response = client.get("/health/live")
        assert response.status_code == status.HTTP_200_OK
        body = response.json()

        assert re.match(ISO_8601_REGEX, body["timestamp"]), (
            f"Timestamp '{body['timestamp']}' does not match ISO 8601"
        )
        # Verify it's a valid datetime and in UTC
        ts = datetime.fromisoformat(body["timestamp"])
        assert ts.tzinfo is not None, "Timestamp must be timezone-aware"
        assert ts.tzinfo == timezone.utc or ts.utcoffset() == timezone.utc.utcoffset(None), (
            "Timestamp must be in UTC"
        )

    def test_timestamp_is_recent(self) -> None:
        """Timestamp should be close to the current time (within 5s)."""
        before = datetime.now(timezone.utc)
        response = client.get("/health/live")
        after = datetime.now(timezone.utc)
        assert response.status_code == status.HTTP_200_OK
        ts = datetime.fromisoformat(response.json()["timestamp"])
        # The timestamp must be between before and after (within tolerance)
        assert before - timedelta(seconds=1) <= ts <= after + timedelta(seconds=1), (
            f"Timestamp {ts} is not close to current time"
        )

    def test_zero_io_no_database_or_cache_calls(self) -> None:
        """Liveness must NOT perform any I/O.

        The handler returns immediately without any dependency
        calls. We verify by mocking the DB engine at sqlalchemy
        and InferenceService — liveness succeeds without them.
        """
        with (
            patch("sqlalchemy.ext.asyncio.create_async_engine") as mock_engine,
            patch(
                "zenith_ops.core.inference_service.InferenceService._models",
                {},
            ),
        ):
            response = client.get("/health/live")
            assert response.status_code == status.HTTP_200_OK
            body = response.json()
            assert body["status"] == "up"
            # DB engine should not be touched by liveness
            mock_engine.assert_not_called()


class TestCheckDatabase:
    """check_database() — async ping via SQLAlchemy."""

    async def test_returns_up_when_select_one_succeeds(self) -> None:
        """When SELECT 1 succeeds, should return 'up'."""
        settings = Settings(DATABASE_URL="postgresql+asyncpg://u:p@localhost:5432/db")  # type: ignore[call-arg]

        mock_engine = MagicMock()
        mock_engine.dispose = AsyncMock()
        mock_conn = AsyncMock()
        mock_engine.connect.return_value.__aenter__.return_value = mock_conn

        with patch("zenith_ops.api.v1.health.create_async_engine", return_value=mock_engine):
            result = await check_database(settings)

        assert result == "up"
        mock_conn.execute.assert_awaited_once()

    async def test_returns_down_when_connection_fails(self) -> None:
        """When database is unreachable, should return 'down'."""
        settings = Settings(DATABASE_URL="postgresql+asyncpg://u:p@localhost:1/nonexistent")  # type: ignore[call-arg]

        mock_engine = MagicMock()
        mock_engine.dispose = AsyncMock()
        mock_engine.connect.side_effect = ConnectionError("Unreachable")

        with patch("zenith_ops.api.v1.health.create_async_engine", return_value=mock_engine):
            result = await check_database(settings)

        assert result == "down"


class TestCheckModelCache:
    """check_model_cache() — checks InferenceService cache."""

    def test_returns_true_when_models_are_cached(self) -> None:
        """When InferenceService has models, should return True."""
        InferenceService._models["test"] = object()
        try:
            result = check_model_cache()
            assert result is True
        finally:
            InferenceService._models.clear()

    def test_returns_false_when_cache_is_empty(self) -> None:
        """When InferenceService has no models, should return False."""
        InferenceService._models.clear()
        result = check_model_cache()
        assert result is False
