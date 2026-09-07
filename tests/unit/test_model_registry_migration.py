"""Unit tests for the model-registry Alembic migration contract."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

from sqlalchemy import (
    Column,
    ForeignKeyConstraint,
    PrimaryKeyConstraint,
    UniqueConstraint,
)

MIGRATION_PATH = (
    Path(__file__).resolve().parents[2]
    / "src"
    / "db"
    / "migrations"
    / "versions"
    / "31b561ac01a5_create_model_registry_and_prediction_.py"
)


class MigrationOpRecorder:
    """Record Alembic operations without connecting to a database."""

    def __init__(self) -> None:
        self.created_tables: dict[str, tuple[object, ...]] = {}
        self.dropped_tables: list[str] = []

    def create_table(self, name: str, *elements: object) -> None:
        """Record a table creation call and its SQLAlchemy elements."""
        self.created_tables[name] = elements

    def drop_table(self, name: str) -> None:
        """Record table drop order."""
        self.dropped_tables.append(name)


def _load_migration_module() -> ModuleType:
    """Load the numeric Alembic revision module by path."""
    spec = importlib.util.spec_from_file_location(
        "model_registry_prediction_metadata_migration",
        MIGRATION_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _record_upgrade(module: ModuleType) -> MigrationOpRecorder:
    """Run upgrade() with a recording op replacement."""
    recorder = MigrationOpRecorder()
    module.op = recorder
    module.upgrade()
    return recorder


def _columns(elements: tuple[object, ...]) -> dict[str, Column[object]]:
    """Return migration columns keyed by name."""
    return {
        element.name: element for element in elements if isinstance(element, Column)
    }


def _constraint_column_names(
    constraint: ForeignKeyConstraint | PrimaryKeyConstraint | UniqueConstraint,
) -> list[str]:
    """Return column names from an Alembic constraint before table binding."""
    pending_columns = getattr(constraint, "_pending_colargs", ())
    return [str(column_name) for column_name in pending_columns]


def test_upgrade_creates_model_registry_table_contract() -> None:
    """The migration must create the registry table with its unique key."""
    # Arrange
    module = _load_migration_module()

    # Act
    recorder = _record_upgrade(module)

    # Assert
    model_registry = recorder.created_tables["model_registry"]
    columns = _columns(model_registry)
    assert list(recorder.created_tables)[:1] == ["model_registry"]
    assert columns["id"].nullable is False
    assert columns["name"].nullable is False
    assert columns["version"].nullable is False
    assert columns["artifact_path"].nullable is False
    assert columns["status"].nullable is False
    assert "created_at" in columns
    assert any(isinstance(element, PrimaryKeyConstraint) for element in model_registry)
    assert any(
        isinstance(element, UniqueConstraint)
        and element.name == "uq_model_registry_name_version"
        and set(_constraint_column_names(element)) == {"name", "version"}
        for element in model_registry
    )


def test_upgrade_creates_prediction_metadata_fk_and_request_id_unique() -> None:
    """Prediction metadata must keep request idempotency and registry FK links."""
    # Arrange
    module = _load_migration_module()

    # Act
    recorder = _record_upgrade(module)

    # Assert
    assert list(recorder.created_tables) == ["model_registry", "prediction_metadata"]
    prediction_metadata = recorder.created_tables["prediction_metadata"]
    columns = _columns(prediction_metadata)
    assert columns["request_id"].nullable is False
    assert columns["model_id"].nullable is False
    assert columns["status"].nullable is False
    assert columns["latency_ms"].nullable is True
    assert any(
        isinstance(element, UniqueConstraint)
        and set(_constraint_column_names(element)) == {"request_id"}
        for element in prediction_metadata
    )
    foreign_keys = [
        element
        for element in prediction_metadata
        if isinstance(element, ForeignKeyConstraint)
    ]
    assert len(foreign_keys) == 1
    assert _constraint_column_names(foreign_keys[0]) == ["model_id"]
    assert [element.target_fullname for element in foreign_keys[0].elements] == [
        "model_registry.id"
    ]


def test_downgrade_drops_prediction_metadata_before_model_registry() -> None:
    """Downgrade must drop the dependent metadata table before the registry."""
    # Arrange
    module = _load_migration_module()
    recorder = MigrationOpRecorder()
    module.op = recorder

    # Act
    module.downgrade()

    # Assert
    assert recorder.dropped_tables == ["prediction_metadata", "model_registry"]
