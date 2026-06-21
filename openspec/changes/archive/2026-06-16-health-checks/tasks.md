# Tasks: SPEC-002 — Health Checks

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~200 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | single-pr |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Low

## Phase 1: Foundation

- [x] 1.1 Create `src/zenith_ops/core/settings.py` — `Settings(BaseSettings)` with `DATABASE_URL: PostgresDsn` from env, tagged `[health]`
- [x] 1.2 Add `get_version()` helper to `health.py` using `importlib.metadata.version("zenith-ops")`, cached at module level

## Phase 2: Health Endpoints (TDD)

- [x] 2.1 **RED** — Write unit tests for `GET /health/live`: status 200, version matches pyproject.toml, timestamp is ISO 8601 UTC, zero I/O (mock all external calls)
- [x] 2.2 **GREEN** — Refactor `health.py`: remove `/healthy`, add `APIRouter(prefix="/health", tags=["health"])`, implement `GET /live` returning `{status, version, timestamp}`
- [x] 2.3 **RED** — Write unit tests for `check_database()` (async ping returns up/down) and `check_model_cache()` (True/False based on InferenceService._models)
- [x] 2.4 **GREEN** — Implement `check_database()`: create async engine from `Settings.DATABASE_URL`, execute `SELECT 1`, return `"up"` or `"down"` (with proper cleanup via `engine.dispose()`)
- [x] 2.5 **GREEN** — Implement `check_model_cache()`: return `bool(InferenceService._models)`
- [x] 2.6 **RED** — Write unit tests for `GET /health/ready`: all healthy → 200 + `{status:"up", components:{database:"up", model_cached:true}}`; db down → 503; no models → 503
- [x] 2.7 **GREEN** — Implement `GET /health/ready`: run both checks concurrently with `asyncio.gather()`, return 200 if all up else 503, include full components map

## Phase 3: Integration & Cleanup

- [x] 3.1 Write integration test via TestClient: verify `/health/live` returns 200 without DB, verify `/health/ready` returns 503 when DB is unreachable
- [x] 3.2 Remove old `test_return_healthy_status` from `tests/unit/test_health.py`; remove any dead imports referencing `/healthy`
