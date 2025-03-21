from typing import ClassVar, TypeVar, Generic

from loguru import logger
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import DeclarativeBase

from app.config.models import CrawlerData, AiTranslationOutput
from app.config.db import AsyncSession
from app.schemas.app import CrawlerDataCreate, CrawlerDataUpdate, AiTranslationOutputCreate, AiTranslationOutputUpdate


ModelType = TypeVar("ModelType", bound=DeclarativeBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

# alias for ease of use
S = AsyncSession


# refer: https://claude.ai/chat/017477b2-0a93-4548-9a05-e20b68dcb68c to learn about an ideal repository pattern implementation
class AppRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    model: ClassVar[ModelType]

    def __init__(self):
        # ensure repository can only be used with a valid DB model type
        if not issubclass(self.model, ModelType.__bound__):
            raise ValueError(
                f"{self.__class__.__name__}'s `model` attribute must be a subclass of {ModelType.__name__}, got {type(self.model)}"
            )

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

    async def add(self, data: CreateSchemaType, session: S) -> ModelType:
        db_record = self.model(**data.model_dump(exclude_unset=True))
        if hasattr(data, "metadata"):
            metadata_column = db_record.metadata_column
            setattr(db_record, metadata_column, data.metadata)
        logger.debug("created model object", model=db_record, class_name=self.__class__.__name__)

        session.add(db_record)
        await session.flush()
        await session.refresh(db_record)
        return db_record

    async def update(self, id: int, data: UpdateSchemaType, session: S) -> ModelType | None:
        db_record = await self.get(id, session)
        if db_record is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_record, field, value)

        if hasattr(data, "metadata"):
            metadata_column = db_record.metadata_column
            setattr(db_record, metadata_column, data.metadata)

        session.add(db_record)
        await session.flush()
        await session.refresh(db_record)
        return db_record

    async def delete(self, id: int, session: S) -> bool:
        db_record = await self.get(id, session)
        if db_record is None:
            return False

        await session.delete(db_record)
        return True

    async def delete_by_filter(self, session: S, **filters) -> bool:
        db_record = await self.get_by_filter(session, **filters)
        if db_record is None:
            return False

        await session.delete(db_record)
        return True

    async def count(self, session: S, **filters) -> int:
        query = select(func.count()).select_from(self.model).filter_by(**filters)
        result = await session.execute(query)
        return result.scalar()

    async def exists(self, id: int, session: S) -> bool:
        return await self.get(id, session) is not None

    async def exists_by_filter(self, session: S, **filters) -> bool:
        return await self.get_by_filter(session, **filters) is not None


class CrawlerDataRepository(AppRepository[CrawlerData, CrawlerDataCreate, CrawlerDataUpdate]):
    model = CrawlerData


class AiTranslationOutputRepository(
    AppRepository[AiTranslationOutput, AiTranslationOutputCreate, AiTranslationOutputUpdate]
):
    model = AiTranslationOutput
