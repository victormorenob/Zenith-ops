"""Unit tests for InferenceService.

Tests cover cache behavior, error handling, timeout, and latency measurement.
"""

import json
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import joblib
import pytest

from zenith_ops.core.dummy_model import DummyIrisClassifier
from zenith_ops.core.exceptions import (
    InferenceError,
    InferenceTimeoutError,
    ModelNotFoundError,
)
from zenith_ops.core.model_registry import FileBasedModelRegistry
from zenith_ops.services.predictor import InferenceService, ResultType


@pytest.fixture(autouse=True)
def reset_cache() -> None:
    """Reset the class-level model cache before each test."""
    InferenceService._models.clear()


class TestCacheMiss:
    """Service loads a model on first access (cache miss)."""

    async def test_cache_miss_loads_model(self) -> None:
        """First call to a model_id should load from disk then cache."""
        model = MagicMock()
        model.predict.return_value = 0.0

        with patch.object(
            InferenceService, "_load_model", new_callable=AsyncMock, return_value=model
        ) as mock_load:
            result, result_type, latency = await InferenceService.predict(
                model_id="test-model",
                features={"sepal_length": 5.1},
            )

            mock_load.assert_awaited_once_with("test-model")
            assert result == 0.0
            assert result_type == ResultType.SCALAR

    async def test_latency_is_positive(self) -> None:
        """Latency_ms should be a positive float after inference."""
        model = MagicMock()
        model.predict.return_value = 42.0

        with patch.object(
            InferenceService, "_load_model", new_callable=AsyncMock, return_value=model
        ):
            _, _, latency = await InferenceService.predict(
                model_id="test-model",
                features={"sepal_length": 5.1},
            )

            assert latency > 0


class TestCacheHit:
    """Subsequent calls to a cached model skip loading."""

    async def test_cache_hit_skips_load(self) -> None:
        """Second call to same model_id should not call _load_model again."""
        model = MagicMock()
        model.predict.return_value = 0.0

        with patch.object(
            InferenceService, "_load_model", new_callable=AsyncMock, return_value=model
        ) as mock_load:
            # First call — cache miss
            await InferenceService.predict("test-model", {"sepal_length": 5.1})
            assert mock_load.call_count == 1

            # Second call — cache hit
            result, result_type, latency = await InferenceService.predict(
                "test-model",
                {"sepal_length": 5.1},
            )

            assert mock_load.call_count == 1  # not incremented
            assert result == 0.0
            assert result_type == ResultType.SCALAR


class TestModelNotFound:
    """Requesting an unknown model_id raises ModelNotFoundError."""

    async def test_invalid_model_id_raises_error(self) -> None:
        """Unknown model_id should raise ModelNotFoundError."""
        with (
            patch.object(
                InferenceService,
                "_load_model",
                new_callable=AsyncMock,
                side_effect=ModelNotFoundError(model_id="unknown"),
            ),
            pytest.raises(ModelNotFoundError, match="No model found with id: unknown"),
        ):
            await InferenceService.predict(
                model_id="unknown",
                features={"sepal_length": 5.1},
            )


class TestTimeout:
    """Inference exceeding the timeout raises InferenceTimeoutError."""

    async def test_timeout_exceeded_raises_error(self) -> None:
        """Predict that blocks > 5s should raise InferenceTimeoutError."""
        slow_model = MagicMock()
        slow_model.predict = MagicMock(side_effect=lambda features: time.sleep(10))

        InferenceService._models["slow-model"] = slow_model

        with (
            pytest.raises(
                InferenceTimeoutError, match="Inference took longer than 5000ms"
            ),
            patch.object(
                InferenceService,
                "_get_model",
                new_callable=AsyncMock,
                return_value=slow_model,
            ),
        ):
            await InferenceService.predict(
                model_id="slow-model",
                features={"sepal_length": 5.1},
            )


class TestInferenceError:
    """Model predict failure raises InferenceError."""

    async def test_predict_failure_raises_error(self) -> None:
        """If model.predict() raises, InferenceError should be raised."""
        broken_model = MagicMock()
        broken_model.predict = MagicMock(
            side_effect=ValueError("Matrix dimension mismatch")
        )

        InferenceService._models["broken-model"] = broken_model

        with (
            pytest.raises(InferenceError, match="Model failed during inference"),
            patch.object(
                InferenceService,
                "_get_model",
                new_callable=AsyncMock,
                return_value=broken_model,
            ),
        ):
            await InferenceService.predict(
                model_id="broken-model",
                features={"sepal_length": 5.1},
            )


class TestResultType:
    """Result type mapping based on predict output."""

    async def test_float_result_is_scalar(self) -> None:
        """A float predict result should map to ResultType.SCALAR."""
        model = MagicMock()
        model.predict.return_value = 0.5

        with patch.object(
            InferenceService, "_load_model", new_callable=AsyncMock, return_value=model
        ):
            result, result_type, _ = await InferenceService.predict(
                model_id="float-model",
                features={"sepal_length": 5.1},
            )
            assert result == 0.5
            assert result_type == ResultType.SCALAR

    async def test_int_result_is_class(self) -> None:
        """An int predict result should map to ResultType.CLASS."""
        model = MagicMock()
        model.predict.return_value = 1

        with patch.object(
            InferenceService, "_load_model", new_callable=AsyncMock, return_value=model
        ):
            result, result_type, _ = await InferenceService.predict(
                model_id="int-model",
                features={"sepal_length": 5.1},
            )
            assert result == 1
            assert result_type == ResultType.CLASS

    async def test_list_result_is_array(self) -> None:
        """A list predict result should map to ResultType.ARRAY."""
        model = MagicMock()
        model.predict.return_value = [0.1, 0.2, 0.3]

        with patch.object(
            InferenceService, "_load_model", new_callable=AsyncMock, return_value=model
        ):
            result, result_type, _ = await InferenceService.predict(
                model_id="list-model",
                features={"sepal_length": 5.1},
            )
            assert result == [0.1, 0.2, 0.3]
            assert result_type == ResultType.ARRAY


class TestModelInRegistry:
    async def test_model_in_registry(self, tmp_path: Path) -> None:
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
        joblib.dump(DummyIrisClassifier(), model_dir / "model.joblib")
        registry.scan()
        InferenceService._registry = registry
        result, result_type, latency = await InferenceService.predict(
            model_id="iris-classifier",
            features={"sepal_length": 5.1},
        )
        assert result == 0.0
        assert result_type == ResultType.SCALAR
        assert latency > 0
        InferenceService._registry = None

    async def test_model_not_in_registry(self, tmp_path: Path) -> None:
        registry = FileBasedModelRegistry(Path(tmp_path / "models"))
        registry.scan()
        InferenceService._registry = registry
        with pytest.raises(ModelNotFoundError):
            await InferenceService.predict("model-not-found", {"sepal_length": 0})
        InferenceService._registry = None
