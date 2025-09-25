import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Base class for models
Base = declarative_base()

# Initialize engine and session maker as None
engine = None
AsyncSessionLocal = None

async def init_database():
    """Initialize database connection"""
    global engine, AsyncSessionLocal

    if engine is None:
        # Determine database URL based on environment
        if os.getenv("TEST_ENV"):
            # Use a shared file database instead of in-memory
            DATABASE_URL = "sqlite+aiosqlite:///./test_shiptrack.db"
        else:
            DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

        # Create engine with appropriate settings
        if "sqlite" in DATABASE_URL:
            from sqlalchemy.pool import StaticPool
            engine = create_async_engine(
                DATABASE_URL,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        else:
            engine = create_async_engine(DATABASE_URL)

        AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        # Create tables for test environment
        if os.getenv("TEST_ENV"):
            # Import all models to ensure they're registered
            from app.models.inventory import Location, Product, Inventory
            from app.models.shipment import Shipment
            from app.models.shipment_item import ShipmentItem
            from app.models.location_tracking import LocationUpdate

            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)  # Clean slate
                await conn.run_sync(Base.metadata.create_all)

# Dependency to get database session
async def get_db():
    # Initialize database if not already done
    if engine is None:
        await init_database()

    async with AsyncSessionLocal() as session:
        yield session
