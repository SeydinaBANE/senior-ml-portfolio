from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BillingReportRequest(BaseModel):
    period_start: datetime
    period_end: datetime


class BillingReportResponse(BaseModel):
    tenant_id: UUID
    total_input_tokens: int
    total_output_tokens: int
    total_cost_usd: float
    total_requests: int
    avg_latency_ms: float
    period_start: datetime
    period_end: datetime
