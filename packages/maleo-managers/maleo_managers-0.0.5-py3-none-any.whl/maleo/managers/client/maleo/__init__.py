from abc import ABC, abstractmethod
from uuid import UUID
from Crypto.PublicKey.RSA import RsaKey
from datetime import datetime
from httpx import Response
from pydantic import ValidationError
from typing import Optional
from maleo.database.managers import RedisManager
from maleo.dtos.authentication import GenericAuthentication
from maleo.dtos.contexts.operation import OperationContext, generate_operation_context
from maleo.dtos.contexts.request import RequestContext
from maleo.dtos.contexts.response import ResponseContext
from maleo.dtos.contexts.service import ServiceContext
from maleo.dtos.resource import Resource
from maleo.enums.cache import Origin as CacheOrigin, Layer as CacheLayer
from maleo.enums.operation import OperationType, Origin, Layer, Target
from maleo.exceptions import (
    UnprocessableEntity,
    InternalServerError,
    from_resource_http_request,
)
from maleo.logging.config import Config as LogConfig
from maleo.logging.logger import Client
from maleo.mixins.timestamp import OperationTimestamp
from maleo.schemas.operation.resource import AllResourceOperationAction
from maleo.schemas.response import ErrorResponse
from maleo.utils.cache import build_namespace
from ...credential import CredentialManager
from ..http import HTTPClientManager
from .config import MaleoClientConfig


class MaleoClientService:
    def __init__(
        self,
        config: MaleoClientConfig,
        logger: Client,
        credential_manager: CredentialManager,
        http_client_manager: HTTPClientManager,
        private_key: RsaKey,
        redis: RedisManager,
        service_context: ServiceContext,
    ):
        self._config = config
        self._logger = logger
        self._credential_manager = credential_manager
        self._http_client_manager = http_client_manager
        self._private_key = private_key
        self._redis = redis
        self._service_context = service_context

        self._namespace = build_namespace(
            base=self._service_context.key,
            client=self._config.key,
            origin=CacheOrigin.CLIENT,
            layer=CacheLayer.SERVICE,
        )

        self._operation_context = generate_operation_context(
            origin=Origin.CLIENT, layer=Layer.SERVICE, target=Target.INTERNAL
        )

    def raise_resource_http_request_error(
        self,
        *,
        executed_at: datetime,
        response: Response,
        operation_id: UUID,
        operation_context: OperationContext,
        operation_action: AllResourceOperationAction,
        request_context: Optional[RequestContext],
        authentication: Optional[GenericAuthentication],
        resource: Resource,
    ):
        """Handle HTTP error response and raise appropriate exception"""
        operation_timestamp = OperationTimestamp.completed_now(executed_at)

        response_context = ResponseContext(
            status_code=response.status_code,
            media_type=response.headers.get("content-type"),
            headers=response.headers.multi_items(),
            body=response.content,
        )

        try:
            error_response = ErrorResponse.model_validate(response.json())
        except ValidationError as ve:
            exception = UnprocessableEntity(
                OperationType.RESOURCE,
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=operation_context,
                operation_timestamp=operation_timestamp,
                operation_summary="Validation error occured while validating resource http request's response",
                operation_action=operation_action,
                request_context=request_context,
                authentication=authentication,
                resource=resource,
                details=ve.errors(),
            )
            raise exception from ve
        except Exception as e:
            exception = InternalServerError(
                OperationType.RESOURCE,
                service_context=self._service_context,
                operation_id=operation_id,
                operation_context=self._operation_context,
                operation_timestamp=operation_timestamp,
                operation_summary="Unexpected error occured while validating resource http request's response",
                operation_action=operation_action,
                request_context=request_context,
                authentication=authentication,
                resource=resource,
                details={
                    "exc_type": type(e).__name__,
                    "exc_data": {
                        "message": str(e),
                        "args": e.args,
                    },
                },
            )
            raise exception from e

        exception = from_resource_http_request(
            logger=self._logger,
            service_context=self._service_context,
            operation_id=operation_id,
            operation_context=self._operation_context,
            operation_timestamp=operation_timestamp,
            operation_action=operation_action,
            request_context=request_context,
            authentication=authentication,
            resource=resource,
            response_context=response_context,
            response=error_response,
        )
        raise exception


class MaleoClientManager(ABC):
    def __init__(
        self,
        config: MaleoClientConfig,
        log_config: LogConfig,
        credential_manager: CredentialManager,
        private_key: RsaKey,
        redis: RedisManager,
        service_context: Optional[ServiceContext] = None,
    ):
        self._config = config
        self._log_config = log_config

        self._key = self._config.key
        self._name = self._config.name

        self._logger = Client(
            environment=self._service_context.environment,
            service_key=self._service_context.key,
            client_key=self._key,
            config=log_config,
        )

        self._credential_manager = credential_manager
        self._http_client_manager = HTTPClientManager()
        self._private_key = private_key
        self._redis = redis

        self._service_context = (
            service_context
            if service_context is not None
            else ServiceContext.from_env()
        )

    @abstractmethod
    def initalize_services(self):
        pass
