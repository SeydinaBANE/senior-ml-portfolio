from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.config import settings
from app.rag.retriever.vector import ScoredChunk

_SYSTEM = """You are a relevance grader. Given a question and a document chunk,
score whether the chunk is relevant to answering the question.
Respond with: {"relevant": true|false, "reason": "..."}"""


class GradeResult(BaseModel):
    relevant: bool
    reason: str


_llm = ChatOpenAI(
    model=settings.openai_model, api_key=settings.openai_api_key, temperature=0
).with_structured_output(GradeResult)


async def grade_chunk(question: str, chunk: ScoredChunk) -> GradeResult:
    return await _llm.ainvoke(
        [
            SystemMessage(content=_SYSTEM),
            HumanMessage(content=f"Question: {question}\n\nChunk: {chunk.content}"),
        ]
    )


async def filter_relevant_chunks(
    question: str, chunks: list[ScoredChunk]
) -> list[ScoredChunk]:
    import asyncio

    grades = await asyncio.gather(*[grade_chunk(question, c) for c in chunks])
    return [chunk for chunk, grade in zip(chunks, grades) if grade.relevant]
