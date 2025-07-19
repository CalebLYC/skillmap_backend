import pytest


async def create_permission(async_client):
    payload = {"code": "users:read", "description": "Permission to read users"}
    response = await async_client.post("/permissions/", json=payload)
    assert response.status_code == 201

    payload = {"code": "users:update", "description": "Permission to update users"}
    response = await async_client.post("/permissions/", json=payload)
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_create_role(bypass_role_and_permission_async_client):
    await create_permission(bypass_role_and_permission_async_client)
    payload = {"name": "user", "permissions": ["users:read"]}
    response = await bypass_role_and_permission_async_client.post(
        "/roles/", json=payload
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "user"


@pytest.mark.asyncio
async def test_list_roles(bypass_permission_async_client):
    # First create a permission to test retrieval
    payload = {"name": "user"}
    await bypass_permission_async_client.post("/roles/", json=payload)
    response = await bypass_permission_async_client.get("/roles/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == "user"


@pytest.mark.asyncio
async def test_get_role(bypass_permission_async_client):
    # First create a permission to test retrieval
    payload = {"name": "user"}
    create_response = await bypass_permission_async_client.post("/roles/", json=payload)
    assert create_response.status_code == 201
    created_data = create_response.json()

    response = await bypass_permission_async_client.get(f"/roles/{created_data['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "user"


@pytest.mark.asyncio
async def test_update_role(bypass_role_and_permission_async_client):
    await create_permission(bypass_role_and_permission_async_client)

    # First create a permission to test update
    payload = {"name": "user", "permissions": ["users:read"]}
    create_response = await bypass_role_and_permission_async_client.post(
        "/roles/", json=payload
    )
    assert create_response.status_code == 201
    created_data = create_response.json()

    update_payload = {"name": "users:update", "description": "Updated description"}
    response = await bypass_role_and_permission_async_client.put(
        f"/roles/{created_data['id']}", json=update_payload
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "users:update"


@pytest.mark.asyncio
async def test_delete_role(bypass_permission_async_client):
    # First create a permission to test deletion
    payload = {"name": "user"}
    create_response = await bypass_permission_async_client.post("/roles/", json=payload)
    assert create_response.status_code == 201
    created_data = create_response.json()

    response = await bypass_permission_async_client.delete(
        f"/roles/{created_data['id']}"
    )
    assert response.status_code == 204

    # Verify deletion
    get_response = await bypass_permission_async_client.get(
        f"/roles/{created_data['id']}"
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_all_roles(bypass_permission_async_client):
    # First create a permission to test deletion
    payload = {"name": "user"}
    await bypass_permission_async_client.post("/roles/", json=payload)

    response = await bypass_permission_async_client.delete("/roles/")
    assert response.status_code == 204

    # Verify all permissions are deleted
    list_response = await bypass_permission_async_client.get("/roles/")
    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data) == 0


@pytest.mark.asyncio
async def test_add_permissions_to_role(bypass_role_and_permission_async_client):
    await create_permission(bypass_role_and_permission_async_client)

    # First create a role to test adding permissions
    payload = {"name": "user"}
    create_response = await bypass_role_and_permission_async_client.post(
        "/roles/", json=payload
    )
    assert create_response.status_code == 201
    created_data = create_response.json()

    # Add permissions to the role
    update_payload = {"permissions": ["users:read", "users:update"]}
    response = await bypass_role_and_permission_async_client.patch(
        f"/roles/{created_data['id']}/permissions", json=update_payload
    )
    assert response.status_code == 200
    data = response.json()
    assert "users:read" in data["permissions"]
    assert "users:update" in data["permissions"]

    get_response = await bypass_role_and_permission_async_client.get(
        f"/roles/{created_data['id']}"
    )
    assert get_response.status_code == 200
    get_data = response.json()
    assert "users:read" in data["permissions"]
    assert "users:update" in data["permissions"]


@pytest.mark.asyncio
async def test_remove_permissions_from_role(bypass_role_and_permission_async_client):
    await create_permission(bypass_role_and_permission_async_client)

    # First create a role to test removing permissions
    payload = {"name": "user", "permissions": ["users:read", "users:update"]}
    create_response = await bypass_role_and_permission_async_client.post(
        "/roles/", json=payload
    )
    assert create_response.status_code == 201
    created_data = create_response.json()

    # Remove permissions from the role
    update_payload = {"permissions": ["users:read"]}
    response = await bypass_role_and_permission_async_client.patch(
        f"/roles/{created_data['id']}/permissions/remove", json=update_payload
    )
    assert response.status_code == 200
    data = response.json()
    assert "users:read" not in data["permissions"]
    assert "users:update" in data["permissions"]

    get_response = await bypass_role_and_permission_async_client.get(
        f"/roles/{created_data['id']}"
    )
    assert get_response.status_code == 200
    get_data = response.json()
    assert "users:read" not in get_data["permissions"]
    assert "users:update" in get_data["permissions"]


@pytest.mark.asyncio
async def test_add__remove_inherited_role(bypass_role_and_permission_async_client):
    await create_permission(bypass_role_and_permission_async_client)

    # First create a role to test adding inherited roles
    payload = {"name": "user"}
    create_response = await bypass_role_and_permission_async_client.post(
        "/roles/", json=payload
    )
    assert create_response.status_code == 201
    created_data = create_response.json()
    admin_response = await bypass_role_and_permission_async_client.post(
        "/roles/", json={"name": "admin"}
    )
    assert admin_response.status_code == 201

    # Add inherited role
    inherited_role_payload = {"role": "admin"}
    response = await bypass_role_and_permission_async_client.patch(
        f"/roles/{created_data['id']}/inherit", json=inherited_role_payload
    )
    assert response.status_code == 200
    data = response.json()
    assert "admin" in data["inherited_roles"]

    get_response = await bypass_role_and_permission_async_client.get(
        f"/roles/{created_data['id']}"
    )
    assert get_response.status_code == 200
    get_data = response.json()
    assert "admin" in get_data["inherited_roles"]

    remove_response = await bypass_role_and_permission_async_client.patch(
        f"/roles/{created_data['id']}/inherit/remove", json={"role": "admin"}
    )
    assert remove_response.status_code == 200
    remove_data = remove_response.json()
    assert "admin" not in remove_data["inherited_roles"]
    assert remove_data["id"] == created_data["id"]


@pytest.mark.asyncio
async def test_inherited_role_circular_dependency(
    bypass_role_and_permission_async_client,
):
    await create_permission(bypass_role_and_permission_async_client)

    # First create a role to test circular dependency
    payload = {"name": "user"}
    create_response = await bypass_role_and_permission_async_client.post(
        "/roles/", json=payload
    )
    assert create_response.status_code == 201
    created_data = create_response.json()

    # Attempt to add the same role as an inherited role
    inherited_role_payload = {"role": "user"}
    response = await bypass_role_and_permission_async_client.patch(
        f"/roles/{created_data['id']}/inherit", json=inherited_role_payload
    )
    assert response.status_code == 400

    admin_create_response = await bypass_role_and_permission_async_client.post(
        "/roles/", json={"name": "admin"}
    )
    assert admin_create_response.status_code == 201
    admin_created_data = admin_create_response.json()
    inherited_admin_role_payload = {"role": "admin"}
    admin_response = await bypass_role_and_permission_async_client.patch(
        f"/roles/{created_data['id']}/inherit", json=inherited_admin_role_payload
    )
    assert admin_response.status_code == 200

    inherited_user_role_payload = {"role": "user"}
    user_response = await bypass_role_and_permission_async_client.patch(
        f"/roles/{admin_created_data['id']}/inherit", json=inherited_user_role_payload
    )
    assert user_response.status_code == 400


@pytest.mark.asyncio
async def test_role_permission_not_exist(bypass_permission_async_client):
    # Attempt to add a non-existent permission to a role
    payload = {"name": "user"}
    create_response = await bypass_permission_async_client.post("/roles/", json=payload)
    assert create_response.status_code == 201
    created_data = create_response.json()

    update_payload = {"permissions": ["non_existent_permission"]}
    response = await bypass_permission_async_client.patch(
        f"/roles/{created_data['id']}/permissions", json=update_payload
    )
    assert response.status_code == 400
    data = response.json()
    assert (
        data["detail"]
        == "Permission 'non_existent_permission' not found. Please create it first."
    )


@pytest.mark.asyncio
async def test_role_not_exist(bypass_permission_async_client):
    # Attempt to get a non-existent role
    response = await bypass_permission_async_client.get("/roles/999999")
    assert response.status_code == 422
    # data = response.json()
    # assert data["detail"] == "Role not found"
    response = await bypass_permission_async_client.get(
        "/roles/687a84a6baa4636cc28e9424"
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Error getting role: Role not found"

    # Attempt to update a non-existent role
    update_payload = {"name": "non_existent_role"}
    response = await bypass_permission_async_client.put(
        "/roles/999999", json=update_payload
    )
    assert response.status_code == 422

    # Attempt to delete a non-existent role
    response = await bypass_permission_async_client.delete(
        "/roles/687a84a6baa4636cc28e9424"
    )
    assert response.status_code == 404
