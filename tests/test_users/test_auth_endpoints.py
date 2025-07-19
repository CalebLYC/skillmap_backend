import pytest


@pytest.mark.asyncio
async def test_register_success(async_client):
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "password": "password123",
        "phone_number": "123456789",
    }
    response = await async_client.post("/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "john@example.com"


@pytest.mark.asyncio
async def test_register_password_match(async_client):
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "password": "password123",
        "password_confirmation": "password123",
        "phone_number": "123456789",
    }
    response = await async_client.post("/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "john@example.com"


@pytest.mark.asyncio
async def test_register_password_mismatch(async_client):
    payload = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane@example.com",
        "password": "password123",
        "password_confirmation": "wrongpassword",
        "phone_number": "987654321",
    }
    response = await async_client.post("/register", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Password not match password confirmation"


@pytest.mark.asyncio
async def test_login_success(async_client):
    # Register first
    payload = {
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice@example.com",
        "password": "alicepass",
        "password_confirmation": "alicepass",
        "phone_number": "55555555",
    }
    await async_client.post("/register", json=payload)
    login_payload = {"email": "alice@example.com", "password": "alicepass"}
    response = await async_client.post("/login", json=login_payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "alice@example.com"


@pytest.mark.asyncio
async def test_login_wrong_password(async_client):
    # Register first
    payload = {
        "first_name": "Bob",
        "last_name": "Brown",
        "email": "bob@example.com",
        "password": "bobpass",
        "password_confirmation": "bobpass",
        "phone_number": "44444444",
    }
    await async_client.post("/register", json=payload)
    login_payload = {"email": "bob@example.com", "password": "wrongpass"}
    response = await async_client.post("/login", json=login_payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Wrong credentials"


@pytest.mark.asyncio
async def test_login_nonexistent_user(async_client):
    login_payload = {"email": "nonexistent@example.com", "password": "nopass"}
    response = await async_client.post("/login", json=login_payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Wrong credentials"


@pytest.mark.asyncio
async def test_get_me_authenticated(auth_async_client):
    response = await auth_async_client.get("/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_get_me_unauthenticated(async_client):
    response = await async_client.get("/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_logout_success(very_auth_async_client):
    response = await very_auth_async_client.delete("/logout")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_logout_unauthenticated(async_client):
    response = await async_client.delete("/logout")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_permission_endpoint_requires_admin(auth_async_client):
    # /permissions endpoints require admin role, so a normal user should get 403 or 500
    payload = {"code": "users:read", "description": "Permission to read users"}
    response = await auth_async_client.post("/permissions/", json=payload)
    # Should fail because user does not have admin role
    assert response.status_code in (403, 500)


@pytest.mark.asyncio
async def test_permission_endpoint_with_admin(bypass_role_async_client):
    # With bypass_role_async_client, should succeed
    payload = {"code": "users:read", "description": "Permission to read users"}
    response = await bypass_role_async_client.post("/permissions/", json=payload)
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_add_role_requires_permission(
    auth_async_client,
):
    # Create a role
    role_payload = {"name": "testrole", "description": "desc"}
    response = await auth_async_client.post("/roles/", json=role_payload)
    assert response.status_code in (403, 500)


@pytest.mark.asyncio
async def test_add_role_with_permission(bypass_permission_async_client):
    # With bypass_permission_async_client, should succeed
    role_payload = {"name": "testrole2", "description": "desc"}
    role_resp = await bypass_permission_async_client.post("/roles/", json=role_payload)
    assert role_resp.status_code == 201
    assert role_resp.json()["name"] == "testrole2"
