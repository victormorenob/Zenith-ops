"""Unit tests for InferenceService.

Tests cover cache behavior, error handling, timeout, latency measurement, and
best-effort prediction metadata logging.
"""

import asyncio
import json
import time
import uuid
from collections.abc import Callable, Coroutine, Generator
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
def reset_service_state() -> Generator[None, None, None]:
    """Reset class-level service state before and after each test."""
    InferenceService._models.clear()
    InferenceService._registry = None
    InferenceService._idempotency_cache.clear()
    yield
    InferenceService._models.clear()
    InferenceService._registry = None
    InferenceService._idempotency_cache.clear()


def _capture_created_tasks() -> tuple[
    list[asyncio.Task[None]],
    Callable[[Coroutine[object, object, None]], asyncio.Task[None]],
]:
    """Return a create_task replacement that records scheduled tasks."""
    original_create_task = asyncio.create_task
    created_tasks: list[asyncio.Task[None]] = []

    def capture_create_task(
        coroutine: Coroutine[object, object, None],
    ) -> asyncio.Task[None]:
        task = original_create_task(coroutine)
        created_tasks.append(task)
        return task

    return created_tasks, capture_create_task


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


class TestIdempotency:
    """Duplicate idempotency keys return the first successful prediction."""

    async def test_successful_prediction_is_cached_by_idempotency_key(self) -> None:
        """A successful keyed prediction is stored for duplicate retries."""
        # Arrange
        model = MagicMock()
        model.predict.return_value = 0.25
        created_tasks, capture_create_task = _capture_created_tasks()

        # Act
        with (
            patch.object(
                InferenceService,
                "_load_model",
                new_callable=AsyncMock,
                return_value=model,
            ) as mock_load,
            patch("asyncio.create_task", side_effect=capture_create_task),
        ):
            first_result = await InferenceService.predict(
                model_id="idempotent-model",
                features={"sepal_length": 5.1},
                idempotency_key="request-123",
            )
            await created_tasks[0]

            second_result = await InferenceService.predict(
                model_id="idempotent-model",
                features={"sepal_length": 99.0},
                idempotency_key="request-123",
            )

        # Assert
        assert first_result == second_result
        assert InferenceService._idempotency_cache["request-123"] == first_result
        mock_load.assert_awaited_once_with("idempotent-model")
        assert model.predict.call_count == 1
        assert len(created_tasks) == 1

    async def test_cached_idempotency_key_skips_model_loading_and_logging(self) -> None:
        """A duplicate retry returns immediately without side effects."""
        # Arrange
        cached_result = (0.7, ResultType.SCALAR, 12.3)
        InferenceService._idempotency_cache["retry-key"] = cached_result

        # Act
        with (
            patch.object(
                InferenceService,
                "_get_model",
                new_callable=AsyncMock,
            ) as mock_get_model,
            patch("asyncio.create_task") as mock_create_task,
        ):
            result = await InferenceService.predict(
                model_id="cached-model",
                features={"sepal_length": 5.1},
                idempotency_key="retry-key",
            )

        # Assert
        assert result == cached_result
        mock_get_model.assert_not_awaited()
        mock_create_task.assert_not_called()


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


