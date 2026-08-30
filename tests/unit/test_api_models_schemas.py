"""Unit tests for API schemas.

Tests cover:
  - PredictRequest / PredictResponse: prediction API validation contract
  - RegisterModelRequest: mutual exclusivity of model_type / artifact_path
  - UpdateStatusRequest: valid status regex
  - ModelResponse: contains model field
"""

from __future__ import annotations

import uuid

import pytest
from pydantic import ValidationError

from zenith_ops.api.schemas.predict import PredictRequest, PredictResponse
from zenith_ops.api.v1.schemas.models import (
    RegisterModelRequest,
    RegisterModelResponse,
    UpdateStatusRequest,
)
from zenith_ops.services.predictor import ResultType


class TestPredictRequest:
    """PredictRequest validates the prediction input contract."""

    def test_valid_numeric_features_with_idempotency_key(self) -> None:
        """Numeric feature mappings and idempotency keys are accepted."""
        # Arrange
        features = {"sepal_length": 5.1, "petal_width": 0.2}

        # Act
        req = PredictRequest(
            model_id="iris-classifier",
            features=features,
            idempotency_key="retry-123",
        )

        # Assert
        assert req.model_id == "iris-classifier"
        assert req.features == features
        assert req.idempotency_key == "retry-123"

    def test_empty_features_raise_field_validation_error(self) -> None:
        """Empty feature dictionaries fail before inference can run."""
        # Arrange
        features: dict[str, float] = {}

        # Act
        with pytest.raises(ValidationError) as exc_info:
            PredictRequest(model_id="iris-classifier", features=features)

        # Assert
        errors = exc_info.value.errors()
        assert errors[0]["loc"] == ("features",)
        assert errors[0]["type"] == "too_short"

    def test_non_numeric_feature_value_raises_validation_error(self) -> None:
        """Feature values must be parseable as floats."""
        # Arrange
        features = {"sepal_length": "not-a-number"}

        # Act
        with pytest.raises(ValidationError) as exc_info:
            PredictRequest(
                model_id="iris-classifier",
                features=features,
            )

        # Assert
        errors = exc_info.value.errors()
        assert errors[0]["loc"] == ("features", "sepal_length")
        assert errors[0]["type"] == "float_parsing"


class TestPredictResponse:
    """PredictResponse serializes the public prediction response contract."""

    def test_serializes_result_type_enum_for_json_response(self) -> None:
        """FastAPI JSON mode returns result_type as its public string value."""
        # Arrange
        prediction_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")

        # Act
        response = PredictResponse(
            prediction_id=prediction_id,
            model_id="iris-classifier",
            result=0.0,
            result_type=ResultType.SCALAR,
            latency_ms=12.5,
        )
        serialized = response.model_dump(mode="json")

        # Assert
        assert serialized == {
            "prediction_id": "550e8400-e29b-41d4-a716-446655440000",
            "model_id": "iris-classifier",
            "result": 0.0,
            "result_type": "scalar",
            "latency_ms": 12.5,
        }


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
