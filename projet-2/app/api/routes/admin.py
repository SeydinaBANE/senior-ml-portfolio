from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.api.deps import get_tenant_id
from app.db.models import AuditLog
from app.db.session import async_session
from pydantic import BaseModel

router = APIRouter()


class AuditLogEntry(BaseModel):
    id: UUID
    user_id: str
    agent_id: str
    event_type: str
    verdict: str | None
    occurred_at: datetime


@router.get("/audit", response_model=list[AuditLogEntry])
async def list_audit_logs(
    tenant_id: UUID = Depends(get_tenant_id),
    limit: int = 100,
) -> list[AuditLogEntry]:
    async with async_session() as db:
        result = await db.execute(
            select(AuditLog)
            .where(AuditLog.tenant_id == tenant_id)
            .order_by(AuditLog.occurred_at.desc())
            .limit(limit)
        )
        logs = result.scalars().all()
        return [
            AuditLogEntry(
                id=log.id,
                user_id=log.user_id,
                agent_id=log.agent_id,
                event_type=log.event_type,
                verdict=log.verdict,
                occurred_at=log.occurred_at,
            )
            for log in logs
        ]
