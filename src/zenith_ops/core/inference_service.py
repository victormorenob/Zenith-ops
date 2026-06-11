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
    """Result shape for the API response."""

    SCALAR = "scalar"  # single float (regression)
    CLASS = "class"  # integer index (argmax)
    ARRAY = "array"  # list of floats (probability vector)


# Hard timeout — if inference exceeds this, we abort and return 503.
INFERENCE_TIMEOUT_S = 5.0


class InferenceService:
    """Lazy-loads models on first access and runs inference with timeout."""

    # Model cache: model_id -> loaded joblib object.
    # Class attribute = shared across ALL instances and requests.
    _models: dict[str, Any] = {}

    # Idempotency cache: key -> (result, result_type, latency_ms).
    # In-memory, no TTL in v0.1. For production, use Redis with TTL.
    _idempotency_cache: dict[str, tuple[float | list[float], ResultType, float]] = {}

    @classmethod
    async def predict(
        cls,
        model_id: str,
        features: dict[str, float],
        idempotency_key: str | None = None,
    ) -> tuple[float | list[float], ResultType, float]:
        # 1. IDEMPOTENCY CHECK — return cached response if duplicate key
        if idempotency_key and idempotency_key in cls._idempotency_cache:
            return cls._idempotency_cache[idempotency_key]

        t0 = time.monotonic()  # monotonic() never jumps backwards (NTP-safe)

        # 2. GET MODEL — load from disk on first access, then cache
        model = cls._get_model(model_id)

        # 3. RUN INFERENCE IN THREAD POOL — don't block the event loop
        # run_in_executor submits sync function to ThreadPoolExecutor
        loop = asyncio.get_event_loop()
        try:
            future = loop.run_in_executor(None, model.predict, features)
            # wait_for enforces the 5s timeout on the Future
            result = await asyncio.wait_for(future, timeout=INFERENCE_TIMEOUT_S)
        except TimeoutError:
            # TimeoutError from wait_for -> our domain exception (-> 503)
            raise InferenceTimeoutError(int(INFERENCE_TIMEOUT_S * 1000)) from None
        except Exception:
            # Any other exception (OOM, corrupt model, etc.) -> 500
            raise InferenceError("Model failed during inference") from None

        # 4. METRICS & CACHE
        latency_ms = (time.monotonic() - t0) * 1000
        result_type = cls._get_result_type(result)

        # Store in idempotency cache for potential retries
        if idempotency_key:
            cls._idempotency_cache[idempotency_key] = (
                result,
                result_type,
                latency_ms,
            )

        return result, result_type, latency_ms

    @classmethod
    def _get_model(cls, model_id: str) -> Any:
        """Return cached model or load from disk (lazy initialization)."""
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
