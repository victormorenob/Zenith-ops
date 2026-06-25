## Exploration: PostgreSQL Model Registry Migration

### Current State

The system uses `FileBasedModelRegistry` — an in-memory catalog that scans `models/` at startup:

```
models/
  <model_id>/
    <version>/
      meta.json      ← ModelMetadata (Pydantic)
      model.joblib   ← artifact
```

**Architecture flow:**

```
App startup
  → FileBasedModelRegistry.get_instance().scan()
    → walks models/, parses meta.json files
    → builds _catalog: dict[str, dict[str, ModelMetadata]]

InferenceService._load_model(model_id)
  → cls._registry.resolve_path(model_id)
    → returns models_dir / model_id / version / model.joblib

API endpoints (GET /v1/models, GET /v1/models/{model_id})
  → Depends(FileBasedModelRegistry.get_instance)
    → sync calls, no DB involved
```

**The `ModelRegistry` Protocol** defines three methods:
- `list_models() → list[ModelSummary]`
- `get_model(model_id) → ModelMetadata`
- `resolve_path(model_id) → Path`

Both the API layer and `InferenceService` code against the Protocol, not the concrete class — this was designed for exactly this migration.

**DB layer already configured:**
- `src/zenith_ops/db/session.py` — Async engine + `async_session_factory` ready
- `src/zenith_ops/db/base.py` — `DeclarativeBase` ready, imported in `env.py` as `target_metadata`
- `src/db/migrations/env.py` — Async Alembic with `target_metadata = Base.metadata`
- `alembic.ini` — Points to `postgresql+asyncpg://postgres:postgres@localhost:5432/ZenithOpsDatabase`
- `docker-compose.dev.yml` — PostgreSQL 16-alpine running on port 5433

**Existing constraints:**
- `.env` has STALE credentials (`user:password` / `mlops` / port 5432) — needs fixing
- `.env.example` has port 5433 (correct exposed port)
- `alembic.ini` has port 5432 (Docker internal, matches container name resolution)
- `db/models/` is empty (only `__init__.py` with `from zenith_ops.db.base import Base`)
- No `migrations/versions/` directory exists — first migration will be `base → head`

**Status semantics differ:**
- FileBasedRegistry: `"active"` / `"staging"` / `"archived"`
- Target DB schema: `"staging"` / `"production"` / `"archived"` (from project guide)

**Key ID semantics:**
- Current API uses `model_id` (string, directory name) as identifier in URL paths
- New DB schema uses UUID `id` as PK, `name` VARCHAR for the human-readable name
- `GET /v1/models/{model_id}` queries by `name` (backward compat)
- `PATCH /v1/models/{id}/status` uses UUID `id` (new endpoint)

### Affected Areas

| File | Impact | Change |
|------|--------|--------|
| `src/zenith_ops/db/models/model_registry.py` | **New** | SQLAlchemy model: `ModelRegistryEntry` with UUID, name, version, framework, artifact_path, status, metrics (JSONB), created_at, deployed_at. Unique constraint on (name, version) |
| `src/zenith_ops/db/models/__init__.py` | **Modify** | Export new model + keep Base |
| `src/zenith_ops/core/model_registry.py` | **Modify** | Add `register()` and `update_status()` to Protocol (or keep separate). Keep `FileBasedModelRegistry` as-is for reference |
| `src/zenith_ops/core/model_registry_db.py` | **New** | `PostgresModelRegistry` implementing `ModelRegistry` Protocol. Async methods with async session DI |
| `src/zenith_ops/api/v1/models.py` | **Modify** | Wire to `PostgresModelRegistry` via async Depends. Add `POST /v1/models/register` → 201, `PATCH /v1/models/{id}/status` → 200 |
| `src/zenith_ops/api/v1/__init__.py` | **Modify** | No change unless adding new schemas |
| `src/zenith_ops/__init__.py` | **Modify** | Startup: run Alembic migrations before app starts (or rely on `just migrate`) |
| `src/zenith_ops/services/predictor.py` | **None** | Already uses `cls._registry` (Protocol). No changes needed |
| `src/zenith_ops/core/exceptions.py` | **Modify** | Add `ModelRegistrationError` (or similar) for duplicate → 409 |
| `src/zenith_ops/core/settings.py` | **None** | Already has `DATABASE_URL` |
| `src/db/migrations/versions/` | **New** | First auto-generated migration: `create model_registry table` |
| `.env` | **Fix** | Update credentials to match docker-compose / alembic.ini |
| `tests/unit/test_model_registry.py` | **Modify** | Adapt FileBasedRegistry tests. Add PostgresModelRegistry unit tests (mocked session) |
| `tests/integration/test_model_registry.py` | **Modify** | Adapt for DB-backed endpoints. Add register + status tests with real PG |
| `openspec/specs/model-registry/spec.md` | **Modify** | Update with new endpoints and DB backend |

