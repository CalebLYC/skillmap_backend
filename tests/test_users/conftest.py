import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from app.providers.providers import get_db
from app.db.repositories.user_repository import UserRepository
from app.main import app
from app.services.auth.user_service import UserService
from tests.common.fake_db import FakeDB


@pytest.fixture
def fake_user_service():
    db = FakeDB()
    repo = UserRepository(db)
    return UserService(repo)
