"""Main FastAPI application factory.

Composition root: wires together all routers, exception handlers,
and shared dependencies. Only the ASGI entry point (uvicorn) imports this.
"""

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

app = FastAPI(
    title="Zenith-ops ML Serving",
    version="0.1.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc",  # ReDoc at /redoc
)

# ──────────────────────────────────────────────────────────────
# Global exception handlers — map domain exceptions to HTTP codes
# ──────────────────────────────────────────────────────────────


# ModelNotFoundError -> 404 (resource doesn't exist)
# Client asked for a model_id that was never registered.
@app.exception_handler(ModelNotFoundError)
async def model_not_found_handler(
    request: Request, exc: ModelNotFoundError
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"error": "model_not_found", "message": str(exc)},
    )


# InferenceTimeoutError -> 503 (service temporarily unavailable)
# Model took too long (>5s). Not a bug, just a slow/blocked inference.
# 503 tells the client: "retry later", not "fix your request".
@app.exception_handler(InferenceTimeoutError)
async def inference_timeout_handler(
    request: Request, exc: InferenceTimeoutError
) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"error": "inference_timeout", "message": str(exc)},
    )


# InferenceError -> 500 (internal server error)
# Something unexpected happened inside the model (corrupt joblib, OOM, etc.).
# We don't expose internals to the client — just log and return 500.
@app.exception_handler(InferenceError)
async def inference_error_handler(
    request: Request, exc: InferenceError
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"error": "inference_error", "message": str(exc)},
    )


# ──────────────────────────────────────────────────────────────
# Router registration — order doesn't matter for path-based routing
# ──────────────────────────────────────────────────────────────

app.include_router(health_router)
app.include_router(feature_router)
app.include_router(predict_router)
