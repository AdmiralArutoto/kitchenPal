"""Domain and API models for the recipe service."""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


class RecipeBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    ingredients: List[str] = Field(..., min_length=1)
    steps: List[str] = Field(..., min_length=1)
    tags: List[str] = Field(default_factory=list)

    @field_validator("ingredients", "steps", "tags")
    @classmethod
    def validate_lists(cls, value: List[str]) -> List[str]:
        cleaned = [item.strip() for item in value]
        if any(not item for item in cleaned):
            raise ValueError(
                "Items in ingredients, steps, and tags must be non-empty strings."
            )
        return cleaned


class RecipeCreate(RecipeBase):
    """Payload for creating a recipe."""


class RecipeUpdate(BaseModel):
    """Payload for updating portions of a recipe."""

    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    ingredients: Optional[List[str]] = Field(None, min_length=1)
    steps: Optional[List[str]] = Field(None, min_length=1)
    tags: Optional[List[str]] = None

    @field_validator("ingredients", "steps", "tags")
    @classmethod
    def validate_optional_lists(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        if value is None:
            return None
        cleaned = [item.strip() for item in value]
        if any(not item for item in cleaned):
            raise ValueError(
                "Items in ingredients, steps, and tags must be non-empty strings."
            )
        return cleaned

    @model_validator(mode="after")
    def validate_non_empty_payload(self) -> "RecipeUpdate":
        if not any(
            value is not None
            for value in (
                self.title,
                self.description,
                self.ingredients,
                self.steps,
                self.tags,
            )
        ):
            raise ValueError("At least one field must be provided for update.")
        return self


class Recipe(RecipeBase):
    """Internal representation stored in repositories."""

    id: UUID = Field(default_factory=uuid4)


class RecipeRead(RecipeBase):
    """Response model exposed to API consumers."""

    id: UUID
