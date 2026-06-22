import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.core.router.classifier import RoutingDecision, classify_intent


@pytest.mark.asyncio
async def test_classify_returns_agent_name() -> None:
    mock_decision = RoutingDecision(
        agent_name="hr-assistant",
        confidence=0.92,
        reasoning="Message is about HR policies",
    )
    mock_agents = []

    with (
        patch("app.core.router.classifier.async_session") as mock_ctx,
        patch("app.core.router.classifier._llm.ainvoke", new_callable=AsyncMock, return_value=mock_decision),
    ):
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = mock_agents
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_ctx.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_ctx.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await classify_intent("What is the vacation policy?", uuid.uuid4())

    assert result.agent_name == "hr-assistant"
    assert result.confidence == 0.92


@pytest.mark.asyncio
async def test_classify_returns_none_when_no_agents() -> None:
    with patch("app.core.router.classifier.async_session") as mock_ctx:
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_ctx.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_ctx.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await classify_intent("Hello", uuid.uuid4())

    assert result.agent_name == "__none__"
    assert result.confidence == 0.0
