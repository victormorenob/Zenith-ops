"""Smoke tests for the feature test endpoint."""

from fastapi import status
from fastapi.testclient import TestClient

from zenith_ops import app

client = TestClient(app)


def test_return_feature() -> None:
    # Arrange / Act
    response = client.post(
        "/v1/test-feature",
        json={
            "request_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "data": {"name": "string", "value": 1},
        },
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "result": 1,
    }


def test_return_feature_defaults_result_when_value_missing() -> None:
    """Missing smoke-test value returns the documented zero fallback."""
    # Arrange / Act
    response = client.post(
        "/v1/test-feature",
        json={
            "request_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "data": {"name": "string"},
        },
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "result": 0,
    }


def test_return_feature_defaults_result_when_value_is_not_int() -> None:
    """Non-integer smoke-test value returns the documented zero fallback."""
    # Arrange / Act
    response = client.post(
        "/v1/test-feature",
        json={
            "request_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "data": {"name": "string", "value": "not-an-int"},
        },
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "result": 0,
    }
