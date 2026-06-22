import uuid
from unittest.mock import AsyncMock, patch

import pytest
from langchain_core.messages import HumanMessage

from app.agents.state import AgentState
from app.agents.supervisor import RoutingDecision, supervisor_node


@pytest.mark.asyncio
async def test_supervisor_routes_to_rag() -> None:
    state = AgentState(
        messages=[HumanMessage(content="What does our policy say about X?")],
        tenant_id=uuid.uuid4(),
        session_id="test",
    )

    with patch(
        "app.agents.supervisor._llm.ainvoke",
        new_callable=AsyncMock,
        return_value=RoutingDecision(next="rag"),
    ):
        result = await supervisor_node(state)

    assert result.next_agent == "rag"
    assert result.iteration_count == 1


@pytest.mark.asyncio
async def test_supervisor_stops_at_max_iterations() -> None:
    state = AgentState(
        messages=[HumanMessage(content="loop")],
        tenant_id=uuid.uuid4(),
        session_id="test",
        iteration_count=5,
    )
    result = await supervisor_node(state)
    assert result.next_agent == "__end__"
