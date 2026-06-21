# Proposal: Model Registry v1 — File-Based Catalog

## Intent

Replace the current hardcoded `models/{model_id}.joblib` path resolution with a structured, file-based Model Registry that discovers models from a versioned directory layout and exposes a metadata catalog via REST API. Every model has a sidecar `meta.json` with version, framework, description, metrics, and status — making the system auditable and professional.

## Context

Today `InferenceService._load_model` does `joblib.load(f"models/{model_id}.joblib")` — a flat path with zero metadata, no versioning, no discovery. You can't ask the system "what models do you have?" without reading source code.

A Model Registry is the industry-standard solution (MLflow, Sagemaker, ML Metadata) and the natural next step for this codebase.

## Scope

### In Scope
- Versioned directory layout: `models/<model_id>/<version>/model.joblib` + `meta.json`
- `ModelMetadata` Pydantic model with: model_id, version, framework, description, created_at, metrics, status, tags
- `ModelRegistryService` — scans `models/`, loads metadata into an in-memory catalog, resolves model paths
- `GET /v1/models` — list all registered models (latest version per model_id)
- `GET /v1/models/{model_id}` — detail of a specific model (latest version)
- Update `InferenceService._load_model` to resolve path via the registry
- Example seed model metadata for `iris-classifier`

### Out of Scope
- Version listing endpoint (`GET /v1/models/{model_id}/versions`)
- Model registration endpoint (`POST /v1/models`)
- Model deletion
- Authentication / authorization on registry endpoints
- Database backend (deferred to Phase 2)
- Model version comparison or diff UI

## Capabilities

### New Capabilities
- `model-registry`: file-based model catalog with metadata via REST API

### Modified Capabilities
- `inference`: `InferenceService` resolves model paths through the registry instead of hardcoded path

## Approach

1. **Directory layout** — create `models/<model_id>/<version>/meta.json` with model metadata and `model.joblib` with the serialized artifact
2. **`core/model_registry.py`** — `ModelMetadata` dataclass/Pydantic model, `ModelRegistryService` singleton that scans the `models/` directory at startup, parses `meta.json` files, and caches them in `{model_id: {version: Metadata}}`
3. **`api/v1/models.py`** — two read-only endpoints that query the registry service
4. **Integration** — update `InferenceService._load_model` to ask the registry for the resolved path of the active model version
5. **Seed data** — write an example `iris-classifier/1.0.0/meta.json` and keep the current `DummyIrisClassifier` as a joblib artifact

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/zenith_ops/core/model_registry.py` | New | Registry service + ModelMetadata model |
| `src/zenith_ops/api/v1/models.py` | New | GET /v1/models, GET /v1/models/{model_id} |
| `src/zenith_ops/core/inference_service.py` | Modified | Use registry path instead of hardcoded |
| `src/zenith_ops/__init__.py` | Modified | Wire registry router |
| `models/iris-classifier/1.0.0/meta.json` | New | Seed model metadata |
| `tests/unit/test_model_registry.py` | New | Registry service unit tests |
| `tests/integration/test_model_registry.py` | New | Registry endpoint integration tests |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Corrupt `meta.json` crashes startup | Low | RegistryService handles parse errors gracefully, skips bad entries |
| Directory scan on every request | Low | Scan once at startup, cache in memory; invalidate only on explicit action |
| InferenceService changes break existing predict endpoint | Low | Backward-compatible: model_id stays the same, only resolution path changes |

## Rollback Plan

1. Revert `src/zenith_ops/core/model_registry.py` and `src/zenith_ops/api/v1/models.py`
2. Restore `InferenceService._load_model` to hardcoded `models/{model_id}.joblib`
3. Remove router import from `__init__.py`
4. `git revert` the change commit

## Dependencies

- `joblib` (already in `pyproject.toml`)
- No new external dependencies

## Success Criteria

- [ ] `GET /v1/models` returns 200 with a list of registered models and their metadata
- [ ] `GET /v1/models/iris-classifier` returns metadata for iris-classifier
- [ ] `POST /v1/predict` continues to work with `model_id: "iris-classifier"`
- [ ] Invalid model_id returns 404 from registry (not FileNotFoundError)
- [ ] All existing tests pass (54 tests)
- [ ] mypy strict passes on new code
