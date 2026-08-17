"""Static production deploy contract tests for SPEC-006."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROD_COMPOSE = ROOT / "infra" / "docker" / "docker-compose.prod.yml"
APP_DOCKERFILE = ROOT / "infra" / "docker" / "Dockerfile"
MIGRATE_DOCKERFILE = ROOT / "infra" / "docker" / "migrate.Dockerfile"
CD_WORKFLOW = ROOT / ".github" / "workflows" / "cd.yml"
ENV_EXAMPLE = ROOT / ".env.example"


def _read(path: Path) -> str:
    """Read a repository text file with UTF-8 encoding."""
    return path.read_text(encoding="utf-8")


def _service_names(compose_text: str) -> set[str]:
    """Return top-level service names from docker-compose.prod.yml."""
    return set(re.findall(r"^  ([a-zA-Z0-9_-]+):\n", compose_text, re.MULTILINE))


def _service_block(compose_text: str, service_name: str) -> str:
    """Return the indented YAML block for one top-level service."""
    pattern = rf"(?ms)^  {re.escape(service_name)}:\n(?P<body>(?:    .*\n)*)"
    match = re.search(pattern, compose_text)
    if match is None:
        msg = f"Service {service_name!r} not found"
        raise AssertionError(msg)
    return match.group("body")


def test_prod_compose_contains_only_app_and_migrate_services() -> None:
    """Production compose must not include a PostgreSQL container."""
    # Arrange
    compose_text = _read(PROD_COMPOSE)

    # Act
    service_names = _service_names(compose_text)
    image_lines = re.findall(r"^\s+image:\s*(.+)$", compose_text, re.MULTILINE)

    # Assert
    assert service_names == {"app", "migrate"}
    assert all("postgres" not in image.lower() for image in image_lines)


def test_prod_compose_gates_app_start_on_successful_migration() -> None:
    """The app must start only after the one-shot migrate service succeeds."""
    # Arrange
    compose_text = _read(PROD_COMPOSE)
    app_block = _service_block(compose_text, "app")
    migrate_block = _service_block(compose_text, "migrate")

    # Act
    depends_on_migrate = re.search(
        r"depends_on:\n"
        r"(?:      .*\n)*"
        r"      migrate:\n"
        r"(?:        .*\n)*"
        r"        condition: service_completed_successfully",
        app_block,
    )

    # Assert
    assert depends_on_migrate is not None
    assert '"8000:8000"' in app_block
    assert "LOG_FORMAT: json" in app_block
    assert '"host.docker.internal:host-gateway"' in app_block
    assert '"host.docker.internal:host-gateway"' in migrate_block


def test_migrate_image_runs_alembic_only_without_seed_script() -> None:
    """The migration image must only apply schema migrations."""
    # Arrange
    dockerfile_text = _read(MIGRATE_DOCKERFILE)

    # Act
    command_is_alembic_upgrade = 'CMD ["alembic", "upgrade", "head"]' in dockerfile_text

    # Assert
    assert command_is_alembic_upgrade
    assert "generate_dummy_model.py" not in dockerfile_text


def test_app_image_exposes_port_and_uses_liveness_healthcheck() -> None:
    """The production app image must expose and healthcheck the API port."""
    # Arrange
    dockerfile_text = _read(APP_DOCKERFILE)

    # Act / Assert
    assert "EXPOSE 8000" in dockerfile_text
    assert "HEALTHCHECK" in dockerfile_text
    assert "http://localhost:8000/health/live" in dockerfile_text
    assert 'CMD ["uvicorn", "zenith_ops.__init__:app"' in dockerfile_text


def test_cd_workflow_uses_pinned_sha_and_runs_migrate_before_app() -> None:
    """CD must deploy immutable images and fail before app start on migrate errors."""
    # Arrange
    workflow_text = _read(CD_WORKFLOW)

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
    assert "IMAGE_TAG: ${{ github.event.workflow_run.head_sha }}" in workflow_text
    assert "script_stop: true" in workflow_text
    assert pull_index < migrate_index < app_index


def test_env_example_documents_required_production_variables() -> None:
    """The production env example must target host PostgreSQL and JSON logs."""
    # Arrange
    env_text = _read(ENV_EXAMPLE)

    # Act / Assert
    assert (
        "DATABASE_URL=postgresql+asyncpg://zenith:CHANGE_ME@"
        "host.docker.internal:5432/ZenithOpsDatabase"
    ) in env_text
    assert "ENVIRONMENT=production" in env_text
    assert "LOG_FORMAT=json" in env_text
    assert "LOG_LEVEL=INFO" in env_text
    assert "SECRET_KEY=generate-a-strong-random-secret-on-the-vps" in env_text