### Approaches

1. **Protocol extension + PostgresModelRegistry** — Recommended
   - Add `register()` and `update_status()` directly to the `ModelRegistry` Protocol
   - `FileBasedModelRegistry` gets stub implementations (raise `NotImplementedError`)
   - `PostgresModelRegistry` implements all five methods
   - API endpoints wire to `PostgresModelRegistry` via async factory `Depends()`
   - Pros: Clean Protocol contract, tests can still use FileBased for unit tests, single DI path
   - Cons: Changes the Protocol (backward-incompatible for hypothetical external consumers), FileBased stubs are dead code
   - Effort: **Medium** (~350 lines new code across 3-4 files)

2. **Separate class hierarchy (keep Protocol unchanged)** — Conservative
   - Keep `ModelRegistry` Protocol as-is with the 3 read methods
   - Add registration/status as separate service class (`ModelMutationService`) or as methods on `PostgresModelRegistry` outside the Protocol
   - `InferenceService` continues using the Protocol for `resolve_path`
   - API uses both: Protocol for reads, new service for writes
   - Pros: Protocol stays stable, no dead code, cleaner SRP
   - Cons: API layer wires two dependencies, less cohesive, extra indirection
   - Effort: **Medium** (~400 lines, but looser coupling)

3. **Replace in-place with no Protocol changes** — Minimal
   - Keep Protocol exactly as-is
   - Replace `FileBasedModelRegistry` implementation with `PostgresModelRegistry`
   - Registration/status methods live in the API router directly (use raw DB queries or a thin service)
   - Pros: Minimum changes to existing code, clean migration
   - Cons: Write logic scattered in API layer, not reusable, breaks tests that depend on FileBasedRegistry singleton
   - Effort: **Low** for API changes, **Medium** for test adaptation

4. **Hybrid: keep both backends switchable** — Maximum flexibility
   - Config flag `REGISTRY_BACKEND=file|postgres`
   - Factory function returns the right implementation
   - Both implementations coexist
   - Pros: Gradual rollout, can compare behavior, tests can use file backend without DB
   - Cons: Two code paths to maintain, adds config complexity, premature for this codebase
   - Effort: **High** (~600 lines, 2 full implementations)

### Recommendation

**Approach 1 (Protocol extension + PostgresModelRegistry)** with a twist: do NOT add write methods to the Protocol. Instead:

```
ModelRegistry (Protocol)           ← read-only, stable
  ├── FileBasedModelRegistry       ← kept for reference/tests (remove in next cleanup)
  └── PostgresModelRegistry        ← new, also implements ModelRegistryProtocol

ModelLifecycle (Service class)      ← write operations
  └── PostgresModelRegistry.register_model()
  └── PostgresModelRegistry.update_status()
```

This keeps the Protocol stable for `InferenceService` (which only needs `resolve_path` and `get_model`) while still having a cohesive class for write operations. The API layer wires one dependency (`PostgresModelRegistry`) and calls both read and write methods on it.

**Specific implementation plan:**

