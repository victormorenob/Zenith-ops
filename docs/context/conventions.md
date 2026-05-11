# Convenciones del proyecto (Zenith-ops)

## Módulos típicos

- `src/core/<feature>.py` — lógica pura, sin FastAPI
- `src/api/v1/<router>.py` — endpoints; dependencias con `Depends()`
- `src/db/<repositorio>.py` — modelos y consultas SQLAlchemy async
- `tests/unit/test_<feature>.py`
- `tests/integration/test_<endpoint_o_flujo>.py`

(El paquete Python puede anidarse bajo `src/zenith_ops/` mientras se alinea la carpeta física con esta convención.)

## Inyección de dependencias (FastAPI)

```python
async def predict(
    request: PredictionRequest,
    model_service: ModelService = Depends(get_model_service),
    db: AsyncSession = Depends(get_db),
) -> PredictionResponse:
    """Ejemplo ilustrativo: nombres reales vienen de la Spec."""
    ...
```

## Jerarquía de errores

```
MLOpsException
├── ModelNotFoundError      → 404
├── ModelNotReadyError      → 503
├── InvalidInputError       → 422
└── InferenceError          → 500
```

Los routers traducen estas excepciones a HTTP; no capturar `Exception` genérico.

## Logging

Usar `structlog` con `event`, `correlation_id` y campos de negocio acordados en la Spec.

```python
log.info(
    "prediction_completed",
    correlation_id=correlation_id,
    model_id=model_id,
    latency_ms=elapsed_ms,
)
```

## Errores HTTP (cuerpo)

```json
{"error": "codigo_snake_case", "message": "descripción legible", "detail": {}}
```
