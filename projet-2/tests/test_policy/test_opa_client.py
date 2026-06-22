import pytest
import respx
import httpx

from app.core.policy.opa_client import OPAClient, PolicyResult


@pytest.mark.asyncio
async def test_opa_client_allow() -> None:
    client = OPAClient()
    with respx.mock:
        respx.post("http://localhost:8181/v1/data/platform/agent_access").mock(
            return_value=httpx.Response(200, json={"result": {"allow": True, "reason": ""}})
        )
        result = await client.evaluate("platform.agent_access", {"tenant_id": "t1", "agent_id": "a1", "action": "invoke"})

    assert result.allowed is True


@pytest.mark.asyncio
async def test_opa_client_deny() -> None:
    client = OPAClient()
    with respx.mock:
        respx.post("http://localhost:8181/v1/data/platform/agent_access").mock(
            return_value=httpx.Response(200, json={"result": {"allow": False, "reason": "agent not allowed for this tenant"}})
        )
        result = await client.evaluate("platform.agent_access", {"tenant_id": "t1", "agent_id": "banned", "action": "invoke"})

    assert result.allowed is False
    assert "agent not allowed" in result.reason
