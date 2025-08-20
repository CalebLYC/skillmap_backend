import asyncio

from dotenv import load_dotenv
from app.core.config import Settings
from app.db.mongo_client import MongoClient
from app.db.repositories.permission_repository import PermissionRepository
from app.db.repositories.role_repository import RoleRepository
from app.schemas.user_schema import UserCreateSchema
from app.db.repositories.user_repository import UserRepository
from app.services.auth.user_service import UserService


async def seed_users():
    load_dotenv()
    settings = Settings()
    # client = None
    client = MongoClient(settings.database_uri, settings.database_name)
    db = client.get_db()

    user_repo = UserRepository(db)
    role_repo = RoleRepository(db)
    permission_repo = PermissionRepository(db)
    user_service = UserService(
        user_repo=user_repo,
        role_repos=role_repo,
        permission_repos=permission_repo,
    )

    users_to_seed = [
        UserCreateSchema(
            email=settings.admin_email,
            password=settings.admin_password,
            first_name="Caleb",
            last_name="LOYI",
            phone_number="91982996",
            roles=["superadmin"],
            permissions=["superadmin:full_access"],
        ),
    ]

    for user_create in users_to_seed:
        try:
            await user_service.create_user(user_create)
        except Exception as e:
            print(f"Seed error: {e}")

    print("Finished seeding superadmin.")
    client.close()


if __name__ == "__main__":
    # python -m scripts.seeds.users.seed_superadmin
    asyncio.run(seed_users())
