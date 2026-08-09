"""Unit tests for PostgresModelRegistry with mocked AsyncSession."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from zenith_ops.core.exceptions import DuplicateModelError, ModelNotFoundError
from zenith_ops.core.model_registry import ModelMetadata, ModelSummary
from zenith_ops.core.model_registry_db import PostgresModelRegistry
from zenith_ops.db.models.model_registry import ModelRegistryEntry
from zenith_ops.db.models.prediction_metadata import PredictionMetadata

# ── Fixtures ────────────────────────────────────────────────────────────


@pytest.fixture
def mock_session() -> AsyncMock:
    """Return an AsyncMock that quacks like an AsyncSession."""
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def mock_session_factory(mock_session: AsyncMock) -> AsyncMock:
    """Return an async_sessionmaker clone that yields mock_session."""
    factory = MagicMock(spec=async_sessionmaker)
    factory.return_value.__aenter__.return_value = mock_session
    factory.return_value.__aexit__ = AsyncMock(return_value=None)
    return factory


@pytest.fixture
def registry(mock_session_factory: AsyncMock) -> PostgresModelRegistry:
    """Return a PostgresModelRegistry wired to the mock factory."""
    return PostgresModelRegistry(mock_session_factory)


def _make_entry(
    name: str = "iris-classifier",
    version: str = "1.0.0",
    status: str = "production",
    created_at: datetime | None = None,
) -> MagicMock:
    """Build a MagicMock that looks like a ModelRegistryEntry ORM row."""
    entry = MagicMock(spec=ModelRegistryEntry)
    entry.id = "550e8400-e29b-41d4-a716-446655440000"
    entry.name = name
    entry.version = version
    entry.framework = "sklearn"
    entry.artifact_path = f"/tmp/models/{name}/{version}/model.joblib"
    entry.status = status
    entry.description = "Test model"
    entry.metrics = {"accuracy": 0.95}
    entry.tags = ["iris"]  # JSONB stores arrays natively
    entry.input_schema = None
    entry.output_schema = None
    entry.created_at = created_at or datetime(2026, 6, 15, 12, 0, 0, tzinfo=UTC)
    entry.updated_at = None
    entry.deployed_at = None
    return entry


# ── B.3: Constructor ────────────────────────────────────────────────────


class TestConstructor:
    """PostgresModelRegistry can be instantiated with a session factory."""

    def test_accepts_session_factory(self, mock_session_factory: AsyncMock) -> None:
        """Constructor stores the factory as _session_factory."""
        reg = PostgresModelRegistry(mock_session_factory)
        assert reg._session_factory is mock_session_factory


# ── B.4: list_models ────────────────────────────────────────────────────


class TestListModels:
    """list_models returns the latest non-archived version per model name."""

    async def test_empty_db_returns_empty_list(
        self, registry: PostgresModelRegistry, mock_session: AsyncMock
    ) -> None:
        """When no models exist, list_models returns [].

        This verifies the query runs and returns nothing.
        """
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = result_mock

        models = await registry.list_models()

        assert models == []
        mock_session.execute.assert_awaited_once()

    async def test_returns_summary_for_each_model(
        self, registry: PostgresModelRegistry, mock_session: AsyncMock
    ) -> None:
        """Each model appears as a ModelSummary with correct fields."""
        entry = _make_entry()
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = [entry]
        mock_session.execute.return_value = result_mock

        models = await registry.list_models()

        assert len(models) == 1
        summary = models[0]
        assert isinstance(summary, ModelSummary)
        assert summary.model_id == "iris-classifier"
        assert summary.name == "iris-classifier"
        assert summary.latest_version == "1.0.0"
        assert summary.framework == "sklearn"
        assert summary.status == "production"
        assert summary.tags == ["iris"]

    async def test_excludes_archived_models(
        self, registry: PostgresModelRegistry, mock_session: AsyncMock
    ) -> None:
        """Archived models should not appear in list_models results.

        The query condition should filter out status='archived'.
        """
        # The mock returns an empty list simulating the WHERE exclusion
        result_mock = MagicMock()
        result_mock.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = result_mock

        models = await registry.list_models()
        assert models == []

        # The query should have been executed — the WHERE clause
        # filters archived, so the archived entry is excluded.
        mock_session.execute.assert_awaited_once()


# ── B.5: get_model ──────────────────────────────────────────────────────


class TestGetModel:
    """get_model returns the latest version of a model by name."""

    async def test_returns_metadata_for_existing_model(
        self, registry: PostgresModelRegistry, mock_session: AsyncMock
    ) -> None:
        """When the model exists, get_model returns full ModelMetadata."""
        entry = _make_entry()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = entry
        mock_session.execute.return_value = result_mock

        metadata = await registry.get_model("iris-classifier")

        assert isinstance(metadata, ModelMetadata)
        assert metadata.model_id == "iris-classifier"
        assert metadata.name == "iris-classifier"
        assert metadata.version == "1.0.0"
        assert metadata.framework == "sklearn"
        assert metadata.status == "production"

    async def test_raises_not_found_for_unknown_model(
        self, registry: PostgresModelRegistry, mock_session: AsyncMock
    ) -> None:
        """When no model matches, get_model raises ModelNotFoundError."""
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = result_mock

        with pytest.raises(ModelNotFoundError, match="unknown"):
            await registry.get_model("unknown")


# ── B.6: resolve_path ───────────────────────────────────────────────────


class TestResolvePath:
    """resolve_path returns the artifact path from the DB."""

    async def test_returns_path_from_artifact_path(
        self, registry: PostgresModelRegistry, mock_session: AsyncMock
    ) -> None:
        """resolve_path delegates to get_model and returns artifact_path as Path."""
        entry = _make_entry()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = entry
        mock_session.execute.return_value = result_mock

        path = await registry.resolve_path("iris-classifier")

        assert isinstance(path, Path)
        assert str(path) == "/tmp/models/iris-classifier/1.0.0/model.joblib"

    async def test_raises_not_found(
        self, registry: PostgresModelRegistry, mock_session: AsyncMock
    ) -> None:
        """If get_model raises, resolve_path propagates the error."""
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = result_mock

        with pytest.raises(ModelNotFoundError):
            await registry.resolve_path("ghost-model")


# ── B.7: register_model ────────────────────────────────────────────────


class TestRegisterModel:
    """register_model creates a new model version or raises DuplicateModelError."""

    async def test_registers_new_model_successfully(
        self, registry: PostgresModelRegistry, mock_session: AsyncMock
    ) -> None:
        """A successful registration returns ModelMetadata and commits."""
        # First query (duplicate check) returns None
        none_result = MagicMock()
        none_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = none_result

        # Mock refresh to populate the entry
        def _refresh_side_effect(obj: ModelRegistryEntry) -> None:
            obj.id = "550e8400-e29b-41d4-a716-446655440000"
            obj.created_at = datetime(2026, 6, 22, 12, 0, 0, tzinfo=UTC)

        mock_session.refresh.side_effect = _refresh_side_effect

        metadata = await registry.register_model(
            name="new-model",
            version="1.0.0",
            framework="sklearn",
            artifact_path="/tmp/models/new-model/1.0.0/model.joblib",
            description="A brand new model",
            metrics={"accuracy": 0.98},
            tags=["new"],
        )

        assert isinstance(metadata, ModelMetadata)
        assert metadata.name == "new-model"
        assert metadata.version == "1.0.0"
        assert metadata.framework == "sklearn"
        assert metadata.status == "staging"  # default status
        assert metadata.tags == ["new"]
        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once()

    async def test_raises_duplicate_for_existing_name_version(
        self, registry: PostgresModelRegistry, mock_session: AsyncMock
    ) -> None:
        """Registering the same (name, version) raises DuplicateModelError."""
        existing_entry = _make_entry()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = existing_entry
        mock_session.execute.return_value = result_mock

        with pytest.raises(DuplicateModelError) as exc_info:
            await registry.register_model(
                name="iris-classifier",
                version="1.0.0",
                framework="sklearn",
                artifact_path="/tmp/models/iris-classifier/1.0.0/model.joblib",
            )

        assert exc_info.value.name == "iris-classifier"
        assert exc_info.value.version == "1.0.0"
        # Should NOT commit or add
        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_awaited()


# ── B.8: update_status ──────────────────────────────────────────────────


class TestUpdateStatus:
    """update_status changes a model version's status by UUID."""

    async def test_updates_status_successfully(
        self, registry: PostgresModelRegistry, mock_session: AsyncMock
    ) -> None:
        """A valid status update returns updated ModelMetadata."""
        entry = _make_entry(status="staging")
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = entry
        mock_session.execute.return_value = result_mock

        def _refresh_side_effect(obj: ModelRegistryEntry) -> None:
            obj.status = "production"
            obj.updated_at = datetime(2026, 6, 22, 12, 0, 0, tzinfo=UTC)

        mock_session.refresh.side_effect = _refresh_side_effect

        metadata = await registry.update_status(
            model_uuid="550e8400-e29b-41d4-a716-446655440000",
            status="production",
        )

        assert metadata.status == "production"
        mock_session.commit.assert_awaited_once()

    async def test_raises_error_for_invalid_status(
        self, registry: PostgresModelRegistry, mock_session: AsyncMock
    ) -> None:
        """An invalid status value raises ValueError."""
        entry = _make_entry()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = entry
        mock_session.execute.return_value = result_mock

        with pytest.raises(ValueError, match="status"):
            await registry.update_status(
                model_uuid="550e8400-e29b-41d4-a716-446655440000",
                status="invalid",
            )

    async def test_raises_not_found_for_unknown_uuid(
        self, registry: PostgresModelRegistry, mock_session: AsyncMock
    ) -> None:
        """A non-existent UUID raises ModelNotFoundError."""
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = result_mock

        with pytest.raises(ModelNotFoundError, match="550e8400"):
            await registry.update_status(
                model_uuid="550e8400-e29b-41d4-a716-446655440000",
                status="production",
            )


