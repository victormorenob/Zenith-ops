from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from zenith_ops.core.settings import Settings

settings = Settings()  # type: ignore[call-arg]
engine = create_async_engine(str(settings.DATABASE_URL))
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
