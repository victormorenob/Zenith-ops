# Proposal: Production Docker Deployment

## Intent

Zenith-ops needs a VPS production path before Phase 3 k3s (DDD-001). Dev compose only today. Deliver host PG + containerized app/migrate and CD from `main`.

## Scope

### In Scope
- `infra/docker/docker-compose.prod.yml` — migrate (one-shot) + app
- `infra/docker/migrate.Dockerfile` — Alembic only, no seed
- `infra/docker/Dockerfile` prod tweaks — HEALTHCHECK `/health/live`, port 8000, `LOG_FORMAT=json`
- `.github/workflows/cd.yml` — GHCR build/push + SSH deploy on `main`
- `.env.example` prod section, `Justfile` `build-prod`/`up-prod`
- `docs/runbooks/deploy-production.md`, ADR-009 (host PG, Docker app)

### Out of Scope
- k8s, Helm, Terraform, Fly.io; PG in Docker for prod
- Observability (Phase 2), HA, multi-region
- TLS/reverse proxy (optional runbook notes only)

## Capabilities

### New Capabilities
- `deploy`: Prod compose, migrate job, CD pipeline, VPS runbook, prod env contract

### Modified Capabilities
- None — `health` and `logging` already define probes and `LOG_FORMAT=json`; wiring only

## Approach

Host PostgreSQL 16 on VPS via `apt`. App uses `host.docker.internal:5432` with `extra_hosts: host-gateway`. Compose: migrate runs `alembic upgrade head` then exits; app depends on migrate, exposes 8000. Reuse `Dockerfile`; new `migrate.Dockerfile`. CD: build/push GHCR, SSH `pull && up -d`. Secrets in VPS `.env`; deploy keys in GitHub Secrets.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `infra/docker/docker-compose.prod.yml` | New | Prod migrate + app |
| `infra/docker/migrate.Dockerfile` | New | Alembic-only image |
| `infra/docker/Dockerfile` | Modified | HEALTHCHECK, prod defaults |
| `.github/workflows/cd.yml` | New | GHCR + SSH deploy |
| `.env.example`, `Justfile` | Modified | Prod targets and vars |
| `docs/runbooks/deploy-production.md` | New | Operator runbook |
| `docs/adr/ADR-009-postgres-host-docker-app.md` | New | ADR |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| `host.docker.internal` gaps | Low | `extra_hosts: host-gateway` |
| Migrate fails, stale schema | Med | `depends_on: completed_successfully`; fail CD on non-zero exit |
| SSH deploy drift | Med | Pin image SHA tags; runbook rollback |
| Host PG misconfig | Med | Runbook: `pg_hba.conf`, `listen_addresses` |

## Rollback Plan

1. **App** — Pull previous image tag; `up -d app` on VPS.
2. **Schema** — `alembic downgrade -1` via migrate container; restore PG backup if needed.
3. **CD** — Revert `main` commit; redeploy last known-good SHA.
4. **Full** — Stop compose; restore host PG snapshot; redeploy prior images.

## Dependencies

- VPS: Docker + Compose v2, host PostgreSQL 16
- GitHub Secrets: VPS SSH, GHCR token (if private)
- Health (SPEC-002) and logging (SPEC-005) specs

## Success Criteria

- [ ] Prod compose: migrate then app on host PG
- [ ] Health endpoints 200 when PG reachable
- [ ] CD deploys on `main`; runbook covers cold-start VPS
