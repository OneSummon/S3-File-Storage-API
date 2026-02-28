from contextlib import asynccontextmanager
from datetime import datetime

from httpx import ASGITransport, AsyncClient
import pytest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.redis import get_redis
from app.core.security import get_current_user, hash_password
from app.database.models import Base
from main import app
from app.database.database import get_session

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL)
TestSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(db_session: AsyncSession):
    async def override_get_session():
        yield db_session
    
    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def auth_client(db_session: AsyncSession, test_user):
    async def override_get_session():
        yield db_session
    
    async def override_get_current_user():
        return test_user
    
    async def override_get_redis():
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.set = AsyncMock()
        mock_redis.incr = AsyncMock()
        return mock_redis

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_redis] = override_get_redis

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession):
    from app.database.models import User

    user = User(
        username="testuser",
        hashed_password=hash_password("testpassword"),
        role="user",
        created_at=datetime.now()
    )
    db_session.add(user)
    await db_session.commit()

    return user


@pytest.fixture
async def test_files(db_session: AsyncSession, test_user):
    from app.database.models import File

    files = [
        File(
            owner_id=test_user.id,
            original_filename="file.jpg",
            stored_filename="uuid1.jpg",
            url="https://s3.selectel.ru/uuid1.jpg",
            bucket="test-bucket",
            size=100,
            content_type="image",
            created_at=datetime.now()
        ),
        File(
            owner_id=test_user.id,
            original_filename="file2.jpg",
            stored_filename="uuid2.jpg",
            url="https://s3.selectel.ru/uuid2.jpg",
            bucket="test-bucket",
            size=200,
            content_type="image",
            created_at=datetime.now()
        ),
    ]

    for file in files:
        db_session.add(file)
    
    await db_session.commit()
    return files


@pytest.fixture
def mock_get_client():
    mock_s3 = AsyncMock()
    mock_s3.delete_object = AsyncMock()
    mock_s3.put_object = AsyncMock()

    @asynccontextmanager
    async def _mock_get_client():
        yield mock_s3
    
    return _mock_get_client