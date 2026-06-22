import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.security.auth import create_access_token
import uuid


TEST_TENANT_ID = uuid.uuid4()


@pytest.fixture
def tenant_id() -> uuid.UUID:
    return TEST_TENANT_ID


@pytest.fixture
def auth_headers(tenant_id: uuid.UUID) -> dict[str, str]:
    token = create_access_token(user_id="test-user", tenant_id=tenant_id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def client() -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