class TestPredictionMetadataLogging:
    """Prediction metadata logging is scheduled as a best-effort side effect."""

    async def test_successful_predict_schedules_success_metadata_log(self) -> None:
        """A successful prediction logs status='success' with inference details."""
        # Arrange
        model = MagicMock()
        model.predict.return_value = 0.5
        mock_registry = MagicMock()
        mock_registry.log_prediction = AsyncMock()
        InferenceService._registry = mock_registry
        created_tasks, capture_create_task = _capture_created_tasks()

        # Act
        with (
            patch.object(
                InferenceService,
                "_load_model",
                new_callable=AsyncMock,
                return_value=model,
            ),
            patch("asyncio.create_task", side_effect=capture_create_task),
        ):
            result, result_type, latency = await InferenceService.predict(
                model_id="iris-classifier",
                features={"sepal_length": 5.1},
            )
            await created_tasks[0]

        # Assert
        assert result == 0.5
        assert result_type == ResultType.SCALAR
        assert latency > 0
        mock_registry.log_prediction.assert_awaited_once()
        log_kwargs = mock_registry.log_prediction.await_args.kwargs
        assert isinstance(log_kwargs["request_id"], uuid.UUID)
        assert log_kwargs["model_id"] == "iris-classifier"
        assert log_kwargs["features"] == {"sepal_length": 5.1}
        assert log_kwargs["result"] == 0.5
        assert log_kwargs["result_type"] == ResultType.SCALAR
        assert log_kwargs["status"] == "success"
        assert log_kwargs["error_message"] is None
        assert isinstance(log_kwargs["latency_ms"], float)

    async def test_successful_predict_uses_supplied_request_id_for_metadata_log(
        self,
    ) -> None:
        """Metadata request_id should match the caller-visible prediction id."""
        # Arrange
        request_id = uuid.UUID("12345678-1234-5678-1234-567812345678")
        model = MagicMock()
        model.predict.return_value = 0.5
        mock_registry = MagicMock()
        mock_registry.log_prediction = AsyncMock()
        InferenceService._registry = mock_registry
        created_tasks, capture_create_task = _capture_created_tasks()

        # Act
        with (
            patch.object(
                InferenceService,
                "_load_model",
                new_callable=AsyncMock,
                return_value=model,
            ),
            patch("asyncio.create_task", side_effect=capture_create_task),
        ):
            await InferenceService.predict(
                model_id="iris-classifier",
                features={"sepal_length": 5.1},
                request_id=request_id,
            )
            await created_tasks[0]

        # Assert
        mock_registry.log_prediction.assert_awaited_once()
        log_kwargs = mock_registry.log_prediction.await_args.kwargs
        assert log_kwargs["request_id"] == request_id

    async def test_inference_error_schedules_error_metadata_log(self) -> None:
        """A model failure logs status='error' before raising InferenceError."""
        # Arrange
        broken_model = MagicMock()
        broken_model.predict = MagicMock(side_effect=ValueError("bad features"))
        mock_registry = MagicMock()
        mock_registry.log_prediction = AsyncMock()
        InferenceService._registry = mock_registry
        created_tasks, capture_create_task = _capture_created_tasks()

        # Act
        with (
            patch.object(
                InferenceService,
                "_get_model",
                new_callable=AsyncMock,
                return_value=broken_model,
            ),
            patch("asyncio.create_task", side_effect=capture_create_task),
            pytest.raises(InferenceError, match="Model failed during inference"),
        ):
            await InferenceService.predict(
                model_id="iris-classifier",
                features={"sepal_length": 5.1},
            )
        await created_tasks[0]

        # Assert
        mock_registry.log_prediction.assert_awaited_once()
        log_kwargs = mock_registry.log_prediction.await_args.kwargs
        assert isinstance(log_kwargs["request_id"], uuid.UUID)
        assert log_kwargs["model_id"] == "iris-classifier"
        assert log_kwargs["features"] == {"sepal_length": 5.1}
        assert log_kwargs["result"] is None
        assert log_kwargs["result_type"] is None
        assert log_kwargs["status"] == "error"
        assert log_kwargs["error_message"] == "inference_failed"
        assert isinstance(log_kwargs["latency_ms"], float)

    async def test_safe_log_prediction_swallows_registry_errors(self) -> None:
        """A metadata DB failure must not propagate to the prediction flow."""
        # Arrange
        mock_registry = MagicMock()
        mock_registry.log_prediction = AsyncMock(side_effect=RuntimeError("db down"))
        InferenceService._registry = mock_registry

        # Act
        await InferenceService._safe_log_prediction(
            model_id="iris-classifier",
            features={"sepal_length": 5.1},
            result=0.5,
            result_type=ResultType.SCALAR,
            latency_ms=1.0,
            status="success",
            error_message=None,
        )

        # Assert
        mock_registry.log_prediction.assert_awaited_once()


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
