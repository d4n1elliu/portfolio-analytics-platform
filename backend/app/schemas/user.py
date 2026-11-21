"""Request and response shapes for signing in."""

from pydantic import BaseModel, Field

from app.models import User
from app.services.permissions import Permission, permissions_of


class LoginRequest(BaseModel):
    # The limits stop a very long value from being hashed.
    email: str = Field(max_length=254)
    password: str = Field(max_length=1024)


class PasswordChange(BaseModel):
    current_password: str = Field(max_length=1024)
    new_password: str = Field(max_length=1024)


class UserRead(BaseModel):
    """The signed-in user. The password hash is never returned."""

    email: str
    name: str
    role: str
    permissions: list[Permission]

    @classmethod
    def from_user(cls, user: User) -> "UserRead":
        return cls(
            email=user.email,
            name=user.name,
            role=user.role,
            permissions=sorted(permissions_of(user.role)),
        )
