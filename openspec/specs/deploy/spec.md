# Deploy Specification

**Domain:** deploy
**Phase:** 1
**Objective:** VPS production path before k3s (DDD-001)

---

## Purpose

Define verifiable production deployment behavior: host PostgreSQL 16 on the VPS, containerized migrate and app services, a production environment contract, continuous deployment from `main`, and operator runbook criteria. Observability, HA, k8s, and in-compose PostgreSQL for production are out of scope.

---

## Requirements

### Requirement: Production Compose Stack

The repository MUST provide `infra/docker/docker-compose.prod.yml` defining exactly two application services: `migrate` (one-shot) and `app` (long-running). The compose file MUST NOT include a PostgreSQL service. The `app` service MUST connect to host PostgreSQL at `host.docker.internal:5432` and MUST declare `extra_hosts: ["host.docker.internal:host-gateway"]`. The `app` service MUST depend on `migrate` with `condition: service_completed_successfully`. The `app` service MUST publish port `8000`.

#### Scenario: Migrate runs before app starts

- GIVEN host PostgreSQL 16 is reachable at `host.docker.internal:5432`
- AND `docker compose -f infra/docker/docker-compose.prod.yml up` is executed
- WHEN the stack starts
- THEN the `migrate` service runs `alembic upgrade head` and exits with code 0
- AND the `app` service starts only after `migrate` completes successfully

#### Scenario: App does not start when migrate fails

- GIVEN `migrate` exits with a non-zero status
- WHEN compose evaluates service dependencies
- THEN the `app` service MUST NOT start

#### Scenario: No PostgreSQL container in prod compose

- GIVEN `infra/docker/docker-compose.prod.yml`
- WHEN the file is inspected
- THEN it MUST NOT define a `postgres` service or PostgreSQL image

### Requirement: Migrate Job Image

The repository MUST provide `infra/docker/migrate.Dockerfile` that builds an image executing Alembic migrations only. The migrate image MUST NOT run seed scripts or `scripts/generate_dummy_model.py`. The migrate container command MUST be `alembic upgrade head`.

#### Scenario: Migrate applies schema without seeding

- GIVEN a fresh host PostgreSQL database
- WHEN the migrate service runs in production compose
- THEN Alembic applies pending migrations to `head`
- AND no seed or dummy-model script is executed

#### Scenario: Migrate failure is observable

- GIVEN Alembic cannot connect or upgrade fails
- WHEN the migrate container runs
- THEN it MUST exit with a non-zero status code

### Requirement: Production App Container

The production `app` service MUST use `infra/docker/Dockerfile`. The image MUST expose port `8000`, MUST define a Docker `HEALTHCHECK` against `GET /health/live`, and the production compose MUST set `LOG_FORMAT=json` for the app service per the logging specification.

#### Scenario: Liveness healthcheck passes

- GIVEN the app container is running and PostgreSQL is reachable
- WHEN Docker evaluates the image healthcheck
- THEN `GET /health/live` returns HTTP 200

#### Scenario: Production logs are JSON

- GIVEN production compose is used
- WHEN the app container starts
- THEN `LOG_FORMAT` is `json`
- AND structlog emits newline-delimited JSON records

### Requirement: Production Environment Contract

`.env.example` MUST document a production section listing required variables: `DATABASE_URL` (host PostgreSQL via `host.docker.internal`), `ENVIRONMENT=production`, `LOG_FORMAT=json`, `LOG_LEVEL`, and `SECRET_KEY`. Production secrets MUST NOT be committed; operators MUST configure them in a VPS-local `.env` file.

#### Scenario: Prod DATABASE_URL targets host gateway

- GIVEN the production section in `.env.example`
- WHEN an operator configures production
- THEN `DATABASE_URL` uses `host.docker.internal` as the database host
- AND the URL scheme is `postgresql+asyncpg`

#### Scenario: Required prod variables documented

- GIVEN `.env.example`
- WHEN the production section is read
- THEN `ENVIRONMENT`, `LOG_FORMAT`, `LOG_LEVEL`, `SECRET_KEY`, and `DATABASE_URL` are documented with example or placeholder values

### Requirement: Justfile Production Targets

The `Justfile` MUST provide `build-prod` and `up-prod` recipes that build images and start `infra/docker/docker-compose.prod.yml` respectively.

#### Scenario: build-prod builds production images

- GIVEN the repository is checked out
- WHEN `just build-prod` runs
- THEN production app and migrate images are built from their Dockerfiles

#### Scenario: up-prod starts production stack

- GIVEN production images exist and VPS `.env` is configured
- WHEN `just up-prod` runs
- THEN `docker compose -f infra/docker/docker-compose.prod.yml up -d` is executed

### Requirement: Continuous Deployment Pipeline

The repository MUST provide `.github/workflows/cd.yml` triggered on push to `main`. The workflow MUST build and push container images to GitHub Container Registry (GHCR), then deploy to the VPS over SSH by pulling images and running production compose. Image references MUST use immutable tags (commit SHA). The workflow MUST fail if migrate exits non-zero during deploy.

#### Scenario: Main push publishes images

- GIVEN a commit is pushed to `main`
- WHEN the CD workflow runs
- THEN app and migrate images are built and pushed to GHCR with the commit SHA tag

#### Scenario: SSH deploy updates running stack

- GIVEN images are published to GHCR
- WHEN the deploy job runs on the VPS
- THEN it pulls the pinned images and runs production compose
- AND migrate completes successfully before app is considered healthy

#### Scenario: Failed migrate fails CD

- GIVEN migrate exits non-zero during deploy
- WHEN the CD workflow evaluates job status
- THEN the workflow MUST fail with a non-success conclusion

### Requirement: Production Runbook

The repository MUST provide `docs/runbooks/deploy-production.md` covering cold-start VPS provisioning, host PostgreSQL 16 installation and configuration (`listen_addresses`, `pg_hba.conf`), Docker and Compose v2 prerequisites, production `.env` setup, first deploy, health verification (`/health/live`, `/health/ready`), rollback of app image and schema, and optional TLS/reverse-proxy notes.

#### Scenario: Cold-start operator can provision VPS

- GIVEN an empty VPS with Ubuntu-compatible packages
- WHEN an operator follows the runbook
- THEN they can install host PostgreSQL 16, Docker, configure `.env`, and bring up production compose

#### Scenario: Runbook documents rollback

- GIVEN a failed or bad deployment
- WHEN an operator consults the runbook
- THEN it describes reverting to a prior image tag and optional `alembic downgrade` steps

#### Scenario: Health verification steps documented

- GIVEN production stack is up
- WHEN an operator follows post-deploy checks in the runbook
- THEN they can confirm `/health/live` returns 200 and `/health/ready` returns 200 when PostgreSQL and models are available

---

## Out of Scope

- Kubernetes, Helm, Terraform, Fly.io
- PostgreSQL in Docker for production
- Observability stack (Phase 2), HA, multi-region
- Mandatory TLS termination (optional runbook guidance only)

## Dependencies

- `health` specification — liveness/readiness endpoints and Docker HEALTHCHECK target
- `logging` specification — `LOG_FORMAT=json` for production
