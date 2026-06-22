from fastapi import APIRouter

from app.agent.graph import compiled_graph
from app.agent.state import ResearchState
from app.schemas.research import ResearchReport, ResearchRequest, SourceSummary
from app.tools.notion import create_notion_page_tool
from app.tools.slack import post_report_to_slack_tool

router = APIRouter()


@router.post("/research", response_model=ResearchReport)
async def research(body: ResearchRequest) -> ResearchReport:
    initial = ResearchState(topic=body.topic)
    final: ResearchState = await compiled_graph.ainvoke(initial)

    if body.post_to_slack:
        await post_report_to_slack_tool.ainvoke(
            {"title": f"Research: {body.topic}", "report": final.report_draft}
        )

    if body.save_to_notion and body.notion_parent_page_id:
        await create_notion_page_tool.ainvoke(
            {
                "title": body.topic,
                "content": final.report_draft,
                "parent_page_id": body.notion_parent_page_id,
            }
        )

    return ResearchReport(
        topic=body.topic,
        report=final.report_draft,
        verified_sources=[
            SourceSummary(
                url=s.url, title=s.title, confidence=s.confidence, excerpt=s.excerpt
            )
            for s in final.verified_sources
        ],
        total_sources_found=len(final.raw_results),
        total_sources_verified=len(final.verified_sources),
        search_queries_used=len(final.search_queries),
    )
