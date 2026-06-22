import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from jose import jwt

from app.config import settings
from app.schemas.admin import AgentResponse, TenantResponse

_ADMIN_TENANT_ID = uuid.uuid4()
_ADMIN_USER_ID = "admin-user"


def _admin_headers() -> dict[str, str]:
    token = jwt.encode(
        {"sub": _ADMIN_USER_ID, "tenant_id": str(_ADMIN_TENANT_ID), "is_admin": True},
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return {"Authorization": f"Bearer {token}"}


def _user_headers() -> dict[str, str]:
    token = jwt.encode(
        {"sub": "regular-user", "tenant_id": str(_ADMIN_TENANT_ID), "is_admin": False},
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_tenant_requires_admin(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/tenants",
        json={"name": "acme", "allowed_agents": []},
        headers=_user_headers(),
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_tenant_success(client: AsyncClient) -> None:
    new_id = uuid.uuid4()
    from datetime import datetime, timezone

    mock_tenant = TenantResponse(
        id=new_id, name="acme", allowed_agents=[], created_at=datetime.now(timezone.utc)
    )
    with patch("app.api.routes.admin.async_session") as mock_session_cls:
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.add = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock(
            side_effect=lambda obj: setattr(obj, "__dict__", mock_tenant.model_dump())
        )
        mock_session_cls.return_value = mock_session

        with patch("app.api.routes.admin.TenantResponse.model_validate", return_value=mock_tenant):
            response = await client.post(
                "/api/v1/tenants",
                json={"name": "acme", "allowed_agents": []},
                headers=_admin_headers(),
            )

    assert response.status_code == 201
    assert response.json()["name"] == "acme"


@pytest.mark.asyncio
async def test_list_tenants_requires_admin(client: AsyncClient) -> None:
    response = await client.get("/api/v1/tenants", headers=_user_headers())
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_agents_requires_admin(client: AsyncClient) -> None:
    response = await client.get(
        f"/api/v1/tenants/{_ADMIN_TENANT_ID}/agents",
        headers=_user_headers(),
    )
    assert response.status_code == 403
