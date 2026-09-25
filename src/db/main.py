from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from src.config import Config
from sqlalchemy.orm import DeclarativeBase


# Base class for models
class Base(DeclarativeBase):
    pass

# Create the async engine
engine=create_async_engine(
    url=Config.DATABASE_URL,
    echo=Config.DEBUG
)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Create an async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Dependency to get an async DB session in FastAPI routes
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session