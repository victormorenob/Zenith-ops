# Tareas: Model Registry — Migración a PostgreSQL

## Revisión de Carga de Trabajo

Decision needed before apply: Yes (resolved — feature-branch-chain)
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: High (mitigated — 5-phase chain)

Líneas estimadas: ~1100-1300. 5 fases → 5 PRs encadenados (~250 líneas c/u).

### Unidades Sugeridas (actualizado)

| Unidad | Objetivo | PR | Base |
|--------|----------|----|------|
| 1 | ORM + migración + DuplicateModelError | PR 1 → `feat/model-registry-pg` | phase-a/feat-model-registry-pg |
| 2 | PostgresModelRegistry + Protocol async | PR 2 → PR1 branch | por definir |
| 3 | Schemas + endpoints POST/PATCH + 409 | PR 3 → PR2 branch | por definir |
| 4 | InferenceService async + log_prediction | PR 4 → PR3 branch | por definir |
| 5 | Seed script + tests completos | PR 5 → PR4 branch | por definir |

Estrategia: **feature-branch-chain** via `feat/model-registry-pg` tracker branch.

## Fase A: Foundation — ORM y Migración ✅

- [x] A.1 Fijar `.env` — credenciales PostgreSQL (`postgres:postgres@localhost:5433/ZenithOpsDatabase`) — ya estaba correcto
- [x] A.2 Crear `db/models/model_registry.py` — `ModelRegistryEntry` (UUID PK, UNIQUE name+version, JSONB, timestamps)
- [x] A.3 Crear `db/models/prediction_metadata.py` — `PredictionMetadata` (request_id UNIQUE, FK→model_registry, latency_ms FLOAT)
- [x] A.4 Exportar modelos en `db/models/__init__.py`
- [x] A.5 Generar migración Alembic: `alembic revision --autogenerate -m "create model_registry and prediction_metadata"`
- [x] A.6 Agregar `DuplicateModelError` en `core/exceptions.py`
- [x] A.7 Verificar `alembic upgrade head` y `pytest tests/` (sin cambios de comportamiento) — 99 tests passing, 0 regressions

## Fase B: PostgresModelRegistry

- [ ] B.1 Hacer `async def` los 3 métodos del Protocol en `core/model_registry.py`
- [ ] B.2 Marcar `FileBasedModelRegistry` como deprecated (docstring)
- [ ] B.3 Crear `core/model_registry_db.py` con `PostgresModelRegistry.__init__(session_factory)`
- [ ] B.4 Implementar `list_models()` — latest version per name (excluir archived)
- [ ] B.5 Implementar `get_model()` — WHERE name=model_id ORDER BY version DESC
- [ ] B.6 Implementar `resolve_path()` — retornar `artifact_path` desde DB
- [ ] B.7 Implementar `register_model()` — INSERT + UniqueViolation → DuplicateModelError
- [ ] B.8 Implementar `update_status()` — validar staging/production/archived
- [ ] B.9 Adaptar tests unitarios FileBased para async
- [ ] B.10 Verificar `pytest tests/unit/test_model_registry.py` + `mypy src/`

## Fase C: API Wiring

- [ ] C.1 Crear `api/v1/schemas/models.py` — `RegisterModelRequest`, `UpdateStatusRequest`, `ModelResponse`
- [ ] C.2 Agregar `async def get_registry()` → Depends factory en `api/v1/models.py`
- [ ] C.3 Refactorizar GET endpoints con `Depends(get_registry)` + await
- [ ] C.4 Agregar `POST /v1/models/register` → 201 (manejar UniqueViolation → 409)
- [ ] C.5 Agregar `PATCH /v1/models/{id}/status` → 200 / 404
- [ ] C.6 Registrar handler `DuplicateModelError → 409` en `zenith_ops/__init__.py`
- [ ] C.7 Verificar con httpie: POST /v1/models/register name="test" version="1.0.0"

## Fase D: InferenceService

- [ ] D.1 Hacer `_load_model` async en `services/predictor.py`
- [ ] D.2 Cambiar `_registry` default → `PostgresModelRegistry(async_session_factory)`
- [ ] D.3 Llamar `await resolve_path(model_id)` dentro de `_load_model`
- [ ] D.4 Implementar `log_prediction()` en PostgresModelRegistry (best-effort, no propaga errores)
- [ ] D.5 Llamar `log_prediction()` tras predict (éxito o error)
- [ ] D.6 Hacer `_get_model` async + actualizar callers internos
- [ ] D.7 Verificar `POST /v1/predict` end-to-end con modelo en DB

## Fase E: Seed + Tests

- [ ] E.1 Hacer `scripts/generate_dummy_model.py` async (session async + INSERT + joblib.dump)
- [ ] E.2 Escribir `tests/unit/test_postgres_model_registry.py` — mock AsyncSession, test CRUD + DuplicateModelError
- [ ] E.3 Adaptar `tests/integration/test_model_registry.py` para DB real con TestClient
- [ ] E.4 Adaptar `tests/integration/test_predict_endpoint.py` para DB-backed registry
- [ ] E.5 Verificar suite completa: `pytest --cov=src --cov-report=term-missing -v && ruff check && mypy src/`
