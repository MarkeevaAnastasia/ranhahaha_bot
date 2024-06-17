__all__ = [
    "async_session_maker",
    "async_create_table",
]

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from .models import Base

engine: AsyncEngine = create_async_engine(url="sqlite+aiosqlite:///instance/database.db", echo=True)
async_session_maker: AsyncSession = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# TODO Костыль переписать под AsyncEngine
# Создание таблицы в sqlite БД
# https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#synopsis-orm
async def async_create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
