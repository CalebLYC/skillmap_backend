from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorDatabase
from pytest_mock import mocker
from app.core.security import SecurityUtils
from app.db.repositories.otp_repository import OTPRepository
from app.db.repositories.permission_repository import PermissionRepository
from app.db.repositories.role_repository import RoleRepository
from app.db.repositories.user_repository import UserRepository
from app.models.user import UserModel
from app.providers.auth_provider import auth_middleware
from app.providers.providers import get_db, get_settings
from app.main import app
from app.services.auth.otp_service import OTPService
from app.services.auth.permission_service import PermissionService
from app.services.auth.role_service import RoleService
from app.services.email_service import EmailService
from tests.common.fake_db import FakeDB
from app.providers.service_provider import get_otp_service as original_get_otp_service


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


@pytest_asyncio.fixture(name="otp_repo")
async def otp_repository_fixture(shared_fake_db: AsyncIOMotorDatabase) -> OTPRepository:
    return OTPRepository(db=shared_fake_db)


@pytest_asyncio.fixture(name="mock_otp_repository")
async def mock_otp_repository_fixture(mocker) -> OTPRepository:
    """Fournit un mock asynchrone pour OTPRepository, pour les tests d'endpoints.

    Args:
        mocker (_type_): _description_

    Returns:
        OTPRepository: _description_
    """
    return mocker.AsyncMock(spec=OTPRepository)


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


@pytest_asyncio.fixture(name="mock_email_service")
async def mock_email_service_fixture(mocker) -> EmailService:
    """Fournit un mock asynchrone pour EmailService.

    Args:
        mocker (_type_): _description_

    Returns:
        EmailService: _description_
    """
    mock_service = mocker.AsyncMock(spec=EmailService)
    mock_service.send_email.return_value = None
    return mock_service


@pytest.fixture
def otp_service(shared_fake_db, mock_email_service: EmailService) -> OTPService:
    """Fournit une instance de OTPService avec les dépôts mockés.

    Args:
        shared_fake_db (_type_): _description_
        mock_email_service (EmailService): _description_

    Returns:
        OTPService: _description_
    """
    return OTPService(
        otp_repos=OTPRepository(shared_fake_db),
        user_repos=UserRepository(shared_fake_db),
        email_service=mock_email_service,
        settings=get_settings(),  # Possibilité d'injecter un autre settings spécifique pour les tests
    )


@pytest_asyncio.fixture(name="override_otp_service_dependency")
def override_otp_service_dependency_fixture(
    shared_fake_db, mock_email_service: EmailService
):
    """Fournit une instance de OTPService avec les dépôts mockés.

    Args:
        shared_fake_db (_type_): _description_
        mock_email_service (EmailService): _description_

    Returns:
        OTPService: _description_
    """
    real_otp_service_instance = OTPService(
        otp_repos=OTPRepository(shared_fake_db),
        user_repos=UserRepository(shared_fake_db),
        email_service=mock_email_service,
        settings=get_settings(),  # Possibilité d'injecter un autre settings spécifique pour les tests
    )

    # Surcharge la dépendance dans l'application FastAPI
    app.dependency_overrides[original_get_otp_service] = (
        lambda: real_otp_service_instance
    )
    yield


@pytest_asyncio.fixture
async def async_client(shared_fake_db):
    app.dependency_overrides[get_db] = lambda: shared_fake_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_async_client(async_client: AsyncClient):
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
async def very_auth_async_client(async_client: AsyncClient):
    payload = {
        "email": "test@example.com",
        "first_name": "User",
        "last_name": "Test",
        "password": "testpasswordunencrypted",
        "roles": ["user"],
    }
    response = await async_client.post("/register", json=payload)
    assert response.status_code == 201
    user_data = response.json()["user"]
    user = UserModel(
        id=user_data["id"],
        email=user_data["email"],
        roles=user_data["roles"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        created_at=user_data["created_at"],
        birthday_date=user_data["birthday_date"],
        phone_number=user_data["phone_number"],
        password=SecurityUtils.hash_password("testpasswordunencrypted"),
    )

    app.dependency_overrides[auth_middleware] = lambda: user

    yield async_client


@pytest_asyncio.fixture
async def bypass_role_async_client(auth_async_client: AsyncClient, monkeypatch):
    # Patch require_role et ensure_role pour bypasser toutes vérifications de rôle
    from app.providers import auth_provider
    from app.services.auth.role_service import RoleService

    monkeypatch.setattr(auth_provider, "require_role", lambda role_name: lambda: None)

    async def always_true(self, user, role_name):
        return True

    monkeypatch.setattr(RoleService, "ensure_role", always_true)

    yield auth_async_client


@pytest_asyncio.fixture
async def bypass_permission_async_client(auth_async_client: AsyncClient, monkeypatch):
    # Patch require_permission pour bypasser toutes vérifications de permission
    from app.providers import auth_provider
    from app.services.auth.permission_service import PermissionService

    monkeypatch.setattr(
        auth_provider, "require_permission", lambda permission_code: lambda: None
    )

    async def always_true(self, user, permission_code):
        return True

    monkeypatch.setattr(PermissionService, "ensure_permission", always_true)

    yield auth_async_client


@pytest_asyncio.fixture
async def bypass_role_and_permission_async_client(
    auth_async_client: AsyncClient, monkeypatch
):
    # Patch require_role, require_permission, ensure_role, ensure_permission
    from app.providers import auth_provider
    from app.services.auth.role_service import RoleService
    from app.services.auth.permission_service import PermissionService

    monkeypatch.setattr(auth_provider, "require_role", lambda role_name: lambda: None)
    monkeypatch.setattr(
        auth_provider, "require_permission", lambda permission_code: lambda: None
    )

    async def always_true_role(self, user, role_name):
        return True

    async def always_true_perm(self, user, permission_code):
        return True

    monkeypatch.setattr(RoleService, "ensure_role", always_true_role)
    monkeypatch.setattr(PermissionService, "ensure_permission", always_true_perm)

    yield auth_async_client
