from typing import Generic, TypeAlias, TypeVar, Type

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import DeclarativeBase

# from app.config.models import CrawlerData, AiTranslationOutput
from app.config.db import AsyncSession


ModelType = TypeVar("ModelType", bound=DeclarativeBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
S: TypeAlias = AsyncSession


# refer: https://claude.ai/chat/017477b2-0a93-4548-9a05-e20b68dcb68c to learn about an ideal repository pattern implementation
class AppRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model

    async def get(self, id: int, session: S) -> ModelType | None:
        return await session.get(self.model, id)

    async def get_by_filter(self, session: S, **filters) -> ModelType | None:
        query = select(self.model).filter_by(**filters)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def list(self, session: S, skip: int = 0, limit: int = 100, **filters) -> list[ModelType]:
        query = select(self.model).filter_by(**filters).offset(skip).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    async def add(self, obj_in: CreateSchemaType, session: S) -> ModelType:
        db_record = self.model(**obj_in.model_dump(exclude_none=True))
        await session.add(db_record)
        await session.flush()
        await session.refresh(db_record)
        return db_record

    async def update(self, id: int, update_schema: UpdateSchemaType, session: S) -> ModelType | None:
        db_record = await self.get(id, session)
        if db_record is None:
            return None

        for name, field_info in update_schema.model_fields.items():
            value = getattr(update_schema, name, None)
            setattr(db_record, name, value)

        await session.add(db_record)
        await session.flush()
        await session.refresh(db_record)
        return db_record

    async def delete(self, id: int, session: S) -> bool:
        db_record = await self.get(id, session)
        if db_record is None:
            return False

        await session.delete(db_record)
        await session.commit()
        return True

    async def delete_by_filter(self, session: S, **filters) -> bool:
        db_record = await self.get_by_filter(session, **filters)
        if db_record is None:
            return False

        await session.delete(db_record)
        await session.commit()
        return True

    async def count(self, session: S, **filters) -> int:
        query = select(func.count()).select_from(self.model).filter_by(**filters)
        result = await session.execute(query)
        return result.scalar()

    async def exists(self, id: int, session: S) -> bool:
        return await self.get(id, session) is not None

    async def exists_by_filter(self, session: S, **filters) -> bool:
        return await self.get_by_filter(session, **filters) is not None
