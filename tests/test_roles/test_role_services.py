import pytest

from app.schemas.role import PermissionCreateSchema, RoleCreateSchema, RoleUpdateSchema
from app.schemas.user import UserReadSchema


async def create_permission(permission_service, code, description):
    permission_data = PermissionCreateSchema(code=code, description=description)
    return await permission_service.create_permission(permission=permission_data)


async def create_user_permissions(permission_service):
    await create_permission(
        permission_service=permission_service,
        code="users:read",
        description="Permission to read users",
    )
    await create_permission(
        permission_service=permission_service,
        code="users:update",
        description="Permission to update users",
    )


@pytest.mark.asyncio
async def test_create_role(role_service, permission_service):
    await create_user_permissions(permission_service)
    role_data = RoleCreateSchema(name="user", permissions=["users:read"])
    created = await role_service.create_role(role=role_data)
    assert created.name == "user"


@pytest.mark.asyncio
async def test_list_roles(role_service, permission_service):
    await create_user_permissions(permission_service)
    role_data = RoleCreateSchema(name="user", permissions=["users:read"])
    await role_service.create_role(role=role_data)
    fetched = await role_service.list_roles()
    assert isinstance(fetched, list)
    assert len(fetched) > 0
    assert fetched[0].name == "user"


@pytest.mark.asyncio
async def test_get_role(role_service, permission_service):
    await create_user_permissions(permission_service)
    role_data = RoleCreateSchema(name="user", permissions=["users:read"])
    created = await role_service.create_role(role=role_data)
    fetched = await role_service.get_role(role_id=created.id)
    assert fetched.name == "user"


@pytest.mark.asyncio
async def test_get_role_by_name(role_service, permission_service):
    await create_user_permissions(permission_service)
    role_data = RoleCreateSchema(name="user", permissions=["users:read"])
    created = await role_service.create_role(role=role_data)
    fetched = await role_service.get_role_by_name(role_name="user")
    assert fetched.name == "user"
    assert fetched.id == created.id


@pytest.mark.asyncio
async def test_update_role(role_service, permission_service):
    await create_user_permissions(permission_service)
    role_data = RoleCreateSchema(name="user", permissions=["users:read"])
    created = await role_service.create_role(role=role_data)
    updated = await role_service.update_role(
        role_id=created.id,
        role_update=RoleUpdateSchema(name="admin", permissions=["users:update"]),
    )
    assert updated.name == "admin"
    assert "users:update" in updated.permissions
    assert updated.id == created.id


@pytest.mark.asyncio
async def test_delete_role(role_service, permission_service):
    await create_user_permissions(permission_service)
    role_data = RoleCreateSchema(name="user", permissions=["users:read"])
    created = await role_service.create_role(role=role_data)
    result = await role_service.delete_role(role_id=created.id)
    fetched = await role_service.list_roles()
    assert len(fetched) == 0
    assert result is None


@pytest.mark.asyncio
async def test_delete_all_roles(role_service, permission_service):
    await create_user_permissions(permission_service)
    role_data = RoleCreateSchema(name="user", permissions=["users:read"])
    await role_service.create_role(role=role_data)
    result = await role_service.delete_all_roles()
    fetched = await role_service.list_roles()
    assert len(fetched) == 0
    assert result is None


@pytest.mark.asyncio
async def test_add_remove_permissions_to_role(role_service, permission_service):
    await create_user_permissions(permission_service)
    role_data = RoleCreateSchema(name="user", permissions=["users:read"])
    created = await role_service.create_role(role=role_data)

    updated_role = await role_service.add_permissions_to_role(
        role_id=created.id, permissions_to_add=["users:update"]
    )
    db_role = await role_service.get_role(role_id=created.id)

    assert "users:update" in db_role.permissions
    assert "users:update" in updated_role.permissions
    assert updated_role.name == "user"
    assert updated_role.id == created.id

    updated_role = await role_service.remove_permissions_from_role(
        role_id=created.id, permissions_to_remove=["users:read"]
    )
    db_role = await role_service.get_role(role_id=created.id)
    assert "users:read" not in db_role.permissions
    assert "users:read" not in updated_role.permissions
    assert updated_role.name == "user"
    assert updated_role.id == created.id


@pytest.mark.asyncio
async def test_add_remove_inherited_role(role_service, permission_service):
    await create_user_permissions(permission_service)
    created = await role_service.create_role(
        role=RoleCreateSchema(name="user", permissions=["users:read"])
    )
    await role_service.create_role(
        role=RoleCreateSchema(name="admin", permissions=["users:update"])
    )

    updated_role = await role_service.add_inherited_role(
        role_id=created.id, inherited_role_name_to_add="admin"
    )
    db_role = await role_service.get_role(role_id=created.id)

    assert "admin" in db_role.inherited_roles
    assert "admin" in updated_role.inherited_roles
    assert updated_role.name == "user"
    assert updated_role.id == created.id

    updated_role = await role_service.remove_inherited_role(
        role_id=created.id, inherited_role_to_remove_name="admin"
    )
    db_role = await role_service.get_role(role_id=created.id)
    assert "admin" not in db_role.inherited_roles
    assert "admin" not in updated_role.inherited_roles
    assert updated_role.name == "user"
    assert updated_role.id == created.id


@pytest.mark.asyncio
async def test_check_circular_inheritance(role_service, permission_service):
    await create_user_permissions(permission_service)
    created = await role_service.create_role(
        role=RoleCreateSchema(name="user", permissions=["users:read"])
    )
    # Check if circular inheritance is detected
    has_circular = await role_service._check_circular_inheritance(
        start_role_name="user", target_role_name="user"
    )
    assert has_circular is True

    await role_service.create_role(
        role=RoleCreateSchema(name="admin", permissions=["users:update"])
    )
    has_circular = await role_service._check_circular_inheritance(
        start_role_name="user", target_role_name="admin"
    )
    assert has_circular is False
    await role_service.add_inherited_role(
        role_id=created.id, inherited_role_name_to_add="admin"
    )
    has_circular = await role_service._check_circular_inheritance(
        start_role_name="user", target_role_name="admin"
    )
    assert has_circular is True


@pytest.mark.asyncio
async def test_get_user_has_ensure_roles(role_service, permission_service):
    await create_user_permissions(permission_service)
    await role_service.create_role(
        role=RoleCreateSchema(name="user", permissions=["users:read"])
    )
    await role_service.create_role(
        role=RoleCreateSchema(
            name="admin", permissions=["users:update"], inherited_roles=["user"]
        )
    )

    user = UserReadSchema(
        id="test_user_id",
        email="test@gmail.com",
        first_name="Test",
        last_name="User",
        roles=["admin"],
    )
    user_roles = await role_service.get_all_roles(user=user)

    has_role = await role_service.has_role(user=user, role_name="admin")
    is_role = await role_service.ensure_role(user=user, role_name="admin")

    assert isinstance(user_roles, set)
    assert len(user_roles) == 2
    assert "user" in user_roles
    assert "admin" in user_roles
    assert is_role is True
    assert has_role is True
