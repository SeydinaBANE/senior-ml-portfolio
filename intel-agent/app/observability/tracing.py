from langfuse import Langfuse
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.config import settings


def setup_tracing(fastapi_app: object | None = None) -> None:
    if settings.app_env == "test":
        return

    resource = Resource({"service.name": settings.otel_service_name})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint))
    )
    trace.set_tracer_provider(provider)

    if fastapi_app is not None:
        FastAPIInstrumentor.instrument_app(fastapi_app)  # type: ignore[arg-type]

    if settings.langfuse_public_key:
        Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
        )


def get_tracer() -> trace.Tracer:
    return trace.get_tracer(settings.otel_service_name)
