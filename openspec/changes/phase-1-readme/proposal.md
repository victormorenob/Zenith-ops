# Proposal: Phase 1 README Update

## Intent

Phase 1 checkpoint requires the root README to reflect the **current** system: correct API paths, VPS Docker production (not k3s), architecture diagram, and a link to the deployed API. The existing README is stale (wrong model routes, k3s as current prod, no production URL).

## Scope

### In Scope
- Update root `README.md` (English, same tone as today)
- Brief "what Zenith-ops is" intro
- Mermaid architecture diagram: client → FastAPI → host PostgreSQL + models volume
- Quick start: `uv`, `just setup` / `just start`, `.env` from `.env.example`
- API endpoints table aligned with `src/zenith_ops/api/v1/` (e.g. `/v1/models/register`)
- Production section: `http://167.233.116.195:8000`, health `curl` examples, CD note (push `main` → CI → CD)
- Link to `docs/runbooks/deploy-production.md`
- Keep stack table if still accurate; fix Deployment table (VPS + Docker Compose, k3s as future Phase 3)

### Out of Scope
- Rewriting `docs/getting-started.md` or other docs
- New features, API changes, or infra changes
- TLS / reverse proxy setup in README (runbook only)
- Spanish translation of README

## Capabilities

### New Capabilities
- `readme`: Phase 1 onboarding surface — architecture, local quick start, API table, production URL and CD pointer

### Modified Capabilities
- None — documentation only; no runtime spec deltas for health, deploy, or registry

## Approach

Single documentation change driven by SDD: proposal + tasks + README delta spec under `openspec/changes/phase-1-readme/`, then apply `README.md`. Endpoint paths verified against live routers. Production facts taken from `docker-prod-deploy` change and VPS deploy. Local dev port documented as `8081` (dev compose) vs `8000` (prod).

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `README.md` | Modified | Phase 1 checkpoint content |
| `openspec/changes/phase-1-readme/` | New | SDD change bundle |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Production URL or port drift | Low | Cross-check runbook and `docker-compose.prod.yml` |
| API table out of date again | Med | Derive from router modules; note in tasks to re-verify on API changes |
| Dev port confusion (8081 vs 8000) | Med | State both explicitly in Quick start vs Production |

## Rollback Plan

Revert `README.md` and remove `openspec/changes/phase-1-readme/` if the change is rejected.

## Dependencies

- Phase 1 features shipped: predict, model registry (PG), health, docker-prod-deploy
- Production VPS live at `http://167.233.116.195:8000`
- `docs/runbooks/deploy-production.md` exists

## Success Criteria

- [ ] README includes Mermaid architecture diagram
- [ ] API table matches `src/zenith_ops/api/v1/` routes
- [ ] Production section with health curls and CD flow
- [ ] Deployment table shows VPS Docker Compose as current prod
- [ ] Link to deploy runbook present
- [ ] Phase 1 checkpoint item "README con diagrama y link a API desplegada" satisfied