# ── C.Extra: register_and_build_model (Phase C) ──────────────────────────


class TestRegisterAndBuildModel:
    """register_and_build_model generates a .joblib from model_type."""

    async def test_calls_build_and_register(
        self, registry: PostgresModelRegistry, mock_session: AsyncMock
    ) -> None:
        """register_and_build_model builds model, dumps it, and calls register_model."""
        # Arrange
        none_result = MagicMock()
        none_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = none_result
        input_schema = {"type": "object", "required": ["sepal_length"]}
        output_schema = {"type": "number"}

        def _refresh_side_effect(obj) -> None:
            obj.id = "550e8400-e29b-41d4-a716-446655440000"
            obj.created_at = datetime(2026, 6, 22, 12, 0, 0, tzinfo=UTC)

        mock_session.refresh.side_effect = _refresh_side_effect

        # Act
        metadata = await registry.register_and_build_model(
            name="new-model",
            version="1.0.0",
            framework="sklearn",
            model_type="dummy_iris",
            description="Built from model_type",
            metrics={"accuracy": 0.99},
            tags=["auto"],
            input_schema=input_schema,
            output_schema=output_schema,
        )

        # Assert
        assert metadata.name == "new-model"
        assert metadata.version == "1.0.0"
        assert metadata.status == "staging"
        mock_session.add.assert_called_once()
        added_entry: ModelRegistryEntry = mock_session.add.call_args.args[0]
        assert added_entry.description == "Built from model_type"
        assert added_entry.metrics == {"accuracy": 0.99}
        assert added_entry.tags == ["auto"]
        assert added_entry.input_schema == input_schema
        assert added_entry.output_schema == output_schema
        mock_session.commit.assert_awaited_once()

    async def test_unknown_model_type_raises_value_error(
        self,
        registry: PostgresModelRegistry,
        mock_session: AsyncMock,
        mock_session_factory: AsyncMock,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """An unknown model_type must fail before artifact or DB writes."""
        # Arrange
        monkeypatch.chdir(tmp_path)

        # Act / Assert
        with pytest.raises(ValueError, match="desconocido"):
            await registry.register_and_build_model(
                name="bad-model",
                version="1.0.0",
                framework="sklearn",
                model_type="nonexistent_type",
            )
        assert not (tmp_path / "models").exists()
        mock_session_factory.assert_not_called()
        mock_session.execute.assert_not_awaited()
        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_awaited()


# ── log_prediction (Phase D) ──────────────────────────────────────────────


class TestLogPrediction:
    """log_prediction saves prediction metadata (best-effort, no error prop)."""

    async def test_log_prediction_success(
        self, registry: PostgresModelRegistry, mock_session: AsyncMock
    ) -> None:
        """When model is found, prediction metadata is inserted and committed."""
        model_uuid = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = model_uuid
        mock_session.execute.return_value = result_mock

        request_id = uuid.uuid4()
        await registry.log_prediction(
            request_id=request_id,
            model_id="iris-classifier",
            features={"sepal_length": 5.1},
            result=0.5,
            result_type="scalar",
            latency_ms=10.0,
            status="success",
            error_message=None,
        )

        mock_session.execute.assert_awaited()
        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()
        added_entry: PredictionMetadata = mock_session.add.call_args[0][0]
        assert added_entry.request_id == request_id
        assert added_entry.status == "success"
        assert added_entry.latency_ms == 10.0
        assert added_entry.result_type == "scalar"
        assert added_entry.result is None

    async def test_log_prediction_model_not_found(
        self, registry: PostgresModelRegistry, mock_session: AsyncMock
    ) -> None:
        """When model_id is not in registry, log_prediction logs warning and returns."""
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = result_mock

        await registry.log_prediction(
            request_id=uuid.uuid4(),
            model_id="unknown-model",
            features={},
            result=0.5,
            result_type="scalar",
            latency_ms=10.0,
            status="success",
            error_message=None,
        )

        mock_session.execute.assert_awaited()
        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_awaited()

    async def test_log_prediction_db_error_does_not_propagate(
        self, registry: PostgresModelRegistry, mock_session: AsyncMock
    ) -> None:
        """A DB error inside log_prediction must be caught and not propagated."""
        mock_session.execute.side_effect = Exception("DB connection lost")

        # Must NOT raise — this is best-effort logging
        await registry.log_prediction(
            request_id=uuid.uuid4(),
            model_id="iris-classifier",
            features={},
            result=0.5,
            result_type="scalar",
            latency_ms=10.0,
            status="error",
            error_message="timeout",
        )


# ── DI factory ──────────────────────────────────────────────────────────


class TestGetRegistry:
    """get_registry() returns a PostgresModelRegistry singleton."""

    @patch("zenith_ops.db.session.async_session_factory")
    async def test_returns_registry_instance(
        self, mock_async_session_factory: MagicMock
    ) -> None:
        """get_registry returns a PostgresModelRegistry wired to the factory."""
        # Reset singleton so it re-creates with our mock
        import zenith_ops.core.model_registry_db as reg_db

        reg_db._registry_instance = None
        reg = await reg_db.get_registry()
        assert isinstance(reg, PostgresModelRegistry)

    @patch("zenith_ops.db.session.async_session_factory")
    async def test_singleton_reuses_instance(
        self, mock_async_session_factory: MagicMock
    ) -> None:
        """Multiple calls to get_registry return the same instance."""
        import zenith_ops.core.model_registry_db as reg_db

        reg_db._registry_instance = None
        reg1 = await reg_db.get_registry()
        reg2 = await reg_db.get_registry()
        assert reg1 is reg2
