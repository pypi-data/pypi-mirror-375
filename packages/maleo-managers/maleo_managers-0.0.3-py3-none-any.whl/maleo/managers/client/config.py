from pydantic import BaseModel, Field
from typing import Generic, Optional, TypeVar
from .maleo.config import MaleoClientsConfigT


class Config(BaseModel, Generic[MaleoClientsConfigT]):
    maleo: MaleoClientsConfigT = Field(
        ...,
        description="Maleo client's configurations",
    )


ConfigT = TypeVar("ConfigT", bound=Optional[Config])


class ConfigMixin(BaseModel, Generic[ConfigT]):
    client: ConfigT = Field(..., description="Client config")
