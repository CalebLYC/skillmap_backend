from functools import lru_cache

from fastapi import Depends

from app.core.config import Settings
from app.db.mongo_client import MongoClient


@lru_cache()
def get_settings():
    return Settings()


def get_db(settings: Settings = Depends(get_settings)):
    mongo = MongoClient(settings.database_uri, settings.database_name)
    return mongo.get_db()
