import os

os.environ.setdefault("OPENAI_API_KEY", "sk-test")
os.environ.setdefault("APP_ENV", "test")

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
