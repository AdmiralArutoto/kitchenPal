# 🍳 KitchenPal — Mongo + AI Recipe Assistant

KitchenPal combines a FastAPI backend, MongoDB persistence, and an OpenAI-powered chat assistant. Track recipes with full CRUD support, brainstorm new dishes with BYOK (bring-your-own-key) chat, and store favorites straight from the conversation into your catalog. A lightweight HTML/CSS/JS frontend ships with the API so everything runs from a single process.

## Features
- FastAPI service with repository/DI architecture
- MongoDB-backed recipe CRUD with UUID identifiers
- OpenAI chat endpoint for brainstorming, improving, and structuring recipes
- One-click promotion of chat suggestions into the recipe database
- Frontend catalog with cards, edit/delete controls, and chat UI (served from `/`)
- Test suite using the in-memory repository for isolated API checks

## Project Structure

```bash
kitchenPal/
├── main.py              # FastAPI entrypoint
├── app/
│   ├── api.py           # /recipes CRUD routes
│   ├── chat_api.py      # /chat endpoints + BYOK logic
│   ├── config.py        # Settings (env-driven)
│   ├── dependencies.py  # Repository & Mongo wiring
│   ├── models.py        # Pydantic models
│   ├── repositories.py  # InMemory + Mongo repositories
│   └── __init__.py
├── frontend/            # Static HTML/CSS/JS interface (served at /)
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── tests/
│   └── test_recipes_api.py
├── pyproject.toml
├── uv.lock
└── Dockerfile
```

## Requirements

- Python 3.12+
- MongoDB instance (local Docker or managed service)
- An OpenAI API key for chat (`gpt-4o-mini` by default)
- [`uv`](https://github.com/astral-sh/uv) for dependency management (or plain `pip`)

## Setup

1. **Clone & enter the repo**
   ```bash
   git clone https://github.com/EASS-HIT-PART-A-2025-CLASS-VIII/kitchenPal.git
   cd kitchenPal
   ```

2. **Create `.env` (or export vars)**
   ```bash
   cp .env.example .env
   # then edit the file to add your Mongo URI + OpenAI key
   ```

3. **Install dependencies & start the API**
   ```bash
   UV_CACHE_DIR=.uv-cache uv sync        # installs into .venv
   source .venv/bin/activate
   uv run uvicorn main:app --reload
   ```

4. **Open the UI** — visit http://localhost:8000/ for the catalog/chat interface or http://localhost:8000/docs for the OpenAPI explorer.

### Docker

```bash
docker build -t kitchenpal .
docker run -e RECIPES_MONGODB_URI=... -p 8000:8000 kitchenpal
```

## Configuration

| Env Var | Default | Description |
| --- | --- | --- |
| `RECIPES_APP_NAME` | `Recipe Assistant API` | FastAPI title + docs branding |
| `RECIPES_DEBUG` | `False` | Toggles uvicorn reload + verbose error pages |
| `RECIPES_MONGODB_URI` | `mongodb://localhost:27017/recipes` | Mongo connection URI (database optional) |
| `RECIPES_MONGODB_DB` | `recipes` | Mongo database name |
| `RECIPES_MONGODB_COLLECTION` | `recipes` | Collection storing recipe documents |
| `RECIPES_OPENAI_MODEL` | `gpt-4o-mini` | Default model for `/chat/respond` |
| `RECIPES_OPENAI_BASE_URL` | `https://api.openai.com/v1` | Override for compatible OpenAI endpoints |
| `RECIPES_OPENAI_API_KEY` | *(empty)* | Optional fallback when the `X-OpenAI-Key` header is missing |

> NOTE: The OpenAI key is *never* stored server-side. The frontend asks for it and sends it as the `X-OpenAI-Key` header per request.

## API Overview

### Recipes CRUD

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/recipes/` | List every stored recipe |
| `POST` | `/recipes/` | Create a new recipe (validated via `RecipeCreate`) |
| `GET` | `/recipes/{id}` | Fetch a single recipe by UUID |
| `PUT` | `/recipes/{id}` | Update any subset of fields |
| `DELETE` | `/recipes/{id}` | Remove a recipe |

Recipe payloads use text fields, `ingredients`/`steps` arrays, and optional `tags`. IDs are UUIDv4 strings even when persisted in Mongo.

### Chat + BYOK Flow

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/chat/respond` | Proxy to OpenAI Responses API, returning `{ reply, suggestions[] }`. Requires `X-OpenAI-Key` header. |
| `POST` | `/chat/recipes` | Persist a recipe suggestion (wraps `/recipes/` create) |

`/chat/respond` accepts:

```jsonc
{
  "messages": [
    {"role": "user", "content": "Need a vegan brunch idea"}
  ],
  "model": "gpt-4o-mini" // optional override
}
```

Responses always comply with a JSON schema so the frontend can safely parse structured suggestions.

## Frontend

- Served automatically at `/` (HTML) and `/app/*` (assets)
- Card-style catalog with edit/delete buttons per recipe
- Recipe form doubles for create/update
- Chat panel collects an OpenAI key, shows assistant replies, and lists suggested recipes with a `Save to Catalog` CTA

No extra build tooling is required—static assets live in `frontend/` and ship with the API.

## Tests

```bash
UV_CACHE_DIR=.uv-cache uv run pytest
```

Tests override the Mongo repository with the in-memory implementation so they remain fast and deterministic. If you cannot download packages (e.g., offline environment), syncing dependencies will fail—install them by other means or run tests where outbound network is allowed.

## License

Using the *Works Today, Might Not Tomorrow* License.
