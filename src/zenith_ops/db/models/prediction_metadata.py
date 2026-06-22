"""SQLAlchemy model for the prediction_metadata table."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import TIMESTAMP, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from zenith_ops.db.base import Base


class PredictionMetadata(Base):
    """Stores metadata about each prediction request.

    Best-effort logging: a failure to insert MUST NOT interrupt the
    prediction response.
    """

    __tablename__ = "prediction_metadata"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    request_id: Mapped[uuid.UUID] = mapped_column(UUID, unique=True, nullable=False)
    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("model_registry.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    result: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    result_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
