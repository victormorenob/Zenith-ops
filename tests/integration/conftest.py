"""Integration test fixtures — creates model files needed by InferenceService
and the Model Registry.

Two model layouts are seeded:
  - ``models/<model_id>.joblib``              → legacy flat path (InferenceService)
  - ``models/<model_id>/<version>/meta.json``  → versioned registry path
  - ``models/<model_id>/<version>/model.joblib``
"""

import json
import os
from collections.abc import Generator
from datetime import UTC, datetime
from pathlib import Path

import joblib
import pytest

from zenith_ops.core.dummy_model import DummyIrisClassifier
from zenith_ops.core.exceptions import ModelNotFoundError
from zenith_ops.core.model_registry import ModelMetadata, ModelSummary

MODELS_DIR = Path("models")
MODEL_ID = "iris-classifier"
MODEL_VERSION = "1.0.0"


def _seed_model_file() -> None:
    """Create the flat model file for the legacy InferenceService path."""
    model_path = MODELS_DIR / f"{MODEL_ID}.joblib"
    if model_path.exists():
        return
    os.makedirs(MODELS_DIR, exist_ok=True)
    model = DummyIrisClassifier()
    joblib.dump(model, model_path)


def _seed_registry_structure() -> None:
    """Create the versioned model directory for the Model Registry.

    ``FileBasedModelRegistry.scan()`` expects:
      ``models/<model_id>/<version>/meta.json``
      ``models/<model_id>/<version>/model.joblib``

    We guard on ``model.joblib`` (not ``meta.json``) because
    ``meta.json`` is committed to git while ``*.joblib`` files are
    gitignored.  In a fresh CI checkout ``meta.json`` exists but
    ``model.joblib`` does not.
    """
    version_dir = MODELS_DIR / MODEL_ID / MODEL_VERSION
    if (version_dir / "model.joblib").exists():
        return
    os.makedirs(version_dir, exist_ok=True)

    (version_dir / "meta.json").write_text(
        json.dumps(
            {
                "model_id": MODEL_ID,
                "name": "Iris Classifier",
                "version": MODEL_VERSION,
                "framework": "sklearn",
                "status": "active",
                "created_at": datetime(2026, 6, 15, 12, 0, 0, tzinfo=UTC).isoformat(),
                "tags": ["classification", "iris", "multiclass"],
            }
        )
    )

    model = DummyIrisClassifier()
    joblib.dump(model, version_dir / "model.joblib")


@pytest.fixture(autouse=True)
def _auto_seed_models() -> None:
    """Ensure all model files exist before each integration test.

    Using function scope with a cheap guard so it works alongside
    both sync and asyncio tests without plugin conflicts.
    """
    _seed_model_file()
    _seed_registry_structure()


# ──────────────────────────────────────────────────────────────────────
# In-memory mock for the ModelRegistry protocol
# ──────────────────────────────────────────────────────────────────────


class MockModelRegistry:
    """In-memory mock of ``ModelRegistry`` — no PostgreSQL, no event-loop
    conflicts.

    Returns hardcoded metadata for ``iris-classifier`` and raises
    ``ModelNotFoundError`` for any unknown ``model_id``.

    ``resolve_path`` points to the real seeded ``.joblib`` file so
    ``InferenceService`` can load the model and run predictions.
    """

    def __init__(self) -> None:
        self._models: dict[str, ModelMetadata] = {
            "iris-classifier": ModelMetadata(
                model_id="iris-classifier",
                name="Iris Classifier",
                version="1.0.0",
                framework="sklearn",
                status="active",
                created_at=datetime(2026, 6, 15, 12, 0, 0, tzinfo=UTC),
                artifact_path=str(
                    (
                        MODELS_DIR / "iris-classifier" / "1.0.0" / "model.joblib"
                    ).resolve()
                ),
                tags=["classification", "iris", "multiclass"],
            ),
        }

    async def list_models(self) -> list[ModelSummary]:
        return [
            ModelSummary(
                model_id=m.model_id,
                name=m.name,
                latest_version=m.version,
                framework=m.framework,
                status=m.status,
                created_at=m.created_at,
                tags=m.tags,
            )
            for m in self._models.values()
        ]

    async def get_model(self, model_id: str) -> ModelMetadata:
        model = self._models.get(model_id)
        if model is None:
            raise ModelNotFoundError(model_id)
        return model

    async def resolve_path(self, model_id: str) -> Path:
        model = self._models.get(model_id)
        if model is None:
            raise ModelNotFoundError(model_id)
        return Path(model.artifact_path).resolve()

    async def log_prediction(self, **kwargs: object) -> None:
        """Best-effort no-op — never raises."""
        return


@pytest.fixture(autouse=True)
def _mock_db_registry() -> Generator[None, None, None]:
    """Replace the PostgreSQL-backed registry with an in-memory mock.

    Overrides both FastAPI's ``Depends(get_registry)`` and
    ``InferenceService._registry`` so no code path reaches ``asyncpg``
    during integration tests.

    Cleans up class-level caches after each test to prevent state
    leaking between tests.
    """
    from zenith_ops import app as _app
    from zenith_ops.core.model_registry_db import get_registry
    from zenith_ops.services.predictor import InferenceService

    mock = MockModelRegistry()

    # Wire into FastAPI DI for routes that depend on get_registry
    async def _override_get_registry() -> MockModelRegistry:
        return mock

    _app.dependency_overrides[get_registry] = _override_get_registry

    # Wire into InferenceService — bypasses DI for class-level _registry
    InferenceService._registry = mock

    yield

    # ── Teardown: reset all class-level state ─────────────────────────
    InferenceService._registry = None
    InferenceService._models.clear()
    InferenceService._idempotency_cache.clear()
    _app.dependency_overrides.clear()
