"""Integration test fixtures — creates model files needed by InferenceService.

The predict endpoint loads models from ``models/<model_id>.joblib``.
This conftest generates the required file so tests pass on CI where
no pre-existing model directory exists.
"""

import os
from pathlib import Path

import joblib
import pytest

from zenith_ops.core.dummy_model import DummyIrisClassifier

MODELS_DIR = Path("models")
MODEL_ID = "iris-classifier"


def _seed_model_file() -> None:
    """Create the model file if it doesn't already exist."""
    model_path = MODELS_DIR / f"{MODEL_ID}.joblib"
    if model_path.exists():
        return
    os.makedirs(MODELS_DIR, exist_ok=True)
    model = DummyIrisClassifier()
    joblib.dump(model, model_path)


@pytest.fixture(autouse=True)
def _auto_seed_models() -> None:
    """Ensure the model file exists before each integration test.

    Using function scope with a cheap guard so it works alongside
    both sync and asyncio tests without plugin conflicts.
    """
    _seed_model_file()
