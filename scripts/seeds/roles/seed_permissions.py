import asyncio

from dotenv import load_dotenv
from app.core.config import Settings
from app.db.mongo_client import MongoClient
from app.db.mongo_collections import DBCollections
from app.db.repositories.permission_repository import PermissionRepository
from app.models.role import PermissionModel
from scripts.seeds.roles.base_permissions_data import BASE_PERMISSIONS_SEED


async def seed_permissions():
    """
    Seeds the database with base permissions.
    Cleans the existing permissions collection before seeding.
    """
    load_dotenv()
    settings = Settings()
    # client = None
    client = MongoClient(settings.database_uri, settings.database_name)
    db = client.get_db()
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
