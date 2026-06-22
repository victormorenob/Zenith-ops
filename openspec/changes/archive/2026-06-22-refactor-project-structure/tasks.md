# Tasks: Refactor Project Structure

## Review Workload Forecast

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

| Field | Value |
|-------|-------|
| Estimated changed lines | ~224 (additions + deletions) |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

All 5 phases stay under 400 lines combined. Single PR is safe.

## Phase A — Foundation (db layer) ✅

| Task | Files | Test | Depends on | Status |
|------|-------|------|------------|--------|
| A1 | Create `src/zenith_ops/db/__init__.py` (empty) + `src/zenith_ops/db/base.py` with `DeclarativeBase` | `uv run pytest tests/` | — | ✅ |
| A2 | Create `src/zenith_ops/db/session.py` with async engine + factory using `Settings.DATABASE_URL` | `uv run pytest tests/` | A1 | ✅ |
| A3 | Create `src/zenith_ops/db/models/__init__.py` re-exporting `Base`, modify `src/db/migrations/env.py` to import `Base.metadata` as `target_metadata` | `uv run pytest tests/` | A1 | ✅ |

## Phase B — Exception Hierarchy ✅

| Task | Files | Test | Depends on | Status |
|------|-------|------|------------|--------|
| B1 | Modify `src/zenith_ops/core/exceptions.py` — add `Zenitherror(Exception)`, change existing exceptions to inherit `Zenitherror` | `uv run pytest tests/` | A3 | ✅ |
| B2 | Modify `src/zenith_ops/__init__.py` — import `Zenitherror`, add `@app.exception_handler(Zenitherror)` 500 fallback | `uv run pytest tests/` | B1 | ✅ |

## Phase C — Service Extraction ✅

| Task | Files | Test | Depends on | Status |
|------|-------|------|------------|--------|
| C1 | Create `src/zenith_ops/services/__init__.py`, `git mv src/zenith_ops/core/inference_service.py src/zenith_ops/services/predictor.py`, update imports in `api/v1/predict.py` (+ `ResultType`) and `api/v1/health.py` | `uv run pytest tests/` | B2 | ✅ |
| C2 | Update imports in `tests/unit/test_inference_service.py`, `tests/unit/test_health.py` (import + patch string line 80), `tests/integration/test_predict_endpoint.py` | `uv run pytest tests/` | C1 | ✅ |

## Phase D — Schema Extraction ✅

| Task | Files | Test | Depends on | Status |
|------|-------|------|------------|--------|
| D1 | Create `src/zenith_ops/api/schemas/__init__.py` + `src/zenith_ops/api/schemas/predict.py` with `PredictRequest`, `PredictResponse`, `ResultType` import | `uv run pytest tests/` | C2 | ✅ |
| D2 | Modify `src/zenith_ops/api/v1/predict.py` — remove model classes, import from `zenith_ops.api.schemas.predict` | `uv run pytest tests/` | D1 | ✅ |

## Phase E — Cleanup ✅

| Task | Files | Test | Depends on | Status |
|------|-------|------|------------|--------|
| E1 | Delete `src/zenith_ops/api/v1/.gitkeep` | `uv run pytest tests/` | D2 | ✅ |
| E2 | Run full quality suite: `uv run pytest tests/ --cov=src --cov-report=term-missing -v && uv run ruff check src/ tests/ && uv run mypy src/` | E2 is the full suite | E1 | ✅ |

## Implementation Order

Sequential, no parallelization — each phase verifies tests green before the next starts:

Phase A (Foundation) → Phase B (Exceptions) → Phase C (Service) → Phase D (Schemas) → Phase E (Cleanup)

No skip-ahead dependencies exist. Each task is verifiable via full test suite.
