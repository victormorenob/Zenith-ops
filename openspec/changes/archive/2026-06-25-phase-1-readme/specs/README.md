# Delta for README (Phase 1)

## ADDED Requirements

### Requirement: Project Overview

The root `README.md` MUST include a brief description of Zenith-ops as an ML serving platform with model registry and health endpoints, in English, matching the existing concise tone.

#### Scenario: Reader understands purpose in one screen

- GIVEN a new visitor opens `README.md`
- WHEN they read the opening sections
- THEN they see what the project does without opening other docs

### Requirement: Architecture Diagram

The root `README.md` MUST include a Mermaid diagram showing: HTTP client → FastAPI application → host PostgreSQL (metadata) and filesystem `models/` volume (artefacts).

#### Scenario: Diagram reflects modular monolith

- GIVEN the README architecture section
- WHEN the Mermaid block is rendered
- THEN it shows a single FastAPI process talking to PostgreSQL and on-disk model artefacts

### Requirement: Local Quick Start

The root `README.md` MUST document local setup using `uv`, copying `.env` from `.env.example`, and `just start` (or equivalent `just setup` + `just start`). It MUST state the local dev API base URL and port (`http://localhost:8081` when using dev compose).

#### Scenario: Clone to running stack

- GIVEN a developer with Docker and `uv` installed
- WHEN they follow the Quick start section
- THEN they can reach the API and Swagger at `/docs` on the documented local port

### Requirement: API Endpoints Table

The root `README.md` MUST list HTTP methods and paths that match the routers in `src/zenith_ops/api/v1/`, including at minimum:

- `GET /health/live`, `GET /health/ready`
- `POST /v1/predict`
- `GET /v1/models`, `GET /v1/models/{model_id}`
- `POST /v1/models/register`, `PATCH /v1/models/{model_id}/status`

It MAY include `POST /v1/test-feature` if documented as a smoke-test endpoint.

#### Scenario: Paths match code

- GIVEN each route registered in `health.py`, `predict.py`, and `models.py`
- WHEN compared to the README API table
- THEN every documented path equals the router path (no stale `/v1/models` POST for register)

### Requirement: Production Section

The root `README.md` MUST include a Production section with:

- Base URL `http://167.233.116.195:8000`
- Example `curl` commands for `/health/live` and `/health/ready`
- A short note that deploys run on push to `main` after CI succeeds (CD workflow)
- A link to `docs/runbooks/deploy-production.md`

#### Scenario: Operator smoke from README

- GIVEN the production base URL is reachable
- WHEN an operator runs the documented health curls
- THEN they receive HTTP 200 for live; ready returns 200 when DB and model cache are up

### Requirement: Deployment Table

The root `README.md` Deployment table MUST list:

- Development: local Docker Compose
- Production: Hetzner VPS with host PostgreSQL and Docker Compose app (not k3s as current state)
- Future Phase 3: k3s/Kubernetes MAY be noted as planned, not current prod

#### Scenario: No k3s as current prod

- GIVEN the Deployment table
- WHEN a reader checks the Production row
- THEN orchestration is VPS Docker Compose, not k3s

### Requirement: Stack Table Accuracy

The root `README.md` Stack table MUST remain present and accurate for Phase 1 technologies (Python 3.12, FastAPI, Pydantic v2, PostgreSQL, joblib/sklearn, pytest).

#### Scenario: Stack matches pyproject and codebase

- GIVEN the Stack table
- WHEN compared to `pyproject.toml` and project rules
- THEN listed choices match the implemented stack
