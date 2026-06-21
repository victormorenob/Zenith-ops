# Design: Model Registry v1 — File-Based Catalog

## 1. Data Model

### `ModelMetadata` (Pydantic model)

```python
class ModelMetadata(BaseModel):
    model_id: str
    name: str
    version: str          # semver: "1.0.0"
    framework: str        # "sklearn", "pytorch", etc.
    description: str = ""
    created_at: datetime
    metrics: dict[str, float] = {}
    status: Literal["active", "staging", "archived"] = "active"
    tags: list[str] = []
    input_schema: ModelIOSchema | None = None
    output_schema: ModelIOSchema | None = None

class ModelIOSchema(BaseModel):
    type: str                         # "class", "regression", "array"
    features: dict[str, str] | None = None   # feature_name -> dtype
    classes: list[str] | None = None         # for classification

class ModelSummary(BaseModel):
    """Resumen para GET /v1/models — sin metrics/schemas."""
    model_id: str
    name: str
    latest_version: str
    framework: str
    status: str
    created_at: datetime
    tags: list[str]
```

### `meta.json` on disk

```json
{
  "model_id": "iris-classifier",
  "name": "Iris Classifier",
  "version": "1.0.0",
  "framework": "sklearn",
  "description": "Clasificador para especies de Iris",
  "created_at": "2026-06-15T12:00:00Z",
  "metrics": {"accuracy": 0.97, "f1_score": 0.96},
  "status": "active",
  "tags": ["classification", "iris"],
  "input_schema": {
    "type": "class",
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

## 2. Directory Structure

```
models/
  <model_id>/
    <version>/
      model.joblib       ← serialized model artifact
      meta.json          ← metadata (parsed as ModelMetadata)
```

Example:

```
models/
  iris-classifier/
    1.0.0/
      model.joblib
      meta.json
```

A model_id can have multiple version dirs. The **highest semver** with `status == "active"` is the default.

## 3. Registry Service

### `ModelRegistryService`

```python
@dataclass
class ModelRegistryService:
    models_dir: Path = Path("models")
    _catalog: dict[str, dict[str, ModelMetadata]] | None = None
    # ^ {model_id: {version: ModelMetadata}}
```

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `scan()` | `None` | Walks `models/`, parses all `meta.json`, builds `_catalog`. Called once at startup |
| `list_models()` | `list[ModelSummary]` | Latest active version per model_id |
| `get_model(model_id)` | `ModelMetadata` | Latest active version for given model_id, or raises `ModelNotFoundError` |
| `resolve_path(model_id)` | `Path` | Returns `models_dir / model_id / version / model.joblib` |

**Behavior:**
- `scan()` is called once at module init
- If a `meta.json` is missing/corrupt, log a warning and skip that version — do NOT crash
- If a model_id has no `meta.json` at all, it's not listed
- `get_model()` reuses the existing `ModelNotFoundError` exception

### Scanning logic (pseudocode)

```
scan():
    _catalog = {}
    for model_dir in models_dir.iterdir():
        if not model_dir.is_dir(): continue
        model_id = model_dir.name
        for version_dir in sorted(model_dir.iterdir(), by=semver, desc):
            meta_path = version_dir / "meta.json"
            if not meta_path.exists(): continue
            try:
                metadata = ModelMetadata.model_validate_json(meta_path.read_text())
                _catalog.setdefault(model_id, {})[version_dir.name] = metadata
            except Exception:
                logger.warning("Skipping corrupt meta.json", path=meta_path)
```

**Key detail:** version dirs sorted by **semver descending**, so the first entry is the latest. No need for symlinks or "current" pointers in v1.

## 4. API Layer

### `api/v1/models.py`

Two read-only endpoints using the `ModelRegistryService` singleton:

```
GET /v1/models         → router.list_models()
GET /v1/models/{id}    → router.get_model(model_id)
```

Both are async. They call the registry service (which is synchronous, no DB calls).

### Router registration

In `__init__.py`, add `from zenith_ops.api.v1.models import router as models_router` and `app.include_router(models_router)`.

## 5. Integration with InferenceService

### Current `_load_model`:

```python
@classmethod
def _load_model(cls, model_id: str) -> Any:
    return joblib.load(f"models/{model_id}.joblib")
