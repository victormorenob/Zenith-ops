"""Unit tests for the dummy-model seed script."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scripts import generate_dummy_model
from zenith_ops.core.exceptions import DuplicateModelError


def _metadata() -> SimpleNamespace:
    """Return minimal model metadata for seed logging assertions."""
    return SimpleNamespace(
        model_id=generate_dummy_model.MODEL_NAME,
        version=generate_dummy_model.MODEL_VERSION,
        status="staging",
        artifact_path=generate_dummy_model.ARTIFACT_PATH,
    )


class TestSeedDummyModel:
    """The seed script registers the default model safely and idempotently."""

    async def test_seed_registers_dummy_model_and_disposes_engine(self) -> None:
        """A fresh seed registers the configured dummy model and closes the engine."""
        # Arrange
        mock_registry = MagicMock()
        mock_registry.register_and_build_model = AsyncMock(return_value=_metadata())
        mock_registry_cls = MagicMock(return_value=mock_registry)
        mock_engine = MagicMock()
        mock_engine.dispose = AsyncMock()

        # Act
        with (
            patch.object(
                generate_dummy_model,
                "PostgresModelRegistry",
                mock_registry_cls,
            ),
            patch.object(generate_dummy_model, "engine", mock_engine),
            patch.object(generate_dummy_model.logger, "info") as mock_log_info,
        ):
            await generate_dummy_model.seed_dummy_model()

        # Assert
        mock_registry_cls.assert_called_once_with(generate_dummy_model.async_session_factory)
        mock_registry.register_and_build_model.assert_awaited_once_with(
            name=generate_dummy_model.MODEL_NAME,
            version=generate_dummy_model.MODEL_VERSION,
            framework=generate_dummy_model.FRAMEWORK,
            model_type=generate_dummy_model.MODEL_TYPE,
            description="Dummy Iris classifier for local development",
            tags=["classification", "iris", "multiclass"],
        )
        mock_engine.dispose.assert_awaited_once()
        mock_log_info.assert_called_once_with(
            "seed_completed",
            model_id=generate_dummy_model.MODEL_NAME,
            version=generate_dummy_model.MODEL_VERSION,
            status="staging",
            artifact_path=generate_dummy_model.ARTIFACT_PATH,
        )

    async def test_seed_treats_duplicate_model_as_idempotent(self) -> None:
        """An existing seed row is logged and does not fail local startup."""
        # Arrange
        mock_registry = MagicMock()
        mock_registry.register_and_build_model = AsyncMock(
            side_effect=DuplicateModelError(
                generate_dummy_model.MODEL_NAME,
                generate_dummy_model.MODEL_VERSION,
            )
        )
        mock_registry_cls = MagicMock(return_value=mock_registry)
        mock_engine = MagicMock()
        mock_engine.dispose = AsyncMock()

        # Act
        with (
            patch.object(
                generate_dummy_model,
                "PostgresModelRegistry",
                mock_registry_cls,
            ),
            patch.object(generate_dummy_model, "engine", mock_engine),
            patch.object(generate_dummy_model.logger, "info") as mock_log_info,
        ):
            await generate_dummy_model.seed_dummy_model()

        # Assert
        mock_registry.register_and_build_model.assert_awaited_once()
        mock_engine.dispose.assert_awaited_once()
        mock_log_info.assert_called_once_with(
            "seed_already_exists",
            name=generate_dummy_model.MODEL_NAME,
            version=generate_dummy_model.MODEL_VERSION,
            artifact_path=generate_dummy_model.ARTIFACT_PATH,
        )

    async def test_seed_disposes_engine_when_unexpected_error_propagates(self) -> None:
        """Unexpected registration failures should fail the command after cleanup."""
        # Arrange
        mock_registry = MagicMock()
        mock_registry.register_and_build_model = AsyncMock(
            side_effect=RuntimeError("database unavailable")
        )
        mock_registry_cls = MagicMock(return_value=mock_registry)
        mock_engine = MagicMock()
        mock_engine.dispose = AsyncMock()

        # Act
        with (
            patch.object(
                generate_dummy_model,
                "PostgresModelRegistry",
                mock_registry_cls,
            ),
            patch.object(generate_dummy_model, "engine", mock_engine),
            pytest.raises(RuntimeError, match="database unavailable"),
        ):
            await generate_dummy_model.seed_dummy_model()

        # Assert
        mock_registry.register_and_build_model.assert_awaited_once()
        mock_engine.dispose.assert_awaited_once()
