from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.api.deps import get_tenant_id, require_admin
from app.db.models import Agent, AuditLog, Tenant
from app.db.session import async_session
from app.schemas.admin import (
    AgentCreate,
    AgentResponse,
    AuditLogEntry,
    TenantCreate,
    TenantResponse,
)

router = APIRouter()


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
        return [AuditLogEntry.model_validate(log) for log in result.scalars().all()]


@router.post(
    "/tenants",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def create_tenant(body: TenantCreate) -> TenantResponse:
    async with async_session() as db:
        existing = await db.execute(select(Tenant).where(Tenant.name == body.name))
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Tenant '{body.name}' already exists",
            )
        tenant = Tenant(name=body.name, allowed_agents=body.allowed_agents)
        db.add(tenant)
        await db.commit()
        await db.refresh(tenant)
        return TenantResponse.model_validate(tenant)


@router.get(
    "/tenants",
    response_model=list[TenantResponse],
    dependencies=[Depends(require_admin)],
)
async def list_tenants() -> list[TenantResponse]:
    async with async_session() as db:
        result = await db.execute(select(Tenant).order_by(Tenant.created_at.desc()))
        return [TenantResponse.model_validate(t) for t in result.scalars().all()]


@router.post(
    "/tenants/{tenant_id}/agents",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def create_agent(tenant_id: UUID, body: AgentCreate) -> AgentResponse:
    async with async_session() as db:
        tenant = await db.get(Tenant, tenant_id)
        if tenant is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
        existing = await db.get(Agent, body.id)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Agent '{body.id}' already exists",
            )
        agent = Agent(
            id=body.id,
            tenant_id=tenant_id,
            name=body.name,
            description=body.description,
            config=body.config,
        )
        db.add(agent)
        await db.commit()
        await db.refresh(agent)
        return AgentResponse.model_validate(agent)


@router.get(
    "/tenants/{tenant_id}/agents",
    response_model=list[AgentResponse],
    dependencies=[Depends(require_admin)],
)
async def list_agents(tenant_id: UUID) -> list[AgentResponse]:
    async with async_session() as db:
        result = await db.execute(
            select(Agent).where(Agent.tenant_id == tenant_id).order_by(Agent.name)
        )
        return [AgentResponse.model_validate(a) for a in result.scalars().all()]
