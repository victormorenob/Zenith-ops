"""Integration tests for error handling middleware.

Tests:
- Task 1.1: X-Correlation-ID header on success responses (GET /health/live)
- Task 1.2: X-Correlation-ID header on domain error responses (POST unknown model → 404)
- Task 1.3: Catch-all returns JSON 500 for unhandled exceptions
- Task 1.4: Domain exception handlers (ModelNotFoundError) still take precedence
"""

import re
from unittest.mock import patch

import structlog
from fastapi.testclient import TestClient

from zenith_ops import app
from zenith_ops.core.exceptions import ModelNotFoundError, Zenitherror

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
        # Arrange
        with patch(
            "zenith_ops.api.v1.predict.InferenceService.predict",
            side_effect=ModelNotFoundError("nonexistent-model"),
        ):
            # Act
            response = client.post(
                "/v1/predict",
                json={"model_id": "nonexistent-model", "features": {"x": 1.0}},
            )

        # Assert
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
        # Arrange
        with patch(
            "zenith_ops.api.v1.predict.InferenceService.predict",
            side_effect=ModelNotFoundError("nonexistent-model"),
        ):
            # Act
            response = client.post(
                "/v1/predict",
                json={"model_id": "nonexistent-model", "features": {"x": 1.0}},
            )

        # Assert
        assert response.status_code == 404
        body = response.json()
        assert body["error"] == "model_not_found", (
            "Domain handler must run, not catch-all"
        )


class TestZenitherrorFallbackHandler:
    """Generic domain fallback keeps future Zenitherror contracts structured."""

    def test_handlerless_zenitherror_returns_domain_message_not_catch_all(
        self,
    ) -> None:
        """Unhandled Zenitherror subclasses use the domain fallback handler."""

        class FutureDomainError(Zenitherror):
            """Test-only domain error without a dedicated HTTP handler."""

        # Arrange
        with patch(
            "zenith_ops.api.v1.predict.InferenceService.predict",
            side_effect=FutureDomainError("registry unavailable"),
        ):
            # Act
            response = client.post(
                "/v1/predict",
                json={"model_id": "iris-classifier", "features": {"x": 1.0}},
            )

        # Assert
        assert response.status_code == 500
        assert response.json() == {
            "error": "internal_error",
            "message": "registry unavailable",
        }
        assert "X-Correlation-ID" in response.headers
        assert re.match(UUID_V4_REGEX, response.headers["X-Correlation-ID"])


# ── Test-only endpoint for triggering unhandled exceptions ──────────
# This route raises an unhandled RuntimeError so the catch-all middleware
# must catch it and return a structured JSON 500 response.
# include_in_schema=False keeps it out of OpenAPI docs.


@app.get("/test/raise-error", include_in_schema=False)
async def _raise_error_handler():
    """Raise an unhandled RuntimeError to test the catch-all middleware."""
    raise RuntimeError("Test unhandled error")
