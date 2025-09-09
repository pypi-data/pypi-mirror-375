from typing import Optional, Callable, Union
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

try:
    from dependency_injector import providers
    ProviderType = providers.Provider  # type: ignore
except Exception:
    ProviderType = object

from nlbone.core.ports.auth import AuthService


def _to_factory(auth: Union[AuthService, Callable[[], AuthService], ProviderType]):
    try:
        from dependency_injector import providers as _p  # type: ignore
        if isinstance(auth, _p.Provider):
            return auth
    except Exception:
        pass
    if callable(auth) and not hasattr(auth, "verify_token"):
        return auth
    return lambda: auth


class AuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, auth: Union[AuthService, Callable[[], AuthService], ProviderType]):
        super().__init__(app)
        self._get_auth = _to_factory(auth)

    async def dispatch(self, request: Request, call_next):
        request.state.client_id = request.headers.get("X-Client-Id")
        request.state.user_id = None
        request.state.token = None

        token: Optional[str] = None
        authz = request.headers.get("Authorization")
        if authz:
            try:
                scheme, token = authz.split(" ", 1)
                if scheme.lower() != "bearer":
                    token = None
            except ValueError:
                token = None

        if token:
            request.state.token = token
            try:
                service: AuthService = self._get_auth()
                data = service.verify_token(token)
                if data:
                    request.state.user_id = data.get("user_id")
            except Exception:
                pass

        return await call_next(request)
