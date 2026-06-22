import time
from typing import cast

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from app.config import settings
from app.observability.logging import get_logger
from app.observability.metrics import summarization_latency, tokens_consumed_total
from app.observability.tracing import get_tracer
from app.schemas.summarize import SummaryRequest, SummaryResponse

_llm = ChatOpenAI(model=settings.openai_model, api_key=SecretStr(settings.openai_api_key))
_log = get_logger(__name__)
_tracer = get_tracer()

_SYSTEM_PROMPT = """You are an expert document analyst.
Produce a structured summary with:
- Key points (bullet list)
- Main conclusion (1-2 sentences)
- Sentiment: positive | neutral | negative
Keep it concise and factual."""


async def summarize_document(request: SummaryRequest) -> SummaryResponse:
    with _tracer.start_as_current_span("summarize_document") as span:
        span.set_attribute("document.length", len(request.content))
        span.set_attribute("language", request.language)

        _log.info("summarizing document", length=len(request.content), language=request.language)

        start = time.monotonic()
        response = await _llm.ainvoke(
            [
                SystemMessage(content=_SYSTEM_PROMPT),
                HumanMessage(content=f"Document:\n{request.content}"),
            ]
        )
        latency = time.monotonic() - start

        ai_msg = cast(AIMessage, response)
        tokens = ai_msg.usage_metadata.get("total_tokens", 0) if ai_msg.usage_metadata else 0
        summarization_latency.labels(model=settings.openai_model).observe(latency)
        tokens_consumed_total.labels(operation="summarize", model=settings.openai_model).inc(tokens)

        span.set_attribute("tokens_used", tokens)
        _log.info("summary complete", latency_ms=round(latency * 1000), tokens=tokens)

        return SummaryResponse(
            summary=str(response.content),
            tokens_used=tokens,
            latency_ms=round(latency * 1000),
            model=settings.openai_model,
        )
