from __future__ import annotations
from typing import Any, Optional, Mapping
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from fastapi import HTTPException as FastAPIHTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException

from .exceptions import BaseHttpException


# ---- Helpers ---------------------------------------------------------------

def _ensure_trace_id(request: Request) -> str:
    rid = request.headers.get("X-Request-Id") or request.headers.get("X-Trace-Id")
    return rid or str(uuid4())


def _json_response(
        request: Request,
        status_code: int,
        *,
        detail: Any,
        headers: Optional[Mapping[str, str]] = None,
        trace_id: Optional[str] = None,
        extra: Optional[Mapping[str, Any]] = None,
) -> JSONResponse:
    payload: dict[str, Any] = {"detail": detail}
    if extra:
        payload.update(extra)
    tid = trace_id or _ensure_trace_id(request)

    payload.setdefault("trace_id", tid)

    base_headers = {"X-Trace-Id": tid}
    if headers:
        base_headers.update(headers)

    return JSONResponse(status_code=status_code, content=payload, headers=base_headers)


# ---- Public Installer ------------------------------------------------------

def install_exception_handlers(
        app: FastAPI,
        *,
        logger: Any = None,
        expose_server_errors: bool = False,
) -> None:
    @app.exception_handler(BaseHttpException)
    async def _handle_base_http_exception(request: Request, exc: BaseHttpException):
        if logger:
            logger.warning(
                "http_error",
                extra={"status": exc.status_code, "detail": exc.detail, "path": request.url.path},
            )
        return _json_response(request, exc.status_code, detail=exc.detail)

    @app.exception_handler(FastAPIHTTPException)
    async def _handle_fastapi_http_exception(request: Request, exc: FastAPIHTTPException):
        if logger:
            logger.warning(
                "fastapi_http_error",
                extra={"status": exc.status_code, "detail": exc.detail, "path": request.url.path},
            )
        return _json_response(request, exc.status_code, detail=exc.detail)

    @app.exception_handler(StarletteHTTPException)
    async def _handle_starlette_http_exception(request: Request, exc: StarletteHTTPException):
        if logger:
            logger.warning(
                "starlette_http_error",
                extra={"status": exc.status_code, "detail": exc.detail, "path": request.url.path},
            )
        return _json_response(request, exc.status_code, detail=exc.detail)

    # 3) خطاهای اعتبارسنجی FastAPI (request body/query/path)
    @app.exception_handler(RequestValidationError)
    async def _handle_request_validation_error(request: Request, exc: RequestValidationError):
        errors = exc.errors()
        if logger:
            logger.info(
                "request_validation_error",
                extra={"errors": errors, "path": request.url.path},
            )
        return _json_response(request, 422, detail=errors)

    @app.exception_handler(ValidationError)
    async def _handle_pydantic_validation_error(request: Request, exc: ValidationError):
        errors = exc.errors()
        if logger:
            logger.info(
                "pydantic_validation_error",
                extra={"errors": errors, "path": request.url.path},
            )
        return _json_response(request, 422, detail=errors)

    @app.exception_handler(Exception)
    async def _handle_unexpected_exception(request: Request, exc: Exception):
        tid = _ensure_trace_id(request)
        if logger:
            logger.exception("unhandled_exception", extra={"trace_id": tid, "path": request.url.path})
        detail = str(exc) if expose_server_errors else "internal server error"
        return _json_response(request, 500, detail=detail, trace_id=tid)
