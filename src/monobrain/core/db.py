import os
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


DB_URL = os.getenv("MONOBRAIN_DB_URL", "sqlite+aiosqlite:///./monobrain.db")
engine = create_async_engine(DB_URL)
Session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with Session() as session:
        yield session
