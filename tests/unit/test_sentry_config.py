"""Unit tests for Sentry configuration."""

from unittest.mock import MagicMock, patch

import pytest

from zenith_ops.core.settings import Settings


class TestSettingsSentryEnabled:
    """Tests for the ``sentry_enabled`` property on Settings."""

    def test_sentry_disabled_when_dsn_empty(self) -> None:
        # Arrange
        settings = Settings(
            DATABASE_URL="postgresql+asyncpg://u:p@localhost:5432/db",  # type: ignore[arg-type]
            SENTRY_DSN="",
        )

        # Act / Assert
        assert settings.sentry_enabled is False

    def test_sentry_disabled_when_dsn_whitespace(self) -> None:
        # Arrange
        settings = Settings(
            DATABASE_URL="postgresql+asyncpg://u:p@localhost:5432/db",  # type: ignore[arg-type]
            SENTRY_DSN="   ",
        )

        # Act / Assert
        assert settings.sentry_enabled is False

    def test_sentry_enabled_when_dsn_set(self) -> None:
        # Arrange
        settings = Settings(
            DATABASE_URL="postgresql+asyncpg://u:p@localhost:5432/db",  # type: ignore[arg-type]
            SENTRY_DSN="https://key@o0.ingest.sentry.io/1",
        )

        # Act / Assert
        assert settings.sentry_enabled is True


class TestConfigureSentry:
    """Tests for ``configure_sentry()`` — init is skipped or called per DSN."""

    def test_configure_sentry_skips_init_when_dsn_empty(self) -> None:
        # Arrange
        from zenith_ops.core.sentry_config import configure_sentry

        settings = Settings(
            DATABASE_URL="postgresql+asyncpg://u:p@localhost:5432/db",  # type: ignore[arg-type]
            SENTRY_DSN="",
        )

        # Act
        with patch("zenith_ops.core.sentry_config.sentry_sdk.init") as mock_init:
            result = configure_sentry(settings)

        # Assert
        assert result is False
        mock_init.assert_not_called()

    @patch("zenith_ops.core.sentry_config.sentry_sdk.init")
    def test_configure_sentry_calls_init_when_dsn_set(
        self, mock_init: MagicMock
    ) -> None:
        # Arrange
        from zenith_ops.core.sentry_config import configure_sentry

        settings = Settings(
            DATABASE_URL="postgresql+asyncpg://u:p@localhost:5432/db",  # type: ignore[arg-type]
            SENTRY_DSN="https://key@o0.ingest.sentry.io/1",
            SENTRY_ENVIRONMENT="staging",
            SENTRY_TRACES_SAMPLE_RATE=0.25,
        )

        # Act
        result = configure_sentry(settings)

        # Assert
        assert result is True
        mock_init.assert_called_once()
        call_kwargs = mock_init.call_args.kwargs
        assert call_kwargs["dsn"] == "https://key@o0.ingest.sentry.io/1"
        assert call_kwargs["environment"] == "staging"
        assert call_kwargs["traces_sample_rate"] == 0.25
        assert call_kwargs["send_default_pii"] is False
        assert len(call_kwargs["integrations"]) == 2


class TestCaptureException:
    """Tests for ``capture_exception()`` — no-op when Sentry is inactive."""

    def test_capture_exception_noop_when_client_inactive(self) -> None:
        # Arrange
        from zenith_ops.core.sentry_config import capture_exception

        mock_client = MagicMock()
        mock_client.is_active.return_value = False

        # Act
        with (
            patch(
                "zenith_ops.core.sentry_config.sentry_sdk.get_client",
                return_value=mock_client,
            ),
            patch(
                "zenith_ops.core.sentry_config.sentry_sdk.capture_exception"
            ) as mock_capture,
        ):
            capture_exception(RuntimeError("test"))

        # Assert
        mock_capture.assert_not_called()

    def test_capture_exception_sends_when_client_active(self) -> None:
        # Arrange
        from zenith_ops.core.sentry_config import capture_exception

        mock_client = MagicMock()
        mock_client.is_active.return_value = True
        exc = RuntimeError("test")

        # Act
        with (
            patch(
                "zenith_ops.core.sentry_config.sentry_sdk.get_client",
                return_value=mock_client,
            ),
            patch(
                "zenith_ops.core.sentry_config.sentry_sdk.capture_exception"
            ) as mock_capture,
        ):
            capture_exception(exc)

        # Assert
        mock_capture.assert_called_once_with(exc)


class TestEnrichEventWithCorrelationId:
    """Tests for the Sentry ``before_send`` hook."""

    def test_adds_correlation_id_tag_from_structlog_context(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange
        from structlog.contextvars import bind_contextvars, clear_contextvars

        from zenith_ops.core.sentry_config import _enrich_event_with_correlation_id

        bind_contextvars(correlation_id="abc-123")
        event: dict[str, object] = {}

        try:
            # Act
            enriched = _enrich_event_with_correlation_id(event, {})

            # Assert
            assert enriched is event
            tags = enriched.get("tags")
            assert isinstance(tags, dict)
            assert tags["correlation_id"] == "abc-123"
        finally:
            clear_contextvars()

    def test_preserves_existing_tags_when_adding_correlation_id(self) -> None:
        # Arrange
        from structlog.contextvars import bind_contextvars, clear_contextvars

        from zenith_ops.core.sentry_config import _enrich_event_with_correlation_id

        bind_contextvars(correlation_id="request-456")
        event: dict[str, object] = {"tags": {"component": "api"}}

        try:
            # Act
            enriched = _enrich_event_with_correlation_id(event, {})

            # Assert
            assert enriched is event
            tags = enriched.get("tags")
            assert isinstance(tags, dict)
            assert tags == {
                "component": "api",
                "correlation_id": "request-456",
            }
        finally:
            clear_contextvars()

    def test_leaves_event_unchanged_without_correlation_id(self) -> None:
        # Arrange
        from zenith_ops.core.sentry_config import _enrich_event_with_correlation_id

        event: dict[str, object] = {}

        # Act
        enriched = _enrich_event_with_correlation_id(event, {})

        # Assert
        assert enriched is event
        assert "tags" not in enriched
