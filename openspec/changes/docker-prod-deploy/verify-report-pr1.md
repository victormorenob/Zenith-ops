# Verification Report — docker-prod-deploy PR1 (Phase A)

**Change:** `docker-prod-deploy`  
**Scope:** PR1 / Phase A only  
**Mode:** Hybrid (openspec file + Engram `sdd/docker-prod-deploy/verify-pr1`)  
**Date:** 2026-06-24  
**Verifier:** sdd-verify executor

---

## Executive Verdict

**PASS WITH WARNINGS** — All Phase A tasks complete; PR1 structural requirements compliant; `docker compose config` passes; 146 pytest green. Runtime Docker stack scenarios remain UNTESTED (deferred to Phase D / VPS smoke).

---

## Task Completeness (PR1 scope)

| Phase | Tasks | Status | Notes |
|-------|-------|--------|-------|
| A — Production Docker Foundation | A.1–A.4 | **4/4 complete** | All checked in `tasks.md` |
| B — Continuous Deployment | B.1–B.3 | **Deferred** | Out of PR1 scope |
| C — Operator Surface & Documentation | C.1–C.5 | **Deferred** | Out of PR1 scope |
| D — Verification | D.1–D.3 | **Deferred** | Manual smoke + scenario confirmation |

---

## Execution Evidence

| Command | Exit | Result |
|---------|------|--------|
| `docker compose -f infra/docker/docker-compose.prod.yml config` | 0 | Valid compose; services `migrate`, `app` only |
| `docker compose -f infra/docker/docker-compose.prod.yml config --services` | 0 | `migrate`, `app` (no `postgres`) |
| `uv run pytest tests/ -q` | 0 | 146 passed, 3 warnings |
| `uv run ruff check infra/docker/` | 0 | No Python files (N/A) |
| `docker build -f infra/docker/migrate.Dockerfile …` | — | **Not run** (registry unreachable in verify environment) |

---

## Spec Compliance Matrix (PR1 requirements only)

### Requirement: Production Compose Stack

| Scenario / MUST | Status | Evidence |
|-----------------|--------|----------|
| File `infra/docker/docker-compose.prod.yml` exists | **COMPLIANT** | File present |
| Exactly two services: `migrate` + `app` | **COMPLIANT** | `config --services` → migrate, app |
| No PostgreSQL service/image | **COMPLIANT** | No `postgres` refs; dev compose unchanged |
| `app` publishes port `8000` | **COMPLIANT** | `ports: "8000:8000"` |
| `app` `extra_hosts: host.docker.internal:host-gateway` | **COMPLIANT** | Present on `app` (also on `migrate` for DB access) |
| `app` depends_on `migrate: service_completed_successfully` | **COMPLIANT** | Validated in rendered config |
| `app` connects via `host.docker.internal:5432` | **PARTIAL** | `extra_hosts` enables gateway; `DATABASE_URL` supplied via `env_file: .env` (operator contract in `.env.example` deferred to Phase C) |
| **Scenario:** Migrate runs before app starts | **PARTIAL** | Dependency declared; no runtime `compose up` against host PG |
| **Scenario:** App does not start when migrate fails | **PARTIAL** | Compose semantics correct; no failure-injection test |
| **Scenario:** No PostgreSQL container in prod compose | **COMPLIANT** | Static + `config` inspection |

### Requirement: Migrate Job Image

| Scenario / MUST | Status | Evidence |
|-----------------|--------|----------|
| File `infra/docker/migrate.Dockerfile` exists | **COMPLIANT** | File present |
| CMD `alembic upgrade head` | **COMPLIANT** | `CMD ["alembic", "upgrade", "head"]` |
| No seed / `generate_dummy_model.py` | **COMPLIANT** | Only alembic.ini, migrations, minimal src; comment documents intent |
| Slim runtime, `uv sync --frozen --no-dev` | **COMPLIANT** | Multi-stage builder pattern |
| Non-root user | **COMPLIANT** | `USER app` (uid/gid 1000) |
| **Scenario:** Migrate applies schema without seeding | **PARTIAL** | Dockerfile correct; no runtime PG test |
| **Scenario:** Migrate failure is observable | **PARTIAL** | Alembic exits non-zero on failure by default; not exercised |

