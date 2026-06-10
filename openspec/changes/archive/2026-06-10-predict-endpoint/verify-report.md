## Verification Report

**Change**: predict-endpoint
**Version**: SPEC-001 (Borrador, Fase 1)
**Mode**: Standard

### Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 14 |
| Tasks complete | 14 |
| Tasks incomplete | 0 |

### Build & Tests Execution

**Build**: ✅ Passed (mypy + ruff)

**Tests**: ✅ 25 passed / ❌ 0 failed / ⚠️ 0 skipped

```text
$ uv run pytest tests/ --cov=src --cov-report=term-missing -v
collected 25 items

tests/integration/test_predict_endpoint.py::test_valid_prediction_returns_200 PASSED
tests/integration/test_predict_endpoint.py::test_unknown_model_returns_404 PASSED
tests/integration/test_predict_endpoint.py::test_invalid_features_returns_422 PASSED
tests/integration/test_predict_endpoint.py::test_missing_model_id_returns_422 PASSED
tests/integration/test_predict_endpoint.py::test_internal_error_returns_500 PASSED
tests/integration/test_predict_endpoint.py::test_cache_warm_second_request_faster PASSED
tests/integration/test_predict_endpoint.py::test_idempotency_key_accepted PASSED
tests/unit/test_exceptions.py ...... PASSED (6 tests)
tests/unit/test_feature.py ......... PASSED (2 tests)
tests/unit/test_health.py .......... PASSED (1 test)
tests/unit/test_inference_service.py PASSED (9 tests)

25 passed in 11.06s
```

**Static Analysis**:

```text
$ uv run mypy src/
Success: no issues found in 11 source files

$ uv run ruff check src/ tests/
All checks passed!
```

**Coverage**: 96.67% / threshold: 70% → ✅ Above

```text
Name                                       Stmts   Miss  Cover
--------------------------------------------------------------
src/zenith_ops/__init__.py                    19      1    95%
src/zenith_ops/api/v1/predict.py              20      0   100%
src/zenith_ops/core/__init__.py                0      0   100%
src/zenith_ops/core/dummy_model.py             5      1    80%
src/zenith_ops/core/exceptions.py             10      0   100%
src/zenith_ops/core/inference_service.py      48      2    96%
--------------------------------------------------------------
TOTAL                                        120      4    97%
```

### Spec Compliance Matrix

| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| REQ-01: POST /v1/predict 200 with valid model + features | Valid request returns all fields (`prediction_id`, `result`, `result_type`, `latency_ms`) | `tests/integration/test_predict_endpoint.py > test_valid_prediction_returns_200` | ✅ COMPLIANT |
| REQ-02: POST /v1/predict with non-existent model_id → 404 | Unknown model_id returns `model_not_found` error | `tests/integration/test_predict_endpoint.py > test_unknown_model_returns_404` | ✅ COMPLIANT |
| REQ-03: POST /v1/predict with invalid features → 422 | Empty features dict triggers Pydantic validation error | `tests/integration/test_predict_endpoint.py > test_invalid_features_returns_422` | ✅ COMPLIANT |
| REQ-04: POST /v1/predict with model that fails → 500 | Broken model during predict returns `inference_error` | `tests/integration/test_predict_endpoint.py > test_internal_error_returns_500` | ✅ COMPLIANT |
| REQ-05: Inference timeout → 503 | Predict exceeding 5000ms returns `inference_timeout` | `tests/unit/test_inference_service.py > test_timeout_exceeded_raises_error` | ⚠️ PARTIAL |
| REQ-06: Second request faster than first (cache) | Cache warm: second request is not >2x slower than first | `tests/integration/test_predict_endpoint.py > test_cache_warm_second_request_faster` | ✅ COMPLIANT |
| REQ-07: Latency < 200ms on warm Iris cache | After cache is hot, response under 200ms | (no direct assertion) | ❌ UNTESTED |
| REQ-08: Idempotency key accepted but not processed | Key in request body does not error | `tests/integration/test_predict_endpoint.py > test_idempotency_key_accepted` | ✅ COMPLIANT |

**Compliance summary**: 6/8 scenarios fully compliant, 1 partial, 1 untested

### Correctness (Static Evidence)

