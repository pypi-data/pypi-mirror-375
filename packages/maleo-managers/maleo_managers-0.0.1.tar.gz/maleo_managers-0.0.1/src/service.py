from abc import ABC, abstractmethod
from fastapi import FastAPI, APIRouter
from fastapi.exceptions import RequestValidationError
from google.cloud import pubsub_v1
from google.oauth2.service_account import Credentials
from pydantic import ValidationError
from starlette.exceptions import HTTPException
from starlette.types import Lifespan, AppType
from sqlalchemy import MetaData
from typing import Generic, Optional
from uuid import UUID
from maleo.dtos.settings import ServiceSettingsT
from maleo.logging.config import Config as LogConfig
from maleo.logging.logger import ServiceLoggers
from maleo.middlewares.manager import MiddlewareManager
from maleo.dtos.key.rsa import Complete
from maleo.dtos.contexts.service import ServiceContext
from maleo.exceptions.handlers.request import (
    http_exception_handler,
    maleo_exception_handler,
    pydantic_validation_exception_handler,
    request_validation_exception_handler,
    general_exception_handler,
)
from maleo.exceptions import MaleoException
from .config import ConfigT


class ServiceManager(ABC, Generic[ServiceSettingsT, ConfigT]):
    """ServiceManager class"""

    key = "service_manager"
    name = "ServiceManager"

    def __init__(
        self,
        db_metadata: MetaData,
        google_credentials: Credentials,
        log_config: LogConfig,
        settings: ServiceSettingsT,
        config: ConfigT,
        keys: Complete,
    ):
        self._db_metadata = db_metadata
        self._google_credentials = google_credentials
        self._log_config = log_config
        self._settings = settings
        self._config = config
        self._keys = keys

        self._service_context = ServiceContext(
            environment=self._settings.ENVIRONMENT, key=self._settings.SERVICE_KEY
        )

        self._initialize_loggers()
        self._initialize_publisher()

    def _initialize_loggers(self) -> None:
        self.loggers = ServiceLoggers.new(
            environment=self._settings.ENVIRONMENT,
            service_key=self._settings.SERVICE_KEY,
            config=self._log_config,
        )

    def _initialize_publisher(self) -> None:
        self.publisher = pubsub_v1.PublisherClient()

    @abstractmethod
    def _initialize_database(self):
        """Initialize all given databases"""

    def create_app(
        self,
        operation_id: UUID,
        router: APIRouter,
        lifespan: Optional[Lifespan[AppType]] = None,
        version: str = "unknown",
    ) -> FastAPI:
        root_path = self._settings.ROOT_PATH
        self.app = FastAPI(
            title=self._settings.SERVICE_NAME,
            version=version,
            lifespan=lifespan,  # type: ignore
            root_path=root_path,
        )

        # Add middleware(s)
        self.middleware_manager = MiddlewareManager(
            self.app,
            operation_id=operation_id,
            config=self._config.middleware,
            keys=self._keys,
            logger=self.loggers.middleware,
            service_context=self._service_context,
        )
        self.middleware_manager.add(operation_id=operation_id)

        # Add exception handler(s)
        self.app.add_exception_handler(
            exc_class_or_status_code=ValidationError,
            handler=pydantic_validation_exception_handler,  # type: ignore
        )
        self.app.add_exception_handler(
            exc_class_or_status_code=RequestValidationError,
            handler=request_validation_exception_handler,  # type: ignore
        )
        self.app.add_exception_handler(
            exc_class_or_status_code=HTTPException,
            handler=http_exception_handler,  # type: ignore
        )
        self.app.add_exception_handler(
            exc_class_or_status_code=MaleoException,
            handler=maleo_exception_handler,  # type: ignore
        )
        self.app.add_exception_handler(
            exc_class_or_status_code=Exception,
            handler=general_exception_handler,  # type: ignore
        )

        # Include router
        self.app.include_router(router)

        return self.app
