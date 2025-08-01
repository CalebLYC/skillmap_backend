import pytest
from app.db.repositories.permission_repository import PermissionRepository
from app.db.repositories.role_repository import RoleRepository
from app.schemas.user import UserCreateSchema, UserReadSchema, UserUpdateSchema
from app.db.repositories.user_repository import UserRepository
from app.services.auth.user_service import UserService
from tests.common.fake_db import FakeDB


@pytest.fixture
def service(shared_fake_db):
    # db = FakeDB()
    user_repo = UserRepository(shared_fake_db)
    role_repo = RoleRepository(shared_fake_db)
    permission_repo = PermissionRepository(shared_fake_db)
    return UserService(
        user_repo=user_repo, role_repos=role_repo, permission_repos=permission_repo
    )


@pytest.mark.asyncio
async def test_create_user(service):
    user_data = UserCreateSchema(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        password="secret",
        phone_number="90000000",
    )
    user = await service.create_user(user_data)
    assert user.first_name == "John"
    assert user.email == "john@example.com"


@pytest.mark.asyncio
async def test_list_user(service):
    user_data = UserCreateSchema(
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        password="pass",
        phone_number="90000000",
    )
    await service.create_user(user_data)
    fetched = await service.list_users()
    assert isinstance(fetched, list)
    assert len(fetched) > 0
    assert isinstance(fetched[0], UserReadSchema)
    assert fetched[0].email == "jane@example.com"


@pytest.mark.asyncio
async def test_get_user(service):
    user_data = UserCreateSchema(
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        password="pass",
        phone_number="90000000",
    )
    created = await service.create_user(user_data)
    fetched = await service.get_user(created.id)
    assert fetched.email == "jane@example.com"


@pytest.mark.asyncio
async def test_update_user(service):
    user_data = UserCreateSchema(
        first_name="Foo",
        last_name="Doo",
        email="foo@bar.com",
        password="baz",
        phone_number="90000000",
    )
    created = await service.create_user(user_data)
    updated = await service.update_user(created.id, UserUpdateSchema(first_name="Bar"))
    assert updated.first_name == "Bar"


@pytest.mark.asyncio
async def test_delete_user(service):
    user_data = UserCreateSchema(
        first_name="Delete",
        last_name="Stricto",
        email="del@me.com",
        password="gone",
        phone_number="90000000",
    )
    created = await service.create_user(user_data)
    result = await service.delete_user(created.id)
    assert result is True
