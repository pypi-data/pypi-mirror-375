from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakAuthenticationError
from nlbone.core.ports.auth import AuthService
from nlbone.config.settings import Settings, get_settings


class KeycloakAuthService(AuthService):
    def __init__(self, settings: Settings | None = None):
        s = settings or get_settings()
        self.keycloak_openid = KeycloakOpenID(
            server_url=s.KEYCLOAK_SERVER_URL.__str__(),
            client_id=s.KEYCLOAK_CLIENT_ID,
            realm_name=s.KEYCLOAK_REALM_NAME,
            client_secret_key=s.KEYCLOAK_CLIENT_SECRET.get_secret_value().strip(),
        )

    def has_access(self, token, permissions):
        try:
            result = self.keycloak_openid.has_uma_access(token, permissions=permissions)
            return result.is_authorized
        except KeycloakAuthenticationError:
            return False
        except Exception as e:
            print(f"Token verification failed: {e}")
            return False

    def verify_token(self, token: str) -> dict | None:
        try:
            result = self.keycloak_openid.introspect(token)
            if not result.get("active"):
                raise KeycloakAuthenticationError("NotActiveSession")
            return result
        except KeycloakAuthenticationError:
            return None
        except Exception as e:
            print(f"Token verification failed: {e}")
            return None

    def get_client_token(self) -> dict | None:
        try:
            return self.keycloak_openid.token(grant_type="client_credentials")
        except Exception as e:
            print(f"Failed to get client token: {e}")
            return None

    def get_client_id(self, token: str):
        data = self.verify_token(token)
        if not data:
            return None

        is_service_account = bool(data.get("username").startswith("service-account-"))
        client_id = data.get("client_id")

        if not is_service_account or not client_id:
            return None

        return client_id

    def is_client_token(self, token: str, allowed_clients: set[str] | None = None) -> bool:
        client_id = self.get_client_id(token)

        if not client_id:
            return False

        if allowed_clients is not None and client_id not in allowed_clients:
            return False

        return True

    def client_has_access(self, token: str, permissions: list[str], allowed_clients: set[str] | None = None) -> bool:
        if not self.is_client_token(token, allowed_clients):
            return False
        return self.has_access(token, permissions)