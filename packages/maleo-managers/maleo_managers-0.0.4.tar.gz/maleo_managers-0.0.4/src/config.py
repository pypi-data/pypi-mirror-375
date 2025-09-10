from pathlib import Path
from pydantic import BaseModel, Field
from typing import Generic, Type, TypeVar
from maleo.database.config import ConfigsT as DatabaseConfigsT
from maleo.dtos.settings import ServiceSettings
from maleo.google.pubsub import ConfigT as PubSubConfigT
from maleo.google.secret import Format, GoogleSecretManager
from maleo.infra.config import Config as InfraConfig
from maleo.middlewares.config import Config as MiddlewareConfig
from maleo.types.base.uuid import OptionalUUID
from maleo.utils.loaders.yaml import from_path, from_string
from .client.config import ConfigT as ClientConfigT


class Config(BaseModel, Generic[ClientConfigT, DatabaseConfigsT]):
    cient: ClientConfigT = Field(..., description="Client config")
    database: DatabaseConfigsT = Field(..., description="Database configs")
    infra: InfraConfig = Field(..., description="Infra config")
    middleware: MiddlewareConfig = Field(..., description="Middleware config")
    pubsub: PubSubConfigT = Field(..., description="PubSub config")


ConfigT = TypeVar("ConfigT", bound=Config)


class ConfigManager(Generic[ConfigT]):
    def __init__(
        self,
        settings: ServiceSettings,
        secret_manager: GoogleSecretManager,
        config_cls: Type[ConfigT],
        operation_id: OptionalUUID = None,
    ) -> None:
        use_local = settings.USE_LOCAL_CONFIG
        config_path = settings.CONFIG_PATH

        if use_local and config_path is not None and isinstance(config_path, str):
            config_path = Path(config_path)
            if config_path.exists() and config_path.is_file():
                data = from_path(config_path)
                self.config: ConfigT = config_cls.model_validate(data)
                return

        name = f"{settings.SERVICE_KEY}-config-{settings.ENVIRONMENT}"
        read_secret = secret_manager.read(
            Format.STRING, name=name, operation_id=operation_id
        )
        data = from_string(read_secret.data.value)
        self.config: ConfigT = config_cls.model_validate(data)
