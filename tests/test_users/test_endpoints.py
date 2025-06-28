import pytest


@pytest.mark.asyncio
async def test_create_user(async_client):
    payload = {
        "first_name": "Alice",
        "last_name": "Borderland",
        "email": "alice@example.com",
        "password": "secret123",
        "phone_number": "90000000",
    }
    response = await async_client.post("/users/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Alice"
    assert data["email"] == "alice@example.com"


@pytest.mark.asyncio
async def test_get_user(async_client):
    payload = {
        "first_name": "AlicBobe",
        "last_name": "Builder",
        "email": "bob@example.com",
        "password": "secret123",
        "phone_number": "90000000",
    }
    create = await async_client.post("/users/", json=payload)
    user_id = create.json()["id"]

    response = await async_client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["email"] == "bob@example.com"


@pytest.mark.asyncio
async def test_update_user(async_client):
    payload = {
        "first_name": "Charles",
        "last_name": "Chocolate",
        "email": "charlie@example.com",
        "password": "pass123",
        "phone_number": "90000000",
    }
    create = await async_client.post("/users/", json=payload)
    user_id = create.json()["id"]

    update_data = {"first_name": "Bob"}
    response = await async_client.put(f"/users/{user_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["first_name"] == "Bob"


@pytest.mark.asyncio
async def test_delete_user(async_client):
    payload = {
        "first_name": "Dave",
        "last_name": "Davido",
        "email": "dave@example.com",
        "password": "pass456",
        "phone_number": "90000000",
    }
    create = await async_client.post("/users/", json=payload)
    # Debug the response
    """print(f"Status code: {create.status_code}")
    print(f"Response body: {create.json()}")
    """ ""
    user_id = create.json()["id"]

    response = await async_client.delete(f"/users/{user_id}")
    assert response.status_code == 204
    # assert response.json()["detail"] == "User deleted successfully"
