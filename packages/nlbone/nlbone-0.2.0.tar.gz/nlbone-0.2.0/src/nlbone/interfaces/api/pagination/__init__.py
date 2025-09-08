from fastapi import Depends

from .offset_base import PaginateResponse, PaginateRequest


def get_pagination(
        req: PaginateRequest = Depends(PaginateRequest)
) -> PaginateRequest:
    return req
