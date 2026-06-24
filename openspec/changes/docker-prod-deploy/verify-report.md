# Verification Report

**Change**: docker-prod-deploy (FULL scope — PR1 + PR2)  
**Version**: deploy spec v1 (7 requirements, 17 scenarios)  
**Mode**: Standard (Strict TDD inactive)  
**Verified at**: 2026-06-24  
**Workspace**: `/home/vmorenob/Zenith-ops`

---

## Executive Verdict

**PASS WITH WARNINGS** — All Phase A–C implementation tasks are complete and match the deploy spec on static inspection. Regression suite (146 tests), ruff, and mypy are green. `docker compose config` validates prod compose. Phase D runtime smoke (`just build-prod && just up-prod` against host PG) is **PARTIAL**: no host PostgreSQL reachable locally; `just build-prod` failed on Docker Hub pull (network EOF), so migrate-before-app and Docker HEALTHCHECK scenarios lack runtime evidence in this environment.

---

## Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 15 |
| Tasks complete (tasks.md checkboxes) | 12 (Phases A–C) |
| Tasks incomplete | 3 (Phase D: D.1, D.2, D.3) |
| Phase A (Docker foundation) | ✅ 4/4 |
| Phase B (CD pipeline) | ✅ 3/3 |
| Phase C (Operator surface) | ✅ 5/5 |
| Phase D (Verification) | ⚠️ 0/3 checked — evidence gathered by this verify run |

### Phase D Status

| Task | Status | Evidence |
|------|--------|----------|
| D.1 Manual smoke `just build-prod && just up-prod` | **PARTIAL** | No host PG on `:5432`/`:5433`; `just build-prod` failed pulling `python:3.12-slim` (Docker Hub EOF). VPS-only constraint documented in runbook §6. |
| D.2 Confirm spec scenarios | **PARTIAL** | Static inspection + `docker compose config`; no runtime compose-up against host PG. |
| D.3 Ruff / CI regression | **DONE** | `uv run ruff check` passed; `uv run pytest tests/ -q` → 146 passed; `uv run mypy src/` passed. |

---

## Build & Tests Execution

**Compose config**: ✅ Passed

```text
$ docker compose -f infra/docker/docker-compose.prod.yml config
# Exit 0 — services: migrate (restart: no), app (depends_on migrate completed_successfully,
# ports 8000:8000, LOG_FORMAT=json, extra_hosts host-gateway). No postgres service.
```

**Regression tests**: ✅ 146 passed / 0 failed / 3 warnings

```text
$ uv run pytest tests/ -q
146 passed, 3 warnings in 11.74s
```

**Lint**: ✅ Passed

```text
$ uv run ruff check src/ tests/
All checks passed!
```

**Type check**: ✅ Passed

```text
$ uv run mypy src/
Success: no issues found in 27 source files
```

**Production image build (D.1)**: ❌ Not completed in verify environment

```text
$ just build-prod
# Failed: Docker Hub metadata pull EOF for python:3.12-slim (network/registry)
```

**Coverage**: ➖ Not re-run for this infra change (CI threshold unchanged; no new `core/` logic).

---

## Spec Compliance Matrix

| Requirement | Scenario | Test / Evidence | Result |
|-------------|----------|-----------------|--------|
| **1. Production Compose Stack** | Migrate runs before app starts | Static: `depends_on.migrate.condition: service_completed_successfully` in `docker-compose.prod.yml`; `docker compose config` | ⚠️ PARTIAL |
| | App does not start when migrate fails | No automated or manual negative test | ❌ UNTESTED |
| | No PostgreSQL container in prod compose | `docker compose config` — no `postgres` service | ✅ COMPLIANT |
| **2. Migrate Job Image** | Migrate applies schema without seeding | Static: `migrate.Dockerfile` CMD `alembic upgrade head`; no `scripts/` copy | ⚠️ PARTIAL |
| | Migrate failure is observable | No runtime failure injection test | ❌ UNTESTED |
| **3. Production App Container** | Liveness healthcheck passes | `tests/unit/test_health.py`, `tests/integration/test_health.py` cover `/health/live` API; Dockerfile HEALTHCHECK present — Docker runtime not exercised | ⚠️ PARTIAL |
| | Production logs are JSON | `tests/unit/test_logging.py::test_json_format`; compose sets `LOG_FORMAT: json` on app | ⚠️ PARTIAL |
| **4. Production Environment Contract** | Prod DATABASE_URL targets host gateway | `.env.example` prod section uses `host.docker.internal`, `postgresql+asyncpg` | ✅ COMPLIANT |
| | Required prod variables documented | `.env.example`: ENVIRONMENT, LOG_FORMAT, LOG_LEVEL, SECRET_KEY, DATABASE_URL, GHCR_OWNER, IMAGE_TAG | ✅ COMPLIANT |
| **5. Justfile Production Targets** | build-prod builds production images | `Justfile` lines 92–93: `docker compose ... build app migrate`; build attempted, blocked by registry | ⚠️ PARTIAL |
| | up-prod starts production stack | `Justfile` line 97: `docker compose ... up -d`; not executed (no host PG) | ⚠️ PARTIAL |
| **6. Continuous Deployment Pipeline** | Main push publishes images | Static: `cd.yml` workflow_run on CI success, build-push-action, SHA + latest tags | ⚠️ PARTIAL |
| | SSH deploy updates running stack | Static: `appleboy/ssh-action`, pull → `up migrate` → `up -d app` | ⚠️ PARTIAL |
| | Failed migrate fails CD | Static: `script_stop: true`, `set -euo pipefail`, migrate before app | ⚠️ PARTIAL |
| **7. Production Runbook** | Cold-start operator can provision VPS | `docs/runbooks/deploy-production.md` §1–6 complete | ✅ COMPLIANT |
| | Runbook documents rollback | Runbook §8 (app, schema, CD, full) | ✅ COMPLIANT |
| | Health verification steps documented | Runbook §7; `/health/live` and `/health/ready` curl examples | ✅ COMPLIANT |

