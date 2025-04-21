import asyncio
import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)

# Base model definition
Base = declarative_base()


class Database:
    def __init__(self) -> None:
        """Initialize the database connection parameters"""
        postgres_host = os.getenv("POSTGRES_HOST")
        postgres_port = os.getenv("POSTGRES_PORT")
        postgres_user = os.getenv("POSTGRES_USER")
        postgres_password = os.getenv("POSTGRES_PASSWORD")
        postgres_db = os.getenv("POSTGRES_DB")
        self.database_url = (
            f"postgresql+asyncpg://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
        )

        self.engine = None
        self.async_session_maker = None
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        """Initialize the async SQLAlchemy engine"""
        if self.engine is None:
            logger.info("Initializing database connection")
            self.engine = create_async_engine(
                self.database_url, echo=False, pool_size=5, max_overflow=10, pool_pre_ping=True
            )

            self.async_session_maker = async_sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)
            logger.info("Database connection initialized")

    async def create_tables(self) -> None:
        """Create all tables defined in models"""
        logger.info("Creating database tables if they don't exist")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created or already exist")

    async def close(self) -> None:
        """Close database connection"""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connection closed")

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Context manager to get a session with lock"""
        if not self.engine:
            await self.initialize()

        async with self._lock:
            session = self.async_session_maker()
            try:
                yield session
            finally:
                await session.close()

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[AsyncSession, None]:
        """Context manager to get a session with an active transaction"""
        async with self.get_session() as session, session.begin():
            yield session


# Create a singleton database instance
db = Database()


# Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides a database session"""
    async with db.get_session() as session:
        yield session
