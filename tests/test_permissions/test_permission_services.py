import pytest

from app.db.repositories.permission_repository import PermissionRepository
from app.db.repositories.role_repository import RoleRepository
from app.schemas.role import PermissionCreateSchema, PermissionUpdateSchema, RoleCreateSchema
from app.schemas.user import UserReadSchema
from app.services.auth.permission_service import PermissionService


@pytest.fixture
def service(shared_fake_db):
    role_repo = RoleRepository(shared_fake_db)
    permission_repo = PermissionRepository(shared_fake_db)
    return PermissionService(
        role_repos=role_repo, permission_repos=permission_repo
    )


@pytest.mark.asyncio
async def test_create_permission(service):
    permission_data = PermissionCreateSchema(code="users:read",description="Permission to read users")
    created = await service.create_permission(permission=permission_data)
    assert created.code == "users:read"

@pytest.mark.asyncio
async def test_list_permissions(service):
    permission_data = PermissionCreateSchema(code="users:read",description="Permission to read users")
    await service.create_permission(permission=permission_data)
    fetched = await service.list_permissions()
    assert isinstance(fetched, list)
    assert len(fetched) > 0
    assert fetched[0].code == "users:read"

@pytest.mark.asyncio
async def test_get_permission(service):
    permission_data = PermissionCreateSchema(code="users:read",description="Permission to read users")
    created = await service.create_permission(permission=permission_data)
    fetched = await service.get_permission(permission_id=created.id)
    assert fetched.code == "users:read"

@pytest.mark.asyncio
async def test_get_permission_by_code(service):
    permission_data = PermissionCreateSchema(code="users:read",description="Permission to read users")
    created = await service.create_permission(permission=permission_data)
    fetched = await service.get_permission_by_code(permission_code="users:read")
    assert fetched.code == "users:read"
    assert fetched.id == created.id

@pytest.mark.asyncio
async def test_update_permission(service):
    permission_data = PermissionCreateSchema(code="users:read",description="Permission to read users")
    created = await service.create_permission(permission=permission_data)
    updated = await service.update_permission(permission_id=created.id, permission_update=PermissionUpdateSchema(code="users:update", description="Updated description"))
    assert updated.code == "users:update"
    assert updated.id == created.id

@pytest.mark.asyncio
async def test_delete_permission(service):
    permission_data = PermissionCreateSchema(code="users:read",description="Permission to read users")
    created = await service.create_permission(permission=permission_data)
    result = await service.delete_permission(permission_id=created.id)
    fetched = await service.list_permissions()
    assert len(fetched) == 0
    assert result is None

@pytest.mark.asyncio
async def test_delete_all_permissions(service):
    permission_data = PermissionCreateSchema(code="users:read",description="Permission to read users")
    await service.create_permission(permission=permission_data)
    result = await service.delete_all_permissions()
    fetched = await service.list_permissions()
    assert len(fetched) == 0
    assert result is None

@pytest.mark.asyncio
async def test_get_all__ensure_has_permissions(service,role_service):
    permission_data = PermissionCreateSchema(code="users:read",description="Permission to read users")
    await service.create_permission(permission=permission_data)
    await role_service.create_role(RoleCreateSchema(name="user", permissions=["users:read"]))
    user = UserReadSchema(
        id="test_user_id",
        first_name="Test",
        last_name="User",
        email="test@gmail.com",
        permissions=["users:delete"],
        roles= ["user"]
    )
    perms = await service.get_all_permissions(user)
    perms = list(perms)
    has_perm = await service.has_permission(user, "users:read")
    is_perm = await service.ensure_permission(user, "users:read")
    assert is_perm is True
    assert has_perm is True
    assert len(perms) == 2
    assert perms[0] == "users:read"
    assert perms[1] == "users:delete"

