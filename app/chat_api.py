"""Chat endpoints that integrate with OpenAI and recipes CRUD."""

from __future__ import annotations

from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from openai import OpenAI
from pydantic import BaseModel, Field

from .config import get_settings
from .dependencies import get_recipe_repository
from .models import RecipeCreate, RecipeRead
from .repositories import RecipeRepository

router = APIRouter(prefix="/chat", tags=["chat"])

SYSTEM_PROMPT = (
    "You are KitchenPal, a helpful culinary assistant. Always respond with JSON "
    "that contains a short natural-language reply and up to three structured "
    "recipe suggestions. The reply should summarize what you created or how "
    "you improved an incoming recipe."
)

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    suggestions: List[RecipeCreate] = Field(default_factory=list)


class ChatRecipeSaveRequest(BaseModel):
    recipe: RecipeCreate


def _build_openai_client(api_key: str) -> OpenAI:
    settings = get_settings()
    return OpenAI(api_key=api_key, base_url=settings.openai_base_url)


def _build_openai_input(messages: List[ChatMessage]):
    payload = [
        {
            "role": "system",
            "content": [{"type": "text", "text": SYSTEM_PROMPT}],
        }
    ]
    for message in messages:
        payload.append(
            {
                "role": message.role,
                "content": [{"type": "text", "text": message.content}],
            }
        )
    return payload


@router.post("/respond", response_model=ChatResponse)
def chat_with_assistant(
    chat_request: ChatRequest,
    openai_key: Optional[str] = Header(default=None, alias="X-OpenAI-Key"),
) -> ChatResponse:
    settings = get_settings()
    api_key = (openai_key or settings.openai_api_key or "").strip()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide X-OpenAI-Key header or RECIPES_OPENAI_API_KEY env var.",
        )

    client = _build_openai_client(api_key)
    try:
        response = client.responses.parse(
            model=chat_request.model or settings.openai_model,
            input=_build_openai_input(chat_request.messages),
            response_format=ChatResponse,
        )
    except Exception as exc:  # pragma: no cover - network failure path
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"OpenAI request failed: {exc}",
        ) from exc

    return response


@router.post("/recipes", response_model=RecipeRead, status_code=status.HTTP_201_CREATED)
def save_chat_recipe(
    request: ChatRecipeSaveRequest,
    repo: RecipeRepository = Depends(get_recipe_repository),
) -> RecipeRead:
    return repo.create_recipe(request.recipe)
