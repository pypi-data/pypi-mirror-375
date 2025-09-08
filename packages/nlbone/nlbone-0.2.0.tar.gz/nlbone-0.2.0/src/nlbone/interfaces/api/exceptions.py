from typing import Any, Iterable
from fastapi import HTTPException, status


def _error_entry(loc: Iterable[Any] | None, msg: str, type_: str) -> dict:
    return {
        "loc": list(loc) if loc else [],
        "msg": msg,
        "type": type_,
    }


def _errors(loc: Iterable[Any] | None, msg: str, type_: str) -> list[dict]:
    return [_error_entry(loc, msg, type_)]


class BadRequestException(HTTPException):
    def __init__(self, msg: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg,
        )


class UnauthorizedException(HTTPException):
    def __init__(self, msg: str = "unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=msg,
        )


class ForbiddenException(HTTPException):
    def __init__(self, msg: str = "forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=msg,
        )


class NotFoundException(HTTPException):
    def __init__(self, msg: str = "not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=msg,
        )


class ConflictException(HTTPException):
    def __init__(self, msg: str = "conflict"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=msg,
        )


class UnprocessableEntityException(HTTPException):
    def __init__(self, msg: str, loc: Iterable[Any] | None = None, type_: str = "unprocessable_entity"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=_errors(loc, msg, type_),
        )


class LogicalValidationException(UnprocessableEntityException):
    def __init__(self, msg: str, loc: Iterable[Any] | None = None, type_: str = "logical_error"):
        super().__init__(msg=msg, loc=loc, type_=type_)