| Requirement | Status | Notes |
|-------------|--------|-------|
| Unique prediction_id (UUID v4) | ✅ Implemented | `uuid.uuid4()` in the router handler |
| Lazy model cache (class-level dict) | ✅ Implemented | `InferenceService._models: dict[str, Any]` class variable |
| Latency measured with `time.monotonic()` | ✅ Implemented | `t0 = time.monotonic()` before cache lookup, `latency_ms = (time.monotonic() - t0) * 1000` |
| Timeout via `asyncio.wait_for` (5000ms) | ✅ Implemented | `INFERENCE_TIMEOUT_S = 5.0` with `asyncio.wait_for(future, timeout=5.0)` |
| Error: `ModelNotFoundError` → 404 | ✅ Implemented | Custom exception + `@app.exception_handler` registered in `__init__.py` |
| Error: `InferenceTimeoutError` → 503 | ✅ Implemented | Custom exception + handler returning 503 JSON |
| Error: `InferenceError` → 500 | ✅ Implemented | Custom exception + handler returning 500 JSON |
| Pydantic validation on features (min_length=1) | ✅ Implemented | `features: dict[str, float] = Field(..., min_length=1)` |
| Structured response with all fields | ✅ Implemented | `PredictResponse` with prediction_id, model_id, result, result_type, latency_ms |
| `idempotency_key` accepted (null | string) | ✅ Implemented | `idempotency_key: str | None = None` in schema |
| Dummy model generator script | ✅ Implemented | `scripts/generate_dummy_model.py` creates `DummyIrisClassifier` pickled to `models/iris-classifier.joblib` |

### Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| Model cache: module-level `dict[str, Any]` | ✅ Yes | Class-level `_models: dict[str, Any] = {}` on `InferenceService` |
| Timeout: `asyncio.wait_for` + `run_in_executor` | ✅ Yes | `loop.run_in_executor(None, model.predict, features)` wrapped in `asyncio.wait_for` |
| Error handling: custom exceptions + `@app.exception_handler` | ✅ Yes | Three exception classes, three handlers in `__init__.py` |
| Blocking predict in thread executor | ✅ Yes | `run_in_executor(None, model.predict, features)` |
| Pydantic schemas (PredictRequest, PredictResponse, ResultType) | ✅ Yes | Defined in `api/v1/predict.py` as specified |
| Test layers: unit + integration | ✅ Yes | `tests/unit/test_inference_service.py` + `tests/integration/test_predict_endpoint.py` |
| Exception handler registration in `__init__.py` | ✅ Yes | All three handlers registered before `include_router` |

### Issues Found

**CRITICAL**: None

**WARNING**:
1. **Timeout → 503 integration gap**: The `InferenceTimeoutError` → 503 HTTP path has no integration test. The unit test (`test_timeout_exceeded_raises_error`) proves the service raises the exception, but the FastAPI exception handler and the full HTTP response format (`{"error": "inference_timeout", "message": "..."}`) are never exercised end-to-end. Adding a test would require a 5s+ blocking call, so this is a deliberate tradeoff — but the acceptance criterion for 503 is not fully verified at the HTTP boundary.

2. **Latency < 200ms acceptance criterion untested**: The spec lists "Latencia < 200ms en modelo Iris después del primer request (caché caliente)" but there is no test asserting this absolute threshold. The existing test `test_cache_warm_second_request_faster` only checks that the second request is not >2x slower than the first — a relative, not absolute, check. This acceptance criterion remains unverified.

**SUGGESTION**:
1. **`dummy_model.predict_proba` untested**: `DummyIrisClassifier.predict_proba()` (line 17 in `src/zenith_ops/core/dummy_model.py`) is uncovered and never called. Either add a test, or if the method is unused, consider removing it.
2. **`_load_model` generic exception handler uncovered**: Lines 79-80 of `inference_service.py` catch a generic `Exception` from `joblib.load()` and re-raise as `InferenceError`. This path is never exercised. Consider a test with a corrupted `.joblib` file, or document the decision to leave it untested.
3. **`VIRTUAL_ENV` path mismatch**: The shell has `VIRTUAL_ENV=/home/victor_moreno/Zenith-ops/.venv` set, but the project's `.venv` is at `projects/Zenith-ops/.venv`. This produces a persistent warning on every `uv` command. Consider unsetting or fixing the stale environment variable.

### Verdict

**PASS WITH WARNINGS**

All 14 tasks are complete. All static analysis checks pass (mypy, ruff). Test coverage is 96.67% (well above the 70% threshold). The core implementation correctly follows the spec and design: model cache, `asyncio.wait_for` timeout, custom exception handlers, Pydantic validation, and all error mappings are in place.

Two acceptance criteria have verification gaps: the timeout→503 HTTP response path is untested at the integration level (by deliberate design, due to the 5s timeout), and the <200ms warm-latency threshold has no direct assertion. Neither is a correctness bug — the code is right — but the automated proof is incomplete.
