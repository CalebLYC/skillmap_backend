import pytest
from app.schemas.user import UserCreateSchema, UserUpdateSchema
from app.db.user_repository import UserRepository
from app.services.auth.user_service import UserService
from tests.common.fake_db import FakeDB


@pytest.fixture
def service():
    db = FakeDB()
    repo = UserRepository(db)
    return UserService(repo)


@pytest.mark.asyncio
async def test_create_user(service):
    user_data = UserCreateSchema(
        full_name="John", email="john@example.com", password="secret"
    )
    user = await service.create_user(user_data)
    assert user.full_name == "John"
    assert user.email == "john@example.com"


@pytest.mark.asyncio
async def test_get_user(service):
    user_data = UserCreateSchema(
        full_name="Jane", email="jane@example.com", password="pass"
    )
    created = await service.create_user(user_data)
    fetched = await service.get_user(created.id)
    assert fetched.email == "jane@example.com"


@pytest.mark.asyncio
async def test_update_user(service):
    user_data = UserCreateSchema(full_name="Foo", email="foo@bar.com", password="baz")
    created = await service.create_user(user_data)
    updated = await service.update_user(created.id, UserUpdateSchema(full_name="Bar"))
    assert updated.full_name == "Bar"


@pytest.mark.asyncio
async def test_delete_user(service):
    user_data = UserCreateSchema(
        full_name="Delete", email="del@me.com", password="gone"
    )
    created = await service.create_user(user_data)
    result = await service.delete_user(created.id)
    assert result is True
