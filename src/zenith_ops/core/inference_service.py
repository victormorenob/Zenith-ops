"""Inference service — lazy-loaded model cache and async predict."""

import asyncio
import time
from enum import StrEnum
from typing import Any

import joblib

from zenith_ops.core.exceptions import (
    InferenceError,
    InferenceTimeoutError,
    ModelNotFoundError,
)


class ResultType(StrEnum):
    """Categorizes the inference result shape."""

    SCALAR = "scalar"
    CLASS = "class"
    ARRAY = "array"


INFERENCE_TIMEOUT_S = 5.0


class InferenceService:
    """Lazy-loads models on first access and runs inference with timeout.

    Class-level cache ensures models survive across requests.
    """

    _models: dict[str, Any] = {}

    @classmethod
    async def predict(
        cls,
        model_id: str,
        features: dict[str, float],
    ) -> tuple[float | list[float], ResultType, float]:
        """Run inference for *model_id* with *features*.

        Returns:
            Tuple of (result, result_type, latency_ms).
        """
        t0 = time.monotonic()

        model = cls._get_model(model_id)

        loop = asyncio.get_event_loop()
        try:
            future = loop.run_in_executor(None, model.predict, features)
            result = await asyncio.wait_for(future, timeout=INFERENCE_TIMEOUT_S)
        except TimeoutError:
            raise InferenceTimeoutError(int(INFERENCE_TIMEOUT_S * 1000)) from None
        except Exception:
            raise InferenceError("Model failed during inference") from None

        latency_ms = (time.monotonic() - t0) * 1000
        result_type = cls._get_result_type(result)

        return result, result_type, latency_ms

    @classmethod
    def _get_model(cls, model_id: str) -> Any:
        """Return cached model or load from disk."""
        if model_id not in cls._models:
            cls._models[model_id] = cls._load_model(model_id)
        return cls._models[model_id]

    @classmethod
    def _load_model(cls, model_id: str) -> Any:
        """Load model from disk using joblib."""
        try:
            return joblib.load(f"models/{model_id}.joblib")
        except FileNotFoundError:
            raise ModelNotFoundError(model_id) from None
        except Exception:
            raise InferenceError("Model failed during inference") from None

    @staticmethod
    def _get_result_type(result: float | list[float]) -> ResultType:
        """Map the result value to the appropriate result type."""
        if isinstance(result, float):
            return ResultType.SCALAR
        if isinstance(result, int):
            return ResultType.CLASS
        return ResultType.ARRAY
