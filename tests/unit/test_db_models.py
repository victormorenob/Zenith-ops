"""Tests for SQLAlchemy ORM models (Phase A — Foundation)."""

import uuid

import pytest
from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy import inspect as sa_inspect

from zenith_ops.db.base import Base
from zenith_ops.db.models.model_registry import ModelRegistryEntry
from zenith_ops.db.models.prediction_metadata import PredictionMetadata


class TestModelRegistryEntry:
    """TDD Cycle: A.2 — ModelRegistryEntry ORM model."""

    def test_tablename(self) -> None:
        """Model MUST use the correct table name."""
        assert ModelRegistryEntry.__tablename__ == "model_registry"

    def test_primary_key_uuid(self) -> None:
        """Primary key MUST be a UUID column named 'id'."""
        mapper = sa_inspect(ModelRegistryEntry)
        pk_columns = [c.name for c in mapper.primary_key]
        assert pk_columns == ["id"]

    def test_unique_constraint_name_version(self) -> None:
        """Table MUST have a unique constraint on (name, version)."""
        constraints = ModelRegistryEntry.__table_args__
        uq_constraints = [
            tc for tc in constraints if isinstance(tc, UniqueConstraint)
        ]
        assert len(uq_constraints) >= 1
        names_found = any(
            set(tc.columns.keys()) == {"name", "version"}
            for tc in uq_constraints
        )
        assert names_found, (
            "No UniqueConstraint covering (name, version) found"
        )

    def test_jsonb_columns_present(self) -> None:
        """Model MUST include JSONB columns for metrics, tags, schemas."""
        mapper = sa_inspect(ModelRegistryEntry)
        col_names = {c.name for c in mapper.columns}
        for jsonb_col in ("metrics", "tags", "input_schema", "output_schema"):
            assert jsonb_col in col_names, (
                f"Missing JSONB column: {jsonb_col}"
            )

    def test_timestamp_columns(self) -> None:
        """Model MUST have created_at, updated_at, deployed_at."""
        mapper = sa_inspect(ModelRegistryEntry)
        col_names = {c.name for c in mapper.columns}
        for ts_col in ("created_at", "updated_at", "deployed_at"):
            assert ts_col in col_names, f"Missing timestamp column: {ts_col}"

    def test_registered_on_base_metadata(self) -> None:
        """Model MUST be registered on Base.metadata."""
        table_names = Base.metadata.tables
        assert "model_registry" in table_names


class TestPredictionMetadata:
    """TDD Cycle: A.3 — PredictionMetadata ORM model."""

    def test_tablename(self) -> None:
        """Model MUST use the correct table name."""
        assert PredictionMetadata.__tablename__ == "prediction_metadata"

    def test_primary_key_uuid(self) -> None:
        """Primary key MUST be a UUID column named 'id'."""
        mapper = sa_inspect(PredictionMetadata)
        pk_columns = [c.name for c in mapper.primary_key]
        assert pk_columns == ["id"]

    def test_request_id_unique(self) -> None:
        """request_id MUST have a unique constraint."""
        mapper = sa_inspect(PredictionMetadata)
        req_id_col = mapper.columns["request_id"]
        assert req_id_col.unique is True

    def test_foreign_key_to_model_registry(self) -> None:
        """model_id MUST be a FK referencing model_registry.id."""
        mapper = sa_inspect(PredictionMetadata)
        model_id_col = mapper.columns["model_id"]
        fks = list(model_id_col.foreign_keys)
        assert len(fks) == 1, "model_id must have exactly one FK"
        fk = fks[0]
        assert fk.column.table.name == "model_registry"
        assert fk.column.name == "id"

    def test_latency_ms_float(self) -> None:
        """latency_ms MUST be a Float column (not Integer)."""
        mapper = sa_inspect(PredictionMetadata)
        latency_col = mapper.columns["latency_ms"]
        # SQLAlchemy Float is an instance of sqlalchemy.Float
        from sqlalchemy import Float as SAFloat

        assert isinstance(latency_col.type, SAFloat), (
            f"Expected Float, got {type(latency_col.type)}"
        )

    def test_nullable_columns(self) -> None:
        """result, latency_ms, error_message MUST be nullable."""
        mapper = sa_inspect(PredictionMetadata)
        nullable_cols = {"result", "result_type", "latency_ms", "error_message"}
        for col_name in nullable_cols:
            col = mapper.columns[col_name]
            assert col.nullable is True, (
                f"{col_name} should be nullable"
            )

    def test_registered_on_base_metadata(self) -> None:
        """Model MUST be registered on Base.metadata."""
        table_names = Base.metadata.tables
        assert "prediction_metadata" in table_names


class TestModelsInit:
    """TDD Cycle: A.4 — Models __init__ exports."""

    def test_model_registry_entry_exported(self) -> None:
        """ModelRegistryEntry MUST be importable from db.models."""
        from zenith_ops.db.models import ModelRegistryEntry  # noqa: F811

        assert ModelRegistryEntry is not None

    def test_prediction_metadata_exported(self) -> None:
        """PredictionMetadata MUST be importable from db.models."""
        from zenith_ops.db.models import PredictionMetadata  # noqa: F811

        assert PredictionMetadata is not None
