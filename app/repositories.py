"""Repository abstractions for recipe persistence."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol
from uuid import UUID

from pymongo import MongoClient, ReturnDocument
from pymongo.collection import Collection

from .models import Recipe, RecipeCreate, RecipeUpdate


class RecipeRepository(Protocol):
    """Repository interface used by the API layer."""

    def list_recipes(self) -> List[Recipe]: ...

    def get_recipe(self, recipe_id: UUID) -> Optional[Recipe]: ...

    def create_recipe(self, recipe_in: RecipeCreate) -> Recipe: ...

    def update_recipe(
        self, recipe_id: UUID, recipe_in: RecipeUpdate
    ) -> Optional[Recipe]: ...

    def delete_recipe(self, recipe_id: UUID) -> bool: ...


class InMemoryRecipeRepository:
    """Simple in-memory repository backed by a dictionary."""

    def __init__(self) -> None:
        self._recipes: Dict[UUID, Recipe] = {}

    def list_recipes(self) -> List[Recipe]:
        return list(self._recipes.values())

    def get_recipe(self, recipe_id: UUID) -> Optional[Recipe]:
        return self._recipes.get(recipe_id)

    def create_recipe(self, recipe_in: RecipeCreate) -> Recipe:
        recipe = Recipe(**recipe_in.model_dump())
        self._recipes[recipe.id] = recipe
        return recipe

    def update_recipe(
        self, recipe_id: UUID, recipe_in: RecipeUpdate
    ) -> Optional[Recipe]:
        recipe = self._recipes.get(recipe_id)
        if recipe is None:
            return None
        update_data = recipe_in.model_dump(exclude_unset=True, exclude_none=True)
        updated_recipe = recipe.model_copy(update=update_data)
        self._recipes[recipe_id] = updated_recipe
        return updated_recipe

    def delete_recipe(self, recipe_id: UUID) -> bool:
        return self._recipes.pop(recipe_id, None) is not None


class MongoRecipeRepository:
    """MongoDB-backed repository for persistent recipe storage."""

    def __init__(self, client: MongoClient, db_name: str, collection_name: str) -> None:
        self._collection: Collection = client[db_name][collection_name]

    @staticmethod
    def _document_to_recipe(document: Dict[str, Any]) -> Recipe:
        data = {**document}
        recipe_id = data.pop("_id", data.pop("id", None))
        if recipe_id is None:
            raise ValueError("Missing recipe identifier in Mongo document")
        data["id"] = UUID(str(recipe_id))
        return Recipe(**data)

    @staticmethod
    def _recipe_to_document(recipe: Recipe) -> Dict[str, Any]:
        doc = recipe.model_dump()
        doc["_id"] = str(doc.pop("id"))
        return doc

    def list_recipes(self) -> List[Recipe]:
        documents = list(self._collection.find())
        return [self._document_to_recipe(doc) for doc in documents]

    def get_recipe(self, recipe_id: UUID) -> Optional[Recipe]:
        document = self._collection.find_one({"_id": str(recipe_id)})
        if document is None:
            return None
        return self._document_to_recipe(document)

    def create_recipe(self, recipe_in: RecipeCreate) -> Recipe:
        recipe = Recipe(**recipe_in.model_dump())
        self._collection.insert_one(self._recipe_to_document(recipe))
        return recipe

    def update_recipe(
        self, recipe_id: UUID, recipe_in: RecipeUpdate
    ) -> Optional[Recipe]:
        update_data = recipe_in.model_dump(exclude_unset=True, exclude_none=True)
        if not update_data:
            return self.get_recipe(recipe_id)
        document = self._collection.find_one_and_update(
            {"_id": str(recipe_id)},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER,
        )
        if document is None:
            return None
        return self._document_to_recipe(document)

    def delete_recipe(self, recipe_id: UUID) -> bool:
        result = self._collection.delete_one({"_id": str(recipe_id)})
        return result.deleted_count > 0
