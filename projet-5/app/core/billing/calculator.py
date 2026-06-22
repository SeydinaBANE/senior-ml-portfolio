from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select

from app.db.models import UsageEvent
from app.db.session import async_session


@dataclass
class BillingSummary:
    tenant_id: UUID
    total_input_tokens: int
    total_output_tokens: int
    total_cost_usd: float
    total_requests: int
    avg_latency_ms: float
    period_start: datetime
    period_end: datetime


async def get_billing_summary(
    tenant_id: UUID, period_start: datetime, period_end: datetime
) -> BillingSummary:
    async with async_session() as db:
        result = await db.execute(
            select(
                func.sum(UsageEvent.input_tokens),
                func.sum(UsageEvent.output_tokens),
                func.sum(UsageEvent.cost_usd),
                func.count(UsageEvent.id),
                func.avg(UsageEvent.latency_ms),
            ).where(
                UsageEvent.tenant_id == tenant_id,
                UsageEvent.occurred_at >= period_start,
                UsageEvent.occurred_at <= period_end,
            )
        )
        row = result.one()

    return BillingSummary(
        tenant_id=tenant_id,
        total_input_tokens=int(row[0] or 0),
        total_output_tokens=int(row[1] or 0),
        total_cost_usd=float(row[2] or 0.0),
        total_requests=int(row[3] or 0),
        avg_latency_ms=float(row[4] or 0.0),
        period_start=period_start,
        period_end=period_end,
    )
