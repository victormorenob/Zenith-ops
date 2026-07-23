"""Integration contract tests for prediction metadata request IDs."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from zenith_ops import app
from zenith_ops.api.v1 import predict as predict_module
from zenith_ops.services.predictor import InferenceService, ResultType


@pytest.fixture(autouse=True)
def _clear_response_cache() -> Generator[None, None, None]:
    """Keep the endpoint idempotency cache isolated from other tests."""
    predict_module._response_cache.clear()
    yield
    predict_module._response_cache.clear()


def test_predict_forwards_response_prediction_id_to_inference_service() -> None:
    """The metadata request_id should match the response prediction_id."""
    # Arrange
    fixed_prediction_id = UUID("12345678-1234-5678-1234-567812345678")
    client = TestClient(app)

    # Act
    with (
        patch.object(
            predict_module.uuid,
            "uuid4",
            return_value=fixed_prediction_id,
        ),
        patch.object(
            InferenceService,
            "predict",
            new_callable=AsyncMock,
            return_value=(0.5, ResultType.SCALAR, 3.2),
        ) as mock_predict,
    ):
        response = client.post(
            "/v1/predict",
            json={
                "model_id": "iris-classifier",
                "features": {"sepal_length": 5.1},
            },
        )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["prediction_id"] == str(fixed_prediction_id)
    mock_predict.assert_awaited_once_with(
        model_id="iris-classifier",
        features={"sepal_length": 5.1},
        idempotency_key=None,
        request_id=fixed_prediction_id,
    )
