import datetime
from fastapi import APIRouter, Depends, Path, Response, status
from app.db.repositories.otp_repository import OTPRepository
from app.providers.repository_provider import get_otp_repository
from app.providers.service_provider import get_otp_service
from app.schemas.otp import (
    OTPRequestSchema,
    OTPVerifyResponseSchema,
    OTPVerifySchema,
    OTPResponseSchema,
)
from app.services.auth.otp_service import OTPService
from app.utils.constants import http_status
from app.utils.image_utils import generate_countdown_image

router = APIRouter(
    prefix="/otp",
    tags=["OTP"],
    responses=http_status.router_responses,
)


@router.post(
    "/request",
    response_model=OTPResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Request a One-Time Password (OTP) for an email.",
)
async def request_otp_endpoint(
    otp_request: OTPRequestSchema,
    otp_service: OTPService = Depends(get_otp_service),
):
    """
    Requests an OTP to be sent to the specified email address.
    The user must exist in the system.
    """
    return await otp_service.request_otp(otp_request)


@router.post(
    "/verify",
    response_model=OTPVerifyResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Verify a One-Time Password (OTP).",
)
async def verify_otp_endpoint(
    otp_verify: OTPVerifySchema,
    otp_service: OTPService = Depends(get_otp_service),
):
    """
    Verifies the provided OTP code for a given email address.
    """
    return await otp_service.verify_otp(otp_verify)


@router.get(
    "/countdown-image/{otp_id}",
    response_class=Response,
    responses={
        200: {"content": {"image/png": {}}},
        404: {"description": "OTP not found or expired"},
    },
    summary="Get a dynamic countdown image for an OTP.",
    description="Returns a PNG image displaying the remaining time for a given OTP. The image is designed to be reloaded frequently by email clients to simulate a dynamic countdown.",
)
async def get_otp_countdown_image(
    otp_id: str = Path(..., description="The ID of the OTP record"),
    otp_repo: OTPRepository = Depends(
        get_otp_repository
    ),  # Accès direct au dépôt pour éviter une dépendance circulaire avec OTPService
):
    """
    Endpoint to generate a dynamic countdown image for an OTP.
    """
    otp_record = await otp_repo.find_by_id(otp_id)

    if not otp_record:
        # Si l'OTP n'est pas trouvé, ou si find_by_id retourne None
        # On peut renvoyer une image "expirée" ou une 404
        # Pour les emails, une image "expirée" est plus conviviale qu'une erreur 404
        # Générons une image "expirée" pour ce cas.
        expired_image_bytes = generate_countdown_image(0)
        return Response(
            content=expired_image_bytes,
            media_type="image/png",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )

    # Calculer le temps restant
    time_remaining = int(
        (otp_record.expires_at - datetime.datetime.utcnow()).total_seconds()
    )

    # Générer l'image du compte à rebours
    image_bytes = generate_countdown_image(time_remaining)

    # Retourner l'image avec les en-têtes appropriés pour éviter le cache
    return Response(
        content=image_bytes,
        media_type="image/png",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )
