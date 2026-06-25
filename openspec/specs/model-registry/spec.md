# SPEC-002: Model Registry v2 — PostgreSQL Backend

**Domain:** model-registry
**Estado:** Implementado
**Fase:** 2
**Objetivo:** Migración file-based → PostgreSQL

---

## Purpose

El Model Registry es la fuente de verdad para modelos ML: descubrimiento, versionado, promoción de status y resolución de artifacts. A partir de esta versión el backend es PostgreSQL (`model_registry` table) con artifacts `.joblib` en disco referenciados por `artifact_path`. `PostgresModelRegistry` implementa el Protocol async; `FileBasedModelRegistry` permanece deprecated para tests unitarios sin DB.

---

## Requirements

### Requirement: GET /v1/models (DB-backed)

El sistema DEBE listar modelos desde PostgreSQL, manteniendo el mismo response shape. La última versión se determina por `created_at DESC` agrupado por `name`.

#### Scenario: Listado con modelos registrados

- DADO que existen modelos en `model_registry` con status `'staging'` y `'production'`
- CUANDO se envía GET /v1/models
- ENTONCES se devuelve 200 con `{"models": [...]}`
- Y cada entry tiene `model_id: <name>`, `status: staging|production|archived`

#### Scenario: Sin modelos

- DADO que `model_registry` está vacío
- CUANDO se envía GET /v1/models
- ENTONCES se devuelve 200 con `{"models": []}`

#### Scenario: Solo muestra última versión por name

- DADO que existen dos versiones de `iris-classifier` (1.0.0 y 2.0.0)
- CUANDO se envía GET /v1/models
- ENTONCES solo aparece la versión más reciente (2.0.0) en la lista

### Requirement: GET /v1/models/{model_id} (name lookup)

El sistema DEBE resolver `{model_id}` contra la columna `name` en DB. Última versión por `created_at DESC`.

#### Scenario: Modelo encontrado por name

- DADO un modelo con `name='iris-classifier'` en DB
- CUANDO se envía GET /v1/models/iris-classifier
- ENTONCES se devuelve 200 con metadata completa y status `staging|production|archived`

#### Scenario: Name no encontrado → 404

- DADO que no existe un modelo con `name='unknown'`
- CUANDO se envía GET /v1/models/unknown
- ENTONCES se devuelve 404

### Requirement: POST /v1/models/register

El sistema DEBE exponer `POST /v1/models/register` que crea una fila en `model_registry` y devuelve 201 con el modelo creado.

#### Scenario: Registro exitoso

- DADO un payload válido con `name`, `version`, `framework`
- CUANDO se envía POST /v1/models/register
- ENTONCES se crea una fila en `model_registry` con status `'staging'`
- Y se devuelve 201 con el modelo completo

#### Scenario: Duplicado (name, version) → 409

- DADO que ya existe un modelo con `name='iris'` y `version='1.0.0'`
- CUANDO se envía POST /v1/models/register con los mismos valores
- ENTONCES se devuelve 409 con `{"error": "duplicate_model"}`

### Requirement: PATCH /v1/models/{id}/status

El sistema DEBE exponer `PATCH /v1/models/{id}/status` que actualiza el status de un modelo por UUID.

#### Scenario: Status actualizado exitosamente

- DADO un modelo con UUID existente
- CUANDO se envía PATCH con `{"status": "production"}`
- ENTONCES se actualiza el status en DB y se devuelve 200
- Y `updated_at` se actualiza a la hora actual

#### Scenario: UUID inexistente → 404

- DADO un UUID que no existe en `model_registry`
- CUANDO se envía PATCH /v1/models/{uuid}/status
- ENTONCES se devuelve 404

### Requirement: Status semantics

El sistema DEBE usar `'staging'`, `'production'`, `'archived'` como valores de status. El valor `'active'` ya no se usa.

#### Scenario: Seed data mapea active → staging

- DADO un registro legacy con status `'active'`
- CUANDO se ejecuta la migración
- ENTONCES `'active'` se mapea a `'staging'`

---

## Reglas de negocio

1. **Última versión**: listado y detalle exponen la versión más reciente por `name` (`created_at DESC`)
2. **Backend DB**: cada query lee del pool de conexiones async; no hay file-scan en startup
3. **Artifacts en disco**: `artifact_path` TEXT apunta al `.joblib`; no BYTEA en DB
4. **Protocol async**: `list_models`, `get_model`, `resolve_path` son `async def`
5. **Escrituras**: `register_model` y `update_status` viven en `PostgresModelRegistry`, no en el Protocol
6. **Unicidad**: constraint `(name, version)` → `DuplicateModelError` → HTTP 409
7. **Backward compatibility**: `model_id` en URL sigue siendo el `name` del modelo; predict endpoint sin cambios de contrato
8. **DI**: API usa `get_registry()` con `Depends`; `InferenceService` usa `PostgresModelRegistry` por defecto

---

## Criterios de aceptación

- [x] GET /v1/models con modelos en DB → 200
- [x] GET /v1/models sin modelos → 200 con lista vacía
- [x] GET /v1/models/{name} → 200 / 404
- [x] POST /v1/models/register → 201 / 409
- [x] PATCH /v1/models/{id}/status → 200 / 404
- [x] InferenceService usa `await resolve_path()` async
- [x] `uv run pytest` verde, cobertura ≥70%
- [x] `uv run mypy src/` 0 errores

---

## Fuera de scope

- MLflow integration, version listing endpoint, model retraining
- Eliminación de `FileBasedModelRegistry` (deprecated, mantenido para tests)
- Autenticación en endpoints del registry
