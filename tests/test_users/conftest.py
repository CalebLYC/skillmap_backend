import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from app.core.providers import get_db
from app.db.user_repository import UserRepository
from app.main import app
from app.services.auth.user_service import UserService
from tests.common.fake_db import FakeDB


@pytest.fixture
def fake_user_service():
    db = FakeDB()
    repo = UserRepository(db)
    return UserService(repo)


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


@pytest_asyncio.fixture
async def async_client(shared_fake_db):
    app.dependency_overrides[get_db] = lambda: shared_fake_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
