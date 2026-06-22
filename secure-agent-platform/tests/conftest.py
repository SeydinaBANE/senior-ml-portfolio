import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from jose import jwt

from app.config import settings
from app.main import app

TEST_TENANT_ID = uuid.uuid4()
TEST_USER_ID = "test-user"


@pytest.fixture
def tenant_id() -> uuid.UUID:
    return TEST_TENANT_ID


@pytest.fixture
def auth_headers(tenant_id: uuid.UUID) -> dict[str, str]:
    token = jwt.encode(
        {"sub": TEST_USER_ID, "tenant_id": str(tenant_id)},
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def client() -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
