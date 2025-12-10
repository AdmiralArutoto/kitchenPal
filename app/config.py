"""Application configuration and settings helpers."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    app_name: str = "Recipe Assistant API"
    debug: bool = False
    mongodb_uri: str = "mongodb://localhost:27017/recipes"
    mongodb_db: str = "recipes"
    mongodb_collection: str = "recipes"
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    openai_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_prefix="RECIPES_", env_file=".env", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance for dependency injection."""
    return Settings()
