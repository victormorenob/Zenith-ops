# Estado actual del proyecto — 2026-06-25

**Nota (2026-05-14):** el repositorio quedó en una sola raíz (`pyproject.toml` y `Justfile` al mismo nivel); se eliminó la carpeta duplicada `Zenith-ops/Zenith-ops/`.

## Completado

- [x] Entorno Python 3.12 con UV (`pyproject.toml`, `uv.lock`)
- [x] Herramientas de calidad en proyecto: Ruff, mypy strict, pytest + coverage mínimo 70%
- [x] `.cursorrules` y reglas por carpeta `.cursor/rules/*.mdc`
- [x] Memory Bank: `docs/context/*`, plantilla y SPEC-000 en `docs/specs/`
- [x] Ajustes de workspace en `.vscode/settings.json` (editor, Ruff, intérprete `.venv`)
- [x] Paquete instalable `zenith_ops` bajo `src/zenith_ops/` (`api/`, `core/`, `db/`, `services/`)
- [x] API Fase 1: `POST /v1/predict`, health checks (`/health/live`, `/health/ready`), model registry CRUD
- [x] Model Registry persistido en PostgreSQL (SQLAlchemy 2.0 async + artefactos `.joblib` en disco)
- [x] Migraciones Alembic en `src/db/migrations/` (ORM en `zenith_ops/db/`, rutas separadas)
- [x] CI/CD: GitHub Actions → deploy en VPS Hetzner (producción en `http://167.233.116.195:8000`)
- [x] Docker multi-stage (`infra/docker/`) con compose dev y prod
- [x] Sentry error tracking (DSN opcional, `correlation_id` tag, middleware catch-all)

## En progreso

- [ ] Fase 2+: MLflow, observabilidad (Prometheus/Grafana/Loki), drift (Evidently AI)
- [ ] Placeholders `src/monitoring/` y `src/training/` — sin código aún

## Pendiente (roadmap orientativo)

- [ ] Fase 3: Kubernetes + Helm + Terraform (`infra/helm/`, `infra/terraform/` — placeholders)
- [ ] Idempotencia con Redis (hoy in-memory, se pierde al reiniciar)

## Estructura canónica (resumen)

```
src/
├── db/migrations/          ← Alembic
├── monitoring/.gitkeep     ← Fase 2+, no implementado
├── training/.gitkeep       ← Fase 2+, no implementado
└── zenith_ops/             ← paquete instalable
    ├── api/ (schemas/, v1/)
    ├── core/ (registry, settings, exceptions, logging, sentry)
    ├── db/ (ORM: base, session, models/)   ← sin migraciones aquí
    └── services/ (predictor.py)
tests/unit/, tests/integration/
docs/adr/, docs/context/, docs/specs/, docs/runbooks/
infra/docker/
openspec/
```

## Dependencias

Ver `[project]` y `[dependency-groups]` en `pyproject.toml`.

## Notas para la IA

- ORM en `zenith_ops/db/`; migraciones Alembic en `src/db/migrations/` (`alembic.ini` apunta a `script_location` allí).
- `InferenceService` vive en `zenith_ops/services/predictor.py` (no en `core/`).
- `src/monitoring/` y `src/training/` son placeholders Fase 2+; no asumir código allí.
- La base de datos se configura con `DATABASE_URL` (ver `.env.example`); tablas: model registry y prediction metadata (ver migraciones).
