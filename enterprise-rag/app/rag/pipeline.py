from typing import Annotated, Literal

from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

from app.config import settings
from app.rag.generator import GeneratedAnswer, generate_answer
from app.rag.grader import filter_relevant_chunks
from app.rag.retriever.hybrid import hybrid_search
from app.rag.retriever.vector import ScoredChunk
from app.rag.rewriter import rewrite_query


class RAGState(BaseModel):
    question: str
    current_query: str = ""
    chunks: list[ScoredChunk] = Field(default_factory=list)
    relevant_chunks: list[ScoredChunk] = Field(default_factory=list)
    answer: GeneratedAnswer | None = None
    iteration: int = 0
    next: Literal["retrieve", "grade", "rewrite", "generate", "__end__"] = "retrieve"


async def retrieve_node(state: RAGState) -> RAGState:
    query = state.current_query or state.question
    chunks = await hybrid_search(query)
    return state.model_copy(update={"chunks": chunks, "next": "grade"})


async def grade_node(state: RAGState) -> RAGState:
    relevant = await filter_relevant_chunks(state.question, state.chunks)
    if relevant:
        return state.model_copy(update={"relevant_chunks": relevant, "next": "generate"})
    if state.iteration >= settings.max_retrieval_iterations - 1:
        return state.model_copy(update={"relevant_chunks": state.chunks, "next": "generate"})
    return state.model_copy(update={"next": "rewrite", "iteration": state.iteration + 1})


async def rewrite_node(state: RAGState) -> RAGState:
    rewritten = await rewrite_query(
        state.question,
        failed_reason=f"No relevant chunks found after iteration {state.iteration}",
    )
    return state.model_copy(update={"current_query": rewritten, "next": "retrieve"})


async def generate_node(state: RAGState) -> RAGState:
    answer = await generate_answer(state.question, state.relevant_chunks)
    return state.model_copy(update={"answer": answer, "next": "__end__"})


def _route(state: RAGState) -> str:
    return state.next


def build_self_rag_graph() -> StateGraph:
    graph = StateGraph(RAGState)

    graph.add_node("retrieve", retrieve_node)
    graph.add_node("grade", grade_node)
    graph.add_node("rewrite", rewrite_node)
    graph.add_node("generate", generate_node)

    graph.set_entry_point("retrieve")

    graph.add_conditional_edges(
        "retrieve", _route, {"grade": "grade"}
    )
    graph.add_conditional_edges(
        "grade", _route, {"generate": "generate", "rewrite": "rewrite"}
    )
    graph.add_conditional_edges(
        "rewrite", _route, {"retrieve": "retrieve"}
    )
    graph.add_edge("generate", END)

    return graph


compiled_rag = build_self_rag_graph().compile()


async def run_rag(question: str) -> tuple[str, list[ScoredChunk], int]:
    initial = RAGState(question=question, current_query=question)
    final: RAGState = await compiled_rag.ainvoke(initial)
    answer_text = final.answer.answer if final.answer else "No answer generated."
    return answer_text, final.relevant_chunks, final.iteration + 1
