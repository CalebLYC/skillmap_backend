import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import Settings
from app.db.mongo_collections import DBCollections
from app.db.repositories.permission_repository import PermissionRepository
from app.models.Role import PermissionModel
from scripts.seeds.roles.base_permissions_data import BASE_PERMISSIONS_SEED


async def seed_permissions():
    """
    Seeds the database with base permissions.
    Cleans the existing permissions collection before seeding.
    """
    settings = Settings()
    client = AsyncIOMotorClient(settings.database_uri)
    db = client[settings.database_name]
    permissions_col = db.get_collection(DBCollections.PERMISSIONS)

    print("Seeding permissions...")

    # Clean the collection before seeding
    await permissions_col.delete_many({})
    print("Cleared existing permissions.")

    permission_repo = PermissionRepository(db)

    for perm_data in BASE_PERMISSIONS_SEED:
        try:
            permission_model = PermissionModel(**perm_data)
            await permission_repo.create(permission_model)
            # print(f"Seeded permission: {perm_data['code']}")
        except Exception as e:
            print(f"Error seeding permission {perm_data.get('code', 'N/A')}: {e}")

    print("Finished seeding permissions.")
    client.close()


if __name__ == "__main__":
    # python -m scripts.seeds.roles.seed_permissions
    asyncio.run(seed_permissions())
