import functools

from nlbone.adapters.auth import KeycloakAuthService
from nlbone.interfaces.api.exceptions import ForbiddenException, UnauthorizedException
from nlbone.utils.context import current_request


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
        request = current_request()
        if not request.state.user_id:
            raise UnauthorizedException()
        return await func(*args, **kwargs)

    return wrapper


def has_access(*, permissions=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            request = current_request()
            if not request.state.user_id:
                raise UnauthorizedException()
            if not KeycloakAuthService().has_access(request.state.token, permissions=permissions):
                raise ForbiddenException(f"Forbidden {permissions}")

            return func(*args, **kwargs)

        return wrapper
    return decorator

