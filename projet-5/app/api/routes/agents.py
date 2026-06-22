from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.api.deps import get_role, get_tenant_id, get_user_id
from app.core.rbac.enforcer import require_permission
from app.core.rbac.roles import Role
from app.db.models import AgentDefinition
from app.db.session import async_session
from app.schemas.agent import AgentCreateRequest, AgentResponse, AgentUpdateRequest

router = APIRouter()


def _to_response(agent: AgentDefinition) -> AgentResponse:
    return AgentResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        category=agent.category,
        tags=agent.tags,
        model=agent.model,
        is_public=agent.is_public,
        owner_id=agent.owner_id,
    )


@router.get("/agents", response_model=list[AgentResponse])
async def list_agents(
    tenant_id: UUID = Depends(get_tenant_id),
    role: Role = Depends(get_role),
) -> list[AgentResponse]:
    require_permission("agent:read")(role)
    async with async_session() as db:
        result = await db.execute(
            select(AgentDefinition).where(
                (AgentDefinition.tenant_id == tenant_id) | AgentDefinition.is_public
            )
        )
        agents = result.scalars().all()
    return [_to_response(a) for a in agents]


@router.post("/agents", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    body: AgentCreateRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    user_id: UUID = Depends(get_user_id),
    role: Role = Depends(get_role),
) -> AgentResponse:
    require_permission("agent:create")(role)
    async with async_session() as db:
        agent = AgentDefinition(
            name=body.name,
            description=body.description,
            category=body.category,
            system_prompt=body.system_prompt,
            tools=body.tools,
            model=body.model,
            tags=body.tags,
            is_public=body.is_public,
            owner_id=user_id,
            tenant_id=tenant_id,
        )
        db.add(agent)
        await db.commit()
        await db.refresh(agent)
    return _to_response(agent)


@router.put("/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: UUID,
    body: AgentUpdateRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    role: Role = Depends(get_role),
) -> AgentResponse:
    require_permission("agent:update")(role)
    async with async_session() as db:
        result = await db.execute(
            select(AgentDefinition).where(
                AgentDefinition.id == agent_id,
                AgentDefinition.tenant_id == tenant_id,
            )
        )
        agent = result.scalar_one_or_none()
        if agent is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
        for field, value in body.model_dump(exclude_none=True).items():
            setattr(agent, field, value)
        await db.commit()
        await db.refresh(agent)
    return _to_response(agent)


@router.delete("/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: UUID,
    tenant_id: UUID = Depends(get_tenant_id),
    user_id: UUID = Depends(get_user_id),
    role: Role = Depends(get_role),
) -> None:
    require_permission("agent:delete")(role)
    async with async_session() as db:
        result = await db.execute(
            select(AgentDefinition).where(
                AgentDefinition.id == agent_id,
                AgentDefinition.tenant_id == tenant_id,
            )
        )
        agent = result.scalar_one_or_none()
        if agent is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
        await db.delete(agent)
        await db.commit()
