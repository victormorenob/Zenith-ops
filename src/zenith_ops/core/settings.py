"""Application settings — loaded from environment variables."""

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App configuration via env vars (or .env file).

    `extra="ignore"` allows extra env vars without validation errors.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: PostgresDsn  # asyncpg DSN: postgresql+asyncpg://user:pass@host/db
    LOG_LEVEL: str = (
        "INFO"  # Default log level; logging_config reads os.environ directly
    )

    # Sentry (optional — leave SENTRY_DSN empty to disable)
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 0.0

    @property
    def sentry_enabled(self) -> bool:
        """Return ``True`` when a non-empty Sentry DSN is configured."""
        return bool(self.SENTRY_DSN.strip())
