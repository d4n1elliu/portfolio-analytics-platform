"""Response shapes for securities."""

from pydantic import BaseModel, ConfigDict


class SecurityRead(BaseModel):
    """A security as returned by the API."""

    # Lets this be built from a Security model object.
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticker: str
    name: str
    sector: str
    asset_class: str
    currency: str
