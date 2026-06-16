from pydantic import BaseModel


class BaseModel_ORIG(BaseModel):
    """Base model with common config."""
    model_config = {"from_attributes": True}
