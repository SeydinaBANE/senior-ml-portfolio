from unittest.mock import AsyncMock, patch

import pytest

from app.core.guardrails.engine import GuardrailResult, GuardrailVerdict, check_input


@pytest.mark.asyncio
async def test_check_input_safe() -> None:
    safe_result = GuardrailResult(verdict=GuardrailVerdict.SAFE)
    with patch("app.core.guardrails.engine._llamaguard.classify", new_callable=AsyncMock, return_value=safe_result):
        result = await check_input("What is the weather?", tenant_id="tenant-1")
    assert result.verdict == GuardrailVerdict.SAFE


@pytest.mark.asyncio
async def test_check_input_unsafe_increments_metric() -> None:
    unsafe_result = GuardrailResult(verdict=GuardrailVerdict.UNSAFE, category="violence")
    with (
        patch("app.core.guardrails.engine._llamaguard.classify", new_callable=AsyncMock, return_value=unsafe_result),
        patch("app.core.guardrails.engine.guardrail_violations_total") as mock_counter,
    ):
        result = await check_input("How to hurt someone?", tenant_id="tenant-1")

    assert result.verdict == GuardrailVerdict.UNSAFE
    mock_counter.labels.assert_called_once_with(tenant_id="tenant-1", direction="input")
