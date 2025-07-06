from typing import List, Dict

# This list defines a set of common, foundational permissions for your application.
# Each dictionary represents a permission with a unique 'code' and a 'description'.
# These can be used to populate your 'permissions' collection in MongoDB during initial setup.
BASE_PERMISSIONS_SEED: List[Dict[str, str]] = [
    # User Management Permissions
    {"code": "user:read", "description": "View user profiles and data"},
    {"code": "user:create", "description": "Create new user accounts"},
    {"code": "user:update", "description": "Modify existing user profiles"},
    {"code": "user:delete", "description": "Delete user accounts"},
    {"code": "user:list", "description": "List all users"},
    # Role Management Permissions
    {"code": "role:read", "description": "View role definitions and permissions"},
    {"code": "role:create", "description": "Create new roles"},
    {"code": "role:update", "description": "Modify existing roles"},
    {"code": "role:delete", "description": "Delete roles"},
    {"code": "role:list", "description": "List all roles"},
    {"code": "role:assign_permissions", "description": "Assign permissions to roles"},
    {"code": "role:remove_permissions", "description": "Remove permissions from roles"},
    {
        "code": "role:assign_inherited_role",
        "description": "Assign inherited roles to roles",
    },
    {
        "code": "role:remove_inherited_role",
        "description": "Remove inherited roles from roles",
    },
    # Permission Management Permissions (for managing permissions themselves)
    {"code": "permission:read", "description": "View permission definitions"},
    {"code": "permission:create", "description": "Create new permissions"},
    {"code": "permission:update", "description": "Modify existing permissions"},
    {"code": "permission:delete", "description": "Delete permissions"},
    {"code": "permission:list", "description": "List all permissions"},
    # Example: General Admin Permissions
    {
        "code": "admin:full_access",
        "description": "Grants full administrative access to the system",
    },
]
