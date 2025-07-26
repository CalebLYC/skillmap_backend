import os
import random
import datetime
from fastapi import HTTPException, status
from app.core.config import Settings
from app.core.security import SecurityUtils
from app.db.repositories.otp_repository import OTPRepository
from app.db.repositories.user_repository import UserRepository
from app.models.OTP import OTPModel, OTPTypeEnum
from app.providers.providers import get_settings
from app.schemas.otp import (
    OTPRequestSchema,
    OTPVerifyResponseSchema,
    OTPVerifySchema,
    OTPResponseSchema,
)
from app.schemas.user import UserReadSchema
from app.services.email_service import EmailService


class OTPService:
    def __init__(
        self,
        otp_repos: OTPRepository,
        user_repos: UserRepository,
        email_service: EmailService,
        settings: Settings,
    ):
        self.otp_repos = otp_repos
        self.user_repos = user_repos
        self.email_service = email_service
        self.settings = settings
        self.otp_expiry_minutes = self.settings.otp_expiry_minutes
        self.otp_length = self.settings.otp_length
        self.templates_dir = self.settings.templates_dir

    def _load_email_template(self, template_name: str, context: dict) -> str:
        """Charge un modèle d'e-mail HTML et y injecte des variables.

        Args:
            template_name (str): _description_
            context (dict): _description_

        Raises:
            FileNotFoundError: _description_

        Returns:
            str: _description_
        """
        template_path = os.path.join(self.templates_dir, "emails", template_name)
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Email template not found: {template_path}")

        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        # Simple remplacement de variables pour cet exemple.
        # Pour des templates plus complexes, Jinja2 ou d'autres moteurs seraient mieux.
        rendered_html = template_content
        for key, value in context.items():
            rendered_html = rendered_html.replace(f"{{{{ {key} }}}}", str(value))

        return rendered_html

    async def request_otp(self, otp_request: OTPRequestSchema) -> OTPResponseSchema:
        """Génère et "envoie" un OTP à l'adresse e-mail spécifiée.
        Vérifie d'abord si l'utilisateur existe.

        Args:
            otp_request (OTPRequestSchema): _description_

        Raises:
            HTTPException: _description_

        Returns:
            OTPResponseSchema: _description_
        """
        user = await self.user_repos.find_by_email(email=otp_request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with this email not found.",
            )

        # Générer un code OTP aléatoire
        otp_code = "".join([str(random.randint(0, 9)) for _ in range(self.otp_length)])
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            minutes=self.otp_expiry_minutes
        )

        # Créer le modèle OTP
        otp_model = OTPModel(
            email=otp_request.email,
            code=otp_code,
            expires_at=expires_at,
            type=otp_request.type,
        )

        # Enregistrer l'OTP en base de données
        await self.otp_repos.create(otp_model)
        db_otp = await self.otp_repos.find_by_email_and_code(
            email=otp_request.email, code=otp_code
        )

        # Envoie de du code OTP à l'adresse mail
        mail_subject = "Votre Code de Vérification OTP pour SkillMap"

        # Formater le temps d'expiration de manière conviviale
        expiry_time_str = f"{self.otp_expiry_minutes} minutes"
        if self.otp_expiry_minutes == 1:
            expiry_time_str = "1 minute"
        elif self.otp_expiry_minutes < 1:
            expiry_seconds = int(self.otp_expiry_minutes * 60)
            expiry_time_str = f"{expiry_seconds} secondes"

        # Contexte pour le template HTML
        template_context = {
            "user_first_name": user.first_name,
            "otp_code": otp_code,
            "expiry_time_str": expiry_time_str,
            "current_year": datetime.datetime.now().year,
        }

        html_body = self._load_email_template("otp_verification.html", template_context)

        await self.email_service.send_email(
            recipient_email=otp_request.email,
            subject=mail_subject,
            body=html_body,
            is_html=True,
        )
        print(
            f"DEBUG: OTP pour {otp_request.email}: {otp_code} (Expire à: {expires_at})"
        )

        return OTPResponseSchema(
            detail=f"OTP sent successfully to {otp_request.email}. It will expire in {self.otp_expiry_minutes} minutes.",
            **db_otp.model_dump(by_alias=True, exclude_none=True),
            otp_id=str(db_otp.id),
        )

    async def verify_otp(
        self,
        otp_verify: OTPVerifySchema,
        otp_type: OTPTypeEnum = OTPTypeEnum.VERIFY_USER,
    ) -> OTPVerifyResponseSchema:
        """Vérifie un OTP fourni par l'utilisateur.

        Args:
            otp_verify (OTPVerifySchema): _description_
            otp_type (OTPTypeEnum, optional): _description_. Defaults to OTPTypeEnum.VERIFY_USER.

        Raises:
            HTTPException: _description_
            HTTPException: _description_
            HTTPException: _description_
            HTTPException: _description_
            HTTPException: _description_

        Returns:
            OTPVerifyResponseSchema: _description_
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

        if otp_record.is_expired():
            # Marquer comme utilisé/expiré si ce n'est pas déjà fait
            await self.otp_repos.mark_as_used(str(otp_record.id))
            otp_record.is_used = True
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="OTP has expired."
            )

        if otp_record.is_used:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP has already been used.",
            )

        # Marquer l'OTP comme utilisé après vérification réussie
        await self.otp_repos.mark_as_used(str(otp_record.id))
        otp_record.is_used = True

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

        return OTPVerifyResponseSchema(
            detail="OTP verified successfully.",
            otp=OTPResponseSchema(
                **otp_record.model_dump(by_alias=True, exclude_none=True),
                otp_id=str(otp_record.id),
            ),
            user=UserReadSchema.model_validate(user) if user else None,
        )
