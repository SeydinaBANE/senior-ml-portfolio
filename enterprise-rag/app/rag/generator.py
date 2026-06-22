from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.config import settings
from app.rag.retriever.vector import ScoredChunk

_SYSTEM = """You are a precise, factual assistant. Answer the question using ONLY
the provided context. If the context is insufficient, say so explicitly.
Cite source references inline as [source_name]."""


class GeneratedAnswer(BaseModel):
    answer: str
    has_sufficient_context: bool


_llm = ChatOpenAI(
    model=settings.openai_model, api_key=settings.openai_api_key, temperature=0
).with_structured_output(GeneratedAnswer)


async def generate_answer(question: str, chunks: list[ScoredChunk]) -> GeneratedAnswer:
    context = "\n\n".join(
        f"[{c.source}] {c.content}" for c in chunks
    )
    return await _llm.ainvoke(
        [
            SystemMessage(content=_SYSTEM),
            HumanMessage(content=f"Context:\n{context}\n\nQuestion: {question}"),
        ]
    )
