# Design: Prediction Endpoint (SPEC-001)

## Technical Approach

Single synchronous inference call wrapped in async boundaries. FastAPI receives the request, validates with Pydantic, delegates to a service layer that loads the model lazily (cached in a `dict`), runs `.predict()` in a thread executor (joblib models are blocking), measures wall-clock time, and returns a structured response. Timeout handled via `asyncio.wait_for`. Error cases map to custom exceptions caught by FastAPI exception handlers — no try/except noise in the router.

## Architecture Decisions

### Decision: Model cache strategy

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Module-level `dict[str, Any]` | Simple, no eviction — fine for Fase 1 | ✅ **Chosen** |
| `functools.lru_cache` | Stateless fetch only, no explicit load/error handling | ❌ |
| Redis / external cache | Overkill for a handful of models on a single process | ❌ |

**Rationale**: Models are loaded once and rarely change. A plain dict with a load + cache pattern keeps things testable and trivially simple. No external dep needed.

### Decision: Timeout mechanism

| Option | Tradeoff | Decision |
|--------|----------|----------|
| `asyncio.wait_for` + `run_in_executor` | Standard async pattern for blocking CPU. Works across platforms | ✅ **Chosen** |
| `signal.alarm` | Unix-only, breaks with async event loop | ❌ |
| Manual timing + abort flag | Race-prone, non-deterministic | ❌ |

**Rationale**: Model `.predict()` is CPU-bound and blocking. Running it in a thread executor with `asyncio.wait_for` is the canonical FastAPI pattern to enforce a timeout without blocking the event loop.

### Decision: Error handling

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Custom exceptions + `@app.exception_handler` | Clean router, extensible, testable | ✅ **Chosen** |
| Inline try/except in router | Repetitive, mixes concerns | ❌ |
| Global middleware | Too wide, harder to test | ❌ |

**Rationale**: Keeps the router focused on HTTP concerns. Each error path maps to exactly one exception class and one handler. Adding new error types in later phases means adding one exception + one handler — no router changes.

### Decision: Blocking predict in thread executor

**Choice**: `await asyncio.get_event_loop().run_in_executor(None, model.predict, features)`  
**Alternatives**: Rewriting model to be async, using `anyio.to_thread`  
**Rationale**: Models are pre-existing `.joblib` files with sync `.predict()` interfaces. `run_in_executor` is the standard bridge. `anyio.to_thread` is equivalent but adds a dependency not yet in the project.

## Data Flow

```ascii
Client                Router                 Service              Filesystem
  │                     │                      │                     │
  │  POST /v1/predict   │                      │                     │
  │────────────────────>│                      │                     │
  │                     │  validate request    │                     │
  │                     │  (Pydantic)          │                     │
  │                     │  gen prediction_id   │                     │
  │                     │  t0 = monotonic()    │                     │
  │                     │                      │                     │
  │                     │  inference_service   │                     │
  │                     │ .predict(model_id,   │                     │
  │                     │  features)           │                     │
  │                     │─────────────────────>│                     │
  │                     │                      │  model in cache?    │
  │                     │                      │  ── no ───────────>│  load .joblib
  │                     │                      │<────────────────────│
  │                     │                      │  store in cache     │
  │                     │                      │  run_in_executor    │
  │                     │                      │  .predict(features) │
  │                     │                      │  asyncio.wait_for   │
  │                     │<─────────────────────│  result + latency   │
  │                     │                      │                     │
  │                     │  build response      │                     │
  │<────────────────────│                      │                     │
  │  200 + prediction   │                      │                     │
```

### Timeout path
If `asyncio.wait_for` raises `TimeoutError` → `InferenceTimeoutError` caught by exception handler → `503 {"error": "inference_timeout", ...}`.

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `src/zenith_ops/__init__.py` | Modify | Register `predict_router` + exception handlers |
| `src/zenith_ops/api/v1/predict.py` | Create | `POST /v1/predict` endpoint with Pydantic schemas |
| `src/zenith_ops/core/__init__.py` | Create | Empty init for core package |
| `src/zenith_ops/core/exceptions.py` | Create | `ModelNotFoundError`, `InferenceTimeoutError`, `InferenceError` |
| `src/zenith_ops/core/inference_service.py` | Create | `InferenceService` — model cache, load, predict |
| `tests/unit/test_inference_service.py` | Create | Unit tests for service (cache hit/miss, timeout, error) |
| `tests/integration/test_predict_endpoint.py` | Create | Integration tests via `TestClient` |
| `models/iris-classifier.joblib` | Create | Dummy model (small pickle of a callable with `.predict()`) |

## Interfaces / Contracts

### Request / Response schemas

```python
# api/v1/predict.py

class PredictRequest(BaseModel):
    model_id: str
    features: dict[str, float] = Field(..., min_length=1)
    idempotency_key: str | None = None


class ResultType(str, enum.Enum):
    scalar = "scalar"
    class_ = "class"
    array = "array"


class PredictResponse(BaseModel):
    prediction_id: UUID
    model_id: str
    result: float | list[float]
    result_type: ResultType
    latency_ms: float
```

### Custom exceptions

```python
# core/exceptions.py

class ModelNotFoundError(Exception):
    def __init__(self, model_id: str) -> None:
        self.model_id = model_id
        super().__init__(f"No model found with id: {model_id}")

class InferenceTimeoutError(Exception):
    def __init__(self, timeout_ms: int) -> None:
        super().__init__(f"Inference took longer than {timeout_ms}ms")

class InferenceError(Exception):
    def __init__(self, message: str = "Model failed during inference") -> None:
        super().__init__(message)
```

### Service contract

```python
# core/inference_service.py

class InferenceService:
    _models: ClassVar[dict[str, Any]] = {}

    async def predict(
        self, model_id: str, features: dict[str, float]
    ) -> tuple[float | list[float], ResultType, float]:
        ...
```

Returns `(result, result_type, latency_ms)`. `latency_ms` measured with `time.monotonic()` inside the method covering cache lookup + inference. Raises `ModelNotFoundError`, `InferenceTimeoutError`, or `InferenceError`.

### Exception handlers (registered in `__init__.py`)

```python
@app.exception_handler(ModelNotFoundError)
async def model_not_found_handler(...) -> JSONResponse:  # 404

@app.exception_handler(InferenceTimeoutError)
async def inference_timeout_handler(...) -> JSONResponse:  # 503

@app.exception_handler(InferenceError)
async def inference_error_handler(...) -> JSONResponse:  # 500
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | `InferenceService` — cache miss loads model, cache hit skips load, timeout raises, model failure raises | Mock `joblib.load`, fake model with `time.sleep` for timeout test |
| Unit | `ModelNotFoundError` on invalid model_id | No mock file → verify exception |
| Integration | Full endpoint — valid request → 200 with all fields | `TestClient` + real dummy model |
| Integration | Error cases: 404, 422, 500 | `TestClient` |

**Dummy model**: A class with a `.predict()` method that returns a constant value, pickled with `joblib.dump()` to `models/iris-classifier.joblib`. For timeout testing, the test can inject a mock that sleeps > 5000ms.

**Shared fixture**: A `conftest.py` at `tests/` or `tests/integration/` with a `TestClient` fixture to avoid repetition is optional — existing tests repeat the client instance per module, so follow that convention.

## Migration / Rollout

No migration required. New endpoint is additive — existing routes are untouched.

## Open Questions

None. All decisions map to spec requirements.
