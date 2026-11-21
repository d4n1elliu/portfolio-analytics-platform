"""Create one demo account for each role.

Run from the backend/ directory, giving each account a password:
    DEMO_PASSWORD_OPERATIONS=... \\
    DEMO_PASSWORD_PORTFOLIO_MANAGER=... \\
    DEMO_PASSWORD_ANALYST=... \\
    python -m scripts.seed_users

The passwords are read from the environment, so none is stored in the repo.
Only their hashes are saved.

Safe to run more than once: an account whose email already exists is skipped,
and its password is left as it was.
"""

import os
import sys
from collections.abc import Mapping

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Role, User
from app.services.inserts import insert_missing
from app.services.passwords import MIN_PASSWORD_LENGTH, hash_password

DEMO_ACCOUNTS = [
    {"email": "operations@example.com", "name": "Demo Operations", "role": Role.OPERATIONS},
    {"email": "pm@example.com", "name": "Demo Portfolio Manager", "role": Role.PORTFOLIO_MANAGER},
    {"email": "analyst@example.com", "name": "Demo Analyst", "role": Role.ANALYST},
]


class SeedError(Exception):
    pass


def password_variable(role: Role) -> str:
    """The environment variable that holds a role's demo password."""
    return f"DEMO_PASSWORD_{role.value.upper()}"


def build_demo_users(environ: Mapping[str, str]) -> list[dict[str, str | bool]]:
    """Return the rows to insert, with each password hashed. Uses no database.

    Raises SeedError naming every password that is missing or too short.
    """
    problems = []
    users = []
    for account in DEMO_ACCOUNTS:
        variable = password_variable(account["role"])
        password = environ.get(variable, "")
        if len(password) < MIN_PASSWORD_LENGTH:
            problems.append(f"{variable} must be at least {MIN_PASSWORD_LENGTH} characters.")
            continue
        users.append(
            {
                "email": account["email"],
                "name": account["name"],
                "role": account["role"].value,
                "password_hash": hash_password(password),
                "is_active": True,
            }
        )
    if problems:
        raise SeedError(" ".join(problems))
    return users


def seed_users(session: Session, users: list[dict[str, str | bool]]) -> list[str]:
    """Insert the users, skipping any whose email already exists.

    Returns the emails that were inserted. The caller commits the session.
    """
    return insert_missing(session, User, users, ["email"], User.email)


def main(environ: Mapping[str, str]) -> int:
    try:
        users = build_demo_users(environ)
    except SeedError as error:
        print(f"Nothing was saved. {error}")
        return 1

    with SessionLocal() as session:
        inserted = seed_users(session, users)
        session.commit()

    skipped = len(users) - len(inserted)
    print(f"Users: inserted {len(inserted)}, skipped {skipped} already present.")
    for email in inserted:
        print(f"  created {email}")
    return 0


if __name__ == "__main__":
    sys.exit(main(os.environ))
