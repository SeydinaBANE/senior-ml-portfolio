from uuid import UUID

from app.config import settings
from app.db.models import UsageEvent
from app.db.session import async_session


def _calculate_cost(input_tokens: int, output_tokens: int) -> float:
    return (
        input_tokens / 1000 * settings.price_per_1k_input_tokens
        + output_tokens / 1000 * settings.price_per_1k_output_tokens
    )


async def record_usage(
    tenant_id: UUID,
    user_id: UUID,
    agent_id: UUID,
    input_tokens: int,
    output_tokens: int,
    latency_ms: int,
) -> None:
    cost = _calculate_cost(input_tokens, output_tokens)
    async with async_session() as db:
        db.add(
            UsageEvent(
                tenant_id=tenant_id,
                user_id=user_id,
                agent_id=agent_id,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost,
                latency_ms=latency_ms,
            )
        )
        await db.commit()
