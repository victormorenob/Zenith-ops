"""Main FastAPI application factory.

Composition root: wires together all routers, exception handlers,
and shared dependencies. Only the ASGI entry point (uvicorn) imports this.
"""

import time
import uuid
from collections.abc import Awaitable, Callable

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

from zenith_ops.api.v1.health import router as health_router
from zenith_ops.api.v1.predict import router as predict_router
from zenith_ops.api.v1.test_feature import router as feature_router
from zenith_ops.core.exceptions import (
    InferenceError,
    InferenceTimeoutError,
    ModelNotFoundError,
)
from zenith_ops.core.logging_config import configure_logging

# ── Configure structured logging before the app is created ────────────
# This ensures the structlog pipeline is active before any request arrives.
configure_logging()

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
# Correlation-ID middleware — wraps every request
# ──────────────────────────────────────────────────────────────


@app.middleware("http")
async def log_requests(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Assign a UUID v4 correlation_id and log request completion.

    Logs ``request_completed`` at INFO (<400), WARNING (400-499),
    or ERROR (500+) level with method, endpoint, status,
    duration_ms, and correlation_id.
    """
    correlation_id = str(uuid.uuid4())
    request.state.correlation_id = correlation_id
    start = time.monotonic()

    response = await call_next(request)

    duration_ms = (time.monotonic() - start) * 1000
    status_code = response.status_code
    logger = structlog.get_logger("zenith_ops.middleware")
    log_kwargs = {
        "method": request.method,
        "endpoint": request.url.path,
        "status": status_code,
        "duration_ms": round(duration_ms, 2),
        "correlation_id": correlation_id,
    }

    if status_code < 400:
        logger.info("request_completed", **log_kwargs)
    elif status_code < 500:
        logger.warning("request_completed", **log_kwargs)
    else:
        logger.error("request_completed", **log_kwargs)

    response.headers["X-Correlation-ID"] = correlation_id
    return response


# ──────────────────────────────────────────────────────────────
# Catch-all middleware — outermost, catches unhandled exceptions
# ──────────────────────────────────────────────────────────────


@app.middleware("http")
async def catch_all(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Catch any Exception that escapes the domain exception handlers.

    Logs the full traceback via structlog and returns a consistent JSON
    500 response. The response body never exposes stacktraces or internal
    details.

    Registered *after* ``log_requests`` so this is the outermost
    middleware. The ``log_requests`` middleware runs inside ``call_next``,
    so it still logs ``request_completed`` with the correlation ID for
    every request — even those that end up here.
    """
    try:
        response = await call_next(request)
    except Exception:
        logger = structlog.get_logger("zenith_ops.middleware")
        logger.error(
            "unhandled_exception",
            method=request.method,
            endpoint=request.url.path,
            correlation_id=getattr(request.state, "correlation_id", "unassigned"),
            exc_info=True,
        )
        response = JSONResponse(
            status_code=500,
            content={
                "error": "internal_error",
                "message": "An unexpected error occurred",
            },
        )

    # Ensure X-Correlation-ID is always present on the response.
    # For the normal path, ``log_requests`` already set it. For the
    # exception path, we set it here as a safety net.
    if "X-Correlation-ID" not in response.headers:
        response.headers["X-Correlation-ID"] = getattr(
            request.state, "correlation_id", "unassigned"
        )
    return response


# ──────────────────────────────────────────────────────────────
# Router registration — order doesn't matter for path-based routing
# ──────────────────────────────────────────────────────────────

app.include_router(health_router)
app.include_router(feature_router)
app.include_router(predict_router)
