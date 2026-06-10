# Tasks: Prediction Endpoint

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~310 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | single-pr |
| Chain strategy | size-exception |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Low

## Phase 1: Foundation

- [x] 1.1 Create `src/zenith_ops/core/__init__.py` — empty package init
- [x] 1.2 Create `src/zenith_ops/core/exceptions.py` — `ModelNotFoundError`, `InferenceTimeoutError`, `InferenceError`
- [x] 1.3 Create `models/` dir with a script to generate dummy `iris-classifier.joblib` (a class with `.predict()` returning constants, pickled via joblib)

## Phase 2: Core Logic

- [x] 2.1 Create `src/zenith_ops/core/inference_service.py` — `InferenceService` with class-level model cache (`dict`), synchronous `.predict()` via `run_in_executor` + `asyncio.wait_for(timeout=5)`, latency measurement with `time.monotonic()`. Raises `ModelNotFoundError`, `InferenceTimeoutError`, `InferenceError`.

## Phase 3: Endpoint

- [x] 3.1 Create `src/zenith_ops/api/v1/predict.py` — Pydantic schemas (`PredictRequest`, `PredictResponse`, `ResultType` enum) + `POST /v1/predict` router that validates, generates UUID, calls service, returns structured response
- [x] 3.2 Register `predict_router` in `__init__.py` — add include_router + exception handlers for `ModelNotFoundError`→404, `InferenceTimeoutError`→503, `InferenceError`→500

## Phase 4: Testing

- [x] 4.1 Write `tests/unit/test_inference_service.py` — cache miss loads model, cache hit skips load, invalid model_id raises 404, sleep>5s raises timeout, .predict() failure raises 500
- [x] 4.2 Write `tests/integration/test_predict_endpoint.py` — valid request→200 with all fields, unknown model→404, invalid features→422, internal error→500, second request faster than first (cache warm)

## Phase 5: Verification

- [x] 5.1 `uv run pytest` — all tests green
- [x] 5.2 `uv run mypy src/` — zero errors
- [x] 5.3 `uv run ruff check src/ tests/` — clean
