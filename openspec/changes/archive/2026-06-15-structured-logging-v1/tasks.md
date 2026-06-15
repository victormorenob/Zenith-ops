# Tasks: Structured Logging v1

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~150-200 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | single-pr |
| Chain strategy | size-exception |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Low

## Phase 1: Foundation (TDD: RED → GREEN)

- [x] 1.1 Write test for `configure_logging()` — `tests/unit/test_logging.py`: log level default, `LogCapture` capture works, level filtering (RED)
- [x] 1.2 Create `core/logging_config.py` with `configure_logging()` — env-aware renderer (`ConsoleRenderer` / `JSONRenderer`), `LOG_LEVEL` from `os.environ`, stdlib capture (GREEN)
- [x] 1.3 Write test for `LOG_FORMAT=json` toggle — `JSONRenderer` in processor chain (RED)
- [x] 1.4 Add `LOG_LEVEL: str = "INFO"` field to `Settings` in `core/settings.py`

## Phase 2: Core Middleware (TDD: RED → GREEN)

- [x] 2.1 Write test for middleware — `tests/unit/test_logging.py`: valid UUID v4 regex, `request_completed` log has all 5 fields (RED)
- [x] 2.2 Wire `configure_logging()` call + `@app.middleware("http")` in `__init__.py` — UUID v4, `request.state.correlation_id`, duration_ms, log at INFO/WARNING/ERROR per status (GREEN)

## Phase 3: Integration & Verification

- [x] 3.1 Write integration test — `TestClient("/health/live")` + `LogCapture` to verify per-request log emission
- [x] 3.2 Run `uv run pytest tests/` — all tests pass, coverage >= 70%, ruff clean
