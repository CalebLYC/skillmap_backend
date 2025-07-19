from fastapi import APIRouter, Depends, status
from app.providers.service_provider import get_otp_service
from app.schemas.otp import (
    OTPRequestSchema,
    OTPVerifyResponseSchema,
    OTPVerifySchema,
    OTPResponseSchema,
)
from app.services.auth.otp_service import OTPService
from app.utils.constants import http_status

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
