"""Model Registry — file-based catalog of ML models with metadata.

Provides an abstract ``ModelRegistry`` protocol and a concrete
``FileBasedModelRegistry`` that discovers models from a versioned directory
layout::

    models/
        <model_id>/
            <version>/
                meta.json      ← ModelMetadata
                model.joblib   ← serialized artifact

Why file-based?
    The current code already stores models as ``.joblib`` files on disk.
    A database backend would require syncing disk ↔ DB, adding complexity
    before MLflow arrives in Phase 2.  This is an *interim* registry that
    keeps things simple and replaces the hardcoded path resolution.

Why a Protocol?
    Phase 2 introduces MLflow.  By coding against ``ModelRegistry`` (a
    Protocol) instead of a concrete class, we can swap implementations
    without touching ``InferenceService`` or the API layer.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar, Protocol, runtime_checkable

from pydantic import BaseModel, Field

from zenith_ops.core.exceptions import ModelNotFoundError

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────
# Data models
# ──────────────────────────────────────────────────────────────────────


class ModelIOSchema(BaseModel):
    """Describes the expected input or output shape of a model.

    This is what lets a client know *how* to call the model without
    reading source code — self-documenting APIs are a hallmark of
    professional MLOps.
    """

    type: str
    """"class", "regression", "array", etc."""

    features: dict[str, str] | None = None
    """Feature name → dtype, e.g. ``{"sepal_length": "float"}``."""

    classes: list[str] | None = None
    """Class labels for classifiers, e.g. ``["setosa", "versicolor"]``."""


class ModelMetadata(BaseModel):
    """Full metadata for a single model *version*.

    Stored on disk as ``meta.json`` and parsed by the registry at startup.
    """

    model_id: str
    name: str
    version: str  # semver, e.g. "1.0.0"
    framework: str
    description: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metrics: dict[str, float] = Field(default_factory=dict)
    status: str = "active"  # "active" | "staging" | "archived"
    artifact_path: str = ""
    """Path to the serialised artifact on disk (empty for file-based)."""
    tags: list[str] = Field(default_factory=list)
    input_schema: ModelIOSchema | None = None
    output_schema: ModelIOSchema | None = None


class ModelSummary(BaseModel):
    """Lightweight summary returned by ``GET /v1/models`` (list).

    Omits metrics, schemas, and descriptions — the detail endpoint
    (``GET /v1/models/{id}``) returns the full ``ModelMetadata``.
    """

    model_id: str
    name: str
    latest_version: str
    framework: str
    status: str
    created_at: datetime
    tags: list[str]


# ──────────────────────────────────────────────────────────────────────
# Registry protocol
# ──────────────────────────────────────────────────────────────────────


@runtime_checkable
class ModelRegistry(Protocol):
    """Abstract contract for any model registry implementation.

    ``InferenceService`` depends on this protocol, not on a concrete
    class.  When Phase 2 brings MLflow, you write an
    ``MLflowModelRegistry`` that satisfies the same protocol and nothing
    in the core layer needs to change.
    """

    async def list_models(self) -> list[ModelSummary]:
        """Return the latest *active* version of every model."""
        ...

    async def get_model(self, model_id: str) -> ModelMetadata:
        """Return the latest *active* version of ``model_id``.

        Raises ``ModelNotFoundError`` if the model does not exist.
        """
        ...

    async def resolve_path(self, model_id: str) -> Path:
        """Return the absolute path to the model artifact on disk.

        Raises ``ModelNotFoundError`` if the model does not exist.
        """
        ...


# ──────────────────────────────────────────────────────────────────────
# File-based implementation
# ──────────────────────────────────────────────────────────────────────


def _parse_semver(version: str) -> tuple[int, ...]:
    """Parse a semver string into a sortable tuple.

    ``"1.2.3"`` → ``(1, 2, 3)``

    Non-numeric segments are treated as ``0`` so the sort never crashes.
    """
    parts = version.split(".")
    result: list[int] = []
    for p in parts:
        try:
            result.append(int(p))
        except ValueError:
            result.append(0)
    return tuple(result)


class FileBasedModelRegistry(ModelRegistry):
    """Scans a ``models/`` directory at startup and builds an in-memory catalog.

    .. deprecated::
       Use :class:`PostgresModelRegistry` instead.  This implementation
       is kept for reference and unit tests without a database.

    Directory layout::

        models/
            <model_id>/
                <version>/
                    meta.json
                    model.joblib

    Singleton + early scan means zero per-request I/O — all metadata
    lives in memory after startup.

    Example
    -------
    >>> registry = FileBasedModelRegistry(Path("models"))
    >>> registry.scan()
    >>> registry.list_models()
    [ModelSummary(model_id="iris-classifier", ...)]
    """

    _instance: ClassVar[FileBasedModelRegistry | None] = None

    def __init__(self, models_dir: str | Path = "models") -> None:
        self.models_dir = Path(models_dir)
        self._catalog: dict[str, dict[str, ModelMetadata]] = {}
        """``{model_id: {version: ModelMetadata}}``."""

    # -- Singleton --------------------------------------------------

    @classmethod
    def get_instance(cls) -> FileBasedModelRegistry:
        """Return the singleton instance.

        Creates one on first call with a default ``models/`` path and
        runs ``scan()``.  Subsequent calls return the cached instance
        without re-scanning.

        This is convenient for the current startup flow; a DI container
        would be cleaner for testing but is overkill in Phase 1.
        """
        if cls._instance is None:
            cls._instance = cls()
            cls._instance.scan()
        return cls._instance

    # -- Scan -------------------------------------------------------

    def scan(self) -> None:
        """Walk ``models/`` and populate the in-memory catalog.

        Robust by design:
        * If a ``meta.json`` is missing or corrupt the version is
          *skipped* (with a warning) — the app still starts.
        * If ``models/`` does not exist the catalog stays empty.
        """
        self._catalog = {}

        if not self.models_dir.is_dir():
            logger.info(
                "Models directory %s does not exist — catalog empty.", self.models_dir
            )
            return

        for model_dir in sorted(self.models_dir.iterdir()):
            if not model_dir.is_dir():
                continue

            model_id = model_dir.name
            versions: dict[str, ModelMetadata] = {}

            # Sort version dirs by semver descending so the first
            # entry in the dict is the latest — no symlinks needed.
            version_dirs = sorted(
                (d for d in model_dir.iterdir() if d.is_dir()),
                key=lambda d: _parse_semver(d.name),
                reverse=True,
            )

            for version_dir in version_dirs:
                version = version_dir.name
                meta_path = version_dir / "meta.json"

                if not meta_path.is_file():
                    logger.debug("Skipping %s — no meta.json", version_dir)
                    continue

                try:
                    metadata = ModelMetadata.model_validate_json(meta_path.read_bytes())
                    versions[version] = metadata
                except (json.JSONDecodeError, ValueError, OSError) as exc:
                    logger.warning(
                        "Skipping corrupt meta.json at %s: %s", meta_path, exc
                    )

            if versions:
                self._catalog[model_id] = versions

        logger.info(
            "Model registry scan complete: %d models, %d versions",
            len(self._catalog),
            sum(len(v) for v in self._catalog.values()),
        )

    # -- Query methods ----------------------------------------------

    async def list_models(self) -> list[ModelSummary]:
        """Latest active version per model, as lightweight summaries."""
        summaries: list[ModelSummary] = []
        for model_id, versions in self._catalog.items():
            latest = self._latest_active(versions)
            if latest is None:
                continue
            summaries.append(
                ModelSummary(
                    model_id=model_id,
                    name=latest.name,
                    latest_version=latest.version,
                    framework=latest.framework,
                    status=latest.status,
                    created_at=latest.created_at,
                    tags=latest.tags,
                )
            )
        return sorted(summaries, key=lambda s: s.model_id)

    async def get_model(self, model_id: str) -> ModelMetadata:
        """Latest active version of ``model_id``, or raises ``ModelNotFoundError``."""
        versions = self._catalog.get(model_id)
        if versions is None:
            raise ModelNotFoundError(model_id)

        latest = self._latest_active(versions)
        if latest is None:
            raise ModelNotFoundError(model_id)

        return latest

    async def resolve_path(self, model_id: str) -> Path:
        """Absolute ``.joblib`` path for ``model_id``.

        The path is computed from the catalog entry (validated during
        ``scan()``), but the ``.joblib`` artifact itself is NOT verified
        — it may be missing if removed after scan.

        Raises ``ModelNotFoundError`` if the ``model_id`` is unknown.
        """
        metadata = await self.get_model(model_id)  # validates existence
        return (
            self.models_dir / model_id / metadata.version / "model.joblib"
        ).resolve()

    # -- Internal helpers -------------------------------------------

    @staticmethod
    def _latest_active(
        versions: dict[str, ModelMetadata],
    ) -> ModelMetadata | None:
        """Return the highest-semver version whose status is ``"active"``.

        ``versions`` is assumed to be sorted descending (scan() does this).
        We iterate in order and return the first match.
        """
        for version in sorted(versions.keys(), key=_parse_semver, reverse=True):
            meta = versions[version]
            if meta.status == "active":
                return meta
        return None
