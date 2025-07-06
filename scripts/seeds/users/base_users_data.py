from typing import Any, Dict, List

# This list defines a set of predefined, foundational users for your application.
# Each entry is a dictionary representing user data.
BASE_USERS_SEED: List[Dict[str, Any]] = [
    {
        "email": "alice@example.com",
        "password": "password123",
        "first_name": "Alice",
        "last_name": "Wonderland",
        "roles": ["admin"],
    },
    {
        "email": "bob@example.com",
        "password": "password123",
        "first_name": "Bob",
        "last_name": "Builder",
        "roles": ["user"],
    },
    {
        "email": "charlie@example.com",
        "password": "password123",
        "first_name": "Charlie",
        "last_name": "Chocolate",
        "roles": ["moderator"],
        "sex": "M",
        "birthday_date": "2000-01-01",
    },
    {
        "email": "david@example.com",
        "password": "password123",
        "first_name": "David",
        "last_name": "Smith",
        "roles": ["guest"],
    },
    {
        "email": "eve@example.com",
        "password": "password123",
        "first_name": "Eve",
        "last_name": "Johnson",
        "sex": "F",
    },
    {
        "email": "frank@example.com",
        "password": "password123",
        "first_name": "Frank",
        "last_name": "Williams",
        "phone_number": "900000000",
        "sex": "M",
        "birthday_date": "2007-01-08",
    },
    {
        "email": "grace@example.com",
        "password": "password123",
        "first_name": "Grace",
        "last_name": "Brown",
        "birthday_date": "2003-06-01",
    },
    {
        "email": "henry@example.com",
        "password": "password123",
        "first_name": "Henry",
        "last_name": "Jones",
    },
    {
        "email": "irene@example.com",
        "password": "password123",
        "first_name": "Irene",
        "last_name": "Garcia",
        "birthday_date": "2000-01-01",
        "sex": "F",
    },
    {
        "email": "jack@example.com",
        "password": "password123",
        "first_name": "Jack",
        "last_name": "Miller",
        "roles": ["admin"],
    },
]
