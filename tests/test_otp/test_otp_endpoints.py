from unittest.mock import patch
import pytest
from httpx import AsyncClient
from fastapi import HTTPException, status

from app.services.auth.otp_service import OTPService


@pytest.mark.asyncio
async def test_request_otp_success(async_client: AsyncClient):
    """
    Teste la requête d'OTP réussie pour un utilisateur existant.
    """
    user_payload = {
        "first_name": "Alice",
        "last_name": "Borderland",
        "email": "test@gmail.com",
        "password": "secret123",
        "phone_number": "90000000",
    }
    response = await async_client.post("/users/", json=user_payload)
    assert response.status_code == 201

    otp_payload = {"email": "test@gmail.com"}
    response = await async_client.post("/otp/request", json=otp_payload)

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["detail"].startswith("OTP sent successfully")
    assert "otp_id" in response_data


@pytest.mark.asyncio
async def test_request_otp_user_not_found(async_client: AsyncClient):
    """
    Teste la requête d'OTP pour un utilisateur non trouvé.
    """
    payload = {"email": "nonexistent@example.com"}
    response = await async_client.post("/otp/request", json=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "User with this email not found."


@pytest.mark.asyncio
async def test_verify_otp_success(async_client: AsyncClient):
    """
    Teste la vérification d'OTP réussie.
    """
    user_payload = {
        "first_name": "Alice",
        "last_name": "Borderland",
        "email": "test@example.com",
        "password": "secret123",
        "phone_number": "90000000",
    }
    user_response = await async_client.post("/users/", json=user_payload)
    assert user_response.status_code == 201

    otp_payload = {"email": "test@example.com"}
    otp_response = await async_client.post("/otp/request", json=otp_payload)

    payload = {"email": "test@example.com", "code": otp_response.json()["code"]}
    response = await async_client.post("/otp/verify", json=payload)

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["detail"] == "OTP verified successfully."
    assert "user" in response_data


@pytest.mark.asyncio
async def test_verify_otp_invalid(async_client: AsyncClient):
    """
    Teste la vérification d'OTP avec un code invalide.
    """
    user_payload = {
        "first_name": "Alice",
        "last_name": "Borderland",
        "email": "test@example.com",
        "password": "secret123",
        "phone_number": "90000000",
    }
    user_response = await async_client.post("/users/", json=user_payload)
    assert user_response.status_code == 201

    otp_payload = {"email": "test@example.com"}
    otp_response = await async_client.post("/otp/request", json=otp_payload)

    payload = {
        "email": "test@example.com",
        "code": otp_response.json()["code"] + "1",
    }  # Invalid code
    response = await async_client.post("/otp/verify", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Invalid OTP or OTP already used/expired."


@pytest.mark.asyncio
async def test_verify_otp_already_used(async_client: AsyncClient):
    """
    Teste la vérification d'OTP avec un code expiré.
    """
    user_payload = {
        "first_name": "Alice",
        "last_name": "Borderland",
        "email": "test@example.com",
        "password": "secret123",
        "phone_number": "90000000",
    }
    user_response = await async_client.post("/users/", json=user_payload)
    assert user_response.status_code == 201

    otp_payload = {"email": "test@example.com"}
    otp_response = await async_client.post("/otp/request", json=otp_payload)

    payload = {"email": "test@example.com", "code": otp_response.json()["code"]}
    await async_client.post("/otp/verify", json=payload)
    response = await async_client.post("/otp/verify", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"].startswith(
        "Invalid OTP or OTP already used/expired"
    )


"""
@pytest.mark.asyncio
async def test_verify_otp_expired(async_client: AsyncClient):
    """
# Teste la vérification d'OTP avec un code déjà utilisé.
"""
    user_payload = {
        "first_name": "Alice",
        "last_name": "Borderland",
        "email": "test@example.com",
        "password": "secret123",
        "phone_number": "90000000",
    }
    user_response = await async_client.post("/users/", json=user_payload)
    assert user_response.status_code == 201

    otp_payload = {"email": "test@example.com"}
    otp_response = await async_client.post("/otp/request", json=otp_payload)

    # Simulate OTP expiration by waiting
    with patch.object(
        OTPService,
        "verify_otp",
        return_value=HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP or OTP already used/expired.",
        ),
    ):
        payload = {"email": "test@example.com", "code": otp_response.json()["code"]}
        response = await async_client.post("/otp/verify", json=payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"].startswith(
            "Invalid OTP or OTP already used/expired"
        )
"""
