import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from zenith_ops.core.exceptions import (
    ModelNotFoundError,
)
from zenith_ops.core.model_registry import (
    FileBasedModelRegistry,
    ModelMetadata,
    ModelSummary,
    _parse_semver,
)


def _write_model_metadata(
    model_dir: Path,
    *,
    model_id: str = "iris-classifier",
    name: str = "Iris Classifier",
    version: str = "1.0.0",
    framework: str = "sklearn",
    status: str = "active",
) -> None:
    """Write a valid file-registry ``meta.json`` for a model version."""
    model_dir.mkdir(parents=True)
    (model_dir / "meta.json").write_text(
        json.dumps(
            {
                "model_id": model_id,
                "name": name,
                "version": version,
                "framework": framework,
                "status": status,
                "created_at": "2026-06-15T12:00:00Z",
                "tags": ["iris"],
            }
        )
    )


async def test_base_model_retrieve(tmp_path: Path) -> None:
    model_dir = tmp_path / "models" / "iris-classifier" / "1.0.0"
    model_dir.mkdir(parents=True)
    Path(model_dir / "meta.json").write_text(
        json.dumps(
            {
                "model_id": "iris-classifier",
                "name": "Iris Classifier",
                "version": "1.0.0",
                "framework": "skitlearn",
                "status": "active",
                "created_at": "2026-06-15T12:00:00Z",
                "tags": ["iris"],
            }
        )
    )
    registry = FileBasedModelRegistry(Path(tmp_path / "models"))
    registry.scan()
    model = await registry.get_model("iris-classifier")
    assert model.name == "Iris Classifier"


async def test_base_model_retrieve_unknown(tmp_path: Path) -> None:
    model_dir = tmp_path / "models" / "iris-classifier" / "1.0.0"
    model_dir.mkdir(parents=True)
    Path(model_dir / "meta.json").write_text("not a json")
    registry = FileBasedModelRegistry(tmp_path / "models")
    registry.scan()
    with pytest.raises(ModelNotFoundError):
        await registry.get_model("unknown")


async def test_base_model_retrieve_corrupt(tmp_path: Path) -> None:
    model_dir = tmp_path / "models" / "iris-classifier" / "1.0.0"
    model_dir.mkdir(parents=True)
    Path(model_dir / "meta.json").write_text(
        json.dumps(
            {
                "model_id": "iris-classifier",
                "name": "Iris Classifier",
                "version": "1.0.0",
                "status": "active",
                "created_at": "2026-06-15T12:00:00Z",
                "tags": ["iris"],
            }
        )
    )
    registry = FileBasedModelRegistry(Path(tmp_path / "models"))
    registry.scan()
    with pytest.raises(ModelNotFoundError):
        await registry.get_model("iris-classifier")


async def test_list_models_return_summary(tmp_path: Path) -> None:
    model_dir = tmp_path / "models" / "iris-classifier" / "1.0.0"
    model_dir.mkdir(parents=True)
    Path(model_dir / "meta.json").write_text(
        json.dumps(
            {
                "model_id": "iris-classifier",
                "name": "Iris Classifier",
                "version": "1.0.0",
                "framework": "skitlearn",
                "status": "active",
                "created_at": "2026-06-15T12:00:00Z",
                "tags": ["iris"],
            }
        )
    )
    registry = FileBasedModelRegistry(Path(tmp_path / "models"))
    registry.scan()
    models = await registry.list_models()
    assert isinstance(models[0], ModelSummary)


async def test_list_models_return_summary_wrong(tmp_path: Path) -> None:
    model_dir = tmp_path / "models" / "iris-classifier" / "1.0.0"
    model_dir.mkdir(parents=True)
    Path(model_dir / "meta.json").write_text("not a json")
    registry = FileBasedModelRegistry(Path(tmp_path / "models"))
    registry.scan()
    models = await registry.list_models()
    assert models == []


async def test_get_model_returns_detail(tmp_path: Path) -> None:
    model_dir = tmp_path / "models" / "iris-classifier" / "1.0.0"
    model_dir.mkdir(parents=True)
    Path(model_dir / "meta.json").write_text(
        json.dumps(
            {
                "model_id": "iris-classifier",
                "name": "Iris Classifier",
                "version": "1.0.0",
                "framework": "skitlearn",
                "status": "active",
                "created_at": "2026-06-15T12:00:00Z",
                "tags": ["iris"],
            }
        )
    )
    registry = FileBasedModelRegistry(Path(tmp_path / "models"))
    registry.scan()
    model = await registry.get_model("iris-classifier")
    assert isinstance(model, ModelMetadata)


async def test_empty_dir_returns_empty(tmp_path: Path) -> None:
    model_dir = tmp_path / "models" / ""
    model_dir.mkdir(parents=True)
    registry = FileBasedModelRegistry(Path(tmp_path / "models"))
    registry.scan()
    models = await registry.list_models()
    assert models == []


async def test_resolve_path(tmp_path: Path) -> None:
    model_dir = tmp_path / "models" / "iris-classifier" / "1.0.0"
    model_dir.mkdir(parents=True)
    Path(model_dir / "meta.json").write_text(
        json.dumps(
            {
                "model_id": "iris-classifier",
                "name": "Iris Classifier",
                "version": "1.0.0",
                "framework": "skitlearn",
                "status": "active",
                "created_at": "2026-06-15T12:00:00Z",
                "tags": ["iris"],
            }
        )
    )
    registry = FileBasedModelRegistry(Path(tmp_path / "models"))
    registry.scan()
    path = await registry.resolve_path("iris-classifier")
    assert path == (model_dir / "model.joblib").resolve()


