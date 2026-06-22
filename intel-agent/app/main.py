from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import health, intelligence, summarize
from app.config import settings
from app.observability.logging import setup_logging
from app.observability.metrics import start_metrics_server
from app.observability.tracing import setup_tracing


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    start_metrics_server()
    setup_tracing(fastapi_app=app)
    yield


app = FastAPI(title="Intel Agent", version="0.1.0", lifespan=lifespan)

app.include_router(health.router, tags=["health"])
app.include_router(summarize.router, prefix=settings.api_v1_prefix, tags=["summarize"])
app.include_router(intelligence.router, prefix=settings.api_v1_prefix, tags=["intelligence"])
