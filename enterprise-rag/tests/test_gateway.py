import pytest

from app.gateway import (
    FailingProvider,
    HttpLLMProvider,
    LLMGateway,
    LLMProviderError,
    LocalProvider,
    build_default_gateway,
)
from app.schemas.llm import LLMRequest, Message, Role


def _req(text: str) -> LLMRequest:
    return LLMRequest(messages=[Message(role=Role.USER, content=text)])


@pytest.mark.asyncio
async def test_local_provider_echoes_last_user_message() -> None:
    gateway = LLMGateway(primary=LocalProvider("m1"), fallback=LocalProvider("m2"))
    response = await gateway.complete(_req("bonjour"))
    assert response.content == "bonjour"
    assert response.model == "m1"
    assert response.used_fallback is False


@pytest.mark.asyncio
async def test_gateway_falls_back_on_primary_failure() -> None:
    gateway = LLMGateway(primary=FailingProvider("bad"), fallback=LocalProvider("good"))
    response = await gateway.complete(_req("salut"))
    assert response.used_fallback is True
    assert response.model == "good"
    assert response.content == "salut"


@pytest.mark.asyncio
async def test_gateway_streams_tokens() -> None:
    gateway = LLMGateway(primary=LocalProvider("m1"), fallback=LocalProvider("m2"))
    tokens = [token async for token in gateway.stream(_req("un deux trois"))]
    assert tokens == ["un", "deux", "trois"]


@pytest.mark.asyncio
async def test_http_provider_raises_on_transport_error() -> None:
    import httpx

    transport = httpx.MockTransport(lambda request: httpx.Response(500))
    async with httpx.AsyncClient(base_url="http://llm", transport=transport) as client:
        provider = HttpLLMProvider(model="remote", client=client)
        with pytest.raises(LLMProviderError):
            await provider.complete(_req("ping"))


def test_build_default_gateway_offline_uses_local() -> None:
    gateway = build_default_gateway()
    assert isinstance(gateway, LLMGateway)
