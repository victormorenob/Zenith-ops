# SPEC-005: Prediction Metadata — Trazabilidad de Predicciones

**Domain:** prediction-metadata
**Estado:** Implementado
**Backend:** PostgreSQL vía `prediction_metadata` table

---

## Purpose

Cada llamada a `/v1/predict` DEBE registrar una fila en `prediction_metadata`. Esto permite auditar predicciones, medir latencia, diagnosticar errores, y correlacionar resultados con la versión del modelo que los generó.

---

## Esquema de base de datos

### Tabla: `prediction_metadata`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | UUID | PK, default `gen_random_uuid()` |
| `request_id` | UUID | NOT NULL, UNIQUE |
| `model_id` | UUID | NOT NULL, FK → `model_registry(id)` |
| `model_name` | VARCHAR(255) | NOT NULL |
| `model_version` | VARCHAR(50) | NOT NULL |
| `input_preview` | JSONB | nullable |
| `output_preview` | JSONB | nullable |
| `latency_ms` | FLOAT | NOT NULL |
| `status` | VARCHAR(20) | NOT NULL, default `'success'` |
| `error_message` | TEXT | nullable |
| `created_at` | TIMESTAMPTZ | NOT NULL, default `now()` |

**Constraints:** UNIQUE (`request_id`); FK (`model_id`) → `model_registry(id)` ON DELETE RESTRICT

---

## Requirements

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

---

## Comportamiento

### Por cada llamada a `/v1/predict`

El sistema DEBE:
1. Generar o recibir un `request_id` (UUID v4)
2. Resolver el modelo vía `PostgresModelRegistry.resolve_path()`
3. Cargar el artifact `.joblib` y ejecutar la predicción
4. Medir `latency_ms` (tiempo total desde resolución hasta predicción)
5. Insertar una fila en `prediction_metadata` con:
   - `model_id`: UUID del modelo usado
   - `model_name` + `model_version`: copia denormalizada para consultas rápidas
   - `input_preview` / `output_preview`: preview de 1-2 registros (no el dataset completo)
   - `latency_ms`: tiempo de ejecución en milisegundos
   - `status`: `'success'` o `'error'`
   - `error_message`: solo si status es `'error'`

### Error handling

- **Fallo en DB:** si la inserción falla, se loguea un warning. La predicción NO DEBE fallar por un error de metadata. La metadata es best-effort
- **request_id duplicado:** si ya existe, la inserción es un no-op (el UNIQUE constraint evita duplicados). El sistema PUEDE loguear un debug
- **model_id huérfano:** la FK previene que se elimine un modelo referenciado. Si se intenta, DB lanza FK violation → el sistema DEBE devolver 409

---

## Criterios de aceptación

- [x] Cada predicción exitosa genera una fila en `prediction_metadata` con `status='success'`
- [x] Cada predicción con error genera una fila con `status='error'` y `error_message` poblado
- [x] `request_id` único previene duplicados en reintentos
- [x] Si la DB no responde, la predicción continúa (metadata es best-effort)
- [x] FK a `model_registry.id` impide borrar modelos con predicciones
- [x] `latency_ms` se registra correctamente
