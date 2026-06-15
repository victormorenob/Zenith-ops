# Design: Error Handling Middleware

## Technical Approach

Add a catch-all HTTP middleware as the outermost layer that wraps the entire request cycle, catching any `Exception` that escapes the three existing domain exception handlers (`ModelNotFoundError`, `InferenceTimeoutError`, `InferenceError`). The existing `log_requests` middleware is extended to set `X-Correlation-ID` on every response.

The key insight: FastAPI's `@app.exception_handler` handlers fire BEFORE middleware — they catch exceptions at the route handler level and return a `JSONResponse`. That response propagates through middlewares normally (no exception thrown). The catch-all only triggers for exceptions that domain handlers don't know about (e.g., `RuntimeError`, `KeyError`, `ValueError`).

## Architecture Decisions

### Decision: Middleware Registration Order

| Option | Tradeoff | Decision |
|--------|----------|----------|
| catch-all first, log_requests second | catch-all catches @app.exception_handler responses too (wrong — those don't raise) | ❌ |
| catch-all after log_requests | catch-all wraps everything — catches exceptions that escape route AND log_requests | ✅ |
| Single middleware doing both | Couples two concerns (error handling + logging + correlation header) | ❌ |

FastAPI registers middlewares in source order. The **last registered middleware is the outermost** (wraps all previous). Placing catch-all's `@app.middleware("http")` definition after `log_requests` ensures the catch-all runs first and catches any exception that log_requests or the route handler doesn't handle.

### Decision: Exception Logging via structlog

| Option | Tradeoff | Decision |
|--------|----------|----------|
| `logger.exception(...)` | Automatic traceback capture, but bound context may vary | ✅ — use explicit `exc_info=True` with structlog |
| `print()` / `logging.exception()` | Bypasses structured pipeline | ❌ |
| Silent catch + generic log | Loses diagnostic value | ❌ |

Use `structlog.get_logger(__name__).error(..., exc_info=True)` inside the catch block. This ensures the traceback goes through the same structured pipeline as all other logs (JSON in prod, console in dev).

### Decision: X-Correlation-ID Header Location

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Set in catch-all | Guarantees header on error responses, but duplicates logic | ❌ |
| Set in log_requests | Single place, header set on ALL responses before return | ✅ |
| New dedicated middleware | Over-engineered for one header | ❌ |

Set `response.headers["X-Correlation-ID"] = correlation_id` in `log_requests` just before the `return response` line. This runs for every response (success, domain error, or catch-all error) because even on exception, the catch-all returns a `JSONResponse` that propagates back through `log_requests`.

## Data Flow

```
Request
  │
  ▼
┌─ Catch-All Middleware ──────────────────────┐
│  try: call_next(request) → response         │
│  except Exception:                          │
│    log(correlation_id, method, path, exc)   │
│    return JSON 500                          │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─ log_requests Middleware ───────────────────┐
│  correlation_id = uuid4()                   │
│  response = call_next(request)              │
│  response.headers["X-Correlation-ID"] = id  │
│  log request_completed                      │
│  return response                            │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─ @app.exception_handler ────────────────────┐
│  ModelNotFoundError → 404 JSON              │
│  InferenceTimeoutError → 503 JSON           │
│  InferenceError → 500 JSON                  │
│  (all return JSONResponse, no raise)        │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─ Route Handler ─────────────────────────────┐
│  /health/live                               │
│  POST /v1/predict                           │
│  POST /v1/predict/feature                   │
└─────────────────────────────────────────────┘

Exception paths:
  Route raises InferenceError → handler catches → JSON 500 → log_requests adds header → catch-all returns it normally
  Route raises RuntimeError  → handler misses  → escapes to catch-all → log + JSON 500 → log_requests adds header
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `src/zenith_ops/__init__.py` | Modify | Add catch-all middleware after `log_requests`; set X-Correlation-ID in `log_requests` |
| `tests/integration/test_error_handling.py` | Create | Integration tests for catch-all behavior and X-Correlation-ID header |

## Interfaces / Contracts

```python
# New middleware signature — follows same pattern as existing log_requests
@app.middleware("http")
async def catch_all(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    ...

# log_requests — one new line before return:
response.headers["X-Correlation-ID"] = correlation_id
```

**API contract for unhandled exceptions:**

```json
// Status: 500
// Headers: X-Correlation-ID: <uuid-v4>
{
  "error": "internal_error",
  "message": "An unexpected error occurred"
}
```

No stacktrace, exception message, or internal details appear in the response body.

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Integration | Unhandled RuntimeError returns JSON 500 | GIVEN a route that raises `RuntimeError`, WHEN hit via TestClient, THEN status=500, body=`{"error":"internal_error","message":"An unexpected error occurred"}` |
| Integration | Stacktrace in structlog, not in response | Use `structlog.testing.capture_logs()` — verify `exc_info` key exists in captured log, response body has no traceback |
| Integration | Domain handlers still take precedence | Hit predict with unknown model → verify 404 `model_not_found`, not catch-all 500 |
| Integration | X-Correlation-ID on every response | Verify header present and matches UUID v4 regex on 200, 404, 422, and unhandled error responses |
| Integration | Catch-all is outermost (runs first) | Inject a route that raises BEFORE `request.state.correlation_id` is set — catch-all should still catch it (correlation_id in log will be empty/fallback) |

## Migration / Rollout

No migration required. This is additive middleware with zero config changes. Deploy as part of the next PR.

## Open Questions

- [ ] What if the exception happens before `request.state.correlation_id` is assigned? The log in catch-all should handle `getattr(request.state, "correlation_id", "unassigned")` gracefully.
