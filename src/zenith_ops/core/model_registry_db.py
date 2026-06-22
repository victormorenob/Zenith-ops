"""PostgreSQL-backed model registry implementation.

Provides :class:`PostgresModelRegistry`, an async implementation of the
``ModelRegistry`` protocol that reads and writes model metadata to the
``model_registry`` table via SQLAlchemy async sessions.

A ``get_registry()`` factory is provided for FastAPI ``Depends`` injection.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from zenith_ops.core.exceptions import DuplicateModelError, ModelNotFoundError
from zenith_ops.core.model_registry import ModelMetadata, ModelSummary
from zenith_ops.db.models.model_registry import ModelRegistryEntry
from zenith_ops.db.models.prediction_metadata import PredictionMetadata

logger = logging.getLogger(__name__)

_VALID_STATUSES = frozenset({"staging", "production", "archived"})


class PostgresModelRegistry:
    """PostgreSQL-backed model registry implementing the (async) ModelRegistry
    protocol plus write methods.

    All queries go through the ``_session_factory`` so no DB connection is
    held outside a request/operation scope.

    Parameters
    ----------
    session_factory:
        An ``async_sessionmaker[AsyncSession]`` bound to the engine.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    # ── Protocol: read methods ──────────────────────────────────────────

    async def list_models(self) -> list[ModelSummary]:
        """Latest version per model name, excluding archived models.

        Uses a subquery to find the maximum version per name, then joins
        back to the full row to extract metadata. Results are ordered by
        model name.
        """
        async with self._session_factory() as session:
            # Subquery: latest version per name (exclude archived)
            latest_version_subq = (
                select(
                    ModelRegistryEntry.name,
                    func.max(ModelRegistryEntry.version).label("max_version"),
                )
                .where(ModelRegistryEntry.status != "archived")
                .group_by(ModelRegistryEntry.name)
            ).subquery()

            stmt = (
                select(ModelRegistryEntry)
                .join(
                    latest_version_subq,
                    and_(
                        ModelRegistryEntry.name == latest_version_subq.c.name,
                        ModelRegistryEntry.version == latest_version_subq.c.max_version,
                    ),
                )
                .order_by(ModelRegistryEntry.name)
            )

            result = await session.execute(stmt)
            entries = result.scalars().all()
            return [self._to_summary(e) for e in entries]

    async def get_model(self, model_id: str) -> ModelMetadata:
        """Latest version of the model identified by ``name``.

        Raises :class:`ModelNotFoundError` if no model with that name exists.
        """
        async with self._session_factory() as session:
            stmt = (
                select(ModelRegistryEntry)
                .where(ModelRegistryEntry.name == model_id)
                .order_by(ModelRegistryEntry.version.desc())
                .limit(1)
            )
            result = await session.execute(stmt)
            entry = result.scalar_one_or_none()
            if entry is None:
                raise ModelNotFoundError(model_id)
            return self._to_metadata(entry)

    async def resolve_path(self, model_id: str) -> Path:
        """Return the on-disk artifact path for the latest version.

        Delegates to :meth:`get_model` and wraps the ``artifact_path``
        column in a :class:`Path`.
        """
        metadata = await self.get_model(model_id)
        return Path(metadata.artifact_path)

    # ── Write methods ───────────────────────────────────────────────────

    async def register_model(
        self,
        name: str,
        version: str,
        framework: str,
        artifact_path: str,
        description: str = "",
        metrics: dict[str, Any] | None = None,
        tags: list[str] | None = None,
        input_schema: dict[str, Any] | None = None,
        output_schema: dict[str, Any] | None = None,
    ) -> ModelMetadata:
        """Register a new model version.

        Parameters
        ----------
        name:
            Model name (e.g. ``"iris-classifier"``).
        version:
            Semantic version string.
        framework:
            ML framework (e.g. ``"sklearn"``, ``"pytorch"``).
        artifact_path:
            Absolute or relative path to the serialised ``.joblib`` file.
        description:
            Human-readable description.
        metrics:
            Optional dict of evaluation metrics.
        tags:
            Optional list of tag strings.
        input_schema, output_schema:
            Optional JSON Schema-compatible dicts describing I/O shape.

        Returns
        -------
        ModelMetadata for the newly created entry.

        Raises
        ------
        DuplicateModelError
            If a row with the same ``(name, version)`` already exists.
        """
        async with self._session_factory() as session:
            # Duplicate check — (name, version) is UNIQUE
            existing = await session.execute(
                select(ModelRegistryEntry).where(
                    ModelRegistryEntry.name == name,
                    ModelRegistryEntry.version == version,
                )
            )
            if existing.scalar_one_or_none():
                raise DuplicateModelError(name, version)

            entry = ModelRegistryEntry(
                name=name,
                version=version,
                framework=framework,
                artifact_path=artifact_path,
                description=description or "",
                metrics=metrics or {},
                tags=tags or [],
                input_schema=input_schema,
                output_schema=output_schema,
                status="staging",
            )
            session.add(entry)
            await session.commit()
            await session.refresh(entry)
            return self._to_metadata(entry)

    async def update_status(
        self,
        model_uuid: str,
        status: str,
    ) -> ModelMetadata:
        """Update the status of a model version by UUID.

        Parameters
        ----------
        model_uuid:
            UUID of the model registry entry (as a string).
        status:
            One of ``"staging"``, ``"production"``, ``"archived"``.

        Returns
        -------
        ModelMetadata with the updated status.

        Raises
        ------
        ValueError
            If *status* is not one of the valid values.
        ModelNotFoundError
            If no entry matches *model_uuid*.
        """
        if status not in _VALID_STATUSES:
            valid = ", ".join(sorted(_VALID_STATUSES))
            msg = f"Invalid status {status!r}. Must be one of: {valid}"
            raise ValueError(msg)

        async with self._session_factory() as session:
            stmt = select(ModelRegistryEntry).where(
                ModelRegistryEntry.id == UUID(model_uuid)
            )
            result = await session.execute(stmt)
            entry = result.scalar_one_or_none()
            if entry is None:
                raise ModelNotFoundError(model_uuid)

            entry.status = status
            entry.updated_at = datetime.now(UTC)
            await session.commit()
            await session.refresh(entry)
            return self._to_metadata(entry)

    async def register_and_build_model(
        self,
        name: str,
        version: str,
        framework: str,
        model_type: str,
        description: str = "",
        metrics: dict[str, Any] | None = None,
        tags: list[str] | None = None,
        input_schema: dict[str, Any] | None = None,
        output_schema: dict[str, Any] | None = None,
    ) -> ModelMetadata:
        """Register a model version AND generate its ``.joblib`` artifact.

        This is a convenience for the common case where the client provides
        a ``model_type`` (e.g. ``"dummy_iris"``) instead of a pre-built
        artifact.  The method:

        1. Builds the model instance via :func:`build_model`.
        2. Serialises it to ``models/{name}/{version}/model.joblib``.
        3. Delegates to :meth:`register_model` for the DB insert.

        Parameters
        ----------
        name:
            Model name.
        version:
            Semantic version string.
        framework:
            ML framework label.
        model_type:
            Key into the model builders registry.
        description:
            Human-readable description.
        metrics, tags, input_schema, output_schema:
            Forwarded to :meth:`register_model`.

        Returns
        -------
        ModelMetadata from the newly created DB row.

        Raises
        ------
        ValueError
            If *model_type* is unknown.
        DuplicateModelError
            If ``(name, version)`` already exists.
        """
        from pathlib import Path

        import joblib

        from zenith_ops.core.model_builders import build_model

        model_obj = build_model(model_type)
        models_dir = Path("models") / name / version
        models_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = str(models_dir / "model.joblib")
        joblib.dump(model_obj, artifact_path)

        return await self.register_model(
            name=name,
            version=version,
            framework=framework,
            artifact_path=artifact_path,
            description=description,
            metrics=metrics,
            tags=tags,
            input_schema=input_schema,
            output_schema=output_schema,
        )

    async def log_prediction(
        self,
        request_id: UUID,
        model_id: str,
        features: dict[str, float],
        result: float | list[float] | None,
        result_type: str | None,
        latency_ms: float | None,
        status: str,
        error_message: str | None = None,
    ) -> None:
        """Log prediction metadata (best-effort, never propagates errors).

        If the DB write fails, log a warning and return — the prediction
        response must NEVER be affected by observability failures.

        Parameters
        ----------
        request_id:
            Unique request identifier (matches the API response).
        model_id:
            Model name (not UUID) — resolved to a FK inside the method.
        features:
            Feature vector sent for inference (not persisted yet — reserved
            for future schema expansion).
        result:
            Inference result (scalar or array).  Stored as ``None`` when
            the value is a scalar — the ``result_type`` column captures
            the shape.
        result_type:
            ``"scalar"``, ``"class"``, or ``"array"``.
        latency_ms:
            Wall-clock inference time in milliseconds.
        status:
            ``"success"`` or ``"error"``.
        error_message:
            Human-readable error reason (``None`` on success).
        """
        try:
            async with self._session_factory() as session:
                stmt = (
                    select(ModelRegistryEntry.id)
                    .where(ModelRegistryEntry.name == model_id)
                    .order_by(ModelRegistryEntry.version.desc())
                    .limit(1)
                )
                result_row = await session.execute(stmt)
                registry_uuid = result_row.scalar_one_or_none()
                if registry_uuid is None:
                    logger.warning(
                        "Cannot log prediction: model %s not found in registry",
                        model_id,
                    )
                    return

                entry = PredictionMetadata(
                    request_id=request_id,
                    model_id=registry_uuid,
                    status=status,
                    result=None,  # scalar floats don't fit JSONB dict
                    result_type=result_type,
                    latency_ms=latency_ms,
                    error_message=error_message,
                )
                session.add(entry)
                await session.commit()
        except Exception:
            logger.warning(
                "Failed to log prediction metadata for model %s",
                model_id,
                exc_info=True,
            )

    # ── Mapping helpers ─────────────────────────────────────────────────

    @staticmethod
    def _to_metadata(entry: ModelRegistryEntry) -> ModelMetadata:
        """Map an ORM row to a :class:`ModelMetadata` Pydantic model."""
        tags: list[str] = []
        if entry.tags is not None:
            if isinstance(entry.tags, list):
                tags = list(entry.tags)
            else:
                # JSONB could be an object if stored as such
                tags = list(str(entry.tags))

        metrics: dict[str, float] = {}
        if entry.metrics:
            metrics = {k: float(v) for k, v in entry.metrics.items()}

        return ModelMetadata(
            model_id=entry.name,
            name=entry.name,
            version=entry.version,
            framework=entry.framework,
            description=entry.description or "",
            created_at=entry.created_at,
            metrics=metrics,
            status=entry.status,
            artifact_path=entry.artifact_path or "",
            tags=tags,
        )

    @staticmethod
    def _to_summary(entry: ModelRegistryEntry) -> ModelSummary:
        """Map an ORM row to a :class:`ModelSummary`."""
        tags: list[str] = []
        if entry.tags is not None:
            if isinstance(entry.tags, list):
                tags = list(entry.tags)
            else:
                tags = list(str(entry.tags))

        return ModelSummary(
            model_id=entry.name,
            name=entry.name,
            latest_version=entry.version,
            framework=entry.framework,
            status=entry.status,
            created_at=entry.created_at,
            tags=tags,
        )


# ── DI factory (singleton) ────────────────────────────────────────────────

_registry_instance: PostgresModelRegistry | None = None


async def get_registry() -> PostgresModelRegistry:
    """FastAPI ``Depends`` factory for :class:`PostgresModelRegistry`.

    Returns a singleton instance wired to the application's async session
    factory.  The instance is created once and reused for the lifetime of
    the process.
    """
    global _registry_instance
    if _registry_instance is None:
        from zenith_ops.db.session import async_session_factory

        _registry_instance = PostgresModelRegistry(async_session_factory)
    return _registry_instance