### Requirement: Production App Container (partial — no Justfile/CD)

| Scenario / MUST | Status | Evidence |
|-----------------|--------|----------|
| `app` uses `infra/docker/Dockerfile` | **COMPLIANT** | `build.dockerfile: infra/docker/Dockerfile` |
| `EXPOSE 8000` | **COMPLIANT** | Line 32 in Dockerfile |
| `HEALTHCHECK` → `GET /health/live` | **COMPLIANT** | `curl -f http://localhost:8000/health/live`; interval 30s, start-period 40s, timeout 5s, retries 3 |
| `curl` available in runtime | **COMPLIANT** | `apt-get install curl` in runtime stage |
| `LOG_FORMAT=json` in prod compose | **COMPLIANT** | `environment: LOG_FORMAT: json` on `app` |
| **Scenario:** Liveness healthcheck passes | **PARTIAL** | HEALTHCHECK defined; `/health/live` covered by unit tests (`tests/unit/test_health.py`) but not Docker HEALTHCHECK at runtime |
| **Scenario:** Production logs are JSON | **PARTIAL** | Env var set in compose; structlog JSON emission not verified inside running container |

---

## Deferred Requirements (out of PR1 scope)

| Requirement | Phase | Status |
|-------------|-------|--------|
| Production Environment Contract (`.env.example` prod section) | C | **DEFERRED** |
| Justfile `build-prod` / `up-prod` | C | **DEFERRED** |
| Continuous Deployment Pipeline (`cd.yml`) | B | **DEFERRED** |
| Production Runbook (`deploy-production.md`) | C | **DEFERRED** |

---

## Design Coherence (PR1 files)

| Design decision | Implementation | Match |
|-----------------|----------------|-------|
| Host PG via `host.docker.internal` + `host-gateway` | `extra_hosts` on migrate + app | Yes |
| One-shot migrate, no seed in migrate image | `restart: "no"`, migrate Dockerfile | Yes |
| Reuse app Dockerfile with HEALTHCHECK | Single Dockerfile modified | Yes |
| `LOG_FORMAT=json` in compose only | App service environment | Yes |
| GHCR image refs with `IMAGE_TAG` | `ghcr.io/${GHCR_OWNER:-local}/zenith-ops-{app,migrate}:${IMAGE_TAG:-latest}` | Yes |
| Models volume mount for inference | `../../models:/app/models` on app | Yes (design VPS layout) |

---

## Issues

### CRITICAL

None for PR1 structural scope.

### WARNING

1. **UNTESTED runtime scenarios** — Migrate-before-app ordering, migrate-failure blocking, container HEALTHCHECK, and JSON log emission require `compose up` against host PostgreSQL (Phase D.1/D.2).
2. **`DATABASE_URL` operator contract** — Prod compose relies on VPS `.env`; `.env.example` production section not yet updated (Phase C.1).
3. **Docker image build not verified** — `docker build` could not pull base image in verify environment; recommend CI or local build smoke before VPS deploy.

### SUGGESTION

1. Add optional CI step: `docker compose -f infra/docker/docker-compose.prod.yml config` (design already recommends).
2. Consider a lightweight compose validation test in `tests/` that parses prod YAML for required keys (future PR).

---

## Files Verified

| File | Action | Result |
|------|--------|--------|
| `infra/docker/migrate.Dockerfile` | Create | Compliant |
| `infra/docker/docker-compose.prod.yml` | Create | Compliant |
| `infra/docker/Dockerfile` | Modify (HEALTHCHECK + curl) | Compliant |

---

## Final Verdict

**PASS WITH WARNINGS** — PR1 is ready for review/merge as the Docker infrastructure slice. Proceed to PR2 (Phase B/C) for CD, operator surface, and runbook. Complete Phase D manual smoke before declaring full change production-ready.
