import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.config import settings
import pytest


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url=settings.BASE_URL
    ) as ac:
        yield ac

@pytest.fixture
def test_user_data():
    return {
        "surname": "Иванов",
        "name": "Иван",
        "email": "ivan@test.com",
        "password": "TestPassword123",
        "repeat_password": "TestPassword123",
        "role_id": 1,
        "is_active": True
    }