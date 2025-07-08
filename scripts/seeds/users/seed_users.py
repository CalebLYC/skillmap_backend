import asyncio
from faker import Faker
import random
import sys
from app.core.config import Settings
from app.db.mongo_client import MongoClient
from app.db.mongo_collections import DBCollections
from app.db.repositories.permission_repository import PermissionRepository
from app.schemas.user import UserCreateSchema
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.role_repository import RoleRepository
from app.services.auth.user_service import UserService
from scripts.seeds.users.base_users_data import BASE_USERS_SEED


fake = Faker()


async def seed_users(num_fake_users: int = 0, clean_db: bool = True):
    """
    Seeds the database with predefined users and optionally with fake users.

    Args:
        num_fake_users (int): The number of fake users to generate.
                              If 0, only predefined users are seeded.
        clean_db (bool): If True, clears the existing users collection before seeding.
                         Defaults to True.
    """
    settings = Settings()
    # client = None
    client = MongoClient(settings.database_uri, settings.database_name)
    db = client.get_db()
    users_col = db.get_collection(DBCollections.USERS)

    print("Seeding users...")

    # Clean the collection (optional, adjust as needed)
    if clean_db:
        await users_col.delete_many({})
        print("Cleared existing users.")
    else:
        print("Skipping database cleaning.")

    user_repo = UserRepository(db)
    role_repo = RoleRepository(db)
    permission_repo = PermissionRepository(db)
    user_service = UserService(
        user_repo=user_repo,
        role_repos=role_repo,
        permission_repos=permission_repo,
    )

    users_to_seed = []

    # --- Add Predefined Users ---
    if num_fake_users == 0:  # Only seed predefined if no fake users are requested
        users_to_seed.extend(
            [UserCreateSchema(**user_data) for user_data in BASE_USERS_SEED]
        )
        print("Seeding predefined users.")
    else:
        print(f"Seeding {num_fake_users} fake users.")

        all_role_models = await role_repo.list_roles()
        all_available_role_names = [r.name for r in all_role_models]

        roles_for_fake_users = [
            role_name
            for role_name in all_available_role_names
            if role_name != "superadmin"
        ]
        if not roles_for_fake_users:
            print(
                "WARNING: No non-superadmin roles found in the database. Fake users will be created without roles."
            )

        # --- Generate Fake Users ---
        for _ in range(num_fake_users):
            first_name = fake.first_name()
            last_name = fake.last_name()
            # email = fake.email()
            email = fake.unique.email()
            password = "password123"
            sex = random.choice(["M", "F"])
            birthday_date = fake.date_of_birth()

            assigned_roles = []
            if roles_for_fake_users:
                num_roles_to_assign = random.randint(
                    1, min(2, len(roles_for_fake_users))
                )
                assigned_roles = random.sample(
                    roles_for_fake_users, num_roles_to_assign
                )

            users_to_seed.append(
                UserCreateSchema(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    roles=assigned_roles,
                    sex=sex,
                    birthday_date=birthday_date,
                )
            )

    # --- Execute Seeding ---
    for user_create in users_to_seed:
        try:
            await user_service.create_user(user_create)
            # print(f"  Seeded user: {user_create.email}")
        except Exception as e:
            print(f"  Error seeding user {user_create.email}: {e}")

    print("Finished seeding users.")
    client.close()


if __name__ == "__main__":
    # To seed only predefined users (clears DB by default):
    # python -m scripts.seeds.users.seed_users

    # To seed 50 fake users (clears DB by default):
    # python -m scripts.seeds.users.seed_users 50

    # To seed predefined users WITHOUT clearing the DB:
    # python -m scripts.seeds.users.seed_users --clean_db=false

    # To seed 50 fake users WITHOUT clearing the DB:
    # python -m scripts.seeds.users.seed_users 50 --clean_db=false

    # Parse command line arguments
    num_users_arg = 0
    clean_db_arg = True

    if len(sys.argv) > 1:
        # Check for num_fake_users argument (first positional arg)
        if sys.argv[1].isdigit():
            num_users_arg = int(sys.argv[1])

        # Check for --clean_db flag
        for arg in sys.argv:
            if arg.startswith("--clean_db="):
                clean_db_str = arg.split("=")[1].lower()
                clean_db_arg = clean_db_str == "true"
                break

    asyncio.run(seed_users(num_fake_users=num_users_arg, clean_db=clean_db_arg))
