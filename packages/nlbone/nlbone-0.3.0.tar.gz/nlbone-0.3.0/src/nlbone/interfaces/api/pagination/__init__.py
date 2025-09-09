from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel
from fastapi import Depends

from .offset_base import PaginateResponse, PaginateRequest


def get_pagination(
        req: PaginateRequest = Depends(PaginateRequest)
) -> PaginateRequest:
    return req


T = TypeVar("T")


class Paginated(BaseModel, Generic[T]):
    total_count: Optional[int]
    total_page: Optional[int]
    data: List[T]
