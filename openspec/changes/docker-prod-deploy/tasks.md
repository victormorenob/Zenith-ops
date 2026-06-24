# Tasks: Production Docker Deployment

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~380–450 |
| 400-line budget risk | Medium |
| Chained PRs recommended | Yes |
| Suggested split | PR1: Docker infra → PR2: CD + operator surface |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: Medium

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Prod compose + migrate image + app HEALTHCHECK | PR1 | `docker-compose.prod.yml`, `migrate.Dockerfile`, `Dockerfile`; `docker compose config` smoke |
| 2 | CD pipeline + operator DX + runbook | PR2 | `cd.yml`, `.env.example`, `Justfile`, `deploy-production.md`; base = PR1 branch if feature-branch-chain |

## Phase A: Production Docker Foundation

- [x] A.1 Create `infra/docker/migrate.Dockerfile` — slim runtime, `uv sync --frozen --no-dev`, copy `alembic.ini` + `src/db/migrations/` + minimal `src/`; CMD `alembic upgrade head`; no seed scripts
- [x] A.2 Create `infra/docker/docker-compose.prod.yml` — `migrate` (restart: no) + `app` only; no `postgres`; `extra_hosts: host-gateway`; `depends_on migrate: service_completed_successfully`; port `8000:8000`; `LOG_FORMAT=json` on app; `IMAGE_TAG` for GHCR refs
- [x] A.3 Modify `infra/docker/Dockerfile` — add `HEALTHCHECK` against `GET /health/live` (interval 30s, start-period 40s); ensure `curl` or `wget` available in runtime stage
- [x] A.4 Verify `docker compose -f infra/docker/docker-compose.prod.yml config` passes locally

## Phase B: Continuous Deployment

- [x] B.1 Create `.github/workflows/cd.yml` — trigger on `main` push after CI green; build/push `zenith-ops-app` and `zenith-ops-migrate` to **public** GHCR with SHA + `latest` tags
- [x] B.2 Add SSH deploy job — `appleboy/ssh-action`; secrets `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`; `timeout-minutes: 15`; pull pinned SHA, run migrate then `up -d app`
- [x] B.3 Ensure CD fails on migrate non-zero exit — workflow checks SSH/compose exit codes per spec scenario "Failed migrate fails CD"

## Phase C: Operator Surface & Documentation

- [x] C.1 Extend `.env.example` — production section: `DATABASE_URL` (`host.docker.internal`), `ENVIRONMENT=production`, `LOG_FORMAT=json`, `LOG_LEVEL`, `SECRET_KEY`, `IMAGE_TAG` docs
- [x] C.2 Add `Justfile` targets `build-prod` and `up-prod` — build app + migrate images; `docker compose -f infra/docker/docker-compose.prod.yml up -d`
- [x] C.3 Create `docs/runbooks/deploy-production.md` — cold start (PG 16 apt, `listen_addresses`, `pg_hba.conf` with bridge CIDR verification via `docker network inspect bridge`, typical `172.17.0.0/16`); Docker/Compose v2; `.env` setup; manual seed; deploy; health checks (`/health/live`, `/health/ready`); rollback; optional TLS note (Caddy/nginx, no implementation); public GHCR pull (no token) vs private PAT note
- [x] C.4 Update `docs/runbooks/index.md` — link deploy-production runbook
- [x] C.5 Verify `docs/adr/ADR-009-postgres-host-docker-app.md` references match implemented paths (update links only if drift)

## Phase D: Verification

- [ ] D.1 Manual smoke: `just build-prod && just up-prod` against host PG (or document VPS-only constraint in runbook if local host PG unavailable)
- [ ] D.2 Confirm spec scenarios: migrate-before-app, migrate-failure blocks app, no postgres service, JSON logs, HEALTHCHECK liveness
- [ ] D.3 Run `uv run ruff check` / existing CI locally — no regressions from infra-only change
