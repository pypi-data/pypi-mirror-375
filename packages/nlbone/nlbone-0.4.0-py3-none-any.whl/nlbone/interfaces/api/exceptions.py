from typing import Any, Iterable
from fastapi import HTTPException, status


def _error_entry(loc: Iterable[Any] | None, detail: str, type_: str) -> dict:
    return {
        "loc": list(loc) if loc else [],
        "msg": detail,
        "type": type_,
    }


def _errors(loc: Iterable[Any] | None, detail: str, type_: str) -> list[dict]:
    return [_error_entry(loc, detail, type_)]


class BaseHttpException(HTTPException):
    pass


class BadRequestException(BaseHttpException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class UnauthorizedException(BaseHttpException):
    def __init__(self, detail: str = "unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )


class ForbiddenException(BaseHttpException):
    def __init__(self, detail: str = "forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class NotFoundException(BaseHttpException):
    def __init__(self, detail: str = "not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class ConflictException(BaseHttpException):
    def __init__(self, detail: str = "conflict"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class NotSupportedException(BaseHttpException):
    def __init__(self, detail: str = "NotSupported"):
        super().__init__(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=detail,
        )


class UnprocessableEntityException(BaseHttpException):
    def __init__(self, detail: str, loc: Iterable[Any] | None = None, type_: str = "unprocessable_entity"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=_errors(loc, detail, type_),
        )


class LogicalValidationException(UnprocessableEntityException):
    def __init__(self, detail: str, loc: Iterable[Any] | None = None, type_: str = "logical_error"):
        super().__init__(detail=detail, loc=loc, type_=type_)


