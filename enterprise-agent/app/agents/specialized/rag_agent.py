from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

from app.agents.state import AgentState
from app.config import settings
from app.rag.retriever import retrieve

_llm = ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key)


async def rag_node(state: AgentState) -> AgentState:
    last_human = next(
        (m.content for m in reversed(state.messages) if isinstance(m, HumanMessage)),
        "",
    )
    chunks = await retrieve(query=str(last_human), tenant_id=state.tenant_id)
    context = "\n\n".join(chunks)

    prompt = f"Answer using this context:\n{context}\n\nQuestion: {last_human}"
    response: AIMessage = await _llm.ainvoke([HumanMessage(content=prompt)])

    return state.model_copy(
        update={
            "messages": [response],
            "context_chunks": chunks,
            "next_agent": "supervisor",
        }
    )
