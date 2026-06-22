import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.core.billing.tracker import _calculate_cost, record_usage


def test_calculate_cost_zero_tokens() -> None:
    assert _calculate_cost(0, 0) == 0.0


def test_calculate_cost_accuracy() -> None:
    cost = _calculate_cost(1000, 500)
    assert abs(cost - 0.0125) < 1e-6


@pytest.mark.asyncio
async def test_record_usage_persists_event() -> None:
    with patch("app.core.billing.tracker.async_session") as mock_ctx:
        mock_session = AsyncMock()
        mock_ctx.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_ctx.return_value.__aexit__ = AsyncMock(return_value=False)

        await record_usage(
            tenant_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            agent_id=uuid.uuid4(),
            input_tokens=500,
            output_tokens=200,
            latency_ms=350,
        )

    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
