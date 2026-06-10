# Archive Report: predict-endpoint

**Date:** 2026-06-10
**Spec Version:** SPEC-001
**Fase:** 1 | **Objetivo:** 1.1
**Mode:** openspec
**Verdict:** PASS WITH WARNINGS

---

## 1. What Was Implemented

The `POST /v1/predict` endpoint — the core inference nucleus of the system. All spec requirements from SPEC-001 are implemented:

| Requirement | Implementation | Status |
|-------------|---------------|--------|
| `POST /v1/predict` with valid model + features → 200 | FastAPI router at `api/v1/predict.py` with `PredictRequest`/`PredictResponse` Pydantic schemas | ✅ COMPLIANT |
| Non-existent `model_id` → 404 | `ModelNotFoundError` + `@app.exception_handler` | ✅ COMPLIANT |
| Invalid `features` → 422 | Pydantic `Field(min_length=1)` validation | ✅ COMPLIANT |
| Model failure → 500 | `InferenceError` + handler | ✅ COMPLIANT |
| Inference timeout → 503 | `InferenceTimeoutError` + `asyncio.wait_for(timeout=5.0)` | ⚠️ PARTIAL (no integration test) |
| Latency < 200ms warm cache | `time.monotonic()` measurement in `InferenceService.predict()` | ❌ UNTESTED (no direct assertion) |
| Cache warm: second request faster | Cache hit verification via test | ✅ COMPLIANT |
| Idempotency key accepted | Optional field, accepted but not processed | ✅ COMPLIANT |

### Key Files Created

| File | Role |
|------|------|
| `src/zenith_ops/api/v1/predict.py` | FastAPI router — `POST /v1/predict`, Pydantic schemas, UUID generation |
| `src/zenith_ops/core/inference_service.py` | `InferenceService` — class-level model cache (`dict`), lazy `.joblib` loading, `run_in_executor` + `asyncio.wait_for` for timeout, `time.monotonic()` latency |
| `src/zenith_ops/core/exceptions.py` | `ModelNotFoundError`, `InferenceTimeoutError`, `InferenceError` |
| `src/zenith_ops/core/__init__.py` | Empty package init |
| `scripts/generate_dummy_model.py` | Generates `models/iris-classifier.joblib` — a pickled `DummyIrisClassifier` with `.predict()` |

### Modified Files

| File | Change |
|------|--------|
| `src/zenith_ops/__init__.py` | Registered `predict_router` via `include_router` + three exception handlers |

---

## 2. Key Stats

| Metric | Value |
|--------|-------|
| **Tasks** | 11/11 completed |
| **Tests** | 25 passed (9 unit + 7 integration + 6 exceptions + 2 feature + 1 health) |
| **Coverage** | 96.67% (threshold: 70%) |
| **Static Analysis** | mypy 0 errors, ruff clean |
| **Changed lines** | ~310 (within budget) |
| **Delivery strategy** | single-pr |
| **Archived at** | `openspec/changes/archive/2026-06-10-predict-endpoint/` |

### Coverage Detail

| Module | Coverage |
|--------|---------|
| `src/zenith_ops/__init__.py` | 95% |
| `src/zenith_ops/api/v1/predict.py` | 100% |
| `src/zenith_ops/core/exceptions.py` | 100% |
| `src/zenith_ops/core/inference_service.py` | 96% |
| `src/zenith_ops/core/dummy_model.py` | 80% |

---

## 3. Known Gaps

### WARNING: Timeout→503 path lacks integration test
The `InferenceTimeoutError` → 503 HTTP response format is exercised only at the unit level. The FastAPI exception handler and the full `{"error": "inference_timeout"}` JSON contract are never verified end-to-end because integration testing would require a 5s+ blocking call. This is a **deliberate tradeoff** — the correctness is proven statically and at unit level, but the HTTP boundary is not.

### WARNING: Latency < 200ms acceptance criterion untested
The spec requires "Latencia < 200ms en modelo Iris después del primer request (caché caliente)", but no test asserts this absolute threshold. The existing test `test_cache_warm_second_request_faster` only checks relative performance (second request not >2x slower than first). The acceptance criterion remains unverified.

### SUGGESTION: Minor uncovered paths
- `dummy_model.predict_proba()` (line 17) is uncovered and unused — consider removing if dead code.
- `_load_model` generic exception handler (lines 79-80) is uncovered — a corrupted `.joblib` test would exercise it.
- Stale `VIRTUAL_ENV` environment variable produces a warning on every `uv` command.

### No Destructive Deltas
This change was additive — no existing routes, schemas, or contracts were modified or removed.

---

## 4. Specs Synced

| Domain | Action | Details |
|--------|--------|---------|
| `predict` | **Created** | `openspec/specs/predict/spec.md` — copied from delta spec (no existing main spec) |

---

## 5. What's Next

**Objetivo 1.2: Model Registry CRUD** — persist model metadata (name, version, path, status) in the database, replacing the hardcoded model discovery in `models/`. This is the next logical step before Fase 2 (monitoring) and Fase 3 (auto-retraining).

### Future phases after Model Registry:
- **Fase 2** (Objetivos 2.1–2.3): Monitoring — request metrics, Prometheus integration, latency histograms, error rate tracking
- **Fase 3** (Objetivos 3.1–3.2): Auto-retraining — performance degradation detection, scheduled retraining
- **Reserved**: Real idempotency (`idempotency_key` processing), authentication

---

## 6. Archive Contents

```
archive/2026-06-10-predict-endpoint/
├── proposal.md
├── specs/spec.md
├── design.md
├── tasks.md
├── verify-report.md
└── archive-report.md
```

All artifacts preserved. No destructive changes. SDD cycle complete.
