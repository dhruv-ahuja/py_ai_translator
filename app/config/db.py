from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy import text, CursorResult
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config.app_settings import settings
from app.config.logger import logger


async_engine = create_async_engine(
    settings.db.async_url,
    pool_size=3,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    echo=False,
    pool_pre_ping=True,
    connect_args={"server_settings": {"timezone": "UTC"}},
)
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,  # Keeps objects alive across commits
)


@asynccontextmanager
async def get_async_session(auto_commit: bool = True) -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        session: AsyncSession
        try:
            yield session
            if auto_commit:
                await session.commit()
        except Exception as ex:
            logger.error("Error during database session execution", error=str(ex))
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_async_session_dependency(auto_commit: bool = True) -> AsyncGenerator[AsyncSession]:
    async with get_async_session(auto_commit=auto_commit) as session:
        yield session  # Ensures the session is properly managed


async def test_db_connection():
    async with get_async_session() as session:
        result: CursorResult = await session.execute(text("SELECT 1"))

        return result
