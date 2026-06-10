# SPEC-001: Prediction Endpoint

**Estado:** Aprobado
**Fase:** 1
**Objetivo:** 1.1

---

## Contexto

Endpoint para servir predicciones de un modelo de Machine Learning registrado.
El sistema recibe datos numéricos preprocesados (features), los pasa por un modelo
cargado en memoria, y devuelve el resultado de la inferencia junto con metadatos
de la ejecución.

## Contrato

### Request

**Método:** POST
**Endpoint:** `/v1/predict`

```json
{
  "model_id": "iris-classifier",
  "features": {
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
  },
  "idempotency_key": null
}
```

### Response (200)

```json
{
  "prediction_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "model_id": "iris-classifier",
  "result": 0.0,
  "result_type": "class",
  "latency_ms": 12.5
}
```

### Errores

| Caso | Código | Respuesta |
|------|--------|-----------|
| `model_id` no encontrado | 404 | `{"error": "model_not_found", "message": "..."}` |
| `features` inválido | 422 | Error Pydantic con campo específico |
| Timeout de inferencia | 503 | `{"error": "inference_timeout", "message": "..."}` |
| Error interno del modelo | 500 | `{"error": "inference_error", "message": "..."}` |

## Reglas de negocio

1. **ID único**: cada predicción genera `prediction_id` UUID v4
2. **Cacheo lazy**: el modelo se carga en memoria en el primer request
3. **Latencia**: se mide con `time.monotonic()`
4. **Timeout**: si la inferencia supera 5000ms, se aborta (503)
5. **Idempotency key**: aceptada pero no procesada (reservado Fase 2)
