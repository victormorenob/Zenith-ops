"""Unit tests for API schemas (Phase C — API Wiring).

Tests cover:
  - RegisterModelRequest: mutual exclusivity of model_type / artifact_path
  - UpdateStatusRequest: valid status regex
  - ModelResponse: contains model field
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from zenith_ops.api.v1.schemas.models import (
    RegisterModelRequest,
    RegisterModelResponse,
    UpdateStatusRequest,
)


class TestRegisterModelRequest:
    """RegisterModelRequest validates register payloads."""

    def test_valid_with_model_type(self) -> None:
        """A request with model_type (and no artifact_path) is valid."""
        req = RegisterModelRequest(
            name="test-model",
            version="1.0.0",
            framework="sklearn",
            model_type="dummy_iris",
        )
        assert req.name == "test-model"
        assert req.version == "1.0.0"
        assert req.framework == "sklearn"
        assert req.model_type == "dummy_iris"
        assert req.artifact_path is None

    def test_valid_with_artifact_path(self) -> None:
        """A request with artifact_path (and no model_type) is valid."""
        req = RegisterModelRequest(
            name="test-model",
            version="1.0.0",
            framework="sklearn",
            artifact_path="models/foo/1.0.0/model.joblib",
        )
        assert req.artifact_path == "models/foo/1.0.0/model.joblib"
        assert req.model_type is None

    def test_mutual_exclusivity_raises_error(self) -> None:
        """Both model_type and artifact_path together must raise."""
        with pytest.raises(ValidationError, match="mutuamente excluyentes"):
            RegisterModelRequest(
                name="test-model",
                version="1.0.0",
                framework="sklearn",
                model_type="dummy_iris",
                artifact_path="models/foo/1.0.0/model.joblib",
            )

    def test_neither_raises_error(self) -> None:
        """Neither model_type nor artifact_path must raise."""
        with pytest.raises(ValidationError, match="Debe proporcionar"):
            RegisterModelRequest(
                name="test-model",
                version="1.0.0",
                framework="sklearn",
            )

    def test_optional_fields_default_correctly(self) -> None:
        """description defaults to '', metrics/tags/schemas default to None."""
        req = RegisterModelRequest(
            name="m",
            version="1",
            framework="f",
            model_type="dummy_iris",
        )
        assert req.description == ""
        assert req.metrics is None
        assert req.tags is None
        assert req.input_schema is None
        assert req.output_schema is None

    def test_name_min_length_enforced(self) -> None:
        """Empty name must raise."""
        with pytest.raises(ValidationError):
            RegisterModelRequest(
                name="",
                version="1.0.0",
                framework="sklearn",
                model_type="dummy_iris",
            )

    def test_string_fields_max_length(self) -> None:
        """Very long strings for name/version/framework must raise."""
        long_str = "x" * 500
        with pytest.raises(ValidationError):
            RegisterModelRequest(
                name=long_str,
                version="1.0.0",
                framework="sklearn",
                model_type="dummy_iris",
            )


class TestUpdateStatusRequest:
    """UpdateStatusRequest validates PATCH status payloads."""

    def test_valid_statuses(self) -> None:
        """staging, production, archived are valid."""
        for status in ("staging", "production", "archived"):
            req = UpdateStatusRequest(status=status)
            assert req.status == status

    def test_invalid_status_raises(self) -> None:
        """Any value outside the allowed set must raise."""
        with pytest.raises(ValidationError):
            UpdateStatusRequest(status="invalid")

    def test_empty_status_raises(self) -> None:
        """Empty string must raise."""
        with pytest.raises(ValidationError):
            UpdateStatusRequest(status="")


class TestRegisterModelResponse:
    """RegisterModelResponse contains a 'model' field."""

    def test_has_model_field(self) -> None:
        """The response must contain a 'model' key in serialized form."""
        from zenith_ops.core.model_registry import ModelMetadata

        meta = ModelMetadata(
            model_id="test",
            name="test",
            version="1.0.0",
            framework="sklearn",
        )
        resp = RegisterModelResponse(model=meta)
        data = resp.model_dump()
        assert "model" in data
        assert data["model"]["name"] == "test"
        assert data["model"]["version"] == "1.0.0"
