# Delta para Model Registry

## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: GET /v1/models (DB-backed)

El sistema DEBE listar modelos desde PostgreSQL, manteniendo el mismo response shape. La última versión se determina por `created_at DESC` agrupado por `name`.
(Previously: file-scan at startup, in-memory cache, last active version by semver sort)

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
(Previously: resolved by directory name under models/ folder)

#### Scenario: Modelo encontrado por name

- DADO un modelo con `name='iris-classifier'` en DB
- CUANDO se envía GET /v1/models/iris-classifier
- ENTONCES se devuelve 200 con metadata completa y status `staging|production|archived`

#### Scenario: Name no encontrado → 404

- DADO que no existe un modelo con `name='unknown'`
- CUANDO se envía GET /v1/models/unknown
- ENTONCES se devuelve 404

### Requirement: Status semantics

El sistema DEBE usar `'staging'`, `'production'`, `'archived'` como valores de status. El valor `'active'` ya no se usa.
(Previously: status values were 'active', 'staging', 'archived')

#### Scenario: Seed data mapea active → staging

- DADO un registro legacy con status `'active'`
- CUANDO se ejecuta la migración
- ENTONCES `'active'` se mapea a `'staging'`

## REMOVED Requirements

### Requirement: Cache en startup (file scan)

(Reason: ya no se escanea el sistema de archivos al iniciar. La DB es la fuente de verdad y cada query lee del pool de conexiones)
