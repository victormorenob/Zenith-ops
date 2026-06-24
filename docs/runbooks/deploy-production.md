# Runbook: Production Deployment (VPS)

Production runs **host PostgreSQL 16** plus **Docker Compose** for `migrate` (one-shot Alembic) and `app` (FastAPI). See [ADR-009](../adr/ADR-009-postgres-host-docker-app.md) for rationale.

**Registry:** Images `ghcr.io/<owner>/zenith-ops-app` and `ghcr.io/<owner>/zenith-ops-migrate` are **public** on GHCR — `docker pull` on the VPS does not require login. If images are made private later, create a PAT with `read:packages` and run `docker login ghcr.io` once on the VPS.

---

## Prerequisites

| Item | Version / note |
|------|----------------|
| OS | Ubuntu 22.04+ (or Debian-compatible) |
| Docker | Engine + Compose v2 (`docker compose`) |
| PostgreSQL | 16 via `apt` on the **host** (not in compose) |
| Repo checkout | `/opt/zenith-ops/` on the VPS |
| Secrets | VPS-local `.env` (never committed) |

---

## 1. Cold start — host PostgreSQL 16

```bash
sudo apt update
sudo apt install -y postgresql-16 postgresql-contrib-16
```

Create database and dedicated user:

```bash
sudo -u postgres psql <<'SQL'
CREATE USER zenith WITH PASSWORD 'CHANGE_ME_STRONG';
CREATE DATABASE "ZenithOpsDatabase" OWNER zenith;
GRANT ALL PRIVILEGES ON DATABASE "ZenithOpsDatabase" TO zenith;
SQL
```

### `listen_addresses`

Edit `postgresql.conf` (path varies; often `/etc/postgresql/16/main/postgresql.conf`):

```ini
listen_addresses = 'localhost,<VPS_PRIVATE_IP>'
```

Replace `<VPS_PRIVATE_IP>` with the server's private IP (Hetzner internal). Avoid `*`.

Reload:

```bash
sudo systemctl reload postgresql
```

### `pg_hba.conf` — Docker bridge CIDR

Containers reach the host via the default Docker bridge. **Do not assume** `172.17.0.0/16` without verifying:

```bash
docker network inspect bridge --format '{{range .IPAM.Config}}{{.Subnet}}{{end}}'
```

Typical output on Hetzner: `172.17.0.0/16`. Add a line to `pg_hba.conf` using the **actual** subnet:

```
host    ZenithOpsDatabase    zenith    172.17.0.0/16    scram-sha-256
```

Reload PostgreSQL after editing `pg_hba.conf`.

### Firewall

Allow PostgreSQL **only** from the Docker bridge — not from the public internet. Example with `ufw`:

```bash
# Adjust interface/CIDR to match docker network inspect output
sudo ufw allow from 172.17.0.0/16 to any port 5432 proto tcp
```

---

## 2. Docker on the VPS

