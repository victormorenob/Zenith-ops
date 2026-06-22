# Design: Refactor Project Structure

## Technical Approach

Sequential 5-phase migration (A→E) with tests passing after each phase. No behavior changes — pure file/path/import restructuring. Each phase is independently verifiable via `uv run pytest tests/ --cov=src --cov-report=term-missing -v`.

## Architecture Decisions

| Decision | Choice | Alternatives | Rationale |
|----------|--------|-------------|-----------|
| Phase order | Foundation → Exceptions → Services → Schemas → Cleanup | Big bang | Each phase introduces zero new capability; sequential order prevents cascading failures and keeps each diff reviewable |
| Service class name | Keep `InferenceService` | Rename to `Predictor` | No behavior change; renaming inflates diff with non-functional churn. Defer rename to a future capabilities change |
| Exception base name | `ZeniTherror` (capital T) | `ZeniTherror`, `ZenithError` | Matches existing casing convention (`ModelNotFoundError`, `InferenceError`) |
| .gitkeep removal | Remove `api/v1/.gitkeep` only | Remove all | `src/db/migrations/.gitkeep` stays — migration directory is still templates-only; `core/` has no .gitkeep |

## Migration Flow

```
Phase A (Foundation)
  ┌─ db/base.py ──┐
  │ db/session.py │──→ alembic env.py imports Base.metadata
  └─ db/models/   ┘

Phase B (Exceptions)
  exceptions.py: add ZeniTherror base ←── existing exceptions inherit
  __init__.py:   add @app.exception_handler(ZeniTherror)

Phase C (Service)
  core/inference_service.py ──git mv──→ services/predictor.py
                                          │
                    ┌──────────────────────┤
                    ▼                      ▼
              api/v1/{predict,health}    tests/{unit,integration}/*.py
                    └── update imports ──┘

Phase D (Schemas)
  api/v1/predict.py ──extract──→ api/schemas/predict.py
     PredictRequest, PredictResponse ─── import from schemas

Phase E (Cleanup)
  Remove api/v1/.gitkeep
  git grep for stale references
```

## File Changes

### Phase A — Foundation

| File | Action | Description |
|------|--------|-------------|
| `src/zenith_ops/db/base.py` | Create | `DeclarativeBase` from SQLAlchemy ORM |
| `src/zenith_ops/db/session.py` | Create | `async_engine` + `async_session_factory` using `Settings.DATABASE_URL` |
| `src/zenith_ops/db/models/__init__.py` | Create | `from zenith_ops.db.base import Base` — re-export for Alembic |
| `src/db/migrations/env.py` | Modify | `target_metadata = Base.metadata` (import from `zenith_ops.db.base`) |

**Verify**: `uv run pytest tests/` — no code depends on these yet, so tests pass unchanged.

### Phase B — Exception Hierarchy

| File | Action | Description |
|------|--------|-------------|
| `src/zenith_ops/core/exceptions.py` | Modify | Add `class ZeniTherror(Exception)`. Change `ModelNotFoundError(ZeniTherror)`, `InferenceError(ZeniTherror)`, `InferenceTimeoutError(ZeniTherror)` |
| `src/zenith_ops/__init__.py` | Modify | Add `@app.exception_handler(ZeniTherror)` → 500 fallback. Import `ZeniTherror` |

**Verify**: `uv run pytest tests/` — handlers still catch the same exceptions by subclass.

### Phase C — Service Extraction

| File | Action | Description |
|------|--------|-------------|
| `src/zenith_ops/services/__init__.py` | Create | Package init (empty) |
| `src/zenith_ops/services/predictor.py` | Create (git mv) | Moved from `core/inference_service.py` via `git mv` to preserve history. Class `InferenceService` kept as-is |
| `src/zenith_ops/core/inference_service.py` | Delete | Replaced by `services/predictor.py` |
| `src/zenith_ops/api/v1/predict.py` | Modify | Import: `zenith_ops.services.predictor` instead of `zenith_ops.core.inference_service` |
| `src/zenith_ops/api/v1/health.py` | Modify | Import: `zenith_ops.services.predictor` instead of `zenith_ops.core.inference_service` |
| `tests/unit/test_inference_service.py` | Modify | Import: `zenith_ops.services.predictor` instead of `zenith_ops.core.inference_service` |
| `tests/unit/test_health.py` | Modify | Import (line 16) + patch string (line 80): `zenith_ops.services.predictor.InferenceService._models` |
| `tests/integration/test_predict_endpoint.py` | Modify | Import: `zenith_ops.services.predictor` instead of `zenith_ops.core.inference_service` |

**Patch strings that stay**: `zenith_ops.api.v1.predict.InferenceService.predict` in `test_logging.py` (line 164) patches the *binding* in predict.py, not the definition module — unchanged.

**Verify**: `uv run pytest tests/ -v` — all imports resolved; no stale references.

### Phase D — Schema Extraction

| File | Action | Description |
|------|--------|-------------|
| `src/zenith_ops/api/schemas/__init__.py` | Create | Package init (empty) |
| `src/zenith_ops/api/schemas/predict.py` | Create | Extract `PredictRequest`, `PredictResponse` from `api/v1/predict.py`. Add import for `ResultType` |
| `src/zenith_ops/api/v1/predict.py` | Modify | Remove model classes. Add `from zenith_ops.api.schemas.predict import PredictRequest, PredictResponse` |

**No test changes** — tests that POST JSON don't import these models.

**Verify**: `uv run pytest tests/ -v` — endpoint responses identical.

### Phase E — Cleanup

| File | Action | Description |
|------|--------|-------------|
| `src/zenith_ops/api/v1/.gitkeep` | Delete | Directory now has real files |
| (verify) | Check | `git grep` for any stale `zenith_ops.core.inference_service` or `zenith_ops.core.exceptions` references |

**Verify**: `uv run pytest tests/ --cov=src --cov-report=term-missing -v && uv run ruff check src/ tests/`

## Interfaces / Contracts

No new interfaces. Existing contracts unchanged:
- `InferenceService.predict(model_id, features, idempotency_key)` — same signature, same module path in API layer
- `PredictRequest` / `PredictResponse` — same fields, just imported from `api.schemas.predict`
- `ModelNotFoundError`, `InferenceError`, `InferenceTimeoutError` — same constructors, now inherit `ZeniTherror`

The `db/` layer introduces foundation stubs only — no consumer depends on them yet.

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | All existing inference, health, exceptions, logging tests | Run full suite after each phase |
| Integration | Predict endpoint, error handling, middleware | Run full suite after each phase — no behavior changes expected |
| Quality | Lint + type check | `ruff check src/ tests/ && mypy src/` after final phase |

## Migration / Rollout

No migration required. Each phase is independently verifiable and reversible:
- **Phase A**: `git checkout -- src/zenith_ops/db/ src/db/migrations/env.py`
- **Phase B**: `git checkout -- src/zenith_ops/core/exceptions.py src/zenith_ops/__init__.py`
- **Phase C**: `git mv` back + restore imports (or `git checkout` the whole change)
- **Phase D**: `git checkout -- src/zenith_ops/api/schemas/ src/zenith_ops/api/v1/predict.py`
- **Phase E**: `git checkout -- src/zenith_ops/api/v1/.gitkeep`

## Open Questions

None.
