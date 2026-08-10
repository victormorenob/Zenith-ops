"""Integration tests for model registry API endpoints (Phase C).

Uses TestClient with dependency overrides to inject a mock
PostgresModelRegistry so tests run without a real PostgreSQL instance.

Tests cover:
  - GET  /v1/models                → list (empty and populated)
  - GET  /v1/models/{model_id}     → detail / 404
  - POST /v1/models/register       → 201 / 409
  - PATCH /v1/models/{id}/status   → 200 / 404
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from zenith_ops import app
from zenith_ops.core.exceptions import DuplicateModelError, ModelNotFoundError
from zenith_ops.core.model_registry import ModelMetadata, ModelSummary
from zenith_ops.core.model_registry_db import (
    PostgresModelRegistry,
    get_registry,
)

# ── Fixtures ────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _override_deps() -> None:
    """Replace get_registry dependency with a mock PostgresModelRegistry.

    Clears overrides after each test so tests are isolated.
    """
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


def _mock_registry() -> PostgresModelRegistry:
    """Build a PostgresModelRegistry with mocked session.

    Returns a fresh instance per call (not the singleton).
    """
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()

    factory = MagicMock(spec=async_sessionmaker)
    factory.return_value.__aenter__.return_value = session
    factory.return_value.__aexit__ = AsyncMock(return_value=None)

    return PostgresModelRegistry(factory)


def _make_entry_dict(
    model_id: str = "iris-classifier",
    version: str = "1.0.0",
    status: str = "production",
) -> dict:
    """Build a dict that looks like a serialized ModelMetadata."""
    return {
        "model_id": model_id,
        "name": model_id,
        "version": version,
        "framework": "sklearn",
        "description": "Test model",
        "created_at": "2026-06-15T12:00:00Z",
        "metrics": {"accuracy": 0.95},
        "status": status,
        "artifact_path": f"/tmp/models/{model_id}/{version}/model.joblib",
        "tags": ["iris"],
        "input_schema": None,
        "output_schema": None,
    }


# ── GET /v1/models ──────────────────────────────────────────────────────


class TestListModelsEndpoint:
    """GET /v1/models returns model summaries."""

    def test_empty_list(self) -> None:
        """When no models exist, returns 200 with empty list."""
        reg = _mock_registry()
        reg.list_models = AsyncMock(return_value=[])  # type: ignore[misc]
        app.dependency_overrides[get_registry] = lambda: reg

        client = TestClient(app)
        response = client.get("/v1/models")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"models": []}

    def test_returns_model_summaries(self) -> None:
        """When models exist, returns 200 with ModelSummary list."""
        reg = _mock_registry()
        summary = ModelSummary(
            model_id="iris-classifier",
            name="iris-classifier",
            latest_version="1.0.0",
            framework="sklearn",
            status="production",
            created_at=datetime(2026, 6, 15, 12, 0, 0, tzinfo=UTC),
            tags=["iris"],
        )
        reg.list_models = AsyncMock(return_value=[summary])  # type: ignore[misc]
        app.dependency_overrides[get_registry] = lambda: reg

        client = TestClient(app)
        response = client.get("/v1/models")
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert len(body["models"]) == 1
        assert body["models"][0]["model_id"] == "iris-classifier"
        assert body["models"][0]["latest_version"] == "1.0.0"


# ── GET /v1/models/{model_id} ───────────────────────────────────────────


class TestGetModelEndpoint:
    """GET /v1/models/{model_id} returns metadata or 404."""

    def test_returns_metadata(self) -> None:
        """Existing model returns 200 with full ModelMetadata."""
        reg = _mock_registry()
        meta = ModelMetadata(
            model_id="iris-classifier",
            name="iris-classifier",
            version="1.0.0",
            framework="sklearn",
            description="Test model",
            status="production",
            tags=["iris"],
        )
        reg.get_model = AsyncMock(return_value=meta)  # type: ignore[misc]
        app.dependency_overrides[get_registry] = lambda: reg

        client = TestClient(app)
        response = client.get("/v1/models/iris-classifier")
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["name"] == "iris-classifier"
        assert body["version"] == "1.0.0"

    def test_unknown_returns_404(self) -> None:
        """Unknown model_id returns 404 with model_not_found error."""
        reg = _mock_registry()
        reg.get_model = AsyncMock(  # type: ignore[misc]
            side_effect=ModelNotFoundError("unknown")
        )
        app.dependency_overrides[get_registry] = lambda: reg

        client = TestClient(app)
        response = client.get("/v1/models/unknown")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        body = response.json()
        assert body["error"] == "model_not_found"


# ── POST /v1/models/register ────────────────────────────────────────────


class TestRegisterModelEndpoint:
    """POST /v1/models/register creates a model or returns 409."""

    def test_register_with_model_type_returns_201(self) -> None:
        """Registering with model_type returns 201 with model metadata."""
        reg = _mock_registry()
        meta = ModelMetadata(
            model_id="new-model",
            name="new-model",
            version="1.0.0",
            framework="sklearn",
            status="staging",
            artifact_path="models/new-model/1.0.0/model.joblib",
            tags=[],
        )
        reg.register_and_build_model = AsyncMock(return_value=meta)  # type: ignore[misc]
        app.dependency_overrides[get_registry] = lambda: reg

        client = TestClient(app)
        response = client.post(
            "/v1/models/register",
            json={
                "name": "new-model",
                "version": "1.0.0",
                "framework": "sklearn",
                "model_type": "dummy_iris",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        assert body["model"]["name"] == "new-model"
        assert body["model"]["status"] == "staging"

    def test_register_with_artifact_path_returns_201(self) -> None:
        """Registering with artifact_path returns 201."""
        reg = _mock_registry()
        meta = ModelMetadata(
            model_id="existing-model",
            name="existing-model",
            version="2.0.0",
            framework="pytorch",
            status="staging",
            artifact_path="models/existing/2.0.0/model.pt",
            tags=[],
        )
        reg.register_model = AsyncMock(return_value=meta)  # type: ignore[misc]
        app.dependency_overrides[get_registry] = lambda: reg

        client = TestClient(app)
        response = client.post(
            "/v1/models/register",
            json={
                "name": "existing-model",
                "version": "2.0.0",
                "framework": "pytorch",
                "artifact_path": "models/existing/2.0.0/model.pt",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        assert body["model"]["artifact_path"] == "models/existing/2.0.0/model.pt"

    def test_duplicate_returns_409(self) -> None:
        """Duplicate (name, version) returns 409 with duplicate_model error."""
        reg = _mock_registry()
        reg.register_and_build_model = AsyncMock(  # type: ignore[misc]
            side_effect=DuplicateModelError("dup-model", "1.0.0")
        )
        app.dependency_overrides[get_registry] = lambda: reg

        client = TestClient(app)
        response = client.post(
            "/v1/models/register",
            json={
                "name": "dup-model",
                "version": "1.0.0",
                "framework": "sklearn",
                "model_type": "dummy_iris",
            },
        )
        assert response.status_code == status.HTTP_409_CONFLICT
        body = response.json()
        assert body["error"] == "duplicate_model"

    def test_invalid_payload_returns_422(self) -> None:
        """Missing required fields returns 422."""
        # Arrange
        reg = _mock_registry()
        reg.register_and_build_model = AsyncMock()  # type: ignore[misc]
        reg.register_model = AsyncMock()  # type: ignore[misc]
        app.dependency_overrides[get_registry] = lambda: reg

        client = TestClient(app)

        # Act
        response = client.post(
            "/v1/models/register",
            json={},  # missing name, version, framework, model_type/artifact_path
        )

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        reg.register_and_build_model.assert_not_awaited()  # type: ignore[attr-defined]
        reg.register_model.assert_not_awaited()  # type: ignore[attr-defined]

    def test_mutual_exclusivity_returns_422(self) -> None:
        """Both model_type and artifact_path returns 422."""
        # Arrange
        reg = _mock_registry()
        reg.register_and_build_model = AsyncMock()  # type: ignore[misc]
        reg.register_model = AsyncMock()  # type: ignore[misc]
        app.dependency_overrides[get_registry] = lambda: reg

        client = TestClient(app)

        # Act
        response = client.post(
            "/v1/models/register",
            json={
                "name": "test",
                "version": "1.0.0",
                "framework": "sklearn",
                "model_type": "dummy_iris",
                "artifact_path": "models/test/model.joblib",
            },
        )

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        reg.register_and_build_model.assert_not_awaited()  # type: ignore[attr-defined]
        reg.register_model.assert_not_awaited()  # type: ignore[attr-defined]

    def test_missing_model_source_returns_422_without_registry_write(self) -> None:
        """A payload without model_type/artifact_path returns 422 before writes."""
        # Arrange
        reg = _mock_registry()
        reg.register_and_build_model = AsyncMock()  # type: ignore[misc]
        reg.register_model = AsyncMock()  # type: ignore[misc]
        app.dependency_overrides[get_registry] = lambda: reg

        client = TestClient(app)

        # Act
        response = client.post(
            "/v1/models/register",
            json={
                "name": "test",
                "version": "1.0.0",
                "framework": "sklearn",
            },
        )

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        reg.register_and_build_model.assert_not_awaited()  # type: ignore[attr-defined]
        reg.register_model.assert_not_awaited()  # type: ignore[attr-defined]


# ── PATCH /v1/models/{id}/status ────────────────────────────────────────


class TestUpdateStatusEndpoint:
    """PATCH /v1/models/{id}/status updates status or returns 404."""

    def test_update_status_returns_200(self) -> None:
        """Valid status update returns 200 with updated metadata."""
        reg = _mock_registry()
        meta = ModelMetadata(
            model_id="test",
            name="test",
            version="1.0.0",
            framework="sklearn",
            status="production",
            tags=[],
        )
        reg.update_status = AsyncMock(return_value=meta)  # type: ignore[misc]
        app.dependency_overrides[get_registry] = lambda: reg

        client = TestClient(app)
        response = client.patch(
            "/v1/models/550e8400-e29b-41d4-a716-446655440000/status",
            json={"status": "production"},
        )
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["status"] == "production"

    def test_unknown_uuid_returns_404(self) -> None:
        """Non-existent UUID returns 404 with model_not_found error."""
        reg = _mock_registry()
        reg.update_status = AsyncMock(  # type: ignore[misc]
            side_effect=ModelNotFoundError("550e8400-e29b-41d4-a716-446655440000")
        )
        app.dependency_overrides[get_registry] = lambda: reg

        client = TestClient(app)
        response = client.patch(
            "/v1/models/550e8400-e29b-41d4-a716-446655440000/status",
            json={"status": "production"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        body = response.json()
        assert body["error"] == "model_not_found"

    def test_invalid_status_returns_422(self) -> None:
        """Invalid status value returns 422."""
        # Arrange
        reg = _mock_registry()
        reg.update_status = AsyncMock()  # type: ignore[misc]
        app.dependency_overrides[get_registry] = lambda: reg

        client = TestClient(app)

        # Act
        response = client.patch(
            "/v1/models/550e8400-e29b-41d4-a716-446655440000/status",
            json={"status": "INVALID"},
        )

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        reg.update_status.assert_not_awaited()  # type: ignore[attr-defined]
