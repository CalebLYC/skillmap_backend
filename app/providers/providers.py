from functools import lru_cache
from dotenv import load_dotenv
from fastapi import Depends

from app.core.config import Settings
from app.db.mongo_client import MongoClient


@lru_cache()
def get_settings():
    return Settings()


@lru_cache()
def get_db(settings: Settings = Depends(get_settings)):
    load_dotenv()
    mongo = MongoClient(settings.database_uri, settings.database_name)
    return mongo.get_db()
