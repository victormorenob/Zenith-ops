"""Model Registry endpoints — register, list, inspect, and manage status.

GET    /v1/models                    → list model summaries
GET    /v1/models/{model_id}         → full ModelMetadata
POST   /v1/models/register           → create new model (with .joblib)
PATCH  /v1/models/{model_id}/status  → update staging/production/archived
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from zenith_ops.api.v1.schemas.models import (
    RegisterModelRequest,
    RegisterModelResponse,
    UpdateStatusRequest,
)
from zenith_ops.core.model_registry import ModelMetadata, ModelSummary
from zenith_ops.core.model_registry_db import (
    PostgresModelRegistry,
    get_registry,
)

router = APIRouter()


@router.get("/v1/models")
async def list_models(
    registry: PostgresModelRegistry = Depends(get_registry),  # noqa: B008
) -> dict[str, list[ModelSummary]]:
    """List all registered models with their latest version summary."""
    models = await registry.list_models()
    return {"models": models}


@router.get("/v1/models/{model_id}")
async def get_model(
    model_id: str,
    registry: PostgresModelRegistry = Depends(get_registry),  # noqa: B008
) -> ModelMetadata:
    """Return full metadata for a specific model.

    Raises ``ModelNotFoundError`` (→ 404) if the model_id is unknown.
    """
    return await registry.get_model(model_id)


@router.post("/v1/models/register", status_code=201)
async def register_model(
    request: RegisterModelRequest,
    registry: PostgresModelRegistry = Depends(get_registry),  # noqa: B008
) -> RegisterModelResponse:
    """Register a new model version.  Use ``model_type`` to auto-generate
    the artifact, or ``artifact_path`` to point to an existing file.

    Returns 201 on success, 409 if the (name, version) pair already exists.
    """
    if request.model_type:
        metadata = await registry.register_and_build_model(
            name=request.name,
            version=request.version,
            framework=request.framework,
            model_type=request.model_type,
            description=request.description,
            metrics=request.metrics,
            tags=request.tags,
            input_schema=request.input_schema,
            output_schema=request.output_schema,
        )
    else:
        # artifact_path is guaranteed non-None by the schema validator
        assert request.artifact_path is not None
        metadata = await registry.register_model(
            name=request.name,
            version=request.version,
            framework=request.framework,
            artifact_path=request.artifact_path,
            description=request.description,
            metrics=request.metrics,
            tags=request.tags,
            input_schema=request.input_schema,
            output_schema=request.output_schema,
        )

    return RegisterModelResponse(model=metadata)


@router.patch("/v1/models/{model_id}/status")
async def update_model_status(
    model_id: str,
    request: UpdateStatusRequest,
    registry: PostgresModelRegistry = Depends(get_registry),  # noqa: B008
) -> ModelMetadata:
    """Update the status of a model version identified by its UUID.

    Valid status values: ``staging``, ``production``, ``archived``.
    Raises ``ModelNotFoundError`` (→ 404) if the UUID is unknown.
    """
    return await registry.update_status(model_id, request.status)
