"""Pydantic request/response schemas for model registry API endpoints.

Schemas
-------
RegisterModelRequest
    POST /v1/models/register — validates mutual exclusion of
    ``model_type`` and ``artifact_path``.
UpdateStatusRequest
    PATCH /v1/models/{id}/status — validates the status enum.
RegisterModelResponse
    Wraps a ``ModelMetadata`` instance for the 201 response.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator

from zenith_ops.core.model_registry import ModelMetadata


class RegisterModelRequest(BaseModel):
    """Request body for ``POST /v1/models/register``.

    Either ``model_type`` (to auto-generate a model) or ``artifact_path``
    (to point to an existing file) **must** be provided — they are mutually
    exclusive.
    """

    name: str = Field(..., min_length=1, max_length=255)
    version: str = Field(..., min_length=1, max_length=50)
    framework: str = Field(..., min_length=1, max_length=50)
    description: str = ""
    model_type: str | None = None
    artifact_path: str | None = None
    metrics: dict[str, Any] | None = None
    tags: list[str] | None = None
    input_schema: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None

    @model_validator(mode="after")
    def check_exclusive(self) -> RegisterModelRequest:
        """Validate that exactly one of model_type / artifact_path is set."""
        if self.model_type and self.artifact_path:
            raise ValueError("model_type y artifact_path son mutuamente excluyentes")
        if not self.model_type and not self.artifact_path:
            raise ValueError("Debe proporcionar model_type o artifact_path")
        return self


class UpdateStatusRequest(BaseModel):
    """Request body for ``PATCH /v1/models/{id}/status``."""

    status: str = Field(
        ...,
        pattern=r"^(staging|production|archived)$",
    )


class RegisterModelResponse(BaseModel):
    """Response body for a successful model registration."""

    message: str = "Modelo registrado correctamente"
    model: ModelMetadata
