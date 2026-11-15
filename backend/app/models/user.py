"""User model: a person who can sign in, and the role that decides what they can do."""

from enum import StrEnum

from sqlalchemy import Boolean, CheckConstraint, String, true
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.common import CreatedAtMixin


class Role(StrEnum):
    """What a user is allowed to do. Each member is also a plain string."""

    OPERATIONS = "operations"
    PORTFOLIO_MANAGER = "portfolio_manager"
    ANALYST = "analyst"


# Builds the rule "role IN (...)" from Role, so the allowed values are listed
# in one place. Adding a role also needs a migration that replaces this
# constraint.
_ROLE_RULE = "role IN ({})".format(", ".join(f"'{role.value}'" for role in Role))


class User(CreatedAtMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(_ROLE_RULE, name="role_valid"),
        # Stops two accounts that differ only by capital letters.
        CheckConstraint("email = lower(email)", name="email_lowercase"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    # An Argon2 hash. The password itself is never stored.
    password_hash: Mapped[str] = mapped_column(String(255))
    # A Role value.
    role: Mapped[str] = mapped_column(String(20))
    # An inactive user keeps their row but cannot sign in.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())

    def __repr__(self) -> str:
        return f"<User {self.email}>"
