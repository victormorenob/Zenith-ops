"""Generate a dummy .joblib model for local development and testing.

Registers ``iris-classifier`` in PostgreSQL and writes the serialized
artifact to ``models/iris-classifier/1.0.0/model.joblib``.
"""

from __future__ import annotations

import asyncio

import structlog
from zenith_ops.core.exceptions import DuplicateModelError
from zenith_ops.core.logging_config import configure_logging
from zenith_ops.core.model_registry_db import PostgresModelRegistry
from zenith_ops.db.session import async_session_factory, engine

logger = structlog.get_logger(__name__)

MODEL_NAME = "iris-classifier"
MODEL_VERSION = "1.0.0"
FRAMEWORK = "sklearn"
MODEL_TYPE = "dummy_iris"
ARTIFACT_PATH = f"models/{MODEL_NAME}/{MODEL_VERSION}/model.joblib"


async def seed_dummy_model() -> None:
    """Insert registry row and dump DummyIrisClassifier to disk."""
    registry = PostgresModelRegistry(async_session_factory)
    try:
        metadata = await registry.register_and_build_model(
            name=MODEL_NAME,
            version=MODEL_VERSION,
            framework=FRAMEWORK,
            model_type=MODEL_TYPE,
            description="Dummy Iris classifier for local development",
            tags=["classification", "iris", "multiclass"],
        )
    except DuplicateModelError:
        logger.info(
            "seed_already_exists",
            name=MODEL_NAME,
            version=MODEL_VERSION,
            artifact_path=ARTIFACT_PATH,
        )
    else:
        logger.info(
            "seed_completed",
            model_id=metadata.model_id,
            version=metadata.version,
            status=metadata.status,
            artifact_path=metadata.artifact_path,
        )
    finally:
        await engine.dispose()


def main() -> None:
    """CLI entry point."""
    configure_logging()
    asyncio.run(seed_dummy_model())


if __name__ == "__main__":
    main()
