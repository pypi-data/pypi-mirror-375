from functools import cached_property
from Crypto.PublicKey.RSA import RsaKey
from google.oauth2.service_account import Credentials
from maleo.crypto.token import encode
from maleo.dtos.credential import Credential, MaleoCredential
from maleo.enums.environment import Environment
from maleo.enums.token import TokenType
from maleo.google.secret import Format, GoogleSecretManager
from maleo.dtos.authentication import (
    PrivilegedCredentials,
    AuthenticatedUser,
    PrivilegedAuthentication,
)
from maleo.dtos.token import (
    PrivilegedCredentialPayload,
    TimestampPayload,
    PrivilegedPayload,
    PrivilegedAuthenticationToken,
)
from maleo.types.base.string import OptionalString
from maleo.types.base.uuid import OptionalUUID
from maleo.utils.loaders.yaml import from_string


class CredentialManager:
    def __init__(
        self,
        environment: Environment,
        private_key: RsaKey,
        secret_manager: GoogleSecretManager,
        operation_id: OptionalUUID = None,
    ) -> None:
        self._private_key = private_key
        self._secret_manager = secret_manager

        name = f"maleo-internal-credentials-{environment}"
        read_secret = secret_manager.read(
            Format.STRING, name=name, operation_id=operation_id
        )
        data = from_string(read_secret.data.value)
        self.maleo_credentials = MaleoCredential.model_validate(data)

    def assign_google_credentials(self, google_credentials: Credentials) -> None:
        self.google_credentials = google_credentials

    @property
    def credentials(self) -> Credential:
        if not hasattr(self, "google_credentials") or not isinstance(
            self.google_credentials, Credentials
        ):
            raise ValueError("Google credential not initialized")
        if not hasattr(self, "maleo_credentials") or not isinstance(
            self.maleo_credentials, MaleoCredential
        ):
            raise ValueError("Maleo credential not initialized")
        return Credential(google=self.google_credentials, maleo=self.maleo_credentials)

    @cached_property
    def token_credential_payload(self) -> PrivilegedCredentialPayload:
        return PrivilegedCredentialPayload(
            iss=None,
            sub=str(self.maleo_credentials.id),
            sr=["administrator"],
            u_i=self.maleo_credentials.id,
            u_uu=self.maleo_credentials.uuid,
            u_u=self.maleo_credentials.username,
            u_e=self.maleo_credentials.email,
            u_ut="service",
            o_i=None,
            o_uu=None,
            o_k=None,
            o_ot=None,
            uor=None,
        )

    @property
    def token(self) -> OptionalString:
        payload = PrivilegedPayload.model_validate(
            {
                **self.token_credential_payload.model_dump(),
                **TimestampPayload.new_timestamp().model_dump(),
            }
        )
        try:
            return encode(
                payload=payload.model_dump(mode="json"), key=self._private_key
            )
        except Exception:
            return None

    @property
    def request_credentials(
        self,
    ) -> PrivilegedCredentials:
        return PrivilegedCredentials(
            token=PrivilegedAuthenticationToken(
                type=TokenType.ACCESS,
                payload=PrivilegedPayload.model_validate(
                    {
                        **self.token_credential_payload.model_dump(),
                        **TimestampPayload.new_timestamp().model_dump(),
                    }
                ),
            ),
            scopes=["authenticated", "administrator"],
        )

    @cached_property
    def request_user(self) -> AuthenticatedUser:
        return AuthenticatedUser(
            display_name=self.maleo_credentials.username,
            identity=self.maleo_credentials.email,
        )

    @property
    def authentication(self) -> PrivilegedAuthentication:
        return PrivilegedAuthentication(
            credentials=self.request_credentials, user=self.request_user
        )
