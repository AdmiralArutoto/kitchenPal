"""Dependency wiring helpers for FastAPI."""

from typing import Optional

from pymongo import MongoClient

from .config import get_settings
from .repositories import MongoRecipeRepository, RecipeRepository

_mongo_client: Optional[MongoClient] = None
_recipe_repository: Optional[RecipeRepository] = None


def get_mongo_client() -> MongoClient:
    """Return a shared Mongo client instance."""
    global _mongo_client
    if _mongo_client is None:
        settings = get_settings()
        _mongo_client = MongoClient(settings.mongodb_uri)
    return _mongo_client


def get_recipe_repository() -> RecipeRepository:
    """Provide the shared recipe repository instance."""
    global _recipe_repository
    if _recipe_repository is None:
        settings = get_settings()
        _recipe_repository = MongoRecipeRepository(
            get_mongo_client(), settings.mongodb_db, settings.mongodb_collection
        )
    return _recipe_repository


def shutdown_resources() -> None:
    """Close open connections on application shutdown."""
    global _mongo_client, _recipe_repository
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None
    _recipe_repository = None
