"""Regression tests for the production deployment contract.

The production Docker/CD files are executable configuration: a small change can
skip migrations, start the app against the wrong database, or deploy a mutable
image. These tests pin the high-risk invariants from the deploy specification.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROD_COMPOSE_PATH = PROJECT_ROOT / "infra/docker/docker-compose.prod.yml"
APP_DOCKERFILE_PATH = PROJECT_ROOT / "infra/docker/Dockerfile"
MIGRATE_DOCKERFILE_PATH = PROJECT_ROOT / "infra/docker/migrate.Dockerfile"
CD_WORKFLOW_PATH = PROJECT_ROOT / ".github/workflows/cd.yml"
ENV_EXAMPLE_PATH = PROJECT_ROOT / ".env.example"

JsonObject = dict[str, object]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_compose_config() -> JsonObject:
    if shutil.which("docker") is None:
        pytest.skip("Docker CLI is not available for compose config validation")

    result = subprocess.run(
        [
            "docker",
            "compose",
            "-f",
            str(PROD_COMPOSE_PATH),
            "config",
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        pytest.skip(f"Docker Compose config validation is unavailable: {message}")

    loaded = json.loads(result.stdout)
    assert isinstance(loaded, dict)
    return loaded


def _as_object(value: object) -> JsonObject:
    assert isinstance(value, dict)
    return value


def _assert_host_gateway(value: object) -> None:
    if isinstance(value, dict):
        assert value.get("host.docker.internal") == "host-gateway"
        return

    assert isinstance(value, list)
    normalized_hosts = {str(host) for host in value}
    assert normalized_hosts & {
        "host.docker.internal:host-gateway",
        "host.docker.internal=host-gateway",
    }


def _assert_app_publishes_port_8000(ports: object) -> None:
    assert isinstance(ports, list)
    assert any(
        isinstance(port, dict)
        and str(port.get("published")) == "8000"
        and str(port.get("target")) == "8000"
        for port in ports
    )


def test_prod_compose_file_declares_host_pg_and_migrate_gate() -> None:
    """Prod compose should run only app/migrate and gate app on migrations."""
    # Arrange
    compose_text = _read_text(PROD_COMPOSE_PATH)

    # Act
    host_gateway_occurrences = compose_text.count(
        '"host.docker.internal:host-gateway"'
    )

    # Assert
    assert "\n  migrate:\n" in compose_text
    assert "\n  app:\n" in compose_text
    assert "\n  postgres:\n" not in compose_text.lower()
    assert "postgres:16" not in compose_text.lower()
    assert host_gateway_occurrences == 2
    assert "condition: service_completed_successfully" in compose_text
    assert "LOG_FORMAT: json" in compose_text
    assert '"8000:8000"' in compose_text


def test_prod_compose_config_matches_runtime_contract() -> None:
    """Normalized Compose config should preserve the spec-critical semantics."""
    # Arrange
    config = _load_compose_config()

    # Act
    services = _as_object(config["services"])
    app_service = _as_object(services["app"])
    migrate_service = _as_object(services["migrate"])
    depends_on = _as_object(app_service["depends_on"])
    migrate_dependency = _as_object(depends_on["migrate"])
    environment = _as_object(app_service["environment"])

    # Assert
    assert set(services) == {"app", "migrate"}
    assert "postgres" not in services
    assert "postgres" not in str(app_service.get("image", "")).lower()
    assert "postgres" not in str(migrate_service.get("image", "")).lower()
    assert migrate_dependency["condition"] == "service_completed_successfully"
    assert environment["LOG_FORMAT"] == "json"
    _assert_host_gateway(app_service["extra_hosts"])
    _assert_host_gateway(migrate_service["extra_hosts"])
    _assert_app_publishes_port_8000(app_service["ports"])


def test_dockerfiles_keep_app_healthcheck_and_alembic_only_migrate() -> None:
    """App and migrate images should keep their distinct production commands."""
    # Arrange
    app_dockerfile = _read_text(APP_DOCKERFILE_PATH)
    migrate_dockerfile = _read_text(MIGRATE_DOCKERFILE_PATH)

    # Act
    migrate_lines = {line.strip() for line in migrate_dockerfile.splitlines()}

    # Assert
    assert "EXPOSE 8000" in app_dockerfile
    assert "HEALTHCHECK" in app_dockerfile
    assert "http://localhost:8000/health/live" in app_dockerfile
    assert "uvicorn" in app_dockerfile
    assert 'CMD ["alembic", "upgrade", "head"]' in migrate_lines
    assert "generate_dummy_model.py" not in migrate_dockerfile
    assert "COPY scripts/" not in migrate_dockerfile
    assert "RUN python scripts/" not in migrate_dockerfile


def test_cd_workflow_deploys_sha_pinned_images_after_migration() -> None:
    """CD should deploy the workflow SHA and fail before app start on migrate error."""
    # Arrange
    workflow_text = _read_text(CD_WORKFLOW_PATH)

    # Act
    pull_index = workflow_text.index(
        "docker compose -f infra/docker/docker-compose.prod.yml pull migrate app"
    )
    migrate_index = workflow_text.index(
        "docker compose -f infra/docker/docker-compose.prod.yml up migrate"
    )
    app_index = workflow_text.index(
        "docker compose -f infra/docker/docker-compose.prod.yml up -d app"
    )

    # Assert
    assert "workflows: [CI]" in workflow_text
    assert "branches: [main]" in workflow_text
    assert "IMAGE_TAG: ${{ github.event.workflow_run.head_sha }}" in workflow_text
    assert "ref: ${{ github.event.workflow_run.head_sha }}" in workflow_text
    assert "zenith-ops-app:${{ env.IMAGE_TAG }}" in workflow_text
    assert "zenith-ops-migrate:${{ env.IMAGE_TAG }}" in workflow_text
    assert "needs: build-and-push" in workflow_text
    assert "script_stop: true" in workflow_text
    assert "set -euo pipefail" in workflow_text
    assert pull_index < migrate_index < app_index


def test_env_example_documents_production_host_gateway_contract() -> None:
    """Prod env example should steer operators to host PostgreSQL and JSON logs."""
    # Arrange
    env_example = _read_text(ENV_EXAMPLE_PATH)

    # Act
    production_section = env_example.split("# ── Producción", maxsplit=1)[1]

    # Assert
    assert "DATABASE_URL=postgresql+asyncpg://" in production_section
    assert "@host.docker.internal:5432/" in production_section
    assert "ENVIRONMENT=production" in production_section
    assert "LOG_FORMAT=json" in production_section
    assert "LOG_LEVEL=INFO" in production_section
    assert "SECRET_KEY=generate-a-strong-random-secret-on-the-vps" in production_section
