"""Request and response shapes for signing in."""

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    # The limits stop a very long value from being hashed.
    email: str = Field(max_length=254)
    password: str = Field(max_length=1024)


class UserRead(BaseModel):
    """The signed-in user. The password hash is never returned."""

    # Lets this be built from a User model object.
    model_config = ConfigDict(from_attributes=True)

    email: str
    name: str
    role: str


class DemoAccessRead(BaseModel):
    """How a visitor can sign in as a demo role. The details are null when not public."""

    model_config = ConfigDict(from_attributes=True)

    role: str
    email: str | None
    password: str | None
