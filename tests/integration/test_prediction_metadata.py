"""Integration tests for persisted prediction metadata."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from unittest.mock import patch

import pytest
from sqlalchemy import select

from zenith_ops.db.models.model_registry import ModelRegistryEntry
from zenith_ops.db.models.prediction_metadata import PredictionMetadata
from zenith_ops.db.session import async_session_factory
from zenith_ops.services.predictor import InferenceService, ResultType

pytestmark = pytest.mark.postgres


def _capture_created_tasks() -> tuple[
    list[asyncio.Task[None]],
    Callable[[Coroutine[object, object, None]], asyncio.Task[None]],
]:
    """Return a create_task replacement that records scheduled tasks."""
    original_create_task = asyncio.create_task
    created_tasks: list[asyncio.Task[None]] = []

    def capture_create_task(
        coroutine: Coroutine[object, object, None],
    ) -> asyncio.Task[None]:
        task = original_create_task(coroutine)
        created_tasks.append(task)
        return task

    return created_tasks, capture_create_task


async def test_successful_predict_persists_prediction_metadata_row() -> None:
    """Successful predictions persist a metadata row for the resolved DB model."""
    # Arrange
    created_tasks, capture_create_task = _capture_created_tasks()
    features = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
    }

    # Act
    with patch("asyncio.create_task", side_effect=capture_create_task):
        prediction_result, result_type, latency_ms = await InferenceService.predict(
            model_id="iris-classifier",
            features=features,
        )

    assert len(created_tasks) == 1
    await created_tasks[0]

    async with async_session_factory() as session:
        query_result = await session.execute(
            select(PredictionMetadata, ModelRegistryEntry).join(
                ModelRegistryEntry,
                PredictionMetadata.model_id == ModelRegistryEntry.id,
            )
        )
        metadata_row, model_row = query_result.one()

    # Assert
    assert prediction_result == 0.0
    assert result_type == ResultType.SCALAR
    assert latency_ms > 0
    assert model_row.name == "iris-classifier"
    assert model_row.version == "1.0.0"
    assert metadata_row.request_id is not None
    assert metadata_row.status == "success"
    assert metadata_row.error_message is None
    assert metadata_row.result_type == ResultType.SCALAR.value
    assert metadata_row.result is None
    assert metadata_row.latency_ms is not None
    assert metadata_row.latency_ms > 0
