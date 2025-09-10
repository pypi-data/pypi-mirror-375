from maleo.dtos.settings import ServiceSettings
from maleo.google.secret import Format, GoogleSecretManager
from maleo.dtos.key.rsa import Complete
from maleo.types.base.uuid import OptionalUUID


class RSAKeyManager:
    def __init__(
        self,
        settings: ServiceSettings,
        secret_manager: GoogleSecretManager,
        operation_id: OptionalUUID = None,
    ) -> None:
        if settings.KEY_PASSWORD is not None:
            password = settings.KEY_PASSWORD
        else:
            read_key_password = secret_manager.read(
                Format.STRING,
                name="maleo-key-password",
                operation_id=operation_id,
            )
            password = read_key_password.data.value

        if settings.PRIVATE_KEY is not None:
            private = settings.PRIVATE_KEY
        else:
            read_private_key = secret_manager.read(
                Format.STRING, name="maleo-private-key", operation_id=operation_id
            )
            private = read_private_key.data.value

        if settings.PUBLIC_KEY is not None:
            public = settings.PUBLIC_KEY
        else:
            read_public_key = secret_manager.read(
                Format.STRING, name="maleo-public-key", operation_id=operation_id
            )
            public = read_public_key.data.value

        self.keys = Complete(password=password, private=private, public=public)
