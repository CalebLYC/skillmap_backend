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
        code="users:delete",
        description="Permission to delete users",
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
