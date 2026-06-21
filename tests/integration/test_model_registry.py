"""Integration tests for GET /v1/models endpoints.

Uses TestClient against the real FastAPI app with exception handlers.
Requires the versioned model directory structure seeded by conftest.
"""

from fastapi import status
from fastapi.testclient import TestClient

from zenith_ops import app

client = TestClient(app)


def test_list_models_returns_200() -> None:
    """GET /v1/models should return 200 with a list of models."""
    response = client.get("/v1/models")
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert "models" in body
    assert len(body["models"]) >= 1

    model = body["models"][0]
    assert model["model_id"] == "iris-classifier"
    assert model["latest_version"] == "1.0.0"
    assert model["framework"] == "sklearn"
    assert model["status"] == "active"


def test_get_model_returns_metadata() -> None:
    """GET /v1/models/iris-classifier should return full ModelMetadata."""
    response = client.get("/v1/models/iris-classifier")
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["model_id"] == "iris-classifier"
    assert body["version"] == "1.0.0"
    assert body["framework"] == "sklearn"
    assert body["status"] == "active"
    assert "created_at" in body
    assert body["tags"] == ["classification", "iris", "multiclass"]


def test_get_model_unknown_returns_404() -> None:
    """GET /v1/models/unknown should return 404 with model_not_found error."""
    response = client.get("/v1/models/unknown")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    body = response.json()
    assert body["error"] == "model_not_found"


def test_predict_still_works() -> None:
    """Backward compatibility: POST /v1/predict still works with the seeded model."""
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
    assert body["model_id"] == "iris-classifier"
    assert isinstance(body["latency_ms"], float)
