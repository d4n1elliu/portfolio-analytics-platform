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
