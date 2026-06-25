# Tasks: Phase 1 README Update

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~120–180 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Delivery strategy | single PR |

## Phase A: SDD Bundle

- [x] A.1 Create `openspec/changes/phase-1-readme/proposal.md` — intent, scope, success criteria
- [x] A.2 Create `openspec/changes/phase-1-readme/specs/README.md` — delta requirements for root README
- [x] A.3 Create `openspec/changes/phase-1-readme/tasks.md` — this file

## Phase B: README Content — Portfolio presentation

- [x] B.0 **Narrative arc** — Problem / What Zenith-ops is / What's live in production today (neutral senior-engineer tone; production URL in outcome section)
- [x] B.1 **Badges** — CI workflow badge + Python 3.12+ (verified in `.github/workflows/ci.yml` and `pyproject.toml`)
- [x] B.2 **At a glance** — bold key-value lines (Phase, Production URL, Planned); key capabilities as bullets; Phase 2 pointer
- [x] B.3 **Architecture** — mermaid diagram + brief modular-monolith text; placed before Engineering highlights
- [x] B.4 **Engineering highlights** — concrete stack and craft: async API, modular monolith, PG registry, ops/CI/CD, specs/ADRs (senior-engineer tone, not recruiter bullets)

## Phase B: README Content — Technical (retained/tightened)

- [x] B.5 **Quick start** — `uv sync`, `just setup`, `.env`, `just start`; API on `http://localhost:8081`
- [x] B.6 **Stack table** — rows confirmed accurate for Phase 1
- [x] B.7 **API endpoints table** — paths from routers; `POST /v1/test-feature` omitted (internal CI smoke only)
- [x] B.8 **Production** — base URL `http://167.233.116.195:8000`, live/ready curls, CD `main` → CI → CD
- [x] B.9 **Deployment table** — Development: Docker Compose local; Production: Hetzner VPS Docker; Phase 3: k3s planned
- [x] B.10 **Documentation links** — runbook, ADR link (also linked from Key design decisions), `/docs`
- [x] B.11 **Key design decisions** — kept; tightened intro; ADR cross-link added

## Phase C: Verification

- [x] C.1 Grep routers under `src/zenith_ops/api/v1/` and diff against README API table
- [x] C.2 Optional: `curl -sf http://167.233.116.195:8000/health/live` from operator machine (200 OK verified)
- [x] C.3 User sign-off on Phase 1 checkpoint README items (narrative arc, at-a-glance fix, Architecture reordered before Engineering highlights)
