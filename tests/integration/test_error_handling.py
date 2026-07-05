"""Integration tests for error handling middleware.

Tests:
- Task 1.1: X-Correlation-ID header on success responses (GET /health/live)
- Task 1.2: X-Correlation-ID header on domain error responses (POST unknown model → 404)
- Task 1.3: Catch-all returns JSON 500 for unhandled exceptions
- Task 1.4: Domain exception handlers (ModelNotFoundError) still take precedence
"""

import re
from typing import NoReturn

import pytest
import structlog
from fastapi import status
from fastapi.testclient import TestClient

from zenith_ops import app
from zenith_ops.core.exceptions import InferenceTimeoutError
from zenith_ops.services.predictor import InferenceService

UUID_V4_REGEX = r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"

client = TestClient(app)


class TestCorrelationIdOnSuccess:
    """Task 1.1: X-Correlation-ID present on 200 responses."""

    def test_header_present_on_health_live(self) -> None:
        """GET /health/live should include X-Correlation-ID header."""
        response = client.get("/health/live")
        assert response.status_code == 200
        assert "X-Correlation-ID" in response.headers
        assert re.match(UUID_V4_REGEX, response.headers["X-Correlation-ID"])


class TestCorrelationIdOnError:
    """Task 1.2: X-Correlation-ID present on domain error responses."""

    def test_header_present_on_domain_404(self) -> None:
        """Domain 404 (unknown model) should include X-Correlation-ID header."""
        response = client.post(
            "/v1/predict",
            json={"model_id": "nonexistent-model", "features": {"x": 1.0}},
        )
        assert response.status_code == 404
        assert "X-Correlation-ID" in response.headers
        assert re.match(UUID_V4_REGEX, response.headers["X-Correlation-ID"])


class TestUnhandledException:
    """Task 1.3: Catch-all middleware catches unhandled RuntimeError."""

    def test_unhandled_error_returns_json_500(self) -> None:
        """Unhandled RuntimeError should return consistent JSON 500."""
        response = client.get("/test/raise-error")
        assert response.status_code == 500
        assert response.headers["content-type"] == "application/json"
        body = response.json()
        assert body == {
            "error": "internal_error",
            "message": "An unexpected error occurred",
        }

    def test_stacktrace_logged_not_exposed(self) -> None:
        """Stacktrace is logged via structlog, not exposed in response body."""
        with structlog.testing.capture_logs() as cap:
            response = client.get("/test/raise-error")
            assert response.status_code == 500

        # Response body MUST NOT expose stacktrace or exception message
        body = response.json()
        assert body == {
            "error": "internal_error",
            "message": "An unexpected error occurred",
        }

        # Stacktrace MUST appear in structlog output
        error_logs = [e for e in cap if e.get("event") == "unhandled_exception"]
        assert len(error_logs) == 1, (
            f"Expected 1 'unhandled_exception' event, got {len(error_logs)}"
        )
        log = error_logs[0]
        assert log["method"] == "GET"
        assert log["endpoint"] == "/test/raise-error"
        assert "correlation_id" in log
        assert "exc_info" in log

    def test_correlation_id_on_unhandled_error(self) -> None:
        """X-Correlation-ID header should be present on unhandled error."""
        response = client.get("/test/raise-error")
        assert response.status_code == 500
        assert "X-Correlation-ID" in response.headers
        assert re.match(UUID_V4_REGEX, response.headers["X-Correlation-ID"])


class TestDomainHandlerPrecedence:
    """Task 1.4: Domain handlers still take precedence over catch-all."""

    def test_model_not_found_returns_404_not_internal_error(self) -> None:
        """ModelNotFoundError should return 404, not catch-all 500."""
        response = client.post(
            "/v1/predict",
            json={"model_id": "nonexistent-model", "features": {"x": 1.0}},
        )
        assert response.status_code == 404
        body = response.json()
        assert body["error"] == "model_not_found", (
            "Domain handler must run, not catch-all"
        )


class TestInferenceTimeoutContract:
    """Inference timeout domain errors keep the public API contract."""

    def test_predict_timeout_returns_503_not_internal_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """InferenceTimeoutError should map to the retryable 503 contract."""

        async def fake_predict(
            model_id: str,
            features: dict[str, float],
            idempotency_key: str | None = None,
        ) -> NoReturn:
            raise InferenceTimeoutError(timeout_ms=5000)

        # Arrange
        monkeypatch.setattr(InferenceService, "predict", fake_predict)

        # Act
        response = client.post(
            "/v1/predict",
            json={
                "model_id": "slow-model",
                "features": {"sepal_length": 5.1},
            },
        )

        # Assert
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert response.json() == {
            "error": "inference_timeout",
            "message": "Inference took longer than 5000ms",
        }
        assert re.match(UUID_V4_REGEX, response.headers["X-Correlation-ID"])


# ── Test-only endpoint for triggering unhandled exceptions ──────────
# This route raises an unhandled RuntimeError so the catch-all middleware
# must catch it and return a structured JSON 500 response.
# include_in_schema=False keeps it out of OpenAPI docs.


@app.get("/test/raise-error", include_in_schema=False)
async def _raise_error_handler():
    """Raise an unhandled RuntimeError to test the catch-all middleware."""
    raise RuntimeError("Test unhandled error")
