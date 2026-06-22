from uuid import UUID

from app.core.policy.opa_client import PolicyResult, opa_client
from app.schemas.policy import AgentAccessInput, DataClassificationInput


async def check_agent_access(
    tenant_id: UUID, user_id: str, agent_id: str, action: str
) -> PolicyResult:
    return await opa_client.evaluate(
        "platform.agent_access",
        AgentAccessInput(
            tenant_id=str(tenant_id),
            user_id=user_id,
            agent_id=agent_id,
            action=action,
        ).model_dump(),
    )


async def check_data_classification(
    tenant_id: UUID, data_labels: list[str], agent_id: str
) -> PolicyResult:
    return await opa_client.evaluate(
        "platform.data_classification",
        DataClassificationInput(
            tenant_id=str(tenant_id),
            data_labels=data_labels,
            agent_id=agent_id,
        ).model_dump(),
    )
