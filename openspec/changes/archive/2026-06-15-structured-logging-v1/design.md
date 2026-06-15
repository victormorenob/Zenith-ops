# Design: Structured Logging v1

## Technical Approach

Create an import-time module `core/logging_config.py` that configures structlog globally (dev: `ConsoleRenderer`, prod: `JSONRenderer` via `LOG_FORMAT=json`, level via `LOG_LEVEL`). Wire it into `__init__.py` **before** the `FastAPI()` call — this guarantees the pipeline is active before any request arrives. Add an `@app.middleware("http")` decorator that generates a UUID v4, attaches it to `request.state.correlation_id`, times the request, and emits a `request_completed` event with method/endpoint/status/duration_ms/correlation_id. Extend `Settings` with `LOG_LEVEL`. Tests use `structlog.testing.LogCapture` — no HTTP dependency for unit coverage.

## Architecture Decisions

| Decision | Options | Tradeoff | Choice |
|---|---|---|---|
| Config timing | Import-time vs lazy init | Import-time: always active, safe against early logs. Lazy init: testable without import side effects. | **Import-time** — app is module-level; config must run before uvicorn binds. |
| Env var source | `os.environ` vs `Settings` singleton | `Settings`: DRY, validated. `os.environ`: no circular imports, zero coupling at import time. | **`os.environ` in logging_config** — `Settings` also gets `LOG_LEVEL` for app-layer consumption, but logging_config reads env directly. |
| Middleware shape | `@app.middleware("http")` vs Starlette `BaseHTTPMiddleware` class | Decorator: ~15 lines, colocated. Class: reusable, isolate-testable. | **Decorator** — single-use, colocated in `__init__.py`. Extract later if reuse arises. |
| Log level per status | Fixed bands | INFO <400, WARNING 400–499, ERROR ≥500. | Per spec. Straightforward, no configuration needed. |
| Stdlib capture | `structlog.stdlib.recreate_defaults()` | Standard structlog recipe. One call; no config surface. | Ship default structlog approach. |

## Data Flow

```
Startup sequence:
  uvicorn → import zenith_ops → __init__ imports logging_config
                                  └─ configure_logging() called
                                     → ConsoleRenderer | JSONRenderer
                                     → stdlib capture active
                                     → global side-effect, returns None
                               → FastAPI() created
                               → middleware registered
                               → handlers + routers registered

Per request:
  Request → middleware: uuid4() → request.state.correlation_id
         → call_next(request) → router → handler → response
         → middleware: compute duration_ms
         → log at INFO|WARNING|ERROR via structlog.get_logger()
```

## File Changes

| File | Action | Description |
|---|---|---|
| `src/zenith_ops/core/logging_config.py` | Create | Import-time structlog config, env-aware renderer & level |
| `src/zenith_ops/core/settings.py` | Modify | Add `LOG_LEVEL: str = "INFO"` |
| `src/zenith_ops/__init__.py` | Modify | Add `configure_logging()` call + `@app.middleware("http")` |
| `tests/unit/test_logging.py` | Create | Log capture, UUID format, JSON renderer tests |

## Interfaces / Contracts

```python
# logging_config.py — no classes, pure side-effect function
def configure_logging() -> None: ...

# __init__.py middleware contract
# request.state.correlation_id: str  (UUID v4 hex string)
# Log event "request_completed" with keys:
#   method, endpoint, status, duration_ms, correlation_id
```

The `configure_logging()` function reads `LOG_FORMAT` and `LOG_LEVEL` from `os.environ` — these are NOT imported from `Settings` to keep the config module dependency-free at import time.

## Testing Strategy

| Layer | What | How |
|---|---|---|
| Unit | Log field shape and levels | `structlog.testing.LogCapture` — assert 5 fields present after middleware run |
| Unit | UUID v4 validity | Regex `^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$` |
| Unit | JSONRenderer env switch | `monkeypatch.setenv("LOG_FORMAT", "json")` → assert `JSONRenderer` in processor chain |
| Unit | Default log level | Assert DEBUG suppressed, INFO emitted |
| Unit | Stdlib bridge | `logging.getLogger().warning(...)` → assert captured in structlog pipeline |
| Integration | Middleware on real endpoints | `TestClient` + `LogCapture` — verify per-request log shape on `/health/live` |

No E2E needed — this is purely an observability concern, tested at unit + integration level.

## Migration / Rollout

No migration required. Entirely additive — new module + new middleware + new settings field with default. No existing code changes behavior.

## Open Questions

None. All decisions are scoped by ADR-001, the spec, and the proposal constraints.
