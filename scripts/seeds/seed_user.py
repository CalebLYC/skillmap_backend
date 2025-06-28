import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import Settings
from app.db.mongo_collections import DBCollections
from app.schemas.user import UserCreateSchema
from app.db.repositories.user_repository import UserRepository
from app.services.auth.user_service import UserService


async def seed_users():
    settings = Settings()
    client = AsyncIOMotorClient(settings.database_uri)
    db = client[settings.database_name]
    users_col = db.get_collection(DBCollections.USERS)

    # Clean la collection
    await users_col.delete_many({})

    user_repo = UserRepository(db)
    user_service = UserService(user_repo)

    users_to_seed = [
        UserCreateSchema(
            email="alice@example.com",
            password="password123",
            first_name="Alice",
            last_name="Wonderland",
        ),
        UserCreateSchema(
            email="bob@example.com",
            password="password123",
            first_name="Bob",
            last_name="Builder",
        ),
        UserCreateSchema(
            email="charlie@example.com",
            password="password123",
            first_name="Charlie",
            last_name="Chocolate",
        ),
    ]

    for user_create in users_to_seed:
        try:
            await user_service.create_user(user_create)
        except Exception as e:
            print(f"Seed error: {e}")

    print("Seeded users.")


if __name__ == "__main__":
    asyncio.run(seed_users())
