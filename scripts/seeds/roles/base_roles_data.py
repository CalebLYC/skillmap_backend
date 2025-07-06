from typing import List, Dict, Any

# This list defines a set of common, foundational roles for your application.
# Each dictionary represents a role with its 'name', assigned 'permissions',
# and 'inherited_roles' (names of other roles it inherits from).
# Ensure that permission codes and inherited role names referenced here exist.
BASE_ROLES_SEED: List[Dict[str, Any]] = [
    {
        "name": "guest",
        "description": "Unauthenticated user with minimal access.",
        "permissions": [
            # Basic read access, e.g., for public content
            "user:read",  # Assuming a public user profile read permission
        ],
        "inherited_roles": [],
    },
    {
        "name": "user",
        "description": "Standard authenticated user.",
        "permissions": [
            "user:read",
            "user:update",  # Can update their own profile
        ],
        "inherited_roles": ["guest"],  # Inherits all permissions from 'guest'
    },
    {
        "name": "moderator",
        "description": "User with content creation and modification privileges.",
        "permissions": [
            "user:read",
            "user:list",
            "role:read",
            "permission:read",
        ],
        "inherited_roles": ["user"],
    },
    {
        "name": "admin",
        "description": "Administrator with a high level access.",
        "permissions": [
            "user:read",
            "user:create",
            "user:update",
            "user:delete",
            "user:list",
            "role:read",
            "role:create",
            "role:update",
            "role:delete",
            "role:list",
            "role:assign_permissions",
            "role:remove_permissions",
            "role:assign_inherited_role",
            "role:remove_inherited_role",
            "permission:read",
            "permission:create",
            "permission:update",
            "permission:delete",
            "permission:list",
        ],
        "inherited_roles": ["moderator"],
    },
    {
        "name": "superadmin",
        "description": "Administrator with full system access.",
        "permissions": ["superadmin:full_access", "role:assign", "permission:assign"],
        "inherited_roles": ["admin"],
    },
]
