import asyncio
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.agent.state import ResearchState, VerifiedSource
from app.config import settings
from app.tools.search import web_search
from app.tools.verifier import verify_source

_llm = ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key, temperature=0.3)


class _QueryPlan(BaseModel):
    queries: list[str]


class _ReportReview(BaseModel):
    approved: bool
    feedback: str


async def plan_node(state: ResearchState) -> ResearchState:
    planner = _llm.with_structured_output(_QueryPlan)
    plan: _QueryPlan = await planner.ainvoke(
        [
            SystemMessage(content=f"Generate {settings.max_search_queries} diverse, specific search queries to research this topic. Return only the list."),
            HumanMessage(content=state.topic),
        ]
    )
    return state.model_copy(update={"search_queries": plan.queries, "next": "search"})


async def search_node(state: ResearchState) -> ResearchState:
    queries = state.search_queries[: settings.max_search_queries]
    all_results = await asyncio.gather(*[web_search(q) for q in queries])
    raw = [
        {"url": r.url, "title": r.title, "content": r.content, "score": r.score, "query": q}
        for q, results in zip(queries, all_results)
        for r in results
        if r.score >= settings.min_source_confidence
    ]
    return state.model_copy(update={"raw_results": raw, "next": "verify"})


async def verify_node(state: ResearchState) -> ResearchState:
    unique = {r["url"]: r for r in state.raw_results}.values()
    verifications = await asyncio.gather(
        *[verify_source(r["url"], state.topic) for r in unique]
    )
    verified = [
        VerifiedSource(
            url=v.url,
            title=next((r["title"] for r in state.raw_results if r["url"] == v.url), ""),
            excerpt=v.excerpt,
            confidence=v.confidence,
            verified=v.supports and v.confidence >= settings.min_source_confidence,
        )
        for v in verifications
    ]
    return state.model_copy(
        update={"verified_sources": [s for s in verified if s.verified], "next": "write"}
    )


async def write_node(state: ResearchState) -> ResearchState:
    context = "\n\n".join(
        f"[{s.title}]({s.url}) — confidence {s.confidence:.2f}\n{s.excerpt}"
        for s in state.verified_sources
    )
    response = await _llm.ainvoke(
        [
            SystemMessage(content="""Write a structured research report with:
## Executive Summary (2-3 sentences)
## Key Findings (bullet list with inline citations [Title](url))
## Analysis (2-3 paragraphs)
## Sources (numbered list)
Be factual. Cite sources inline."""),
            HumanMessage(content=f"Topic: {state.topic}\n\nVerified sources:\n{context}"),
        ]
    )
    return state.model_copy(
        update={"report_draft": str(response.content), "next": "review"}
    )


async def review_node(state: ResearchState) -> ResearchState:
    reviewer = _llm.with_structured_output(_ReportReview)

    if state.iteration >= 1:
        return state.model_copy(update={"next": "__end__"})

    review: _ReportReview = await reviewer.ainvoke(
        [
            SystemMessage(content="Review this research report. Approve if comprehensive and well-cited. Reject with feedback if it needs improvement."),
            HumanMessage(content=f"Topic: {state.topic}\n\nReport:\n{state.report_draft}"),
        ]
    )
    if review.approved:
        return state.model_copy(update={"next": "__end__"})
    return state.model_copy(
        update={
            "messages": [HumanMessage(content=f"Reviewer feedback: {review.feedback}")],
            "next": "write",
            "iteration": state.iteration + 1,
        }
    )


def _route(state: ResearchState) -> str:
    return state.next


def build_research_graph():  # type: ignore[no-untyped-def]
    from langgraph.graph import END, StateGraph

    graph = StateGraph(ResearchState)
    graph.add_node("plan", plan_node)
    graph.add_node("search", search_node)
    graph.add_node("verify", verify_node)
    graph.add_node("write", write_node)
    graph.add_node("review", review_node)

    graph.set_entry_point("plan")
    graph.add_conditional_edges("plan", _route, {"search": "search"})
    graph.add_conditional_edges("search", _route, {"verify": "verify"})
    graph.add_conditional_edges("verify", _route, {"write": "write"})
    graph.add_conditional_edges("write", _route, {"review": "review"})
    graph.add_conditional_edges("review", _route, {"write": "write", "__end__": END})

    return graph.compile()


compiled_graph = build_research_graph()
