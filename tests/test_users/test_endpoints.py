import pytest


@pytest.mark.asyncio
async def test_create_user(async_client):
    payload = {
        "full_name": "Alice",
        "email": "alice@example.com",
        "password": "secret123",
    }
    response = await async_client.post("/users/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "Alice"
    assert data["email"] == "alice@example.com"


@pytest.mark.asyncio
async def test_get_user(async_client):
    payload = {"full_name": "Bob", "email": "bob@example.com", "password": "mypassword"}
    create = await async_client.post("/users/", json=payload)

    # Debug the response
    print(f"Status code: {create.status_code}")
    print(f"Response body: {create.json()}")
    user_id = create.json()["id"]

    response = await async_client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["email"] == "bob@example.com"


@pytest.mark.asyncio
async def test_update_user(async_client):
    payload = {
        "full_name": "Charlie",
        "email": "charlie@example.com",
        "password": "pass123",
    }
    create = await async_client.post("/users/", json=payload)
    user_id = create.json()["id"]

    update_data = {"full_name": "Charles"}
    response = await async_client.put(f"/users/{user_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["full_name"] == "Charles"


@pytest.mark.asyncio
async def test_delete_user(async_client):
    payload = {"full_name": "Dave", "email": "dave@example.com", "password": "pass456"}
    create = await async_client.post("/users/", json=payload)
    user_id = create.json()["id"]

    response = await async_client.delete(f"/users/{user_id}")
    assert response.status_code == 204
    # assert response.json()["detail"] == "User deleted successfully"
