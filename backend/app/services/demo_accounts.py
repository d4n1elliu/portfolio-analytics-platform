"""The demo accounts, and which of their sign-in details may be shown to visitors.

Uses no database.
"""

from collections.abc import Mapping
from dataclasses import dataclass

from app.models import Role

DEMO_ACCOUNTS = [
    {"email": "operations@example.com", "name": "Demo Operations", "role": Role.OPERATIONS},
    {"email": "pm@example.com", "name": "Demo Portfolio Manager", "role": Role.PORTFOLIO_MANAGER},
    {"email": "analyst@example.com", "name": "Demo Analyst", "role": Role.ANALYST},
]

# Only read-only roles. Operations can change data, so its details are never shown.
PUBLIC_ROLES = (Role.PORTFOLIO_MANAGER, Role.ANALYST)


@dataclass(frozen=True)
class DemoAccess:
    """How a visitor can sign in as a role. The email and password are None when not public."""

    role: Role
    email: str | None
    password: str | None


def password_variable(role: Role) -> str:
    """The environment variable that holds a role's demo password."""
    return f"DEMO_PASSWORD_{role.value.upper()}"


def list_demo_access(environ: Mapping[str, str]) -> list[DemoAccess]:
    """Return every demo role, with sign-in details for the public ones that have a password set."""
    access = []
    for account in DEMO_ACCOUNTS:
        role = account["role"]
        password = environ.get(password_variable(role)) if role in PUBLIC_ROLES else None
        email = account["email"] if password else None
        access.append(DemoAccess(role=role, email=email, password=password or None))
    return access
