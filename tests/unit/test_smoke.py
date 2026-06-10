"""Quick smoke test for the FastAPI app — does the factory work?"""

from fastapi.testclient import TestClient

from zenith_ops import app


def test_health_live() -> None:
    """GET /health/live returns 200."""
    client = TestClient(app)
    resp = client.get("/health/live")
    assert resp.status_code == 200
    assert resp.json()["status"] == "up"
