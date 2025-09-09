import functools

from nlbone.adapters.auth import KeycloakAuthService
from nlbone.interfaces.api.exceptions import ForbiddenException, UnauthorizedException
from nlbone.utils.context import current_request


def current_user_id() -> int:
    user_id = current_request().state.user_id
    if user_id is not None:
        return int(user_id)
    raise UnauthorizedException()


def current_client_id() -> str:
    request = current_request()
    if client_id := KeycloakAuthService().get_client_id(request.state.token):
        return str(client_id)
    raise UnauthorizedException()


def client_has_access(*, permissions=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            request = current_request()
            if not KeycloakAuthService().client_has_access(request.state.token, permissions=permissions):
                raise ForbiddenException(f"Forbidden {permissions}")

            return func(*args, **kwargs)

        return wrapper
    return decorator


def user_authenticated(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if not current_user_id():
            raise UnauthorizedException()
        return await func(*args, **kwargs)

    return wrapper


def has_access(*, permissions=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            request = current_request()
            if not current_user_id():
                raise UnauthorizedException()
            if not KeycloakAuthService().has_access(request.state.token, permissions=permissions):
                raise ForbiddenException(f"Forbidden {permissions}")

            return func(*args, **kwargs)

        return wrapper
    return decorator