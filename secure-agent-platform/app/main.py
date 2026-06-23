from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_client import start_http_server

from app.api.routes import admin, agents, health
from app.config import settings
from app.db.session import engine
from app.middleware import setup_middlewares
from app.observability.logging import setup_logging
from app.observability.tracing import setup_tracing


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    setup_tracing()
    start_http_server(settings.metrics_port)
    setup_middlewares(
        app,
        max_requests=settings.rate_limit_max_requests,
        window_sec=settings.rate_limit_window_sec,
    )
    yield
    await engine.dispose()


app = FastAPI(title="Secure Agent Platform", version="0.1.0", lifespan=lifespan)

app.include_router(health.router, tags=["health"])
app.include_router(agents.router, prefix=settings.api_v1_prefix, tags=["agents"])
app.include_router(admin.router, prefix=settings.api_v1_prefix, tags=["admin"])
