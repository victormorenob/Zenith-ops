# SPEC-002: Health Checks

**Domain:** health
**Phase:** 1
**Objective:** 1.2

---

## Purpose

Endpoints for system health monitoring — used by load balancers, orchestrators (K8s probes), and monitoring infrastructure to determine service availability and readiness. Liveness and readiness are separated per the standard pattern: liveness is self-only, readiness checks dependencies.

---

## Requirements

### Requirement: Liveness Probe — `GET /health/live`

The system MUST expose a liveness endpoint at `GET /health/live` that returns immediately without performing any I/O or dependency checks.

- **Response 200**: `{ "status": "up", "version": "0.1.0", "timestamp": "2026-06-10T12:30:00Z" }`
- `version` MUST be read dynamically from `pyproject.toml` `[project] version` — NOT hardcoded
- `timestamp` MUST be ISO 8601 in UTC

#### Scenario: Successful liveness check

- GIVEN the service is running
- WHEN a GET request is sent to `/health/live`
- THEN the response status MUST be 200
- AND the body MUST contain `status: "up"`, `version`, and `timestamp` per contract

#### Scenario: Version from pyproject.toml

- GIVEN the service is running
- WHEN `/health/live` is called
- THEN the `version` field MUST match the value in `pyproject.toml` `[project] version`

#### Scenario: No I/O on liveness

- GIVEN the service is running
- WHEN `/health/live` is called
- THEN the handler MUST NOT perform any database queries, cache lookups, or network I/O

### Requirement: Readiness Probe — `GET /health/ready`

The system MUST expose a readiness endpoint at `GET /health/ready` that checks component health and returns 200 only when all components are healthy.

- **Response 200**: `{ "status": "up", "version": "0.1.0", "timestamp": "...", "components": { "database": "up", "model_cached": true } }`
- **Response 503**: `{ "status": "down", "version": "0.1.0", "timestamp": "...", "components": { "database": "up"|"down", "model_cached": true|false } }`
- Components: `database` (SQLAlchemy async ping), `model_cached` (InferenceService cache — at least one model)

#### Scenario: All components healthy

- GIVEN PostgreSQL is reachable via SQLAlchemy async connection
- AND InferenceService has at least one model in cache
- WHEN a GET request is sent to `/health/ready`
- THEN the response status MUST be 200
- AND `status` MUST be `"up"`
- AND `components.database` MUST be `"up"`
- AND `components.model_cached` MUST be `true`

#### Scenario: Database unreachable

- GIVEN PostgreSQL is NOT reachable
- WHEN a GET request is sent to `/health/ready`
- THEN the response status MUST be 503
- AND `status` MUST be `"down"`
- AND `components.database` MUST be `"down"`

#### Scenario: Model cache empty

- GIVEN PostgreSQL is reachable
- AND InferenceService has zero models in cache
- WHEN a GET request is sent to `/health/ready`
- THEN the response status MUST be 503
- AND `status` MUST be `"down"`
- AND `components.model_cached` MUST be `false`

#### Scenario: Timestamp is ISO 8601 UTC

- GIVEN the service is running
- WHEN any health endpoint returns a response
- THEN the `timestamp` field MUST be a string in ISO 8601 format
- AND the time MUST be in UTC
- AND the value MUST reflect the moment of response generation

### Requirement: Refactor existing endpoint

The system MUST replace the existing `GET /healthy` returning `{"status": "ok"}` with the two new endpoints above. (Previously: single synthetic health check with no contract.)

#### Scenario: Old endpoint removed

- GIVEN the system had a `GET /healthy` endpoint
- WHEN the new health endpoints are deployed
- THEN `GET /healthy` MUST be removed
- AND `GET /health/live` SHOULD serve as its behavioral replacement

---

## Out of Scope

- Structured logging (issue #11)
- Idempotency (issue #12)
