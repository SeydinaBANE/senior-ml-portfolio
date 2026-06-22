from datetime import datetime, timezone
from uuid import UUID

from app.core.audit.models import AuditEventType
from app.db.models import AuditLog
from app.db.session import async_session


async def log_event(
    tenant_id: UUID,
    user_id: str,
    agent_id: str,
    event_type: AuditEventType,
    payload: dict,
    verdict: str | None = None,
) -> None:
    async with async_session() as db:
        db.add(
            AuditLog(
                tenant_id=tenant_id,
                user_id=user_id,
                agent_id=agent_id,
                event_type=event_type.value,
                payload=payload,
                verdict=verdict,
                occurred_at=datetime.now(timezone.utc),
            )
        )
        await db.commit()
