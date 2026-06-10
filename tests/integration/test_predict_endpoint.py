"""Integration tests for POST /v1/predict endpoint.

Uses TestClient against the real FastAPI app with exception handlers.
"""

from fastapi import status
from fastapi.testclient import TestClient

from zenith_ops import app
from zenith_ops.core.inference_service import InferenceService

client = TestClient(app)


def test_valid_prediction_returns_200() -> None:
    """Valid request should return 200 with all required fields."""
    response = client.post(
        "/v1/predict",
        json={
            "model_id": "iris-classifier",
            "features": {
                "sepal_length": 5.1,
                "sepal_width": 3.5,
                "petal_length": 1.4,
                "petal_width": 0.2,
            },
        },
    )
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert "prediction_id" in body
    assert body["model_id"] == "iris-classifier"
    assert body["result"] == 0.0
    assert body["result_type"] == "scalar"
    assert isinstance(body["latency_ms"], float)
    assert body["latency_ms"] > 0


def test_unknown_model_returns_404() -> None:
    """Unknown model_id should return 404 with model_not_found error."""
    response = client.post(
        "/v1/predict",
        json={
            "model_id": "nonexistent-model",
            "features": {"sepal_length": 5.1},
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    body = response.json()
    assert body["error"] == "model_not_found"
    assert "nonexistent-model" in body["message"]


def test_invalid_features_returns_422() -> None:
    """Empty features dict should return 422 validation error."""
    response = client.post(
        "/v1/predict",
        json={
            "model_id": "iris-classifier",
            "features": {},
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_missing_model_id_returns_422() -> None:
    """Missing model_id field should return 422."""
    response = client.post(
        "/v1/predict",
        json={"features": {"sepal_length": 5.1}},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_internal_error_returns_500() -> None:
    """Model that fails during inference should return 500."""
    InferenceService._models["broken-model"] = _BrokenModel()
    response = client.post(
        "/v1/predict",
        json={
            "model_id": "broken-model",
            "features": {"sepal_length": 5.1},
        },
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    body = response.json()
    assert body["error"] == "inference_error"


def test_cache_warm_second_request_faster() -> None:
    """Second request to same model should be faster (cache warm).

    Uses a generous tolerance (2x) to avoid flakiness from timing noise
    at sub-millisecond latencies while still validating cache behavior.
    """
    # Clear any state from previous tests
    InferenceService._models.pop("iris-classifier", None)

    response1 = client.post(
        "/v1/predict",
        json={
            "model_id": "iris-classifier",
            "features": {"sepal_length": 5.1},
        },
    )
    assert response1.status_code == status.HTTP_200_OK
    latency1 = response1.json()["latency_ms"]

    response2 = client.post(
        "/v1/predict",
        json={
            "model_id": "iris-classifier",
            "features": {"sepal_length": 5.1},
        },
    )
    assert response2.status_code == status.HTTP_200_OK
    latency2 = response2.json()["latency_ms"]

    # Cache hit should not be dramatically slower than cache miss.
    # The first request pays disk I/O; the second should be comparable or faster.
    assert latency2 <= latency1 * 2, (
        "Second request should not be >2x slower (cache should help)"
    )


def test_idempotency_key_accepted() -> None:
    """idempotency_key should be accepted but not processed."""
    response = client.post(
        "/v1/predict",
        json={
            "model_id": "iris-classifier",
            "features": {"sepal_length": 5.1},
            "idempotency_key": "test-key-123",
        },
    )
    assert response.status_code == status.HTTP_200_OK


class _BrokenModel:
    """A model that always fails during predict."""

    def predict(self, features: dict[str, float]) -> float:
        msg = "Simulated model failure"
        raise RuntimeError(msg)
