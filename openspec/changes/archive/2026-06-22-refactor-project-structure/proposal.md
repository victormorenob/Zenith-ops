# Proposal: Refactor Project Structure

## Intent

The current flat `core/` package conflates business logic, infrastructure, and framework concerns. Schemas live inside route files, the inference service sits alongside settings and exceptions, and the db layer has no foundation. This makes the codebase harder to navigate, test, and extend as we add capabilities in future phases.

## Scope

### In Scope
- Move `core/inference_service.py` → `services/predictor.py` (rename + import fix)
- Extract `PredictRequest` / `PredictResponse` from `api/v1/predict.py` into new `api/schemas/predict.py`
- Add `ZeniTherror` base class in `core/exceptions.py`; make `ModelNotFoundError`, `InferenceError`, `InferenceTimeoutError` inherit from it
- Create `db/base.py` (DeclarativeBase), `db/session.py` (async engine + session factory), `db/models/__init__.py` (ORM stubs)
- Update all imports across `src/`, `tests/`, `alembic/env.py`

### Out of Scope
- No behavior or API contract changes
- No new deps, no `pyproject.toml` changes
- No infra, CI, or docs changes

## Capabilities

### New Capabilities
None. This is a pure structural refactor — no new capabilities introduced.

### Modified Capabilities
None. All existing specs (`predict`, `health`, `error-handling`, `logging`) describe behavior that remains unchanged. Only file paths change.

## Approach

1. Create `services/` package, copy + rename `inference_service.py` → `services/predictor.py`, update internal imports
2. Create `api/schemas/` package, extract Pydantic models, update `api/v1/predict.py` imports
3. Edit `core/exceptions.py` — add `ZeniTherror(Exception)` base, re-parent existing exceptions
4. Create `db/base.py`, `db/session.py`, `db/models/__init__.py` with foundation stubs
5. Glob all cross-references in `src/` and `tests/`, update import paths
6. Run test suite — green before moving on

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/zenith_ops/services/` | New | predictor.py (moved from core/) |
| `src/zenith_ops/api/schemas/` | New | predict.py (extracted schemas) |
| `src/zenith_ops/core/exceptions.py` | Modified | ZeniTherror base added |
| `src/zenith_ops/db/` | New | base.py, session.py, models/ |
| `src/zenith_ops/__init__.py` | Modified | Import paths |
| `src/zenith_ops/api/v1/*.py` | Modified | Import paths |
| `tests/` | Modified | Import paths |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Missing an import reference | Med | `git grep` after each move, run full test suite |
| git blame / history loss | Low | Use `git mv` for moved files |

## Rollback Plan

1. `git stash` or revert the single commit — all changes are import-path renames, a clean revert restores state
2. If partial: restore moved files via `git checkout HEAD -- src/zenith_ops/core/inference_service.py`, then revert import changes

## Dependencies

None.

## Success Criteria

- [ ] All tests pass (`uv run pytest tests/ --cov=src --cov-report=term-missing -v`)
- [ ] `ruff check src/ tests/` passes
- [ ] `mypy src/` passes
- [ ] No behavior change — existing integration tests for predict, health return same responses
