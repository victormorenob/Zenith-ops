"""Feature flag test endpoint — for validating CI/CD and smoke testing."""

from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()


class TestFeatureRequest(BaseModel):
    request_id: str
    data: dict[str, str | int]


class TestFeatureResponse(BaseModel):
    id: str
    result: int


@router.post("/v1/test-feature", status_code=status.HTTP_200_OK)
async def feature_test(request: TestFeatureRequest) -> TestFeatureResponse:
    """Echo endpoint for CI/CD smoke tests.

    Returns the input `value` (or 0 if missing/invalid).
    """
    result = request.data.get("value", 0)
    if not isinstance(result, int):
        result = 0
    return TestFeatureResponse(id=request.request_id, result=result)