**Compliance summary**: 5/17 scenarios **COMPLIANT** (static or API tests); 9/17 **PARTIAL**; 3/17 **UNTESTED**; 0 **FAILING**.

> **Note**: Deploy-domain scenarios are predominantly infra/ops. Design testing strategy explicitly defers runtime proof to VPS manual smoke and `docker compose config`. Related API behavior (`/health/live`, `LOG_FORMAT=json`) is covered by existing unit/integration tests.

---

## Correctness (Static Evidence)

| Requirement | Status | Notes |
|-------------|--------|-------|
| Production Compose Stack | ✅ Implemented | `infra/docker/docker-compose.prod.yml` — migrate + app only; `host-gateway`; port 8000; `depends_on` correct |
| Migrate Job Image | ✅ Implemented | `infra/docker/migrate.Dockerfile` — slim runtime, `uv sync --frozen --no-dev`, CMD `alembic upgrade head`, no seed |
| Production App Container | ✅ Implemented | `infra/docker/Dockerfile` — EXPOSE 8000, HEALTHCHECK curl `/health/live`, curl installed |
| Production Environment Contract | ✅ Implemented | `.env.example` production section complete |
| Justfile Production Targets | ✅ Implemented | `build-prod`, `up-prod` recipes present |
| Continuous Deployment Pipeline | ✅ Implemented | `.github/workflows/cd.yml` — CI-gated workflow_run, GHCR push, SSH deploy, 15m timeout |
| Production Runbook | ✅ Implemented | `docs/runbooks/deploy-production.md` + index link; ADR-009 paths consistent |

### CD Workflow Structure Validation

| Check | Result |
|-------|--------|
| Trigger after CI on `main` | ✅ `workflow_run` workflows: [CI], branches: [main], conclusion success |
| GHCR build/push app + migrate | ✅ `docker/build-push-action@v6` for both Dockerfiles |
| Immutable SHA tags | ✅ `IMAGE_TAG: ${{ github.event.workflow_run.head_sha }}` |
| Also pushes `latest` | ✅ Second tag on each image |
| SSH deploy secrets | ✅ `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY` |
| Deploy timeout 15 min | ✅ `timeout-minutes: 15` on deploy job |
| Migrate before app | ✅ Explicit `up migrate` then `up -d app` |
| Fail on migrate non-zero | ✅ `script_stop: true` + `set -euo pipefail` |

---

## Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| Host apt PG 16, no PG in compose | ✅ Yes | No postgres service in prod compose |
| `host.docker.internal` + `host-gateway` | ✅ Yes | On both migrate and app |
| One-shot migrate, manual seed | ✅ Yes | migrate image has no seed; runbook §5 documents manual seed |
| Reuse app Dockerfile | ✅ Yes | Same `infra/docker/Dockerfile` |
| CD SHA pin + latest | ✅ Yes | `cd.yml` tags |
| `LOG_FORMAT=json` in compose | ✅ Yes | app `environment` block |
| Public GHCR (no VPS token) | ✅ Yes | Documented in runbook § intro |
| TLS out of scope | ✅ Yes | Runbook §9 optional guidance only |
| Bridge CIDR not pinned | ✅ Yes | Runbook instructs `docker network inspect bridge` |

---

## Issues Found

### CRITICAL

None — no spec MUST violated on inspection; no regression test failures.

### WARNING

1. **Phase D runtime smoke not executed** — D.1 blocked locally (no host PG; Docker Hub pull failure). Recommend VPS smoke before first production deploy.
2. **9 deploy scenarios PARTIAL, 3 UNTESTED** — No dedicated tests for compose orchestration, migrate failure blocking app, or CD workflow execution. Acceptable per design testing strategy but leaves ops risk until VPS validation.
3. **tasks.md Phase D checkboxes still open** — Implementation verify gathered evidence; orchestrator should mark D.2/D.3 complete and D.1 PARTIAL after VPS smoke.

### SUGGESTION

1. Add optional CI job: `docker compose -f infra/docker/docker-compose.prod.yml config` (already run in verify).
2. Consider integration test with compose profile mocking migrate failure (future).
3. First VPS deploy should confirm GHCR public pull without login per runbook.

---

## Verdict

**PASS WITH WARNINGS**

Implementation for PR1+PR2 is complete and spec-aligned on static review. All regression checks pass. Runtime deploy scenarios remain unproven in this environment (Phase D PARTIAL); VPS operator smoke is the recommended gate before archive.

**Next recommended**: `sdd-archive` after optional VPS smoke completes D.1; otherwise archive with documented PARTIAL runtime evidence.
