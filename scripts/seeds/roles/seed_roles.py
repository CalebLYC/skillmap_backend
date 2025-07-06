import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import Settings
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
    client = AsyncIOMotorClient(settings.database_uri)
    db = client[settings.database_name]
    roles_col = db.get_collection(DBCollections.ROLES)  # Assuming DBCollections.ROLES

    print("Seeding roles...")

    # Clean the collection before seeding
    await roles_col.delete_many({})
    print("Cleared existing roles.")

    # Instantiate repositories and service
    role_repo = RoleRepository(db)
    permission_repo = PermissionRepository(db)  # RoleService depends on this
    role_service = RoleService(role_repos=role_repo, permission_repos=permission_repo)

    # It's crucial to seed roles in an order that respects inheritance,
    # i.e., inherited roles must exist before the role inheriting them is created.
    # The BASE_ROLES_SEED list is ordered from least dependent (guest) to most dependent (admin).
    for role_data in BASE_ROLES_SEED:
        try:
            # Create a RoleCreateSchema instance from the dictionary
            role_create_schema = RoleCreateSchema(**role_data)
            # Use the RoleService to create the role, as it handles validations
            await role_service.create_role(role_create_schema)
            print(f"Seeded role: {role_data['name']}")
        except Exception as e:
            print(f"Error seeding role {role_data.get('name', 'N/A')}: {e}")

    print("Finished seeding roles.")
    client.close()  # Close the client connection


if __name__ == "__main__":
    # This block allows you to run the seeder directly from the command line
    # python -m app.db.seeds.roles.seed_roles
    asyncio.run(seed_roles())