async def test_not_real_path(tmp_path: Path) -> None:
    model_dir = tmp_path / "models" / "iris-classifier" / "1.0.0"
    model_dir.mkdir(parents=True)
    Path(model_dir / "meta.json").write_text(
        json.dumps(
            {
                "model_id": "iris-classifier",
                "name": "Iris Classifier",
                "version": "1.0.0",
                "framework": "skitlearn",
                "status": "active",
                "created_at": "2026-06-15T12:00:00Z",
                "tags": ["iris"],
            }
        )
    )
    registry = FileBasedModelRegistry(Path(tmp_path / "models"))
    registry.scan()
    path = await registry.resolve_path("iris-classifier")
    assert not path.exists()


async def test_resolve_path_wrong(tmp_path: Path) -> None:
    registry = FileBasedModelRegistry(Path(tmp_path / "models"))
    registry.scan()
    with pytest.raises(ModelNotFoundError):
        await registry.resolve_path("non-existent-model")


def test_latest_active(tmp_path: Path) -> None:
    registry = FileBasedModelRegistry(Path(tmp_path / "models"))
    registry.scan()
    latest_active = registry._latest_active(
        {
            "1.0.0": ModelMetadata(
                model_id="iris-classifier",
                name="Iris Classifier",
                version="1.0.0",
                framework="sklearn",
                status="active",
                created_at=datetime(2026, 6, 15, 12, 0, 0, tzinfo=UTC),
                tags=["iris"],
            ),
            "2.0.0": ModelMetadata(
                model_id="iris-classifier",
                name="Iris Classifier",
                version="2.0.0",
                framework="sklearn",
                status="active",
                created_at=datetime(2026, 6, 15, 12, 0, 0, tzinfo=UTC),
                tags=["iris"],
            ),
        }
    )
    assert latest_active == ModelMetadata(
        model_id="iris-classifier",
        name="Iris Classifier",
        version="2.0.0",
        framework="sklearn",
        status="active",
        created_at=datetime(2026, 6, 15, 12, 0, 0, tzinfo=UTC),
        tags=["iris"],
    )


def test_active_vs_notactive(tmp_path: Path) -> None:
    registry = FileBasedModelRegistry(Path(tmp_path / "models"))
    registry.scan()
    latest_active = registry._latest_active(
        {
            "1.0.0": ModelMetadata(
                model_id="iris-classifier",
                name="Iris Classifier",
                version="1.0.0",
                framework="sklearn",
                status="active",
                created_at=datetime(2026, 6, 15, 12, 0, 0, tzinfo=UTC),
                tags=["iris"],
            ),
            "2.0.0": ModelMetadata(
                model_id="iris-classifier",
                name="Iris Classifier",
                version="2.0.0",
                framework="sklearn",
                status="staging",
                created_at=datetime(2026, 6, 15, 12, 0, 0, tzinfo=UTC),
                tags=["iris"],
            ),
        }
    )
    assert latest_active == ModelMetadata(
        model_id="iris-classifier",
        name="Iris Classifier",
        version="1.0.0",
        framework="sklearn",
        status="active",
        created_at=datetime(2026, 6, 15, 12, 0, 0, tzinfo=UTC),
        tags=["iris"],
    )


def test_notactive_models(tmp_path: Path) -> None:
    registry = FileBasedModelRegistry(Path(tmp_path / "models"))
    registry.scan()
    latest_active = registry._latest_active(
        {
            "1.0.0": ModelMetadata(
                model_id="iris-classifier",
                name="Iris Classifier",
                version="1.0.0",
                framework="sklearn",
                status="archived",
                created_at=datetime(2026, 6, 15, 12, 0, 0, tzinfo=UTC),
                tags=["iris"],
            ),
            "2.0.0": ModelMetadata(
                model_id="iris-classifier",
                name="Iris Classifier",
                version="2.0.0",
                framework="sklearn",
                status="archived",
                created_at=datetime(2026, 6, 15, 12, 0, 0, tzinfo=UTC),
                tags=["iris"],
            ),
        }
    )
    assert latest_active is None


async def test_list_models_skips_model_when_no_active_versions(tmp_path: Path) -> None:
    """Models with only staging/archived versions must not be listed."""
    # Arrange
    _write_model_metadata(
        tmp_path / "models" / "iris-classifier" / "2.0.0",
        version="2.0.0",
        status="staging",
    )
    _write_model_metadata(
        tmp_path / "models" / "iris-classifier" / "1.0.0",
        version="1.0.0",
        status="archived",
    )
    registry = FileBasedModelRegistry(tmp_path / "models")
    registry.scan()

    # Act
    models = await registry.list_models()

    # Assert
    assert models == []


async def test_get_model_raises_when_model_has_no_active_versions(
    tmp_path: Path,
) -> None:
    """A known model name with no active versions is not serveable."""
    # Arrange
    _write_model_metadata(
        tmp_path / "models" / "iris-classifier" / "1.0.0",
        status="archived",
    )
    registry = FileBasedModelRegistry(tmp_path / "models")
    registry.scan()

    # Act / Assert
    with pytest.raises(ModelNotFoundError, match="iris-classifier"):
        await registry.get_model("iris-classifier")


def test_compare_two_index_semver(tmp_path: Path) -> None:
    assert _parse_semver("1.9.0") < _parse_semver("1.10.0")


def test_parse_semver_treats_non_numeric_segments_as_zero() -> None:
    """Non-numeric version segments should not crash registry sorting."""
    # Arrange / Act
    parsed_version = _parse_semver("1.beta.2")

    # Assert
    assert parsed_version == (1, 0, 2)
    assert _parse_semver("1.beta.2") < _parse_semver("1.1.0")
