import asyncio
import sys
import subprocess  # Import the subprocess module


async def run_necessary_seeds():
    """
    Exécute tous les scripts d'initialisation de la base de données dans l'ordre correct
    en les appelant comme des processus Python séparés.

    Args:
        clean_db (bool): Si True, nettoie les collections avant l'initialisation.
                         Cette valeur est passée à tous les seeders individuels.
    """
    print(
        "\n--- Démarrage de toutes les opérations d'initialisation de la base de données en production ---"
    )

    # Exécution de seed_permissions
    print(
        "********Création des permissions de base : python -m scripts.seeds.roles.seed_permissions...********"
    )
    process_permissions = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.seeds.roles.seed_permissions",
        ],
        capture_output=True,
        text=True,
    )
    print(process_permissions.stdout)
    if process_permissions.stderr:
        print(
            f"Erreur lors de l'initialisation des permissions:\n{process_permissions.stderr}"
        )
        sys.exit(1)  # Quitter si une erreur se produit

    # Exécution de seed_roles
    print(
        "********Création des roles de base  : python -m scripts.seeds.roles.seed_roles...********"
    )
    process_roles = subprocess.run(
        [sys.executable, "-m", "scripts.seeds.roles.seed_roles"],
        capture_output=True,
        text=True,
    )
    print(process_roles.stdout)
    if process_roles.stderr:
        print(f"Erreur lors de l'initialisation des rôles:\n{process_roles.stderr}")
        sys.exit(1)

    # Exécution de seed_superadmin
    print(
        "********Ajout du superadmin : python -m scripts.seeds.users.seed_superadmin...********"
    )
    process_users = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.seeds.users.seed_superadmin",
            "0",
        ],
        capture_output=True,
        text=True,
    )
    print(process_users.stdout)
    if process_users.stderr:
        print(f"Erreur lors de la création du superadmin:\n{process_users.stderr}")
        sys.exit(1)

    print(
        "\n--- Toutes les opérations d'initialisation de la base de données en production terminées ---"
    )


if __name__ == "__main__":
    # Pour exécuter tous les seeders nécéssaires en production :
    # python -m scripts.seeds.prod_seeder

    if len(sys.argv) > 1:
        for arg in sys.argv:
            if arg.startswith("--clean_db="):
                clean_db_str = arg.split("=")[1].lower()
                clean_db_arg = clean_db_str == "true"
                break

    asyncio.run(run_necessary_seeds())
