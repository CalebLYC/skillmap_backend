import pytest


@pytest.mark.asyncio
async def test_create_permission(bypass_role_async_client):
    payload = {"code": "users:read", "description": "Permission to read users"}
    response = await bypass_role_async_client.post("/permissions/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "users:read"


@pytest.mark.asyncio
async def test_list_permissions(bypass_role_async_client):
    # First create a permission to test retrieval
    payload = {"code": "users:read", "description": "Permission to read users"}
    await bypass_role_async_client.post("/permissions/", json=payload)
    response = await bypass_role_async_client.get("/permissions/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["code"] == "users:read"


@pytest.mark.asyncio
async def test_get_permission(bypass_role_async_client):
    # First create a permission to test retrieval
    payload = {"code": "users:read", "description": "Permission to read users"}
    create_response = await bypass_role_async_client.post("/permissions/", json=payload)
    assert create_response.status_code == 201
    created_data = create_response.json()

    response = await bypass_role_async_client.get(f"/permissions/{created_data['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "users:read"


@pytest.mark.asyncio
async def test_update_permission(bypass_role_async_client):
    # First create a permission to test update
    payload = {"code": "users:read", "description": "Permission to read users"}
    create_response = await bypass_role_async_client.post("/permissions/", json=payload)
    assert create_response.status_code == 201
    created_data = create_response.json()

    update_payload = {"code": "users:update", "description": "Updated description"}
    response = await bypass_role_async_client.put(
        f"/permissions/{created_data['id']}", json=update_payload
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "users:update"


@pytest.mark.asyncio
async def test_delete_permission(bypass_role_async_client):
    # First create a permission to test deletion
    payload = {"code": "users:read", "description": "Permission to read users"}
    create_response = await bypass_role_async_client.post("/permissions/", json=payload)
    assert create_response.status_code == 201
    created_data = create_response.json()

    response = await bypass_role_async_client.delete(
        f"/permissions/{created_data['id']}"
    )
    assert response.status_code == 204

    # Verify deletion
    get_response = await bypass_role_async_client.get(
        f"/permissions/{created_data['id']}"
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_all_permissions(bypass_role_async_client):
    # First create a permission to test deletion
    payload = {"code": "users:read", "description": "Permission to read users"}
    await bypass_role_async_client.post("/permissions/", json=payload)

    response = await bypass_role_async_client.delete("/permissions/")
    assert response.status_code == 204

    # Verify all permissions are deleted
    list_response = await bypass_role_async_client.get("/permissions/")
    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data) == 0
