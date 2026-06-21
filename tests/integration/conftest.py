"""Integration test fixtures — creates model files needed by InferenceService
and the Model Registry.

Two model layouts are seeded:
  - ``models/<model_id>.joblib``              → legacy flat path (InferenceService)
  - ``models/<model_id>/<version>/meta.json``  → versioned registry path
  - ``models/<model_id>/<version>/model.joblib``
"""

import json
import os
from datetime import UTC, datetime
from pathlib import Path

import joblib
import pytest

from zenith_ops.core.dummy_model import DummyIrisClassifier

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
