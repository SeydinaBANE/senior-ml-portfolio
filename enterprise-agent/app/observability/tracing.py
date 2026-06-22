from langfuse import Langfuse
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from app.config import settings

_tracer: trace.Tracer | None = None


def setup_tracing() -> None:
    resource = Resource(attributes={"service.name": "enterprise-agent"})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)

    if settings.langfuse_public_key:
        Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
        )


def get_tracer() -> trace.Tracer:
    global _tracer
    if _tracer is None:
        _tracer = trace.get_tracer("enterprise-agent")
    return _tracer
