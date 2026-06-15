"""Integration tests for the correlation_id middleware.

Uses TestClient against the real FastAPI app with structlog's
``capture_logs`` to verify that every request produces a
``request_completed`` log with all required fields.
"""

import re

import structlog
from fastapi.testclient import TestClient

from zenith_ops import app

UUID_V4_REGEX = r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"

client = TestClient(app)


class TestLivenessLogCapture:
    """Middleware logs from the liveness endpoint."""

    def test_health_live_produces_request_completed_log(self) -> None:
        """GET /v1/health/live should emit a ``request_completed`` event."""
        with structlog.testing.capture_logs() as cap:
            response = client.get("/health/live")
            assert response.status_code == 200

        req_logs = [e for e in cap if e.get("event") == "request_completed"]
        assert len(req_logs) == 1, (
            f"Expected 1 'request_completed' log, got {len(req_logs)}"
        )

    def test_health_live_log_has_all_required_fields(self) -> None:
        """The ``request_completed`` log should contain all 5 fields."""
        with structlog.testing.capture_logs() as cap:
            response = client.get("/health/live")
            assert response.status_code == 200

        req_logs = [e for e in cap if e.get("event") == "request_completed"]
        assert len(req_logs) == 1
        log = req_logs[0]

        assert log["method"] == "GET"
        assert log["endpoint"] == "/health/live"
        assert log["status"] == 200
        assert isinstance(log["duration_ms"], (int, float))
        assert log["duration_ms"] >= 0
        assert re.match(UUID_V4_REGEX, log["correlation_id"]), (
            f"correlation_id '{log['correlation_id']}' is not valid UUID v4"
        )

    def test_health_live_logs_at_info_level(self) -> None:
        """200 responses should log at INFO level."""
        with structlog.testing.capture_logs() as cap:
            response = client.get("/health/live")
            assert response.status_code == 200

        req_logs = [e for e in cap if e.get("event") == "request_completed"]
        assert len(req_logs) == 1
        assert req_logs[0]["log_level"] == "info"


class TestPredictInvalidInputLogCapture:
    """Middleware logs from the predict endpoint with bad input."""

    def test_predict_invalid_features_logs_at_warning(self) -> None:
        """422 responses should log at WARNING level."""
        with structlog.testing.capture_logs() as cap:
            response = client.post(
                "/v1/predict",
                json={
                    "model_id": "test",
                    "features": "not-a-dict",  # should be dict[str, float]
                },
            )
            assert response.status_code == 422

        req_logs = [e for e in cap if e.get("event") == "request_completed"]
        assert len(req_logs) == 1
        assert req_logs[0]["status"] == 422
        assert req_logs[0]["log_level"] == "warning"
