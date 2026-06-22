from pydantic import BaseModel


class AgentAccessInput(BaseModel):
    tenant_id: str
    user_id: str
    agent_id: str
    action: str


class DataClassificationInput(BaseModel):
    tenant_id: str
    data_labels: list[str]
    agent_id: str
