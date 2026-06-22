import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.tenancy.isolation import assert_agent_belongs_to_tenant, resolve_tenant
from app.db.models import Agent, Tenant


@pytest.mark.asyncio
async def test_resolve_tenant_found() -> None:
    tenant_id = uuid.uuid4()
    mock_tenant = MagicMock(spec=Tenant)
    mock_tenant.id = tenant_id

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_tenant

    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)
    mock_session.execute = AsyncMock(return_value=mock_result)

    with patch("app.core.tenancy.isolation.async_session", return_value=mock_session):
        tenant = await resolve_tenant(tenant_id)

    assert tenant.id == tenant_id


@pytest.mark.asyncio
async def test_resolve_tenant_not_found_raises() -> None:
    tenant_id = uuid.uuid4()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None

    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)
    mock_session.execute = AsyncMock(return_value=mock_result)

    with patch("app.core.tenancy.isolation.async_session", return_value=mock_session):
        with pytest.raises(ValueError, match="not found"):
            await resolve_tenant(tenant_id)


@pytest.mark.asyncio
async def test_assert_agent_belongs_to_tenant_ok() -> None:
    tenant_id = uuid.uuid4()
    mock_agent = MagicMock(spec=Agent)
    mock_agent.id = "agent-1"
    mock_agent.tenant_id = tenant_id

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_agent

    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)
    mock_session.execute = AsyncMock(return_value=mock_result)

    with patch("app.core.tenancy.isolation.async_session", return_value=mock_session):
        agent = await assert_agent_belongs_to_tenant("agent-1", tenant_id)

    assert agent.id == "agent-1"


@pytest.mark.asyncio
async def test_assert_agent_belongs_to_tenant_wrong_tenant_raises() -> None:
    tenant_id = uuid.uuid4()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None

    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)
    mock_session.execute = AsyncMock(return_value=mock_result)

    with patch("app.core.tenancy.isolation.async_session", return_value=mock_session):
        with pytest.raises(PermissionError):
            await assert_agent_belongs_to_tenant("agent-other", tenant_id)
