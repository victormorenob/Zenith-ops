"""Model Registry endpoints — discover and inspect registered models.

GET /v1/models          → list all models (ModelSummary)
GET /v1/models/{model_id} → full ModelMetadata detail
"""

from fastapi import APIRouter, Depends

from zenith_ops.core.model_registry import (
    FileBasedModelRegistry,
    ModelMetadata,
    ModelRegistry,
    ModelSummary,
)

router = APIRouter()


@router.get("/v1/models")
async def list_models(
    registry: ModelRegistry = Depends(FileBasedModelRegistry.get_instance),  # noqa: B008
) -> dict[str, list[ModelSummary]]:
    """List all registered models with their latest version summary."""
    return {"models": registry.list_models()}


@router.get("/v1/models/{model_id}")
async def get_model(
    model_id: str,
    registry: ModelRegistry = Depends(FileBasedModelRegistry.get_instance),  # noqa: B008
) -> ModelMetadata:
    """Return full metadata for a specific model.

    Raises ``ModelNotFoundError`` (→ 404) if the model_id is unknown.
    """
    return registry.get_model(model_id)
