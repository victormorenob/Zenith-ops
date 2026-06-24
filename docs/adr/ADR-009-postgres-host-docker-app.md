# ADR-009: PostgreSQL on Host, Application in Docker (Production VPS)

**Estado:** Aprobado  
**Fecha:** 2026-06-24  
**Autor:** Víctor Moreno  
**Relacionado:** DDD-001 (k3s deferred), change `docker-prod-deploy`

---

## Decisión

En el VPS de producción (Hetzner), **PostgreSQL 16 se instala nativamente en el host** (`apt`). La aplicación FastAPI y el job de migraciones Alembic se ejecutan en **contenedores Docker** gestionados por `docker-compose.prod.yml`. La app se conecta a la base de datos mediante `host.docker.internal:5432` con `extra_hosts: host-gateway`.

---

## Contexto

Zenith-ops necesita un camino de despliegue en VPS antes de Fase 3 (Kubernetes, DDD-001). El entorno de desarrollo usa `docker-compose.dev.yml` con PostgreSQL containerizado, init con seed y uvicorn con `--reload`. Producción requiere:

- Datos persistentes sin depender del ciclo de vida de contenedores de aplicación
- Migraciones automáticas en cada deploy
- CD desde `main` vía GHCR + SSH
- Sin complejidad de k8s/Helm/Terraform en esta fase

---

## Alternativas consideradas

| Alternativa | Motivo de rechazo |
|-------------|-------------------|
| PostgreSQL en Docker (prod) | Volúmenes y backups acoplados al stack compose; riesgo al `docker compose down`; duplica patrón dev sin beneficio en VPS single-node |
| `network_mode: host` para app | Expone puertos del proceso directamente; pierde aislamiento de red del bridge |
| IP fija del bridge en `DATABASE_URL` | Frágil si Docker recrea la red; `host.docker.internal` + `host-gateway` es estable |
| Migrate + seed en mismo contenedor | Seed es bootstrap único; mezclarlo con migrate en cada deploy es lento y no idempotente para datos de demo |
| Fly.io / PaaS | Fuera de alcance explícito del change |

---

## Consecuencias

### Positivas

- Backups y upgrades de PG con herramientas estándar del host (`pg_dump`, `apt`)
- Redeploy de app/migrate no reinicia PostgreSQL
- Mismo `Dockerfile` multi-stage y usuario no-root que CI/dev
- Migraciones gateadas: app no arranca si `alembic upgrade head` falla

### Negativas

- Configuración manual de `postgresql.conf`, `pg_hba.conf` y firewall en cold start
- `host.docker.internal` requiere `extra_hosts` en Linux (no automático como en Docker Desktop)
- Operador debe ejecutar seed manual una vez (`scripts/generate_dummy_model.py` o equivalente)
- Readiness (`/health/ready`) requiere modelos en volumen — sin seed, readiness devuelve 503 hasta bootstrap

### Operación

- **Cold start:** runbook `docs/runbooks/deploy-production.md` — PG host, `.env`, seed manual, primer `compose up`
- **Deploy rutinario:** CD → pull imágenes SHA → migrate → app
- **Rollback app:** `IMAGE_TAG` anterior; **rollback schema:** `alembic downgrade` vía contenedor migrate

---

## Referencias

- `infra/docker/docker-compose.prod.yml`
- `infra/docker/migrate.Dockerfile`
- `docs/runbooks/deploy-production.md`
- `openspec/changes/docker-prod-deploy/design.md`
- Proposal: `openspec/changes/docker-prod-deploy/proposal.md`
