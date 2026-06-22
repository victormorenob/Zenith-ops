# Proposal: Local Stack Funcional — Zenith-ops

## Intent

Current dev setup requires 4+ manual steps (docker compose, migrations, app start, seeding) with port mismatch between `.env.example` and `docker-compose.dev.yml`. Goal: `just start` provisions everything and gets the app running in one command.

## Scope

### In Scope
- Add `app` service to docker-compose.dev.yml with depends_on + healthcheck
- Fix `.env.example` DATABASE_URL port to match docker-compose (5433)
- Add `just seed` for idempotent model seeding; wire `just start` as migrate + seed chain
- Add PostgreSQL service container in CI so integration tests can run
- Make seed script idempotent (skip if model file exists)

### Out of Scope
- Terraform / Helm / K8s manifests (production infra deferred)
- Monitoring stack (Grafana, Prometheus)
- Cloud service emulators (Localstack)
- Multi-region or HA setups

## Capabilities

### New Capabilities
None — pure infrastructure/dev-tooling; no spec-level behavior changes.

### Modified Capabilities
None — no existing spec requirements change.

## Approach

1. **docker-compose.dev.yml**: Add `app` service with `depends_on: postgres_healthy`, healthcheck, env_file, and volume mount `./src:/app/src` for hot-reload.
2. **.env.example**: Change DATABASE_URL from port 5432 to 5433.
3. **Justfile**: Add `seed` → `uv run python scripts/generate_dummy_model.py`. Make `start` chain: infra up → migrate → seed.
4. **Seed script**: Guard with `os.path.exists()` check — skip if model already present.
5. **ci.yml**: Add postgres service container with healthcheck so integration tests have a database.
6. **Dockerfile**: No changes needed — dev compose uses it for build, mounts source for hot-reload.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `infra/docker/docker-compose.dev.yml` | Modified | Add app service |
| `.env.example` | Modified | Fix port 5432→5433 |
| `Justfile` | Modified | Add seed, chain start |
| `scripts/generate_dummy_model.py` | Modified | Add idempotency guard |
| `.github/workflows/ci.yml` | Modified | Add postgres service container |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Port 5433 conflict locally | Med | Document override in .env |
| Seed import fails inside container | Low | Test `just seed` before commit |
| CI integration tests flaky (pg not ready) | Low | GH Actions service container has native healthcheck |
| Hot-reload mount differs on macOS | Low | Compose comment notes `:cached` option |

## Rollback Plan

Each file is independently revertible via `git checkout <file>` — no data migration involved.

| File | Revert |
|------|--------|
| `infra/docker/docker-compose.dev.yml` | Remove `app` service block (7 lines) |
| `.env.example` | Restore port 5432 |
| `Justfile` | Remove seed line, restore start to bare `up -d` |
| `scripts/generate_dummy_model.py` | Remove idempotency check |
| `.github/workflows/ci.yml` | Remove services block |

## Dependencies

None — no new Python packages. `joblib` and `DummyIrisClassifier` already exist.

## Success Criteria

- [ ] `just start` from clean checkout: infra up → migrations run → model seeded → app responds on :8000
- [ ] `just seed` is idempotent (second run skips without error)
- [ ] CI integration tests pass with postgres service container
- [ ] `.env.example` connects to compose postgres without manual edit
