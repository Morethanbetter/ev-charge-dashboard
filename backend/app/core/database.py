from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import get_settings
import os

settings = get_settings()

# Auto-convert postgresql:// to postgresql+asyncpg:// for async driver
db_url = settings.database_url
if db_url.startswith("postgresql://") and "+" not in db_url.split("://")[0]:
    db_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# SQLite needs different connect_args; also ensure data dir exists
if db_url.startswith("sqlite"):
    os.makedirs("data", exist_ok=True)
    engine = create_async_engine(
        db_url,
        echo=False,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_async_engine(db_url, echo=False, pool_pre_ping=True)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
