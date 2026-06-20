"""Pydantic models for the predict endpoint."""

import uuid

from pydantic import BaseModel, Field

from zenith_ops.services.predictor import ResultType


class PredictRequest(BaseModel):
    """Request body for the predict endpoint."""

    model_id: str
    features: dict[str, float] = Field(..., min_length=1)  # at least 1 feature
    idempotency_key: str | None = None  # client-generated UUID for retries


class PredictResponse(BaseModel):
    """Response body returned after successful inference."""

    prediction_id: uuid.UUID  # unique ID for this prediction
    model_id: str  # which model was used
    result: float | list[float]  # prediction (scalar, class, or probs)
    result_type: ResultType  # how to interpret `result`
    latency_ms: float  # time spent in inference
