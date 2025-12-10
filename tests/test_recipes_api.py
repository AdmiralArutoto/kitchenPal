import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_recipe_repository
from app.repositories import InMemoryRecipeRepository
from main import create_app


@pytest.fixture()
def client() -> TestClient:
    app = create_app()
    repo = InMemoryRecipeRepository()
    app.dependency_overrides[get_recipe_repository] = lambda: repo
    with TestClient(app) as test_client:
        yield test_client


def sample_recipe_payload() -> dict:
    return {
        "title": "Spicy Tomato Pasta",
        "description": "Weeknight dinner favorite.",
        "ingredients": ["pasta", "tomatoes", "garlic"],
        "steps": ["Boil pasta", "Simmer sauce", "Combine everything"],
        "tags": ["pasta", "quick"],
    }


def test_create_recipe_returns_recipe_with_id(client: TestClient):
    response = client.post("/recipes/", json=sample_recipe_payload())
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Spicy Tomato Pasta"
    assert body["id"]


def test_list_recipes_returns_all_created_recipes(client: TestClient):
    client.post("/recipes/", json=sample_recipe_payload())
    client.post(
        "/recipes/",
        json={
            "title": "idf breakfast",
            "description": None,
            "ingredients": ["marlboro red", "XL/Blue", "regret"],
            "steps": [
                "light up a cig",
                "take a sip of XL",
                "reflect on life choises...",
            ],
            "tags": [],
        },
    )

    response = client.get("/recipes/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_recipe_returns_404_for_unknown_id(client: TestClient):
    response = client.get("/recipes/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_update_recipe_replaces_fields(client: TestClient):
    created = client.post("/recipes/", json=sample_recipe_payload()).json()

    response = client.put(
        f"/recipes/{created['id']}",
        json={"tags": ["comfort"]},
    )

    assert response.status_code == 200
    assert response.json()["tags"] == ["comfort"]


def test_delete_recipe_removes_resource(client: TestClient):
    created = client.post("/recipes/", json=sample_recipe_payload()).json()

    delete_response = client.delete(f"/recipes/{created['id']}")
    assert delete_response.status_code == 204

    follow_up = client.get(f"/recipes/{created['id']}")
    assert follow_up.status_code == 404


def test_update_requires_non_empty_payload(client: TestClient):
    created = client.post("/recipes/", json=sample_recipe_payload()).json()

    response = client.put(f"/recipes/{created['id']}", json={})
    assert response.status_code == 422
