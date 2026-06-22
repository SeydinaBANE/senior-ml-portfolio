from uuid import UUID

from sqlalchemy import select

from app.db.models import Agent, Tenant
from app.db.session import async_session


async def resolve_tenant(tenant_id: UUID) -> Tenant:
    async with async_session() as db:
        result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = result.scalar_one_or_none()
        if tenant is None:
            raise ValueError(f"Tenant {tenant_id} not found")
        return tenant


async def assert_agent_belongs_to_tenant(agent_id: str, tenant_id: UUID) -> Agent:
    async with async_session() as db:
        result = await db.execute(
            select(Agent).where(Agent.id == agent_id, Agent.tenant_id == tenant_id)
        )
        agent = result.scalar_one_or_none()
        if agent is None:
            raise PermissionError(f"Agent {agent_id} not accessible for tenant {tenant_id}")
        return agent
