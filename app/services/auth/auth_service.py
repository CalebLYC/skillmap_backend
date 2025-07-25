import asyncio
import datetime

from bson import ObjectId
from fastapi import HTTPException, status
from app.core.jwt import JWTUtils
from app.core.security import SecurityUtils
from app.db.repositories.access_token_repository import AccessTokenRepository
from app.db.repositories.otp_repository import OTPRepository
from app.db.repositories.user_repository import UserRepository
from app.models.AccessToken import AccessTokenModel
from app.models.OTP import OTPModel, OTPTypeEnum
from app.schemas.auth_schema import (
    LoginRequestSchema,
    LoginResponseSchema,
    RegisterSchema,
    ResetUserPasswordSchema,
)
from app.models.User import UserModel
from app.schemas.otp import OTPResponseSchema, OTPVerifyResponseSchema, OTPVerifySchema
from app.schemas.user import UserReadSchema


class AuthService:
    def __init__(
        self,
        access_token_repos: AccessTokenRepository,
        user_repos: UserRepository,
        otp_repos: OTPRepository,
    ):
        self.access_token_repos = access_token_repos
        self.user_repos = user_repos
        self.otp_repos = otp_repos
        # Définir la dépendance de l'entête Authorization

    async def generate_access_token(
        self, user_id: str, expires_in_minutes: int | None = None
    ) -> str:
        expire = None
        if expires_in_minutes:
            expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
                minutes=expires_in_minutes
            )
        payload = {
            "sub": user_id,
            "exp": expire if expire else None,
            "iat": datetime.datetime.now(datetime.timezone.utc),
        }
        token, expires_at = JWTUtils.create_access_token(
            data=payload, expires_delta=expire if expire else None
        )
        token_doc = AccessTokenModel(
            token=token,
            user_id=ObjectId(user_id),
            expires_at=expires_at,
            revoked=False,
        )
        return await self.access_token_repos.create(access_token=token_doc)

    async def login(self, user: LoginRequestSchema) -> LoginResponseSchema:
        db_user = await self.user_repos.find_by_email(email=user.email)
        if not db_user:
            raise HTTPException(status_code=404, detail="Wrong credentials")
        is_auth = SecurityUtils.verify_password(
            hashed=db_user.password, plain=user.password
        )
        if not is_auth:
            raise HTTPException(status_code=401, detail="Wrong credentials")
        token_id = await self.generate_access_token(user_id=db_user.id)
        access_token = await self.access_token_repos.find_by_id(id=token_id)
        return_user = UserReadSchema.model_validate(db_user)
        return LoginResponseSchema(access_token=access_token, user=return_user)

    async def register(self, user: RegisterSchema) -> LoginResponseSchema:
        if user.password_confirmation:
            if user.password != user.password_confirmation:
                raise HTTPException(
                    status_code=400, detail="Password not match password confirmation"
                )
        # Hash the password before saving
        hashed_password = SecurityUtils.hash_password(user.password)
        user_doc = UserModel.model_validate(user)
        user_doc.password = hashed_password
        inserted_id = await self.user_repos.create(user_doc)
        db_user = await self.user_repos.find_by_id(user_id=inserted_id)
        token_id = await self.generate_access_token(user_id=db_user.id)
        access_token = await self.access_token_repos.find_by_id(id=token_id)
        return_user = UserReadSchema.model_validate(db_user)
        return LoginResponseSchema(access_token=access_token, user=return_user)

    async def logout(self, user_id: str) -> LoginResponseSchema:
        result = await self.access_token_repos.delete_by_user_id(user_id=user_id)
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        return result

    async def verify_otp(
        self,
        otp_verify: OTPVerifySchema,
        otp_type: OTPTypeEnum = OTPTypeEnum.VERIFY_USER,
    ) -> tuple[OTPVerifyResponseSchema, OTPModel]:
        """
        Vérifie un OTP fourni par l'utilisateur.
        """
        # Vérifier si l'utilisateur existe
        user = await self.user_repos.find_by_email(email=otp_verify.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this email not found.",
            )

        otp_record = await self.otp_repos.find_by_email_and_code(
            email=otp_verify.email, code=otp_verify.code
        )

        if (not otp_record) or (otp_record.type != otp_type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP or OTP already used/expired.",
            )

        if otp_record.is_used:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP has already been used.",
            )

        # Mettre à jour l'utilisateur pour le marquer comme vérifié
        success = await self.user_repos.update(
            user.id, {"is_verified": True, "is_active": True}
        )
        if success:
            user.is_active = True
            user.is_verified = True
        else:
            if otp_type == OTPTypeEnum.VERIFY_USER:
                raise HTTPException(status_code=409, detail="User already verified")

        return (
            OTPVerifyResponseSchema(
                detail="OTP verified successfully.",
                otp=OTPResponseSchema(
                    **otp_record.model_dump(by_alias=True, exclude_none=True),
                    otp_id=str(otp_record.id),
                ),
                user=UserReadSchema.model_validate(user) if user else None,
            ),
            otp_record,
        )

    async def reset_user_password(
        self, user_request: ResetUserPasswordSchema
    ) -> LoginResponseSchema:
        """
        Vérifie un OTP fourni par l'utilisateur et mets à jour son mot de passe.
        """
        otp_verify = OTPVerifySchema(code=user_request.code, email=user_request.email)
        verify_reponse, otp_record = await self.verify_otp(
            otp_verify=otp_verify, otp_type=OTPTypeEnum.RESET_PASSWORD
        )
        if not verify_reponse.user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this email not found.",
            )
        if not verify_reponse.otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP has already been used.",
            )

        if user_request.new_password and user_request.new_password_confirmation:
            if user_request.new_password_confirmation != user_request.new_password:
                raise HTTPException(
                    status_code=400, detail="Password not match password confirmation"
                )
            update_data = {}
            update_data["password"] = SecurityUtils.hash_password(
                user_request.new_password
            )
            success = await self.user_repos.update(verify_reponse.user.id, update_data)
            if not success:
                raise HTTPException(status_code=500, detail="Update failed")

        # Marquer l'OTP comme utilisé après vérification réussie et mis à jours
        await self.otp_repos.mark_as_used(str(otp_record.id))
        otp_record.is_used = True

        updated = await self.user_repos.find_by_id(verify_reponse.user.id)
        token_id = await self.generate_access_token(user_id=verify_reponse.user.id)
        access_token = await self.access_token_repos.find_by_id(id=token_id)
        return_user = UserReadSchema.model_validate(updated)
        return LoginResponseSchema(access_token=access_token, user=return_user)

    """async def clean_expired_tokens():
        await mongo_db["access_tokens"].delete_many({"expires_at": {"$lt": datetime.utcnow()}})"""
