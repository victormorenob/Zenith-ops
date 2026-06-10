"""POST /v1/predict — run ML inference against a registered model."""

import uuid

from fastapi import APIRouter
from pydantic import BaseModel, Field

from zenith_ops.core.inference_service import InferenceService, ResultType

router = APIRouter()


class PredictRequest(BaseModel):
    """Request body for the predict endpoint."""

    model_id: str
    features: dict[str, float] = Field(..., min_length=1)
    idempotency_key: str | None = None


class PredictResponse(BaseModel):
    """Response body returned after successful inference."""

    prediction_id: uuid.UUID
    model_id: str
    result: float | list[float]
    result_type: ResultType
    latency_ms: float


@router.post("/v1/predict", status_code=200)
async def predict(request: PredictRequest) -> PredictResponse:
    """Run inference and return prediction results with latency."""
    prediction_id = uuid.uuid4()

    result, result_type, latency_ms = await InferenceService.predict(
        model_id=request.model_id,
        features=request.features,
    )

    return PredictResponse(
        prediction_id=prediction_id,
        model_id=request.model_id,
        result=result,
        result_type=result_type,
        latency_ms=latency_ms,
    )
