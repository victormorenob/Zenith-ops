# Proposal: Structured Logging v1

## Intent

Replace the current unconfigured Python logger with structured, correlation-ID-tracked logs per ADR-001. Every request must produce a machine-parseable log line with method, endpoint, status, duration_ms, and a UUIDv4 correlation_id — debuggable in dev, shipable to log aggregators in production.

## Scope

### In Scope
- Centralized structlog config module (`core/logging_config.py`)
- Request middleware: UUIDv4 correlation ID → `request.state`, auto-log on completion
- Tests: log field shape, UUID format, JSON renderer toggle via `LOG_FORMAT=json`

### Out of Scope
- PII/data redaction (deferred)
- Log file rotation (handled by deploy infra)
- Global error logging middleware (separate change)
- Unit tests for prediction logic

## Capabilities

### New Capabilities
- `logging`: structured logging config, per-request correlation IDs, env-aware format switching (console vs JSON)

### Modified Capabilities
- None

## Approach

1. **`core/logging_config.py`**: configure structlog with `ConsoleRenderer` (dev) or `JSONRenderer` (prod via `LOG_FORMAT=json`), capture stdlib logs from third-party libs, expose `structlog.get_logger(__name__)` per module
2. **Middleware**: `@app.middleware("http")` — generate UUIDv4, attach to `request.state.correlation_id`, time the request, log `request_completed` with all fields on response
3. **Tests**: capture log output with `structlog.testing.LogCapture`, assert field presence, check UUID format, verify JSON output under env var

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/zenith_ops/core/logging_config.py` | New | Centralized structlog setup |
| `src/zenith_ops/__init__.py` | Modified | Wire middleware + call `configure_logging()` |
| `tests/` | New | Log structure, UUID, format tests |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Middleware logs before config loaded | Low | Configure at module import time before app factory |
| Third-party log noise | Low | Tune `structlog.stdlib.filter_by_level` per logger |

## Rollback Plan

1. Revert `core/logging_config.py` creation
2. Remove middleware lines from `__init__.py`
3. `git revert` the change commit — entire change is additive, no schema migrations

## Dependencies

- `structlog>=25.5.0` (already in `pyproject.toml`)
- ADR-001 (approved)

## Success Criteria

- [ ] Log line on every request contains: method, endpoint, status, duration_ms, correlation_id
- [ ] correlation_id is valid UUID v4
- [ ] `LOG_FORMAT=json` switches to JSONRenderer
- [ ] All existing tests pass
- [ ] mypy strict passes on new code
