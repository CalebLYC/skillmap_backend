from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from app.providers.providers import get_db
from app.main import app
from tests.common.fake_db import FakeDB


@pytest_asyncio.fixture
async def async_client():
    app.dependency_overrides[get_db] = lambda: FakeDB()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


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
