"""Base repository with common CRUD operations."""

from __future__ import annotations

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, entity_id: UUID) -> ModelT | None:
        return await self.session.get(self.model, entity_id)

    async def list_all(self, *, limit: int = 100, offset: int = 0) -> list[ModelT]:
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, stmt: Select | None = None) -> int:
        if stmt is None:
            stmt = select(func.count()).select_from(self.model)
        else:
            stmt = select(func.count()).select_from(stmt.subquery())
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def delete(self, entity: ModelT) -> None:
        await self.session.delete(entity)
        await self.session.flush()
