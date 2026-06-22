from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.config import settings

_SYSTEM = """You are a query optimizer for a RAG system.
Rewrite the given question to be more specific, precise, and retrieval-friendly.
Return only the rewritten question, nothing else."""

_llm = ChatOpenAI(
    model=settings.openai_model, api_key=settings.openai_api_key, temperature=0.3
)


async def rewrite_query(question: str, failed_reason: str) -> str:
    response = await _llm.ainvoke(
        [
            SystemMessage(content=_SYSTEM),
            HumanMessage(
                content=f"Original question: {question}\nReason retrieval failed: {failed_reason}\nRewritten question:"
            ),
        ]
    )
    return str(response.content).strip()
