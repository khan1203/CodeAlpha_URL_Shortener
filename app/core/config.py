"""
Application configuration.

All settings are loaded from environment variables (via a .env file in local
development, or real environment variables in production/containers).
Using pydantic-settings gives us validation + type-casting for free.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    app_name: str = "URL Shortener"
    app_env: str = "development"
    debug: bool = True

    # Public base URL used to build the short links returned to clients
    base_url: str = "http://localhost:8000"
    short_code_length: int = 6

    # MongoDB
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "url_shortener"
    mongo_collection_name: str = "urls"

    # CORS
    allowed_origins: str = "*"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        if self.allowed_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Cached accessor so we parse the .env file only once."""
    return Settings()


settings = get_settings()