Install Docker Engine and Compose v2 per [official docs](https://docs.docker.com/engine/install/ubuntu/). Add the deploy user to the `docker` group:

```bash
sudo usermod -aG docker "$USER"
```

Log out and back in so group membership applies.

---

## 3. Application layout

```bash
sudo mkdir -p /opt/zenith-ops
sudo chown "$USER":"$USER" /opt/zenith-ops
cd /opt/zenith-ops
git clone <repo-url> .
```

Ensure `models/` exists for inference artifacts (volume mount in compose):

```bash
mkdir -p models
```

---

## 4. Production `.env`

Copy from the repository example and set production values:

```bash
cp .env.example .env
# Edit .env — use the production section
```

Required variables:

| Variable | Example / note |
|----------|----------------|
| `DATABASE_URL` | `postgresql+asyncpg://zenith:SECRET@host.docker.internal:5432/ZenithOpsDatabase` |
| `ENVIRONMENT` | `production` |
| `LOG_FORMAT` | `json` (also set in compose for `app`) |
| `LOG_LEVEL` | `INFO` or `WARNING` |
| `SECRET_KEY` | Strong random string (VPS-only) |
| `GHCR_OWNER` | GitHub org/user in **lowercase** |
| `IMAGE_TAG` | Pinned SHA from CD, or `latest` for manual pulls |

Compose reads `.env` via `env_file`; CD exports `IMAGE_TAG` and `GHCR_OWNER` during deploy.

---

## 5. Manual seed (one-time)

Migrations do **not** seed demo models. Run once after first schema apply:

**Option A — host (with `uv` and repo checkout):**

```bash
uv sync
uv run python scripts/generate_dummy_model.py
```

**Option B — via app container:**

```bash
docker compose -f infra/docker/docker-compose.prod.yml run --rm app \
  python scripts/generate_dummy_model.py
```

Without seed, `/health/ready` may return 503 until models exist under `models/`.

---

## 6. Deploy

### Automated (CD)

On every **successful CI run** for a push to `main`, `.github/workflows/cd.yml`:

1. Builds and pushes `zenith-ops-app` and `zenith-ops-migrate` to GHCR (`:<sha>` and `:latest`)
2. SSHs to the VPS (`VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY` secrets)
3. Pulls images, runs `migrate`, then `up -d app`

If `migrate` exits non-zero, the SSH step fails and the workflow reports failure — the app is not started.

### Manual (operator)

From `/opt/zenith-ops`:

```bash
export IMAGE_TAG=<commit-sha-or-latest>
export GHCR_OWNER=<github-owner-lowercase>
docker compose -f infra/docker/docker-compose.prod.yml pull migrate app
docker compose -f infra/docker/docker-compose.prod.yml up migrate
docker compose -f infra/docker/docker-compose.prod.yml up -d app
```

Local development of the prod stack (requires host PG reachable as `host.docker.internal`):

```bash
just build-prod
just up-prod
```

---

## 7. Health checks

| Endpoint | Purpose |
|----------|---------|
| `GET /health/live` | Liveness — Docker `HEALTHCHECK` on the app image |
| `GET /health/ready` | Readiness — DB + models available |

```bash
curl -sf http://localhost:8000/health/live
curl -sf http://localhost:8000/health/ready
```

Docker container health:

```bash
docker inspect --format '{{.State.Health.Status}}' zenith-app-prod
```

---

## 8. Rollback

### App only (schema unchanged)

```bash
cd /opt/zenith-ops
export IMAGE_TAG=<previous-good-sha>
export GHCR_OWNER=<owner>
docker compose -f infra/docker/docker-compose.prod.yml pull app
docker compose -f infra/docker/docker-compose.prod.yml up -d app
```

### Schema (reversible migration)

Test on staging first. Override migrate CMD:

```bash
docker compose -f infra/docker/docker-compose.prod.yml run --rm migrate alembic downgrade -1
```

### CD / config regression

Revert the commit on `main`; the next green CI run redeploys the previous SHA.

### Full recovery

`docker compose -f infra/docker/docker-compose.prod.yml down`, restore host PostgreSQL from snapshot, redeploy last known-good `IMAGE_TAG`.

---

## 9. TLS / reverse proxy (optional)

This change does **not** ship a reverse proxy. The app listens on HTTP port `8000`. For production TLS, place **Caddy** or **nginx** in front of the host (terminate TLS, proxy to `127.0.0.1:8000`). Configure certificates (Let's Encrypt) and firewall so only 443 is public.

---

## 10. Troubleshooting

| Symptom | Check |
|---------|--------|
| Migrate cannot connect | `pg_hba.conf` CIDR matches `docker network inspect bridge`; `listen_addresses` includes private IP |
| `host.docker.internal` fails on Linux | `extra_hosts: host-gateway` present on `app` and `migrate` in `docker-compose.prod.yml` |
| Pull fails | Image visibility (public vs private); `GHCR_OWNER` lowercase; `IMAGE_TAG` exists on GHCR |
| App unhealthy | `docker logs zenith-app-prod`; verify `DATABASE_URL` and PostgreSQL reachability |
| Readiness 503 | Run manual seed; confirm `models/` volume content |

---

## References

- [ADR-009: PostgreSQL on Host, Application in Docker](../adr/ADR-009-postgres-host-docker-app.md)
- `infra/docker/docker-compose.prod.yml`
- `openspec/specs/deploy/spec.md`