1. **Phase A — Foundation:**
   - Fix `.env` credentials to match docker-compose/alembic.ini
   - Create `db/models/model_registry.py` with SQLAlchemy model
   - Generate first Alembic migration (`alembic revision --autogenerate`)

2. **Phase B — PostgresModelRegistry:**
   - Create `core/model_registry_db.py` with async implementation
   - Implement `list_models()`, `get_model()`, `resolve_path()` per Protocol
   - Add `register_model()` and `update_status()` methods
   - Handle `(name, version)` unique constraint → 409 with proper exception

3. **Phase C — API wiring:**
   - Update `models.py` endpoints to use async `Depends()` returning `PostgresModelRegistry`
   - Add `POST /v1/models/register` → 201
   - Add `PATCH /v1/models/{id}/status` → 200
   - Add exception handler for duplicate → 409

4. **Phase D — Tests:**
   - Unit tests: mock async session, test `PostgresModelRegistry` logic
   - Integration tests: standalone Postgres (via testcontainers or docker-compose), test full CRUD flow
   - Existing FileBasedRegistry tests stay passing

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **`.env` credentials mismatch** | High | Medium | Fix `.env` to match docker-compose before any DB work. Currently has `user:password@localhost:5432/mlops` — must be `postgres:postgres@localhost:5433/ZenithOpsDatabase` |
| **Backward compat: `model_id` vs UUID `id`** | Medium | High | Existing endpoints use string `model_id` as path param. Mapping: URL `{model_id}` → DB query `WHERE name = :model_id`. New PATCH uses UUID `{id}`. Must be crystal clear in docs and tests |
| **Status semantics change** | Medium | Medium | FileBased uses `"active"` — new DB uses `"production"`. Existing seed data uses `"active"`. Migration must handle this mapping, or seed data needs updating |
| **Async session management** | Medium | Medium | `PostgresModelRegistry` must receive an `AsyncSession` (via DI or factory). `InferenceService` uses class-level sync methods — `resolve_path` will become async. Protocol currently returns `Path` synchronously → **this is the breaking change** |
| **FileBasedModelRegistry still used in PredictorService** | High | High | `InferenceService._load_model` uses `cls._registry` which defaults to `FileBasedModelRegistry.get_instance()`. Must reconfigure to use `PostgresModelRegistry`. Also, `_registry` is a class attribute — tests mock this, but the default must change |

**The async Protocol problem:**

The `ModelRegistry` Protocol defines sync methods:
```python
def resolve_path(self, model_id: str) -> Path: ...
```

But `PostgresModelRegistry` needs async:
```python
async def resolve_path(self, model_id: str) -> Path: ...
```

Python Protocols don't enforce sync/async. FastAPI `Depends()` can handle async callables. **However**, `InferenceService._load_model` calls `cls._registry.resolve_path()` synchronously in `_get_model()` — this will BREAK if the method becomes async.

**Resolution:** Make `resolve_path` in the Protocol async-compatible. Either:
- (A) Change Protocol to `async def resolve_path(...)` — requires changes in `InferenceService._load_model` and `FileBasedModelRegistry` (add `async` keyword, no behavior change for file-based)
- (B) Keep sync Protocol, have `PostgresModelRegistry` do sync DB calls via `run_sync()` on the engine
- (C) Cache a read-replica in memory for sync paths

**Recommendation: (A)** — Make the Protocol async across the board. It's the cleanest, and `InferenceService._get_model` already runs in a thread pool (`run_in_executor`), so calling an async `resolve_path` inside it requires a small refactor but is architecturally correct.

### Ready for Proposal

**Yes.** Exploration is complete. The orchestrator should:

1. Proceed with creating a change proposal (`sdd-propose`) using the name `model-registry-pg`
2. Note the async Protocol issue as a key design decision that the proposal MUST address
3. Flag the `.env` credentials fix as a prerequisite
4. Use Approach 1 (protocol + separate write methods) as the recommended path
