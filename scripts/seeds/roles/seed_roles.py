import asyncio
from app.core.config import Settings
from app.db.mongo_client import MongoClient
from app.db.mongo_collections import DBCollections
from app.schemas.role import RoleCreateSchema
from app.db.repositories.role_repository import RoleRepository
from app.db.repositories.permission_repository import PermissionRepository
from app.services.auth.role_service import RoleService
from scripts.seeds.roles.base_roles_data import BASE_ROLES_SEED


async def seed_roles():
    """
    Seeds the database with base roles, including their permissions and inherited roles.
    Cleans the existing roles collection before seeding.
    """
    settings = Settings()
    # client = None
    client = MongoClient(settings.database_uri, settings.database_name)
    db = client.get_db()
    roles_col = db.get_collection(DBCollections.ROLES)

    print("Seeding roles...")

    # Clean the collection before seeding
    await roles_col.delete_many({})
    print("Cleared existing roles.")

    # Instantiate repositories and service
    role_repo = RoleRepository(db)
    permission_repo = PermissionRepository(db)
    role_service = RoleService(role_repos=role_repo, permission_repos=permission_repo)

    for role_data in BASE_ROLES_SEED:
        try:
            role_create_schema = RoleCreateSchema(**role_data)
            await role_service.create_role(role_create_schema)
            # print(f"Seeded role: {role_data['name']}")
        except Exception as e:
            print(f"Error seeding role {role_data.get('name', 'N/A')}: {e}")

    print("Finished seeding roles.")
    client.close()


if __name__ == "__main__":
    # python -m scripts.seeds.roles.seed_roles
    asyncio.run(seed_roles())
