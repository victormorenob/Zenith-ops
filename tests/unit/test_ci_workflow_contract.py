"""Static regression tests for the GitHub Actions CI workflow."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"


def _read_ci_workflow() -> str:
    """Return the repository CI workflow as text."""
    return CI_WORKFLOW.read_text(encoding="utf-8")


def _assert_appears_before(content: str, first: str, second: str) -> None:
    """Assert that two workflow snippets exist and appear in order."""
    first_index = content.index(first)
    second_index = content.index(second)
    assert first_index < second_index


def test_ci_workflow_runs_postgres_backed_full_test_suite() -> None:
    """CI must run DB-backed integration tests against PostgreSQL."""
    # Arrange
    workflow = _read_ci_workflow()
    database_url = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/ZenithOpsDatabase"
    )

    # Act / Assert
    assert "postgres:" in workflow
    assert "image: postgres:16-alpine" in workflow
    assert "POSTGRES_DB: ZenithOpsDatabase" in workflow
    assert "--health-cmd pg_isready" in workflow
    assert "5432:5432" in workflow
    assert workflow.count(database_url) == 2
    assert "uv run alembic upgrade head" in workflow
    assert (
        "uv run pytest tests/ --cov=src --cov-report=xml --cov-report=term-missing"
        in workflow
    )
    _assert_appears_before(workflow, "- name: Run migrations", "- name: Pytest")


def test_ci_quality_gates_run_before_database_tests() -> None:
    """Lint, format, and mypy gates should run before migrations and tests."""
    # Arrange
    workflow = _read_ci_workflow()

    # Act / Assert
    assert "uv run ruff check src/ tests/" in workflow
    assert "uv run ruff format --check src/ tests/" in workflow
    assert "uv run mypy src/" in workflow
    _assert_appears_before(workflow, "- name: Ruff check", "- name: Run migrations")
    _assert_appears_before(
        workflow,
        "- name: Ruff format (check only)",
        "- name: Run migrations",
    )
    _assert_appears_before(workflow, "- name: Mypy", "- name: Run migrations")
