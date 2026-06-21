# SPEC-002: Model Registry v1 — File-Based Catalog

**Estado:** Implementado
**Fase:** 1
**Objetivo:** 1.1

---

## Contexto

Actualmente los modelos se resuelven con `joblib.load(f"models/{model_id}.joblib")` — un path plano sin metadata, versionado, ni posibilidad de descubrimiento. No hay forma de preguntarle al sistema "qué modelos tenés?" ni "qué versión está activa?".

Un Model Registry es el estándar de la industria (MLflow, Sagemaker, ML Metadata) y resuelve:
- **Descubrimiento**: listar modelos disponibles con sus metadatos
- **Versionado**: múltiples versiones del mismo modelo con promoción (active/staging/archived)
- **Auto-documentación**: input_schema y output_schema le dicen al cliente cómo usar el modelo
- ** trazabilidad**: metrics, framework, created_at para auditoría

---

## Contrato

### GET /v1/models

Lista todos los modelos registrados, mostrando la **última versión** de cada uno.

**Método:** GET
**Endpoint:** `/v1/models`

**Response (200):**

```json
{
  "models": [
    {
      "model_id": "iris-classifier",
      "name": "Iris Classifier",
      "latest_version": "1.0.0",
      "framework": "sklearn",
      "status": "active",
      "created_at": "2026-06-15T12:00:00Z",
      "tags": ["classification", "iris", "multiclass"]
    }
  ]
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `models` | `array` | Lista de modelos, cada uno representa la última versión |

### GET /v1/models/{model_id}

Devuelve el detalle completo del modelo (última versión activa).

**Método:** GET
**Endpoint:** `/v1/models/{model_id}`

**Response (200):**

```json
{
  "model_id": "iris-classifier",
  "name": "Iris Classifier",
  "version": "1.0.0",
  "framework": "sklearn",
  "description": "Clasificador para especies de Iris (setosa, versicolor, virginica)",
  "created_at": "2026-06-15T12:00:00Z",
  "metrics": {
    "accuracy": 0.97,
    "f1_score": 0.96
  },
  "status": "active",
  "tags": ["classification", "iris", "multiclass"],
  "input_schema": {
    "features": {
      "sepal_length": "float",
      "sepal_width": "float",
      "petal_length": "float",
      "petal_width": "float"
    }
  },
  "output_schema": {
    "type": "class",
    "classes": ["setosa", "versicolor", "virginica"]
  }
}
```

### Errores

| Caso | Código | Respuesta |
|------|--------|-----------|
| `model_id` no existe | 404 | `{"error": "model_not_found", "message": "No model found with id: unknown-model"}` |
| Directorio `models/` no existe o vacío | 200 | `{"models": []}` (lista vacía, no error) |

---

## Reglas de negocio

1. **Última versión**: los endpoints de listado y detalle exponen siempre la última versión (semver) cuyo status sea `active`
2. **Caché en startup**: el registry escanea `models/` una vez al arrancar la aplicación. Los cambios en disco requieren reinicio para reflejarse
3. **Graceful degradation**: si un `meta.json` está corrupto o falta, se salta ese modelo y se loguea un warning — no se cae el startup
4. **Path resolution**: `InferenceService` consulta al registry el path absoluto del artifact en vez del hardcoded `models/{model_id}.joblib`
5. **Doble estrategia de singleton**: la API usa `get_registry()` (module-level con `Depends`), mientras que `InferenceService` usa `cls._registry` (class-level attribute con lazy init). Ambos apuntan al mismo `FileBasedModelRegistry`, pero la separación permite inyectar un registry distinto en tests sin afectar la API
6. **Backward compatibility**: `model_id` sigue siendo la clave de identificación. El predict endpoint no cambia su contrato

---

## Estructura de archivos propuesta

```
models/
  iris-classifier/
    1.0.0/
      model.joblib
      meta.json

src/zenith_ops/
├── api/v1/
│   ├── models.py               # NUEVO: GET /v1/models, GET /v1/models/{id} con Depends(get_registry)
│   └── predict.py              # Sin cambios funcionales
├── core/
│   ├── model_registry.py       # NUEVO: ModelMetadata, ModelSummary, ModelIOSchema, ModelRegistry (Protocol), FileBasedModelRegistry
│   └── exceptions.py           # MODIFICADO: ModelNotFoundError (ya existía)
├── services/
│   └── predictor.py            # MODIFICADO: _load_model usa cls._registry en vez de path hardcodeado
└── __init__.py                 # MODIFICADO: incluido models_router

tests/
├── unit/
│   ├── test_model_registry.py  # NUEVO: ~14 tests del registry (scan, list, get, resolve, latest_active, etc.)
│   └── test_inference_service.py  # MODIFICADO: TestModelInRegistry (test_model_in_registry, test_model_not_in_registry)
└── integration/
    └── test_model_registry.py  # NUEVO: tests de endpoints con TestClient
```

---

## Criterios de aceptación

- [x] `GET /v1/models` con modelos registrados → 200 con lista de modelos
- [x] `GET /v1/models` sin modelos → 200 con `{"models": []}`
- [x] `GET /v1/models/iris-classifier` → 200 con metadata completa
- [x] `GET /v1/models/unknown-model` → 404
- [x] `POST /v1/predict` con model_id existente → 200 (backward compat)
- [x] `POST /v1/predict` con model_id que no existe en registry → 404
- [x] meta.json corrupto no rompe el startup
- [x] `uv run pytest` → verde (80 tests)
- [ ] `uv run mypy src/` → 0 errores
- [ ] Cobertura > 70%

---

## Fuera de scope (Phase 1)

- Endpoint POST para registrar modelos
- Version listing (`GET /v1/models/{model_id}/versions`)
- Status management (promover/archivar versiones)
- Base de datos como backend
- Autenticación en endpoints del registry
- Validación de features contra `input_schema`
