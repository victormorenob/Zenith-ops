# Zenith-ops

**ML Serving platform** — REST API for model inference, registry, and monitoring.

---

## What it does

Zenith-ops exposes ML models via a REST API. Register a model, run predictions, monitor health. Designed for production-like operation from day one: async serving, sane defaults, observability-ready.

## Quick start

```bash
pip install uv
uv sync
just start
```

The API listens on `http://localhost:8000`.

## Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Language | Python 3.12 | ML ecosystem standard |
| API | FastAPI (async) | Performance + auto-docs |
| Validation | Pydantic v2 | Runtime type safety |
| Database | PostgreSQL + asyncpg | Fit for structured metadata |
| Models | joblib + scikit-learn | Industry standard for serialisation |
| Testing | pytest | Universal Python tooling |

## Architecture (modular monolith)

```
src/
  api/v1/          — HTTP layer (routers, schemas)
  core/            — Business logic (inference, registry)
db/                — Storage models and migrations
tests/
  unit/            — No I/O, mocked dependencies
  integration/     — Real PostgreSQL connections
```

One process, clear separation. The `core/` package never imports from `api/`.

## API

```
GET  /health/live         → Liveness probe
GET  /health/ready        → Readiness probe (DB + model cache)
POST /v1/predict          → Run inference (with idempotency)
POST /v1/models           → Register a model
GET  /v1/models           → List registered models
GET  /v1/models/{name}    → Get model metadata
```

Full auto-docs at `/docs` (Swagger) and `/redoc` (ReDoc).

## Key design decisions

| Decision | Choice | Context |
|----------|--------|---------|
| Serving | Modular monolith | Microservices overhead doesn't pay for a single-node deployment |
| Model registry | PostgreSQL + filesystem | Metadata in tables, artefacts on disk. Object storage when scale demands it |
| Inference | Thread pool + timeout | 5s hard limit with `asyncio.wait_for`. Blocks neither the event loop nor the caller |
| Idempotency | In-memory key cache | Client-generated UUID deduplicates retries. Lost on restart — Redis later |
| Caching | Class-level dict | Models survive across requests. Future: LRU + TTL |

## Deployment

| Phase | Target | Orchestration |
|-------|--------|--------------|
| Development | Local | Docker Compose |
| Production | Hetzner VPS | k3s (Kubernetes) |

CI/CD via GitHub Actions.

## Documentation

- [Architecture decisions](docs/adr/DDD-001-arquitectura.md)
- API docs at `/docs`
