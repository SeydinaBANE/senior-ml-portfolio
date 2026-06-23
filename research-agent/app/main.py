from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import health, research, tools
from app.config import settings
from app.middleware import setup_middlewares


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_middlewares(app, max_requests=settings.rate_limit_max_requests, window_sec=settings.rate_limit_window_sec)
    yield


app = FastAPI(title="Research Agent", version="0.1.0", lifespan=lifespan)

app.include_router(health.router, tags=["health"])
app.include_router(research.router, prefix=settings.api_v1_prefix, tags=["research"])
app.include_router(tools.router, prefix=settings.api_v1_prefix, tags=["tools"])
