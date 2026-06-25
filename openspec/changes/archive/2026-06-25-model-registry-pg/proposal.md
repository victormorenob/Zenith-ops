# Proposal: Model Registry PostgreSQL Migration

## Intent

Migrate Model Registry from file-based scanning to PostgreSQL, enabling concurrent writes, proper version tracking, prediction metadata logging, and multi-instance deployments. File-based singleton scanning doesn't scale beyond a single process.

## Scope

### In Scope
- SQLAlchemy models: `model_registry` + `prediction_metadata` tables
- Async Alembic migration (0001 + 0002)
- `PostgresModelRegistry` implementing async Protocol + write methods
- Protocol migration: all 3 methods become `async def`
- API: GET endpoints migrate to DB, add POST register + PATCH status
- `InferenceService._load_model` → async, uses `PostgresModelRegistry`
- Seed script writes DB row + .joblib on disk
- `DuplicateModelError` → 409
- Unit + integration tests; `.env` fix as prerequisite

### Out of Scope
- MLflow integration, version listing endpoint, model retraining
- Removing `FileBasedModelRegistry` (kept for reference)

## Capabilities

### New Capabilities
- `model-registration`: POST /v1/models/register (201), PATCH /v1/models/{id}/status (200). Status: staging/production/archived. Duplicate (name, version) → 409
- `prediction-metadata`: PredictionMetadata table with request_id idempotency, model_id FK, latency, error capture

### Modified Capabilities
- `model-registry`: Protocol becomes async. Backend changes from file scan to DB queries. Status "active" → "production". GET /v1/models/{model_id} queries by name column

## Approach

| Phase | What | Key Files |
|-------|------|-----------|
| A — Foundation | Fix .env, SA models, migration, DuplicateModelError | db/models/, exceptions.py |
| B — Registry | PostgresModelRegistry: async reads + writes | core/model_registry_db.py |
| C — API wiring | Migrate GET, add POST+PATCH, 409 handler | api/v1/models.py |
| D — InferenceService | _load_model async, _registry default change | services/predictor.py |
| E — Tests & seed | Unit (mocked), integration (real PG), seed script | tests/*, scripts/* |

## Affected Areas

| Area | Impact | Change |
|------|--------|--------|
| `core/model_registry.py` | Modified | Protocol → async def; status "production" |
| `core/model_registry_db.py` | New | PostgresModelRegistry |
| `core/exceptions.py` | Modified | Add DuplicateModelError |
| `db/models/model_registry.py` | New | ModelRegistryEntry (UUID PK, JSONB) |
| `db/models/prediction_metadata.py` | New | PredictionMetadata (UUID PK, FK, request_id UNIQUE) |
| `db/models/__init__.py` | Modified | Export new models |
| `db/migrations/versions/` | New | 0001 + 0002 |
| `api/v1/models.py` | Modified | Async Depends, POST+PATCH, schemas |
| `services/predictor.py` | Modified | _load_model async, _registry default |
| `.env` | Modified | Fix stale credentials |
| `scripts/generate_dummy_model.py` | Modified | DB row + .joblib |
| `tests/unit/test_postgres_model_registry.py` | New | Mocked session tests |
| `tests/unit/test_model_registry.py` | Modified | Adapt FileBased for async |
| `tests/integration/test_model_registry.py` | Modified | DB-backed endpoint tests |
| `openspec/specs/model-registry/spec.md` | Modified | Update for DB backend |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| `.env` stale creds blocks all DB work | High | Fix first — prerequisite before any code |
| GET /v1/models/{model_id} string → name lookup breaks clients | Medium | Clear test + doc: URL param maps to name column |
| Status "active" → "production" breaks seed data | Medium | Update seed script; migration maps if needed |
| Async Protocol breaks InferenceService._load_model | High | Refactor _load_model to async in same phase; verify predict still works |

## Rollback Plan

1. `git revert` all changes
2. Drop model_registry + prediction_metadata tables
3. Restore .env to previous credentials
4. FileBasedModelRegistry still exists — API and InferenceService fall back via git revert

## Dependencies

- PostgreSQL 16 running (docker-compose.dev.yml)
- `.env` credentials fixed (prerequisite)
- Alembic configured (target_metadata in env.py done)

## Success Criteria

- [ ] Alembic upgrade creates both tables; downgrade drops them cleanly
- [ ] GET /v1/models returns models from DB (matches file-based output)
- [ ] GET /v1/models/{name} resolves by name (backward compat)
- [ ] POST /v1/models/register creates DB row + .joblib on disk → 201
- [ ] PATCH /v1/models/{id}/status updates status → 200
- [ ] Duplicate (name, version) → 409
- [ ] `InferenceService.predict` works end-to-end (async resolve_path)
- [ ] `uv run pytest --cov=src --cov-report=term-missing -v` green (≥70%)
- [ ] `uv run mypy src/` 0 errors
