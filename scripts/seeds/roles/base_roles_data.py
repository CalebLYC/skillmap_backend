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
        "name": "editor",
        "description": "User with content creation and modification privileges.",
        "permissions": [
            "user:read",
            "user:list",
            "role:read",
            "permission:read",
            # Add permissions specific to content editing, e.g.,
            # "content:create",
            # "content:update",
            # "content:delete",
        ],
        "inherited_roles": ["user"],  # Inherits all permissions from 'user'
    },
    {
        "name": "admin",
        "description": "Administrator with full system access.",
        "permissions": [
            "admin:full_access",  # A single permission that grants all
            # Alternatively, list all specific admin permissions:
            # "user:read", "user:create", "user:update", "user:delete", "user:list",
            # "role:read", "role:create", "role:update", "role:delete", "role:list",
            # "role:assign_permissions", "role:remove_permissions",
            # "role:assign_inherited_role", "role:remove_inherited_role",
            # "permission:read", "permission:create", "permission:update", "permission:delete", "permission:list",
        ],
        "inherited_roles": [
            "editor"
        ],  # Inherits all permissions from 'editor' (and transitively from 'user', 'guest')
    },
]
