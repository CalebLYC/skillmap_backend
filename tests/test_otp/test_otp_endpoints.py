import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_request_otp_success(
    async_client: AsyncClient,
    override_otp_service_dependency,
):
    """
    Teste la requête d'OTP réussie pour un utilisateur existant.
    """
    user_payload = {
        "first_name": "Alice",
        "last_name": "Borderland",
        "email": "aegontargaryen061@gmail.com",
        "password": "secret123",
        "phone_number": "90000000",
    }
    response = await async_client.post("/users/", json=user_payload)
    assert response.status_code == 201

    otp_payload = {"email": "aegontargaryen061@gmail.com"}
    response = await async_client.post("/otp/request", json=otp_payload)

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["detail"].startswith("OTP sent successfully")
    assert "otp_id" in response_data


@pytest.mark.asyncio
async def test_request_otp_user_not_found(
    async_client: AsyncClient,
    override_otp_service_dependency,
):
    """
    Teste la requête d'OTP pour un utilisateur non trouvé.
    """
    payload = {"email": "nonexistent@example.com"}
    response = await async_client.post("/otp/request", json=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "User with this email not found."


"""
@pytest.mark.asyncio
async def test_verify_otp_success(
    async_client: AsyncClient,
    override_otp_service_dependency,
    mock_otp_repository: OTPRepository,
):
    
    user_payload = {
        "first_name": "Alice",
        "last_name": "Borderland",
        "email": "test@example.com",
        "password": "secret123",
        "phone_number": "90000000",
    }
    user_response = await async_client.post("/users/", json=user_payload)
    assert user_response.status_code == 201

    mock_otp_code = "123456"
    valid_otp_model = OTPModel(
        id="65b3c4d5e6f7a8b9c0d1e2f3",
        email="test@example.com",
        code=mock_otp_code,
        expires_at=datetime.datetime.utcnow() + timedelta(minutes=5),
        is_used=False,
    )
    # Configure le mock_otp_repository pour simuler un OTP valide trouvé
    mock_otp_repository.find_by_email_and_code.return_value = valid_otp_model
    mock_otp_repository.mark_as_used.return_value = 1

    payload = {"email": "test@example.com", "code": mock_otp_code}
    response = await async_client.post("/otp/verify", json=payload)

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["detail"] == "OTP verified successfully."
    assert "user" in response_data


@pytest.mark.asyncio
async def test_verify_otp_invalid(
    async_client: AsyncClient,
    override_otp_service_dependency,
):
    
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
async def test_verify_otp_already_used(
    async_client: AsyncClient,
    override_otp_service_dependency,
):
    
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


@pytest.mark.asyncio
async def test_verify_otp_expired(
    async_client: AsyncClient,
    override_otp_service_dependency,
):
    
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

    with freeze_time("2024-01-01 12:00:00") as frozen_time:
        otp_response = await async_client.post("/otp/request", json=otp_payload)
        frozen_time.tick(delta=timedelta(minutes=6))

        payload = {"email": "test@example.com", "code": otp_response.json()["code"]}
        response = await async_client.post("/otp/verify", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"].startswith("OTP has expired")
"""
