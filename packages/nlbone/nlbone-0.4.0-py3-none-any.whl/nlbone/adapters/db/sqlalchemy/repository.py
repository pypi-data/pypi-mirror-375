from __future__ import annotations
from typing import Generic, Iterable, Optional, Type, TypeVar, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from nlbone.core.ports.repo import Repository, AsyncRepository

T = TypeVar("T")


class SqlAlchemyRepository(Repository[T], Generic[T]):
    def __init__(self, session: Session, model: Type[T]) -> None:
        self.session = session
        self.model = model

    def get(self, id) -> Optional[T]:
        return self.session.get(self.model, id)

    def add(self, obj: T) -> None:
        self.session.add(obj)

    def remove(self, obj: T) -> None:
        self.session.delete(obj)

    def list(self, *, limit: int | None = None, offset: int = 0) -> Iterable[T]:
        q = self.session.query(self.model).offset(offset)
        if limit is not None:
            q = q.limit(limit)
        return q.all()


class AsyncSqlAlchemyRepository(AsyncRepository, Generic[T]):
    def __init__(self, session: AsyncSession, model: Type[T]) -> None:
        self.session = session
        self.model = model

    async def get(self, id) -> Optional[T]:
        return await self.session.get(self.model, id)

    def add(self, obj: T) -> None:
        self.session.add(obj)

    async def remove(self, obj: T) -> None:
        await self.session.delete(obj)

    async def list(self, *, limit: int | None = None, offset: int = 0) -> List[T]:
        stmt = select(self.model).offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
