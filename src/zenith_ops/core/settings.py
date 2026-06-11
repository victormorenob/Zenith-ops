"""Application settings — loaded from environment variables."""

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App configuration via env vars (or .env file).

    `extra="ignore"` allows extra env vars without validation errors.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: PostgresDsn  # asyncpg DSN: postgresql+asyncpg://user:pass@host/db
