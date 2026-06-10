# SPEC-001: Prediction Endpoint

**Estado:** Borrador
**Fase:** 1
**Objetivo:** 1.1

---

## Contexto

Endpoint para servir predicciones de un modelo de Machine Learning registrado.
El sistema recibe datos numéricos preprocesados (features), los pasa por un modelo
cargado en memoria, y devuelve el resultado de la inferencia junto con metadatos
de la ejecución.

Este endpoint es el núcleo del sistema y el primer ladrillo sobre el que se
construirán el monitoreo (Fase 2) y el reentrenamiento automático (Fase 3).

---

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

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `model_id` | `string` | Sí | Nombre del modelo a usar. Se mapea a un archivo `.joblib` en `models/` |
| `features` | `dict[str, float]` | Sí | Features numéricas preprocesadas. Debe contener al menos una feature |
| `idempotency_key` | `string \| null` | No | Reservado para idempotencia en Fase 2. Si se envía, se almacena pero no se procesa |

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

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `prediction_id` | `UUID` | Identificador único generado para esta predicción |
| `model_id` | `string` | Mismo valor que el recibido en la request |
| `result` | `float \| list[float]` | Resultado de la inferencia. Tipo concreto según `result_type` |
| `result_type` | `enum` | Tipo del resultado: `scalar`, `class`, `array` |
| `latency_ms` | `float` | Tiempo de inferencia en milisegundos |

### Errores

| Caso | Código | Respuesta |
|------|--------|-----------|
| `model_id` no encontrado | 404 | `{"error": "model_not_found", "message": "No model found with id: iris-classifier"}` |
| `features` con formato inválido | 422 | Error de validación Pydantic con campo específico |
| Inferencia supera el timeout | 503 | `{"error": "inference_timeout", "message": "Inference took longer than 5000ms"}` |
| Error interno del modelo | 500 | `{"error": "inference_error", "message": "Model failed during inference"}` |

---

## Reglas de negocio

1. **ID único**: cada predicción genera un `prediction_id` UUID v4, incluso con los mismos datos de entrada
2. **Cacheo lazy**: el modelo se carga en memoria en el primer request que lo solicita y queda cacheadopara los siguientes. No se carga al arrancar la aplicación
3. **Latencia**: se mide con `time.monotonic()` desde que se recibe la request hasta que se devuelve la respuesta
4. **Timeout**: si la inferencia supera los 5000ms, se aborta y devuelve 503
5. **Idempotency key**: se acepta en el contrato pero no se procesa. Reservado para Fase 2

---

## Estructura de archivos propuesta

```
src/zenith_ops/
├── api/v1/predict.py           # Router con el endpoint
├── core/
│   ├── inference_service.py    # Lógica de carga y predicción
│   └── exceptions.py           # Excepciones personalizadas
tests/
├── unit/
│   └── test_inference_service.py
└── integration/
    └── test_predict_endpoint.py
models/
└── iris-classifier.joblib      # Modelo dummy para pruebas
```

---

## Criterios de aceptación

- [ ] `POST /v1/predict` con modelo existente y features válidas → 200 con `prediction_id`, `result`, `result_type`, `latency_ms`
- [ ] `POST /v1/predict` con `model_id` que no existe → 404
- [ ] `POST /v1/predict` con features en formato incorrecto → 422
- [ ] `POST /v1/predict` con modelo que falla al inferir → 500
- [ ] Segunda request al mismo modelo responde más rápido que la primera (verifica caché)
- [ ] Latencia < 200ms en modelo Iris después del primer request (caché caliente)
- [ ] `uv run pytest` → verde
- [ ] `uv run mypy src/` → 0 errores
- [ ] Cobertura > 70%

---

## Fuera de scope (Fase 1)

- Base de datos para persistir modelos (Objetivo 1.2)
- Idempotencia real (reservado para Fase 2)
- Métricas Prometheus (Objetivo 2.2)
- Autenticación
- Tasa de error < 1% (requiere Prometheus, Objetivo 2.2)
- Throughput 100 ppm (requiere Prometheus, Objetivo 2.2)
