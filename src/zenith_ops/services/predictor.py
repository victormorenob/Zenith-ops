"""Inference service — lazy-loaded model cache and async predict."""

import asyncio
import logging
import time
import uuid
from enum import StrEnum
from typing import Any

import joblib

from zenith_ops.core.exceptions import (
    InferenceError,
    InferenceTimeoutError,
    ModelNotFoundError,
)
from zenith_ops.core.model_registry import ModelRegistry

logger = logging.getLogger(__name__)


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

    # Registry singleton — class-level so tests can inject a mock or
    # Protocol alternative from Phase 2 (e.g. MLflowModelRegistry).
    _registry: ModelRegistry | None = None

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
        model = await cls._get_model(model_id)

        # 3. RUN INFERENCE IN THREAD POOL — don't block the event loop
        result: float | list[float] | None = None
        result_type: ResultType | None = None
        error_message: str | None = None
        prediction_status = "success"

        loop = asyncio.get_event_loop()
        try:
            future = loop.run_in_executor(None, model.predict, features)
            # wait_for enforces the 5s timeout on the Future
            result = await asyncio.wait_for(future, timeout=INFERENCE_TIMEOUT_S)
        except TimeoutError:
            # TimeoutError from wait_for -> our domain exception (-> 503)
            prediction_status = "error"
            error_message = "timeout"
            raise InferenceTimeoutError(int(INFERENCE_TIMEOUT_S * 1000)) from None
        except Exception:
            # Any other exception (OOM, corrupt model, etc.) -> 500
            prediction_status = "error"
            error_message = "inference_failed"
            raise InferenceError("Model failed during inference") from None
        finally:
            latency_ms = (time.monotonic() - t0) * 1000
            if prediction_status == "success":
                assert result is not None  # success path always sets result
                result_type = cls._get_result_type(result)
            # Fire-and-forget: log prediction metadata (never interrupts response)
            asyncio.create_task(
                cls._safe_log_prediction(
                    model_id=model_id,
                    features=features,
                    result=result,
                    result_type=result_type,
                    latency_ms=latency_ms,
                    status=prediction_status,
                    error_message=error_message,
                )
            )

        # 4. Store in idempotency cache for potential retries
        # NOTE: error paths always raise, so result/result_type are never None here
        assert result is not None
        assert result_type is not None
        if idempotency_key:
            cls._idempotency_cache[idempotency_key] = (
                result,
                result_type,
                latency_ms,
            )

        return result, result_type, latency_ms

    @classmethod
    async def _get_model(cls, model_id: str) -> Any:
        """Return cached model or load from disk (lazy initialization)."""
        if model_id not in cls._models:
            cls._models[model_id] = await cls._load_model(model_id)
        return cls._models[model_id]

    @classmethod
    async def _load_model(cls, model_id: str) -> Any:
        """Resolve the model path via the registry and load from disk."""
        if cls._registry is None:
            from zenith_ops.core.model_registry_db import get_registry

            cls._registry = await get_registry()
        model_path = await cls._registry.resolve_path(model_id)
        try:
            return joblib.load(model_path)
        except FileNotFoundError:
            raise ModelNotFoundError(model_id) from None
        except Exception:
            raise InferenceError("Model failed during inference") from None

    @classmethod
    async def _safe_log_prediction(cls, **kwargs: Any) -> None:
        """Best-effort prediction logging — never propagates errors.

        Called as a fire-and-forget task from :meth:`predict`.  If the
        registry doesn't support logging (e.g. ``FileBasedModelRegistry``
        or a mock), the call is silently skipped.
        """
        if cls._registry is None or not hasattr(cls._registry, "log_prediction"):
            return
        try:
            await cls._registry.log_prediction(
                request_id=uuid.uuid4(),
                model_id=kwargs["model_id"],
                features=kwargs["features"],
                result=kwargs["result"],
                result_type=kwargs["result_type"],
                latency_ms=kwargs["latency_ms"],
                status=kwargs["status"],
                error_message=kwargs.get("error_message"),
            )
        except Exception:
            logger.exception("Prediction logging failed (best-effort, ignoring)")

    @staticmethod
    def _get_result_type(result: float | list[float]) -> ResultType:
        """Map the result value to the appropriate result type."""
        if isinstance(result, float):
            return ResultType.SCALAR
        if isinstance(result, int):
            return ResultType.CLASS
        return ResultType.ARRAY
