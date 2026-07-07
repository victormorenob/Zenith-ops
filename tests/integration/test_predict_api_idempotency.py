"""Deterministic API tests for predict endpoint idempotency caching."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from zenith_ops import app
from zenith_ops.api.v1 import predict as predict_module
from zenith_ops.core.exceptions import InferenceError
from zenith_ops.services.predictor import ResultType


@pytest.fixture(autouse=True)
def reset_predict_response_cache() -> Generator[None, None, None]:
    """Clear the endpoint idempotency cache around each test."""
    predict_module._response_cache.clear()
    yield
    predict_module._response_cache.clear()


class TestPredictEndpointIdempotency:
    """POST /v1/predict caches only successful responses by idempotency key."""

    def test_duplicate_idempotency_key_reuses_cached_response(self) -> None:
        """A duplicate retry returns the first response without rerunning inference."""
        # Arrange
        client = TestClient(app)

        # Act
        with patch.object(
            predict_module.InferenceService,
            "predict",
            new_callable=AsyncMock,
            return_value=(0.25, ResultType.SCALAR, 4.2),
        ) as mock_predict:
            first_response = client.post(
                "/v1/predict",
                json={
                    "model_id": "iris-classifier",
                    "features": {"sepal_length": 5.1},
                    "idempotency_key": "retry-123",
                },
            )
            second_response = client.post(
                "/v1/predict",
                json={
                    "model_id": "iris-classifier",
                    "features": {"sepal_length": 9.9},
                    "idempotency_key": "retry-123",
                },
            )

        # Assert
        assert first_response.status_code == status.HTTP_200_OK
        assert second_response.status_code == status.HTTP_200_OK
        assert second_response.json() == first_response.json()
        mock_predict.assert_awaited_once_with(
            model_id="iris-classifier",
            features={"sepal_length": 5.1},
            idempotency_key="retry-123",
        )

    def test_failed_keyed_prediction_is_not_cached(self) -> None:
        """A transient inference failure must not block a later retry from running."""
        # Arrange
        client = TestClient(app)

        # Act
        with patch.object(
            predict_module.InferenceService,
            "predict",
            new_callable=AsyncMock,
            side_effect=[
                InferenceError("Model failed during inference"),
                (0.75, ResultType.SCALAR, 3.1),
            ],
        ) as mock_predict:
            first_response = client.post(
                "/v1/predict",
                json={
                    "model_id": "iris-classifier",
                    "features": {"sepal_length": 5.1},
                    "idempotency_key": "retry-after-error",
                },
            )
            second_response = client.post(
                "/v1/predict",
                json={
                    "model_id": "iris-classifier",
                    "features": {"sepal_length": 5.1},
                    "idempotency_key": "retry-after-error",
                },
            )

        # Assert
        assert first_response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert first_response.json()["error"] == "inference_error"
        assert second_response.status_code == status.HTTP_200_OK
        assert second_response.json()["result"] == 0.75
        assert mock_predict.await_count == 2
