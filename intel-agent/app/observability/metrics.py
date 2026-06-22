from prometheus_client import Counter, Histogram, start_http_server

from app.config import settings

summarization_latency = Histogram(
    "summarization_latency_seconds",
    "Time to summarize a document",
    labelnames=["model"],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
)

intelligence_requests_total = Counter(
    "intelligence_requests_total",
    "Total competitive intelligence requests",
    labelnames=["status"],
)

tokens_consumed_total = Counter(
    "tokens_consumed_total",
    "Total LLM tokens consumed",
    labelnames=["operation", "model"],
)


def start_metrics_server() -> None:
    if settings.app_env != "test":
        start_http_server(settings.metrics_port)
