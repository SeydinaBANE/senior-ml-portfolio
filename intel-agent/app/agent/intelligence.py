from typing import cast

from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from app.config import settings
from app.observability.logging import get_logger
from app.observability.metrics import intelligence_requests_total, tokens_consumed_total
from app.observability.tracing import get_tracer
from app.schemas.intelligence import IntelRequest, IntelResponse

_llm = ChatOpenAI(model=settings.openai_model, api_key=SecretStr(settings.openai_api_key))
_search = DuckDuckGoSearchRun()
_log = get_logger(__name__)
_tracer = get_tracer()

_SYSTEM_PROMPT = """You are a competitive intelligence analyst.
Given recent search results about a company or topic, produce a structured report with:
- Recent developments (bullet list, max 5 items)
- Market positioning assessment
- Key risks and opportunities
- Confidence level: high | medium | low (based on source quality)
Cite facts only. Flag speculation explicitly."""


async def gather_intelligence(request: IntelRequest) -> IntelResponse:
    with _tracer.start_as_current_span("gather_intelligence") as span:
        span.set_attribute("query", request.query)

        _log.info("gathering intelligence", query=request.query)

        try:
            search_results = await _search.arun(request.query)
        except Exception as exc:
            _log.warning("search failed", error=str(exc))
            intelligence_requests_total.labels(status="search_error").inc()
            search_results = "No search results available."

        response = await _llm.ainvoke(
            [
                SystemMessage(content=_SYSTEM_PROMPT),
                HumanMessage(
                    content=f"Query: {request.query}\n\nSearch results:\n{search_results}"
                ),
            ]
        )

        ai_msg = cast(AIMessage, response)
        tokens = ai_msg.usage_metadata.get("total_tokens", 0) if ai_msg.usage_metadata else 0
        tokens_consumed_total.labels(operation="intelligence", model=settings.openai_model).inc(
            tokens
        )
        intelligence_requests_total.labels(status="success").inc()

        span.set_attribute("tokens_used", tokens)
        _log.info("intelligence report ready", tokens=tokens)

        return IntelResponse(
            query=request.query,
            report=str(response.content),
            tokens_used=tokens,
            sources_searched=True,
        )
