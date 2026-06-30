"""Unit tests for database session engine configuration."""

from __future__ import annotations

import importlib
import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.pool import NullPool

SESSION_MODULE = "zenith_ops.db.session"
DATABASE_URL = "postgresql+asyncpg://u:p@localhost:5432/db"


def _import_session_with_pool_flag(
    monkeypatch: pytest.MonkeyPatch,
    *,
    null_pool_enabled: bool,
) -> tuple[ModuleType, MagicMock, MagicMock]:
    """Import ``zenith_ops.db.session`` with isolated env and SQLAlchemy mocks."""
    previous_module = sys.modules.pop(SESSION_MODULE, None)
    monkeypatch.setenv("DATABASE_URL", DATABASE_URL)
    if null_pool_enabled:
        monkeypatch.setenv("ZENITH_OPS_DB_NULL_POOL", "1")
    else:
        monkeypatch.delenv("ZENITH_OPS_DB_NULL_POOL", raising=False)

    mock_create_async_engine = MagicMock(name="create_async_engine")
    mock_async_sessionmaker = MagicMock(name="async_sessionmaker")

    try:
        with (
            patch(
                "sqlalchemy.ext.asyncio.create_async_engine",
                new=mock_create_async_engine,
            ),
            patch(
                "sqlalchemy.ext.asyncio.async_sessionmaker",
                new=mock_async_sessionmaker,
            ),
        ):
            module = importlib.import_module(SESSION_MODULE)
    finally:
        sys.modules.pop(SESSION_MODULE, None)
        if previous_module is not None:
            sys.modules[SESSION_MODULE] = previous_module

    return module, mock_create_async_engine, mock_async_sessionmaker


def test_uses_null_pool_when_env_flag_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """ZENITH_OPS_DB_NULL_POOL=1 should disable connection pooling."""
    # Arrange / Act
    module, mock_create_async_engine, mock_async_sessionmaker = (
        _import_session_with_pool_flag(monkeypatch, null_pool_enabled=True)
    )

    # Assert
    mock_create_async_engine.assert_called_once_with(DATABASE_URL, poolclass=NullPool)
    mock_async_sessionmaker.assert_called_once_with(
        mock_create_async_engine.return_value,
        expire_on_commit=False,
    )
    assert module.engine is mock_create_async_engine.return_value
    assert module.async_session_factory is mock_async_sessionmaker.return_value


def test_uses_default_pool_when_env_flag_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing ZENITH_OPS_DB_NULL_POOL should keep SQLAlchemy's default pool."""
    # Arrange / Act
    module, mock_create_async_engine, mock_async_sessionmaker = (
        _import_session_with_pool_flag(monkeypatch, null_pool_enabled=False)
    )

    # Assert
    mock_create_async_engine.assert_called_once_with(DATABASE_URL)
    mock_async_sessionmaker.assert_called_once_with(
        mock_create_async_engine.return_value,
        expire_on_commit=False,
    )
    assert module.engine is mock_create_async_engine.return_value
    assert module.async_session_factory is mock_async_sessionmaker.return_value
