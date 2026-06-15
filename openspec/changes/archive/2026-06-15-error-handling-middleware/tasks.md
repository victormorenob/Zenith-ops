# Tasks: Error Handling Middleware

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~115 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | single-pr |
| Chain strategy | size-exception |

Decision needed before apply: Yes
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Low

## Phase 1: RED — Write Failing Tests

- [x] 1.1 Create `tests/integration/test_error_handling.py` — test X-Correlation-ID present on success (GET /health/live)
- [x] 1.2 Add test: X-Correlation-ID present on domain error response (POST /v1/predict unknown model → 404)
- [x] 1.3 Add test: unhandled `RuntimeError` in test endpoint returns 500 with `{"error":"internal_error","message":"An unexpected error occurred"}`
- [x] 1.4 Add test: domain handlers (`ModelNotFoundError`→404, `InferenceTimeoutError`→503, `InferenceError`→500) still take precedence over catch-all

## Phase 2: GREEN — Implement Features

- [x] 2.1 In `log_requests` middleware, add `response.headers["X-Correlation-ID"] = correlation_id` before `return response`
- [x] 2.2 Add `catch_all` middleware after `log_requests` — wrap `call_next` in try/except Exception, log via structlog with `exc_info=True`, return `JSONResponse(status_code=500, content={"error":"internal_error","message":"An unexpected error occurred"})`

## Phase 3: REFACTOR — Verify

- [x] 3.1 Run full test suite (`uv run pytest tests/ --cov=src --cov-report=term-missing -v`), make all tests pass
- [x] 3.2 Run lint + type check (`uv run ruff check src/ tests/ && uv run mypy src/`)
