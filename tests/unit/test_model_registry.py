import json
from pathlib import Path

import pytest

from zenith_ops.core.exceptions import (
    ModelNotFoundError,
)
from zenith_ops.core.model_registry import (
    FileBasedModelRegistry,
    ModelMetadata,
    ModelSummary,
)


def test_base_model_retrieve(tmp_path: Path) -> None:
    model_dir = tmp_path / "models" / "iris-classifier" / "1.0.0"
    model_dir.mkdir(parents=True)
    Path(tmp_path / model_dir / "meta.json").write_text(
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
    model = registry.get_model("iris-classifier")
    assert model.name == "Iris Classifier"


def test_base_model_retrieve_unknown(tmp_path: Path) -> None:
    model_dir = tmp_path / "models" / "iris-classifier" / "1.0.0"
    model_dir.mkdir(parents=True)
    Path(model_dir / "meta.json").write_text("not a json")
    registry = FileBasedModelRegistry(tmp_path / "models")
    registry.scan()
    with pytest.raises(ModelNotFoundError):
        registry.get_model("unknown")


def test_list_models_return_summary(tmp_path: Path) -> None:
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
    models = registry.list_models()
    assert isinstance(models[0], ModelSummary)


def test_list_models_return_summary_wrong(tmp_path: Path) -> None:
    model_dir = tmp_path / "models" / "iris-classifier" / "1.0.0"
    model_dir.mkdir(parents=True)
    Path(model_dir / "meta.json").write_text("not a json")
    registry = FileBasedModelRegistry(Path(tmp_path / "models"))
    registry.scan()
    models = registry.list_models()
    assert models == []


def test_get_model_returns_detail(tmp_path: Path) -> None:
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
    model = registry.get_model("iris-classifier")
    assert isinstance(model, ModelMetadata)


def test_empty_dir_returns_empty(tmp_path: Path) -> None:
    model_dir = tmp_path / "models" / ""
    model_dir.mkdir(parents=True)
    registry = FileBasedModelRegistry(Path(tmp_path / "models"))
    registry.scan()
    assert registry.list_models() == []


def test_resolve_path(tmp_path: Path) -> None:
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
    path = registry.resolve_path("iris-classifier")
    assert path == (model_dir / "model.joblib").resolve()


def test_resolve_path_wrong(tmp_path: Path) -> None:
    registry = FileBasedModelRegistry(Path(tmp_path / "models"))
    registry.scan()
    with pytest.raises(ModelNotFoundError):
        registry.resolve_path("non-existent-model")
