"""HTTP API routes for the recipe assistant."""

from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from .dependencies import get_recipe_repository
from .models import RecipeCreate, RecipeRead, RecipeUpdate
from .repositories import RecipeRepository

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.get("/", response_model=List[RecipeRead])
def list_recipes(
    repo: RecipeRepository = Depends(get_recipe_repository),
) -> List[RecipeRead]:
    return repo.list_recipes()


@router.post("/", response_model=RecipeRead, status_code=status.HTTP_201_CREATED)
def create_recipe(
    recipe_in: RecipeCreate, repo: RecipeRepository = Depends(get_recipe_repository)
) -> RecipeRead:
    return repo.create_recipe(recipe_in)


@router.get("/{recipe_id}", response_model=RecipeRead)
def get_recipe(
    recipe_id: UUID, repo: RecipeRepository = Depends(get_recipe_repository)
) -> RecipeRead:
    recipe = repo.get_recipe(recipe_id)
    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found."
        )
    return recipe


@router.put("/{recipe_id}", response_model=RecipeRead)
def update_recipe(
    recipe_id: UUID,
    recipe_in: RecipeUpdate,
    repo: RecipeRepository = Depends(get_recipe_repository),
) -> RecipeRead:
    recipe = repo.update_recipe(recipe_id, recipe_in)
    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found."
        )
    return recipe


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(
    recipe_id: UUID, repo: RecipeRepository = Depends(get_recipe_repository)
) -> Response:
    deleted = repo.delete_recipe(recipe_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found."
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
