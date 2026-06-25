import os

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from zenith_ops.core.settings import Settings

settings = Settings()  # type: ignore[call-arg]

_engine_kwargs: dict[str, object] = {}
if os.environ.get("ZENITH_OPS_DB_NULL_POOL") == "1":
    _engine_kwargs["poolclass"] = NullPool

engine = create_async_engine(str(settings.DATABASE_URL), **_engine_kwargs)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
