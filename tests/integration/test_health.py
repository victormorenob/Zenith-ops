"""Integration tests for health check endpoints.

Uses TestClient against the real FastAPI app. The liveness endpoint
is verified to work without any database connection. The readiness
endpoint is tested with database mocked to confirm 503 behavior.
"""

from unittest.mock import patch

from fastapi import status
from fastapi.testclient import TestClient

from zenith_ops import app

client = TestClient(app)


class TestLiveIntegration:
    """GET /health/live — zero I/O, no dependencies needed."""

    def test_liveness_succeeds_without_database(self) -> None:
        """Liveness should return 200 even when there is no DB connection."""
        with patch("zenith_ops.api.v1.health.create_async_engine") as mock_db:
            response = client.get("/health/live")

            assert response.status_code == status.HTTP_200_OK
            body = response.json()
            assert body["status"] == "up"
            # Liveness MUST NOT touch the database
            mock_db.assert_not_called()


class TestReadyIntegration:
    """GET /health/ready — depends on check_database and check_model_cache."""

    def test_ready_returns_503_when_db_unreachable(self) -> None:
        """Readiness should return 503 when the database is down.

        Mocks check_database to simulate DB failure without needing
        a real PostgreSQL instance.
        """
        with (
            patch(
                "zenith_ops.api.v1.health.check_database",
                return_value="down",
            ),
            patch(
                "zenith_ops.api.v1.health.check_model_cache",
                return_value=True,
            ),
        ):
            response = client.get("/health/ready")

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        body = response.json()
        assert body["status"] == "down"
        assert body["components"]["database"] == "down"
        assert body["components"]["model_cached"] is True
