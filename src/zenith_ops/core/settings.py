"""Application settings — loaded from environment variables."""

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment.

    Reads DATABASE_URL from environment (or .env file).
    """

    model_config = SettingsConfigDict(env_file=".env")

    DATABASE_URL: PostgresDsn
