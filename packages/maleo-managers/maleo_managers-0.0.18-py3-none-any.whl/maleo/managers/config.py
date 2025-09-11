from pathlib import Path
from pydantic import BaseModel
from typing import Generic, Type, TypeVar
from maleo.database.config import (
    ConfigsT as DatabaseConfigsT,
    ConfigsMixin as DatabaseConfigMixin,
)
from maleo.dtos.settings import ServiceSettingsT
from maleo.google.pubsub import (
    ConfigT as PubSubConfigT,
    ConfigMixin as PubSubConfigMixin,
)
from maleo.google.secret import Format, GoogleSecretManager
from maleo.infra.config import ConfigMixin as InfraConfigMixin
from maleo.middlewares.config import ConfigMixin as MiddlewareConfigMixin
from maleo.types.base.uuid import OptionalUUID
from maleo.utils.loaders.yaml import from_path, from_string
from .client.config import ConfigT as ClientConfigT, ConfigMixin as ClientConfigMixin


class Config(
    PubSubConfigMixin[PubSubConfigT],
    MiddlewareConfigMixin,
    InfraConfigMixin,
    DatabaseConfigMixin[DatabaseConfigsT],
    ClientConfigMixin[ClientConfigT],
    BaseModel,
    Generic[ClientConfigT, DatabaseConfigsT, PubSubConfigT],
):
    pass


ConfigT = TypeVar("ConfigT", bound=Config)


class ConfigManager(Generic[ServiceSettingsT, ConfigT]):
    def __init__(
        self,
        settings: ServiceSettingsT,
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
