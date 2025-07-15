import pytest


async def create_permission(async_client):
    payload = {"code": "users:read", "description": "Permission to read users"}
    response = await async_client.post("/permissions/", json=payload)
    assert response.status_code == 201

    payload = {"code": "users:update", "description": "Permission to update users"}
    response = await async_client.post("/permissions/", json=payload)
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_create_role(async_client):
    await create_permission(async_client)
    payload = {"name": "user", "permissions": ["users:read"]}
    response = await async_client.post("/roles/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "user"


@pytest.mark.asyncio
async def test_list_roles(async_client):
    # First create a permission to test retrieval
    payload = {"name": "user"}
    await async_client.post("/roles/", json=payload)
    response = await async_client.get("/roles/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == "user"


@pytest.mark.asyncio
async def test_get_role(async_client):
    # First create a permission to test retrieval
    payload = {"name": "user"}
    create_response = await async_client.post("/roles/", json=payload)
    assert create_response.status_code == 201
    created_data = create_response.json()

    response = await async_client.get(f"/roles/{created_data['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "user"


@pytest.mark.asyncio
async def test_update_role(async_client):
    await create_permission(async_client)

    # First create a permission to test update
    payload = {"name": "user", "permissions": ["users:read"]}
    create_response = await async_client.post("/roles/", json=payload)
    assert create_response.status_code == 201
    created_data = create_response.json()

    update_payload = {"name": "users:update", "description": "Updated description"}
    response = await async_client.put(
        f"/roles/{created_data['id']}", json=update_payload
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "users:update"


@pytest.mark.asyncio
async def test_delete_role(async_client):
    # First create a permission to test deletion
    payload = {"name": "user"}
    create_response = await async_client.post("/roles/", json=payload)
    assert create_response.status_code == 201
    created_data = create_response.json()

    response = await async_client.delete(f"/roles/{created_data['id']}")
    assert response.status_code == 204

    # Verify deletion
    get_response = await async_client.get(f"/roles/{created_data['id']}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_all_roles(async_client):
    # First create a permission to test deletion
    payload = {"name": "user"}
    await async_client.post("/roles/", json=payload)

    response = await async_client.delete("/roles/")
    assert response.status_code == 204

    # Verify all permissions are deleted
    list_response = await async_client.get("/roles/")
    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data) == 0


@pytest.mark.asyncio
async def test_add_permissions_to_role(async_client):
    await create_permission(async_client)

    # First create a role to test adding permissions
    payload = {"name": "user"}
    create_response = await async_client.post("/roles/", json=payload)
    assert create_response.status_code == 201
    created_data = create_response.json()

    # Add permissions to the role
    update_payload = {"permissions": ["users:read", "users:update"]}
    response = await async_client.patch(
        f"/roles/{created_data['id']}/permissions", json=update_payload
    )
    assert response.status_code == 200
    data = response.json()
    assert "users:read" in data["permissions"]
    assert "users:update" in data["permissions"]

    get_response = await async_client.get(f"/roles/{created_data['id']}")
    assert get_response.status_code == 200
    get_data = response.json()
    assert "users:read" in data["permissions"]
    assert "users:update" in data["permissions"]


@pytest.mark.asyncio
async def test_remove_permissions_from_role(async_client):
    await create_permission(async_client)

    # First create a role to test removing permissions
    payload = {"name": "user", "permissions": ["users:read", "users:update"]}
    create_response = await async_client.post("/roles/", json=payload)
    assert create_response.status_code == 201
    created_data = create_response.json()

    # Remove permissions from the role
    update_payload = {"permissions": ["users:read"]}
    response = await async_client.patch(
        f"/roles/{created_data['id']}/permissions/remove", json=update_payload
    )
    assert response.status_code == 200
    data = response.json()
    assert "users:read" not in data["permissions"]
    assert "users:update" in data["permissions"]

    get_response = await async_client.get(f"/roles/{created_data['id']}")
    assert get_response.status_code == 200
    get_data = response.json()
    assert "users:read" not in get_data["permissions"]
    assert "users:update" in get_data["permissions"]


@pytest.mark.asyncio
async def test_add__remove_inherited_role(async_client):
    await create_permission(async_client)

    # First create a role to test adding inherited roles
    payload = {"name": "user"}
    create_response = await async_client.post("/roles/", json=payload)
    assert create_response.status_code == 201
    created_data = create_response.json()
    admin_response = await async_client.post("/roles/", json={"name": "admin"})
    assert admin_response.status_code == 201

    # Add inherited role
    inherited_role_payload = {"role": "admin"}
    response = await async_client.patch(
        f"/roles/{created_data['id']}/inherit", json=inherited_role_payload
    )
    assert response.status_code == 200
    data = response.json()
    assert "admin" in data["inherited_roles"]

    get_response = await async_client.get(f"/roles/{created_data['id']}")
    assert get_response.status_code == 200
    get_data = response.json()
    assert "admin" in get_data["inherited_roles"]

    remove_response = await async_client.patch(
        f"/roles/{created_data['id']}/inherit/remove", json={"role": "admin"}
    )
    assert remove_response.status_code == 200
    remove_data = remove_response.json()
    assert "admin" not in remove_data["inherited_roles"]
    assert remove_data["id"] == created_data["id"]


@pytest.mark.asyncio
async def test_inherited_role_circular_dependency(async_client):
    await create_permission(async_client)

    # First create a role to test circular dependency
    payload = {"name": "user"}
    create_response = await async_client.post("/roles/", json=payload)
    assert create_response.status_code == 201
    created_data = create_response.json()

    # Attempt to add the same role as an inherited role
    inherited_role_payload = {"role": "user"}
    response = await async_client.patch(
        f"/roles/{created_data['id']}/inherit", json=inherited_role_payload
    )
    assert response.status_code == 400

    admin_create_response = await async_client.post("/roles/", json={"name": "admin"})
    assert admin_create_response.status_code == 201
    admin_created_data = admin_create_response.json()
    inherited_admin_role_payload = {"role": "admin"}
    admin_response = await async_client.patch(
        f"/roles/{created_data['id']}/inherit", json=inherited_admin_role_payload
    )
    assert admin_response.status_code == 200

    inherited_user_role_payload = {"role": "user"}
    user_response = await async_client.patch(
        f"/roles/{admin_created_data['id']}/inherit", json=inherited_user_role_payload
    )
    assert user_response.status_code == 400
