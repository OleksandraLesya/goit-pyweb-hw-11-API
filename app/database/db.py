# app/database/db.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Now we import the function get_settings() instead of the global settings object.
from app.conf.config import get_settings

# We call the get_settings() function to get the configuration object.
settings = get_settings()

# We get the database URL from the settings object.
DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create an asynchronous database engine.
# `echo=True` will log all SQL statements, which is useful for debugging.
engine = create_async_engine(DATABASE_URL, echo=True)

# Base class for our models.
# All our database models will inherit from this base.
Base = declarative_base()

# Configure the asynchronous session.
# `expire_on_commit=False` prevents objects from being expired after commit,
# which is helpful when working with ORM objects outside the session.
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Dependency function to get a database session.
async def get_db():
    """
    Provides an asynchronous database session.

    Yields:
        AsyncSession: An asynchronous database session.
    """
    async with async_session() as session:
        yield session
