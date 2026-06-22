# Delta para Prediction Metadata (Nuevo)

Nueva capacidad. No existía spec previa. Ver `openspec/specs/prediction-metadata/spec.md` para la especificación completa.

---

## ADDED Requirements

### Requirement: PredictionMetadata table

El sistema DEBE crear la tabla `prediction_metadata` con UUID PK, `request_id` UNIQUE, FK a `model_registry(id)`, y columnas para latencia, preview y error.

#### Scenario: Inserción exitosa tras predicción

- DADO una predicción exitosa con `request_id`, `model_name` y `model_version` conocidos
- CUANDO se completa la predicción
- ENTONCES se inserta una fila en `prediction_metadata` con `status='success'` y `latency_ms` > 0

#### Scenario: Error capturado en metadata

- DADO una predicción que falla (ej: modelo no cargado, input inválido)
- CUANDO ocurre el error
- ENTONCES se inserta una fila con `status='error'` y `error_message` descriptivo

### Requirement: Idempotencia por request_id

El sistema DEBE garantizar que el mismo `request_id` no genere filas duplicadas.

#### Scenario: Retry con mismo request_id

- DADO una predicción existente con `request_id = X`
- CUANDO se recibe una nueva solicitud con `request_id = X`
- ENTONCES no se inserta una segunda fila (UNIQUE constraint previene duplicado)

### Requirement: Best-effort logging

La metadata NO DEBE interrumpir la predicción si la DB falla.

#### Scenario: DB caída no detiene la predicción

- DADO que PostgreSQL no responde
- CUANDO se ejecuta una predicción
- ENTONCES la predicción se completa exitosamente
- Y se loguea un warning de que la metadata no se pudo persistir

### Requirement: FK constraint ON DELETE RESTRICT

El sistema DEBE impedir eliminar un modelo referenciado por `prediction_metadata`.

#### Scenario: Borrado de modelo con predicciones → error

- DADO un modelo con filas en `prediction_metadata`
- CUANDO se intenta eliminar ese modelo
- ENTONCES la DB lanza FK violation y el sistema devuelve 409
