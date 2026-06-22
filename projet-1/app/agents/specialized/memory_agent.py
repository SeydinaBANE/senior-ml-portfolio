from langchain_core.messages import AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.agents.state import AgentState
from app.config import settings
from app.memory.persistent import load_session_history

_llm = ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key)


async def memory_node(state: AgentState) -> AgentState:
    history = await load_session_history(
        tenant_id=state.tenant_id, session_id=state.session_id
    )
    context_msg = SystemMessage(content=f"Past conversation summary:\n{history}")
    response: AIMessage = await _llm.ainvoke([context_msg] + state.messages)
    return state.model_copy(
        update={"messages": [response], "next_agent": "supervisor"}
    )
