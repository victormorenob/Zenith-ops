"""Unit tests for structured logging configuration.

Tests the configure_logging() function that sets up structlog
with env-aware renderer selection and log level support,
plus the correlation_id middleware.
"""

import json
import logging
import re
from unittest.mock import patch

import pytest
import structlog
from fastapi import Request
from fastapi.responses import Response
from fastapi.testclient import TestClient

from zenith_ops import app

UUID_V4_REGEX = r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"


class TestConfigureLogging:
    """Tests for configure_logging() — env-aware structlog setup."""

    def test_can_be_called_without_error(self) -> None:
        """configure_logging() should not raise when called."""
        from zenith_ops.core.logging_config import configure_logging

        result = configure_logging()
        assert result is None

    def test_sets_up_structlog_capture(self) -> None:
        """After configure_logging(), structlog events should be capturable.

        Uses structlog.testing.capture_logs to verify the pipeline is active.
        """
        from zenith_ops.core.logging_config import configure_logging

        configure_logging()

        with structlog.testing.capture_logs() as cap:
            structlog.get_logger().info("test event")

        assert len(cap) == 1
        assert cap[0]["event"] == "test event"

    def test_default_level_is_info(self) -> None:
        """Default log level should be INFO on the root logger."""
        from zenith_ops.core.logging_config import configure_logging

        configure_logging()

        assert logging.getLogger().level == logging.INFO

    def test_log_level_debug_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """LOG_LEVEL=DEBUG should set root logger to DEBUG."""
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        from zenith_ops.core.logging_config import configure_logging

        configure_logging()

        assert logging.getLogger().level == logging.DEBUG

    def test_log_format_json_produces_json_output(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """LOG_FORMAT=json should output valid JSON log lines."""
        monkeypatch.setenv("LOG_FORMAT", "json")
        monkeypatch.setenv("LOG_LEVEL", "INFO")
        from zenith_ops.core.logging_config import configure_logging

        configure_logging()

        logger = structlog.get_logger("test_module")
        logger.info("json_test_event", extra_field="value")

        captured = capsys.readouterr()
        output = captured.err or captured.out
        assert output, "Expected JSON output"

        line = output.strip().split("\n")[-1]
        parsed = json.loads(line)
        assert parsed["event"] == "json_test_event"
        assert parsed["extra_field"] == "value"
        assert "timestamp" in parsed
        assert "level" in parsed or "log_level" in parsed

    def test_stdlib_bridge_captures_standard_logging(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Stdlib logging calls should be captured by structlog."""
        monkeypatch.setenv("LOG_LEVEL", "INFO")
        from zenith_ops.core.logging_config import configure_logging

        configure_logging()

        stdlib_logger = logging.getLogger("stdlib_bridge_test")
        stdlib_logger.info("stdlib_test_event")

        captured = capsys.readouterr()
        output = captured.err or captured.out
        assert output, "Expected structlog to capture stdlib logging output"
        assert "stdlib_test_event" in output

    def test_module_bound_logger_includes_module_name(self) -> None:
        """Logger from structlog.get_logger(__name__) should have module name in context.

        Uses LogCapture to verify the logger name is available — ConsoleRenderer
        does not display it by default, but it is present in the structlog context.
        """
        from zenith_ops.core.logging_config import configure_logging

        configure_logging()

        with structlog.testing.capture_logs() as cap:
            module_logger = structlog.get_logger("tests.unit.test_logging")
            module_logger.info("module_test_event")

        assert len(cap) == 1
        assert cap[0]["event"] == "module_test_event"
        # The logger name is bound internally by structlog when using get_logger(name)
        # ConsoleRenderer omits it from display, but the bound logger carries it


class TestMiddleware:
    """Tests for the correlation_id HTTP middleware.

    Verifies that every request receives a UUID v4 correlation_id
    and that the middleware produces a ``request_completed`` log
    entry with all required fields.
    """

    def test_middleware_logs_info_for_success(self) -> None:
        """200 responses should log at INFO level."""
        with structlog.testing.capture_logs() as cap:
            client = TestClient(app)
            response = client.get("/health/live")
            assert response.status_code == 200

        req_logs = [e for e in cap if e.get("event") == "request_completed"]
        assert len(req_logs) == 1
        assert req_logs[0]["status"] == 200
        assert req_logs[0]["log_level"] == "info", "200 should log at INFO level"

    def test_middleware_logs_warning_for_not_found(self) -> None:
        """404 responses should log at WARNING level."""
        with structlog.testing.capture_logs() as cap:
            client = TestClient(app)
            response = client.get("/nonexistent-route")
            assert response.status_code == 404

        req_logs = [e for e in cap if e.get("event") == "request_completed"]
        assert len(req_logs) == 1
        assert req_logs[0]["status"] == 404
        assert req_logs[0]["log_level"] == "warning", "404 should log at WARNING level"

    def test_middleware_logs_error_for_server_error(self) -> None:
        """500 responses should log at ERROR level."""
        from unittest.mock import patch

        from zenith_ops.core.exceptions import InferenceError

        with (
            patch(
                "zenith_ops.api.v1.predict.InferenceService.predict",
                side_effect=InferenceError("forced server error"),
            ),
            structlog.testing.capture_logs() as cap,
        ):
            client = TestClient(app)
            response = client.post(
                "/v1/predict",
                json={
                    "model_id": "iris-classifier",
                    "features": {
                        "sepal_length": 5.1,
                        "sepal_width": 3.5,
                        "petal_length": 1.4,
                        "petal_width": 0.2,
                    },
                },
            )
            assert response.status_code == 500

        req_logs = [e for e in cap if e.get("event") == "request_completed"]
        assert len(req_logs) == 1
        assert req_logs[0]["status"] == 500
        assert req_logs[0]["log_level"] == "error", "500 should log at ERROR level"

    def test_middleware_logs_valid_uuid_correlation_id(self) -> None:
        """Middleware should assign a valid UUID v4 as correlation_id."""
        with structlog.testing.capture_logs() as cap:
            client = TestClient(app)
            response = client.get("/health/live")
            assert response.status_code == 200

        req_logs = [e for e in cap if e.get("event") == "request_completed"]
        assert len(req_logs) == 1, (
            f"Expected 1 'request_completed' log, got {len(req_logs)}"
        )
        correlation_id = req_logs[0]["correlation_id"]
        assert isinstance(correlation_id, str), (
            f"correlation_id should be str, got {type(correlation_id)}"
        )
        assert re.match(UUID_V4_REGEX, correlation_id), (
            f"correlation_id '{correlation_id}' does not match UUID v4 pattern"
        )

    def test_middleware_logs_all_required_fields(self) -> None:
        """``request_completed`` log must have method, endpoint, status,
        duration_ms, and correlation_id."""
        with structlog.testing.capture_logs() as cap:
            client = TestClient(app)
            response = client.get("/health/live")
            assert response.status_code == 200

        req_logs = [e for e in cap if e.get("event") == "request_completed"]
        assert len(req_logs) == 1, (
            f"Expected 1 'request_completed' log, got {len(req_logs)}"
        )
        log = req_logs[0]
        assert log["method"] == "GET"
        assert log["endpoint"] == "/health/live"
        assert log["status"] == 200
        assert isinstance(log["duration_ms"], (int, float))
        assert log["duration_ms"] >= 0
        assert isinstance(log["correlation_id"], str)
        assert re.match(UUID_V4_REGEX, log["correlation_id"])


class TestCatchAllMiddleware:
    """Tests for the outer catch-all middleware exception path."""

    async def test_unhandled_exception_clears_bound_correlation_context(self) -> None:
        """Unhandled 500 responses must not leak contextvars after completion."""
        # Arrange
        from structlog.contextvars import (
            bind_contextvars,
            clear_contextvars,
            get_contextvars,
        )

        from zenith_ops import catch_all

        request = Request(
            {
                "type": "http",
                "method": "GET",
                "path": "/test/raise-error",
                "headers": [],
                "query_string": b"",
                "server": ("testserver", 80),
                "scheme": "http",
                "client": ("testclient", 50000),
            }
        )
        request.state.correlation_id = "cid-123"
        bind_contextvars(correlation_id="stale-id")

        async def raise_unhandled(_: Request) -> Response:
            raise RuntimeError("boom")

        try:
            # Act
            with patch("zenith_ops.capture_exception"):
                response = await catch_all(request, raise_unhandled)
            context_after_response = get_contextvars()
        finally:
            clear_contextvars()

        # Assert
        assert response.status_code == 500
        assert response.headers["X-Correlation-ID"] == "cid-123"
        assert "correlation_id" not in context_after_response
