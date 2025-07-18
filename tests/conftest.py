from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from app.db.repositories.permission_repository import PermissionRepository
from app.db.repositories.role_repository import RoleRepository
from app.models.User import UserModel
from app.providers.auth_provider import auth_middleware
from app.providers.providers import get_db
from app.main import app
from app.services.auth.permission_service import PermissionService
from app.services.auth.role_service import RoleService
from tests.common.fake_db import FakeDB


@pytest.fixture
def override_get_db():
    def _override():
        return FakeDB()

    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def new_fake_db():
    return FakeDB()


@pytest.fixture(scope="session")
def shared_fake_db():
    """Instance partagée de FakeDB pour toute la session de test"""
    return FakeDB()


@pytest.fixture(autouse=True)
def clean_db(shared_fake_db):
    """Nettoie la DB avant chaque test"""
    shared_fake_db.collections.clear()
    yield
    # Pas besoin de nettoyer après, le prochain test le fera


@pytest.fixture
def role_service(shared_fake_db):
    role_repo = RoleRepository(shared_fake_db)
    permission_repo = PermissionRepository(shared_fake_db)
    return RoleService(role_repos=role_repo, permission_repos=permission_repo)


@pytest.fixture
def permission_service(shared_fake_db):
    role_repo = RoleRepository(shared_fake_db)
    permission_repo = PermissionRepository(shared_fake_db)
    return PermissionService(role_repos=role_repo, permission_repos=permission_repo)


@pytest_asyncio.fixture
async def async_client(shared_fake_db):
    app.dependency_overrides[get_db] = lambda: shared_fake_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_async_client(async_client):
    app.dependency_overrides[auth_middleware] = lambda: UserModel(
        id="test_user_id",
        email="test@example.com",
        first_name="User",
        last_name="Test",
        password="testpasswordencrypted",
        roles=["user"],
    )

    yield async_client


@pytest_asyncio.fixture
async def admin_async_client(async_client):
    payload = {"name": "admin"}
    response = await async_client.post("/roles/", json=payload)
    assert response.status_code == 201
    app.dependency_overrides[auth_middleware] = lambda: UserModel(
        id="test_user_id",
        email="admin@example.com",
        first_name="Admin",
        last_name="Test",
        password="testpasswordencrypted",
        roles=["admin"],
    )

    yield async_client


@pytest_asyncio.fixture
async def super_async_client(async_client):
    app.dependency_overrides[auth_middleware] = lambda: UserModel(
        id="superadmin_user_id",
        email="superadmin@example.com",
        first_name="Superadmin",
        last_name="Test",
        password="testpasswordencrypted",
        roles=["superadmin"],
    )

    yield async_client
