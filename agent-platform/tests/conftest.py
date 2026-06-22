import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from jose import jwt

from app.config import settings
from app.main import app

TEST_TENANT_ID = uuid.uuid4()
TEST_USER_ID = uuid.uuid4()


def _make_token(role: str = "developer") -> str:
    return jwt.encode(
        {"sub": str(TEST_USER_ID), "tenant_id": str(TEST_TENANT_ID), "role": role},
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )


@pytest.fixture
def admin_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {_make_token('admin')}"}


@pytest.fixture
def dev_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {_make_token('developer')}"}


@pytest.fixture
def user_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {_make_token('user')}"}


@pytest.fixture
async def client() -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
