# SPEC-005: Prediction Metadata — Trazabilidad de Predicciones

**Estado:** Por implementar (fase 2)
**Backend:** PostgreSQL vía `prediction_metadata` table

---

## Propósito

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

## Relaciones

- `prediction_metadata.model_id` → FK a `model_registry.id`. La FK usa ON DELETE RESTRICT: no se puede eliminar un modelo que tenga predicciones asociadas
- `request_id` es único para garantizar idempotencia: si el cliente retry el mismo request_id, no se DUPLICA la fila

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

### Idempotencia

`request_id` con UNIQUE constraint garantiza que reintentos del mismo request no generen filas duplicadas. Si el cliente envía el mismo `request_id`, el INSERT falla silenciosamente (no-op para metadata, la predicción se ejecuta igual).

---

## Criterios de aceptación

- [ ] Cada predicción exitosa genera una fila en `prediction_metadata` con `status='success'`
- [ ] Cada predicción con error genera una fila con `status='error'` y `error_message` poblado
- [ ] `request_id` único previene duplicados en reintentos
- [ ] Si la DB no responde, la predicción continúa (metadata es best-effort)
- [ ] FK a `model_registry.id` impide borrar modelos con predicciones
- [ ] `latency_ms` se registra correctamente
