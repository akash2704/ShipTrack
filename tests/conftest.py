import pytest
import pytest_asyncio
import sys
import os
from pathlib import Path
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

def pytest_configure(config):
    os.environ["TEST_ENV"] = "1"

def pytest_unconfigure(config):
    os.environ.pop("TEST_ENV", None)

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from main import app
from app.core.database import get_db, Base
from app.models.inventory import Location, Product, Inventory
from app.models.shipment import Shipment
from app.models.shipment_item import ShipmentItem
from app.models.location_tracking import LocationUpdate
from app.models.expense import Expense, ExpenseCategory, Vendor, Budget, BudgetLineItem
from app.models.user import User, UserRole
from app.core.auth import get_password_hash, create_access_token
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)

@pytest_asyncio.fixture(scope="function")
async def test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

async def override_get_db():
    async with TestSessionLocal() as session:
        yield session

@pytest_asyncio.fixture
async def client(test_db):
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.fixture
def sync_client(test_db):
    """Synchronous TestClient for WebSocket testing"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
@pytest_asyncio.fixture
async def test_user():
    """Create a test user."""
    async with TestSessionLocal() as session:
        user = User(
            email="testuser@example.com",
            hashed_password=get_password_hash("testpass123"),
            full_name="Test User",
            role=UserRole.EMPLOYEE
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

@pytest.fixture
def auth_headers(test_user):
    """Create auth headers with JWT token."""
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}
