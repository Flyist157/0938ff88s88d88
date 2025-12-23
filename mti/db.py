from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from mti.config import settings


engine: AsyncEngine = create_async_engine(
    settings.db_url,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if settings.db_url.startswith("sqlite") else {},
)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    # Import models for metadata registration.
    from mti.models.db_models import Base  # noqa: WPS433

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # SQLite WAL is helpful for API + worker concurrency.
        if settings.db_url.startswith("sqlite"):
            await conn.execute(text("PRAGMA journal_mode=WAL;"))

