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


async def test_scan_skips_files_and_versions_without_metadata(tmp_path: Path) -> None:
    """Partial model artifacts must not prevent valid versions from loading."""
    # Arrange
    models_dir = tmp_path / "models"
    models_dir.mkdir()
    (models_dir / "README.txt").write_text("not a model directory")

    model_root = models_dir / "iris-classifier"
    valid_version_dir = model_root / "1.0.0"
    incomplete_version_dir = model_root / "2.0.0"
    valid_version_dir.mkdir(parents=True)
    incomplete_version_dir.mkdir(parents=True)
    Path(valid_version_dir / "meta.json").write_text(
        json.dumps(
            {
                "model_id": "iris-classifier",
                "name": "Iris Classifier",
                "version": "1.0.0",
                "framework": "sklearn",
                "status": "active",
                "created_at": "2026-06-15T12:00:00Z",
                "tags": ["iris"],
            }
        )
    )

    registry = FileBasedModelRegistry(models_dir)

    # Act
    registry.scan()
    models = await registry.list_models()
    model = await registry.get_model("iris-classifier")

    # Assert
    assert [summary.model_id for summary in models] == ["iris-classifier"]
    assert models[0].latest_version == "1.0.0"
    assert model.version == "1.0.0"


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


def test_compare_two_index_semver(tmp_path: Path) -> None:
    assert _parse_semver("1.9.0") < _parse_semver("1.10.0")
