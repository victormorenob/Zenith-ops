from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from zenith_ops.api.v1.health import router as health_router
from zenith_ops.api.v1.predict import router as predict_router
from zenith_ops.api.v1.test_feature import router as feature_router
from zenith_ops.core.exceptions import (
    InferenceError,
    InferenceTimeoutError,
    ModelNotFoundError,
)

app = FastAPI()


@app.exception_handler(ModelNotFoundError)
async def model_not_found_handler(
    request: Request, exc: ModelNotFoundError
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"error": "model_not_found", "message": str(exc)},
    )


@app.exception_handler(InferenceTimeoutError)
async def inference_timeout_handler(
    request: Request, exc: InferenceTimeoutError
) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"error": "inference_timeout", "message": str(exc)},
    )


@app.exception_handler(InferenceError)
async def inference_error_handler(
    request: Request, exc: InferenceError
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"error": "inference_error", "message": str(exc)},
    )


app.include_router(health_router)
app.include_router(feature_router)
app.include_router(predict_router)
