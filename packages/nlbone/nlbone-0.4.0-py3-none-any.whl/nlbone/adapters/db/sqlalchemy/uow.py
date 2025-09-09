from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session, sessionmaker
from nlbone.core.ports.uow import UnitOfWork
from nlbone.core.ports.uow import AsyncUnitOfWork as AsyncUnitOfWorkPort


class SqlAlchemyUnitOfWork(UnitOfWork):
    """sync UoW for SQLAlchemy."""

    def __init__(self, session_factory: sessionmaker) -> None:
        self._session_factory = session_factory
        self.session: Session | None = None

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self.session = self._session_factory()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        try:
            if exc_type is None:
                self.commit()
            else:
                self.rollback()
        finally:
            if self.session is not None:
                self.session.close()
                self.session = None

    def commit(self) -> None:
        if self.session:
            self.session.commit()

    def rollback(self) -> None:
        if self.session:
            self.session.rollback()


class AsyncSqlAlchemyUnitOfWork(AsyncUnitOfWorkPort):
    """Transactional boundary for async SQLAlchemy."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sf = session_factory
        self.session: Optional[AsyncSession] = None

    async def __aenter__(self) -> "AsyncSqlAlchemyUnitOfWork":
        self.session = self._sf()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        try:
            if exc_type is None:
                await self.commit()
            else:
                await self.rollback()
        finally:
            if self.session is not None:
                await self.session.close()
                self.session = None

    async def commit(self) -> None:
        if self.session:
            await self.session.commit()

    async def rollback(self) -> None:
        if self.session:
            await self.session.rollback()
