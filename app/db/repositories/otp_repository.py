import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from bson import ObjectId
from app.db.mongo_collections import DBCollections

from app.models.OTP import OTPModel
from app.utils.db_utils.mongo_utils import MongoCollectionOperations


class OTPRepository:
    """
    Dépôt pour la gestion des données OTP dans MongoDB.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self._db_ops = MongoCollectionOperations(db, DBCollections.OTPS)

    async def list_otps(self) -> List[OTPModel]:
        docs = await self._db_ops.find_many({})
        return [OTPModel(**doc) for doc in docs]

    async def create(self, otp: OTPModel) -> str:
        """
        Crée un nouveau document OTP dans la base de données.
        Retourne l'ID de l'OTP inséré.
        """
        return await self._db_ops.insert_one(
            otp.model_dump(by_alias=True, exclude=["id"])
        )

    async def find_by_email_and_code(self, email: str, code: str) -> Optional[OTPModel]:
        """
        Trouve un OTP par e-mail et code.
        """
        doc = await self._db_ops.find_one(
            {"email": email, "code": code, "is_used": False}
        )
        return OTPModel.model_validate(doc) if doc else None

    async def find_latest_by_email(self, email: str) -> Optional[OTPModel]:
        """
        Trouve le dernier OTP non utilisé pour un e-mail donné, trié par date de création descendante.
        """
        docs = await self._db_ops.find_many(
            query={"email": email, "is_used": False},
            sort={"created_at": -1},
            limit=1,
        )
        if docs:
            return OTPModel.model_validate(docs[0])
        return None

    async def find_by_email(self, email: str) -> List[OTPModel]:
        docs = await self._db_ops.find_many({"email": email})
        return [OTPModel(**doc) for doc in docs]

    async def find_by_code(self, code: str) -> List[OTPModel]:
        docs = await self._db_ops.find_many({"code": code})
        return [OTPModel(**doc) for doc in docs]

    async def mark_as_used(self, otp_id: str) -> int:
        """
        Marque un OTP comme utilisé par son ID.
        Retourne le nombre de documents modifiés.
        """
        return await self._db_ops.update_one(
            {"_id": ObjectId(otp_id)}, {"$set": {"is_used": True}}
        )

    async def delete_expired_otps(self) -> int:
        """
        Supprime tous les OTPs expirés de la base de données.
        Retourne le nombre de documents supprimés.
        """
        return await self._db_ops.delete_many(
            {"expires_at": {"$lt": datetime.datetime.now(datetime.timezone.utc)}}
        )