```

### New `_load_model`:

```python
@classmethod
def _load_model(cls, model_id: str) -> Any:
    registry = ModelRegistryService.get_instance()
    model_path = registry.resolve_path(model_id)  # raises ModelNotFoundError if not in registry
    try:
        return joblib.load(model_path)
    except FileNotFoundError:
        raise ModelNotFoundError(model_id) from None
```

**Key change:** the registry's `get_model()` validates the model exists (404 path), then `resolve_path()` gives the actual file location. This decouples location logic from loading logic.

## 6. Seed Data

Create `models/iris-classifier/1.0.0/` with:
- `model.joblib`: the current `DummyIrisClassifier` pickled via joblib
- `meta.json`: matching metadata

Need a one-time script or a conftest fixture that generates the seed model. For simplicity, do it in a conftest fixture for tests and provide a script to generate it for local dev.

## 7. Testing Strategy

### Unit: `tests/unit/test_model_registry.py`

| Test | What it verifies |
|------|------------------|
| `test_scan_loads_metadata` | scan() correctly parses meta.json into catalog |
| `test_list_models_returns_summary` | list_models() returns ModelSummary (no full metadata) |
| `test_get_model_returns_detail` | get_model() returns full ModelMetadata |
| `test_get_model_unknown_raises_404` | unknown model_id raises ModelNotFoundError |
| `test_corrupt_meta_skipped` | bad meta.json logs warning, doesn't crash |
| `test_empty_dir_returns_empty` | no models/ or empty dir returns [] |
| `test_resolve_path_returns_correct_path` | path resolution points to right file |

### Integration: `tests/integration/test_model_registry.py`

| Test | What it verifies |
|------|------------------|
| `test_list_models_endpoint` | GET /v1/models returns 200 with list |
| `test_get_model_endpoint` | GET /v1/models/iris-classifier returns 200 with detail |
| `test_get_model_unknown_returns_404` | GET /v1/models/unknown returns 404 |
| `test_predict_still_works` | POST /v1/predict with seeded model returns 200 |

### Test fixtures

A `conftest.py` at `tests/` (or in each test directory) creates a temporary `models/` dir with a seeded `iris-classifier/1.0.0/` to avoid polluting the real directory.

## 8. Error Handling

| Scenario | Handling |
|----------|----------|
| `models/` dir missing | `scan()` logs info, catalog stays empty, endpoints return `[]` |
| `meta.json` missing for a version | Version is skipped silently |
| `meta.json` corrupt (invalid JSON) | Warning logged, version skipped |
| Model file missing but meta exists | `resolve_path()` returns the path, `joblib.load()` raises FileNotFoundError → `ModelNotFoundError` |
| Multiple versions, none active | `get_model()` returns latest regardless of status in v1 (status filtering deferred) |

## 9. Migration Path

**No migration needed.** The old path `models/{model_id}.joblib` was never used with real files — only the `DummyIrisClassifier` in tests. The new structure is additive.

## 10. Sequence Diagrams

### Startup scan

```
App starts
  → configure_logging()
  → ModelRegistryService.get_instance().scan()
    → walk models/
    → parse meta.json files
    → build in-memory catalog
  → FastAPI app created
  → ready to serve
```

### Predict request (with registry)

```
POST /v1/predict {model_id: "iris-classifier", ...}
  → InferenceService.predict(model_id, features)
    → InferenceService._get_model(model_id)
      → ModelRegistryService.get_instance().resolve_path("iris-classifier")
        → returns models/iris-classifier/1.0.0/model.joblib
      → joblib.load(path)
      → cache in _models[model_id]
    → model.predict(features)
    → return result
```
