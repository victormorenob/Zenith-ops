"""Static integration contract tests for the production deploy path."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HOST_GATEWAY_ENTRY = '"host.docker.internal:host-gateway"'
PROD_DATABASE_URL = (
    "postgresql+asyncpg://zenith:CHANGE_ME@host.docker.internal:5432/ZenithOpsDatabase"
)


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _service_names(compose_text: str) -> set[str]:
    service_lines = (
        line.strip().removesuffix(":")
        for line in compose_text.splitlines()
        if line.startswith("  ") and not line.startswith("    ") and line.endswith(":")
    )
    return set(service_lines)


def _service_block(compose_text: str, service_name: str) -> str:
    lines = compose_text.splitlines()
    start = lines.index(f"  {service_name}:") + 1
    block: list[str] = []

    for line in lines[start:]:
        if line.startswith("  ") and not line.startswith("    "):
            break
        block.append(line)

    return "\n".join(block)


def _env_values(env_text: str) -> dict[str, str]:
    values: dict[str, str] = {}

    for line in env_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", maxsplit=1)
        values[key] = value

    return values


class TestProductionComposeContract:
    """Production compose enforces migration-first host-PostgreSQL deploys."""

    def test_compose_defines_only_migrate_and_app_without_postgres(self) -> None:
        """Production compose must not reintroduce a PostgreSQL container."""
        # Arrange
        compose_text = _read("infra/docker/docker-compose.prod.yml")

        # Act
        services = _service_names(compose_text)

        # Assert
        assert services == {"migrate", "app"}
        assert "postgres" not in compose_text.lower()

    def test_app_waits_for_migrate_and_uses_host_gateway_database(self) -> None:
        """The app must start only after migrations can finish successfully."""
        # Arrange
        compose_text = _read("infra/docker/docker-compose.prod.yml")

        # Act
        app_block = _service_block(compose_text, "app")
        migrate_block = _service_block(compose_text, "migrate")

        # Assert
        assert "condition: service_completed_successfully" in app_block
        assert HOST_GATEWAY_ENTRY in app_block
        assert HOST_GATEWAY_ENTRY in migrate_block

    def test_app_exposes_public_port_and_json_logs(self) -> None:
        """Production app service must expose the API and emit JSON logs."""
        # Arrange
        compose_text = _read("infra/docker/docker-compose.prod.yml")

        # Act
        app_block = _service_block(compose_text, "app")

        # Assert
        assert '- "8000:8000"' in app_block
        assert "LOG_FORMAT: json" in app_block


class TestProductionImageContract:
    """Production images keep runtime and migration concerns separated."""

    def test_app_image_uses_non_root_user_and_liveness_healthcheck(self) -> None:
        """The app image must expose port 8000 and healthcheck liveness only."""
        # Arrange
        dockerfile_text = _read("infra/docker/Dockerfile")

        # Act
        normalized_text = " ".join(dockerfile_text.split())

        # Assert
        assert "USER app" in dockerfile_text
        assert "EXPOSE 8000" in dockerfile_text
        assert "/health/live" in dockerfile_text
        assert "/health/ready" not in dockerfile_text
        assert "CMD curl -f http://localhost:8000/health/live || exit 1" in (
            normalized_text
        )

    def test_migrate_image_runs_only_alembic_upgrade_head(self) -> None:
        """The migrate image must not seed models as part of schema deploy."""
        # Arrange
        dockerfile_text = _read("infra/docker/migrate.Dockerfile")

        # Act
        command_line = 'CMD ["alembic", "upgrade", "head"]'

        # Assert
        assert command_line in dockerfile_text
        assert "scripts/generate_dummy_model.py" not in dockerfile_text
        assert "USER app" in dockerfile_text


class TestProductionEnvironmentContract:
    """The example environment documents required production values."""

    def test_env_example_documents_required_production_variables(self) -> None:
        """Operators must have all production variables in the committed example."""
        # Arrange
        env_text = _read(".env.example")

        # Act
        env_values = _env_values(env_text)

        # Assert
        assert env_values["DATABASE_URL"] == PROD_DATABASE_URL
        assert env_values["ENVIRONMENT"] == "production"
        assert env_values["LOG_FORMAT"] == "json"
        assert env_values["LOG_LEVEL"] == "INFO"
        assert env_values["SECRET_KEY"]
        assert "No commitear secretos reales" in env_text


class TestContinuousDeploymentContract:
    """CD must deploy the exact CI commit and fail on migration errors."""

    def test_cd_uses_workflow_run_sha_for_build_and_checkout(self) -> None:
        """Published images must be tied to the CI workflow run head SHA."""
        # Arrange
        workflow_text = _read(".github/workflows/cd.yml")

        # Act
        image_tag_source = "IMAGE_TAG: ${{ github.event.workflow_run.head_sha }}"
        checkout_ref = "ref: ${{ github.event.workflow_run.head_sha }}"

        # Assert
        assert "workflow_run:" in workflow_text
        assert "workflows: [CI]" in workflow_text
        assert "branches: [main]" in workflow_text
        assert image_tag_source in workflow_text
        assert checkout_ref in workflow_text
        assert "github.event.workflow_run.event == 'push'" in workflow_text

    def test_cd_deploy_pulls_then_runs_migrate_before_app(self) -> None:
        """The deploy script must fail fast if migrate exits non-zero."""
        # Arrange
        workflow_text = _read(".github/workflows/cd.yml")
        pull_command = (
            "docker compose -f infra/docker/docker-compose.prod.yml pull migrate app"
        )
        migrate_command = (
            "docker compose -f infra/docker/docker-compose.prod.yml up migrate"
        )
        app_command = "docker compose -f infra/docker/docker-compose.prod.yml up -d app"

        # Act
        pull_index = workflow_text.index(pull_command)
        migrate_index = workflow_text.index(migrate_command)
        app_index = workflow_text.index(app_command)

        # Assert
        assert "script_stop: true" in workflow_text
        assert "set -euo pipefail" in workflow_text
        assert pull_index < migrate_index < app_index


class TestOperatorDeployContract:
    """Operator-facing production commands must remain documented."""

    def test_justfile_exposes_build_and_up_prod_targets(self) -> None:
        """Just recipes should run production compose with the prod file."""
        # Arrange
        justfile_text = _read("Justfile")

        # Act
        build_command = (
            "docker compose -f infra/docker/docker-compose.prod.yml build app migrate"
        )
        up_command = "docker compose -f infra/docker/docker-compose.prod.yml up -d"

        # Assert
        assert "build-prod:" in justfile_text
        assert build_command in justfile_text
        assert "up-prod:" in justfile_text
        assert up_command in justfile_text

    def test_runbook_documents_health_checks_and_rollback(self) -> None:
        """The runbook must preserve deploy verification and recovery paths."""
        # Arrange
        runbook_text = _read("docs/runbooks/deploy-production.md")

        # Act
        required_phrases = {
            "host PostgreSQL 16",
            "docker compose -f infra/docker/docker-compose.prod.yml up migrate",
            "curl -sf http://localhost:8000/health/live",
            "curl -sf http://localhost:8000/health/ready",
            "export IMAGE_TAG=<previous-good-sha>",
            "alembic downgrade -1",
        }

        # Assert
        missing_phrases = {
            phrase for phrase in required_phrases if phrase not in runbook_text
        }
        assert missing_phrases == set()
