import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from unittest.mock import AsyncMock

from app.db.repositories.permission_repository import PermissionRepository
from app.db.repositories.role_repository import RoleRepository
from app.schemas.user import UserCreateSchema
from app.services.auth.otp_service import OTPService
from app.db.repositories.otp_repository import OTPRepository
from app.db.repositories.user_repository import UserRepository
from app.schemas.otp import (
    OTPRequestSchema,
    OTPVerifyResponseSchema,
    OTPVerifySchema,
    OTPResponseSchema,
)
from app.models.OTP import OTPModel
from app.models.User import UserModel
from app.services.auth.user_service import UserService


# --- Fixtures pour les mocks des dépôts et le service ---


@pytest.fixture
def otp_service(shared_fake_db) -> OTPService:
    """Fournit une instance de OTPService avec les dépôts mockés."""
    # Vous pouvez ajuster otp_expiry_minutes et otp_length ici si nécessaire pour des tests spécifiques
    return OTPService(
        otp_repos=OTPRepository(shared_fake_db),
        user_repos=UserRepository(shared_fake_db),
        otp_expiry_minutes=5,
        otp_length=6,
    )


@pytest.fixture
def user_service(shared_fake_db):
    user_repo = UserRepository(shared_fake_db)
    role_repo = RoleRepository(shared_fake_db)
    permission_repo = PermissionRepository(shared_fake_db)
    return UserService(
        user_repo=user_repo, role_repos=role_repo, permission_repos=permission_repo
    )


# --- Tests pour OTPService.request_otp ---


@pytest.mark.asyncio
async def test_request_otp_success(
    otp_service: OTPService,
    user_service: UserService,
):
    """
    Teste la requête d'OTP réussie : l'utilisateur existe et l'OTP est créé.
    """
    user_data = UserCreateSchema(
        first_name="John",
        last_name="Doe",
        email="test@gmail.com",
        password="secret",
        phone_number="90000000",
    )
    user = await user_service.create_user(user_data)

    request_schema = OTPRequestSchema(email=user.email)
    response = await otp_service.request_otp(request_schema)

    assert isinstance(response, OTPResponseSchema)
    assert response.detail.startswith("OTP sent successfully")


@pytest.mark.asyncio
async def test_request_otp_user_not_found(
    otp_service: OTPService,
):
    """
    Teste la requête d'OTP quand l'utilisateur n'est pas trouvé.
    """
    request_schema = OTPRequestSchema(email="nonexistent@example.com")

    with pytest.raises(HTTPException) as exc_info:
        await otp_service.request_otp(request_schema)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "User with this email not found."


# --- Tests pour OTPService.verify_otp ---


@pytest.mark.asyncio
async def test_verify_otp_success(otp_service: OTPService, user_service: UserService):
    """
    Teste la vérification d'OTP réussie : OTP valide, non expiré et non utilisé.
    """

    user_data = UserCreateSchema(
        first_name="John",
        last_name="Doe",
        email="test@gmail.com",
        password="secret",
        phone_number="90000000",
    )
    user = await user_service.create_user(user_data)

    request_schema = OTPRequestSchema(email=user.email)
    response = await otp_service.request_otp(request_schema)

    verify_schema = OTPVerifySchema(email=user.email, code=response.code)
    response = await otp_service.verify_otp(verify_schema)

    assert isinstance(response, OTPVerifyResponseSchema)
    assert response.detail == "OTP verified successfully."
    assert response.user.is_verified is True
    assert response.user.is_active is True
    assert response.otp.is_used is True


@pytest.mark.asyncio
async def test_verify_otp_invalid_code(
    otp_service: OTPService, user_service: UserService
):
    """
    Teste la vérification d'OTP avec un code invalide (non trouvé en base).
    """

    user_data = UserCreateSchema(
        first_name="John",
        last_name="Doe",
        email="test@example.com",
        password="secret",
        phone_number="90000000",
    )
    await user_service.create_user(user_data)

    verify_schema = OTPVerifySchema(email="test@example.com", code="000000")

    with pytest.raises(HTTPException) as exc_info:
        await otp_service.verify_otp(verify_schema)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Invalid OTP or OTP already used/expired."


@pytest.mark.asyncio
async def test_verify_otp_expired(otp_service: OTPService, user_service: UserService):
    """
    Teste la vérification d'OTP avec un code expiré.
    """
    user_data = UserCreateSchema(
        first_name="John",
        last_name="Doe",
        email="test@gmail.com",
        password="secret",
        phone_number="90000000",
    )
    await user_service.create_user(user_data)

    verify_schema = OTPVerifySchema(email="test@gmail.com", code="123456")

    with pytest.raises(HTTPException) as exc_info:
        await otp_service.verify_otp(verify_schema)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail.startswith("Invalid OTP")


@pytest.mark.asyncio
async def test_verify_otp_already_used(
    otp_service: OTPService, user_service: UserService
):
    """
    Teste la vérification d'OTP avec un code déjà utilisé.
    """
    user_data = UserCreateSchema(
        first_name="John",
        last_name="Doe",
        email="test@gmail.com",
        password="secret",
        phone_number="90000000",
    )
    await user_service.create_user(user_data)

    verify_schema = OTPVerifySchema(email="test@gmail.com", code="123456")

    with pytest.raises(HTTPException) as exc_info:
        await otp_service.verify_otp(verify_schema)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail.startswith("Invalid OTP")


@pytest.mark.asyncio
async def test_verify_otp_with_inexistant_user(
    otp_service: OTPService,
):
    """
    Teste la vérification d'OTP avec un utilisateur inexistant.
    """
    verify_schema = OTPVerifySchema(email="test@gmail.com", code="123456")

    with pytest.raises(HTTPException) as exc_info:
        await otp_service.verify_otp(verify_schema)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail.startswith("User with this email not found")
