from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_role, get_tenant_id
from app.core.billing.calculator import get_billing_summary
from app.core.rbac.enforcer import require_permission
from app.core.rbac.roles import Role
from app.schemas.billing import BillingReportRequest, BillingReportResponse

router = APIRouter()


@router.post("/billing/report", response_model=BillingReportResponse)
async def billing_report(
    body: BillingReportRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    role: Role = Depends(get_role),
) -> BillingReportResponse:
    require_permission("billing:read")(role)
    summary = await get_billing_summary(tenant_id, body.period_start, body.period_end)
    return BillingReportResponse(
        tenant_id=summary.tenant_id,
        total_input_tokens=summary.total_input_tokens,
        total_output_tokens=summary.total_output_tokens,
        total_cost_usd=summary.total_cost_usd,
        total_requests=summary.total_requests,
        avg_latency_ms=summary.avg_latency_ms,
        period_start=summary.period_start,
        period_end=summary.period_end,
    )
