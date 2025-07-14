from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from app.db.repositories.permission_repository import PermissionRepository
from app.db.repositories.role_repository import RoleRepository
from app.providers.providers import get_db
from app.main import app
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
    return RoleService(
        role_repos=role_repo, permission_repos=permission_repo
    )



@pytest_asyncio.fixture
async def async_client(shared_fake_db):
    app.dependency_overrides[get_db] = lambda: shared_fake_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
